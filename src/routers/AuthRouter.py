# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from slowapi.errors import RateLimitExceeded

from domain.schemas.AuthSchema import LoginRequest, TokenResponse, RefreshTokenRequest, FuncionarioAuth
from infra.orm.models import FuncionarioModel as FuncionarioDB
from infra.database import get_db
from infra.security import verify_password, create_access_token, create_refresh_token, verify_refresh_token
from infra.dependencies import get_current_active_user
from infra.rate_limit import limiter, get_rate_limit
from services.AuditoriaService import AuditoriaService
from settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse, tags=["Autenticação"],
             summary="Login - pública")
@limiter.limit(get_rate_limit("critical"))
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        funcionario = db.query(FuncionarioDB).filter(
            FuncionarioDB.cpf == login_data.cpf).first()

        if not funcionario or not verify_password(login_data.senha, funcionario.senha):
            raise HTTPException(status_code=401, detail="CPF ou senha inválidos",
                                headers={"WWW-Authenticate": "Bearer"})

        access_token = create_access_token(
            data={"sub": funcionario.cpf, "id": funcionario.id_funcionario, "grupo": funcionario.grupo},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"sub": funcionario.cpf, "id": funcionario.id_funcionario, "grupo": funcionario.grupo}
        )

        AuditoriaService.registrar_acao(db=db, funcionario_id=funcionario.id_funcionario,
            acao="LOGIN", recurso="AUTH", request=request)

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/refresh", response_model=TokenResponse, tags=["Autenticação"],
             summary="Refresh token - pública")
@limiter.limit(get_rate_limit("critical"))
async def refresh_token(request: Request, refresh_data: RefreshTokenRequest,
                        db: Session = Depends(get_db)):
    try:
        payload = verify_refresh_token(refresh_data.refresh_token)
        cpf = payload.get("sub")
        funcionario = db.query(FuncionarioDB).filter(FuncionarioDB.cpf == cpf).first()
        if not funcionario:
            raise HTTPException(status_code=401, detail="Funcionário não encontrado")

        access_token = create_access_token(
            data={"sub": funcionario.cpf, "id": funcionario.id_funcionario, "grupo": funcionario.grupo},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        new_refresh = create_refresh_token(
            data={"sub": funcionario.cpf, "id": funcionario.id_funcionario, "grupo": funcionario.grupo}
        )
        return TokenResponse(
            access_token=access_token, refresh_token=new_refresh,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/auth/me", response_model=FuncionarioAuth, tags=["Autenticação"],
            summary="Dados do usuário atual - protegida")
async def get_me(current_user: FuncionarioAuth = Depends(get_current_active_user)):
    return current_user


@router.post("/auth/logout", tags=["Autenticação"], summary="Logout - pública")
async def logout():
    return {"message": "Logout realizado com sucesso"}

# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi.errors import RateLimitExceeded

from infra.database import get_db
from infra.orm.models import ClienteModel as ClienteDB
from infra.dependencies import get_current_active_user, require_group
from infra.rate_limit import limiter, get_rate_limit
from domain.schemas.AuthSchema import FuncionarioAuth
from domain.entities.Cliente import Cliente
from services.AuditoriaService import AuditoriaService

router = APIRouter()


@router.get("/cliente/", tags=["Cliente"], status_code=200,
            summary="Listar todos - protegida")
@limiter.limit(get_rate_limit("moderate"))
async def get_cliente(
    request: Request,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    try:
        return db.query(ClienteDB).all()
    except RateLimitExceeded: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cliente/{id}", tags=["Cliente"], status_code=200,
            summary="Listar um - protegida")
@limiter.limit(get_rate_limit("moderate"))
async def get_cliente_por_id(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    try:
        c = db.query(ClienteDB).filter(ClienteDB.id_cliente == id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        return c
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cliente/", tags=["Cliente"], status_code=201,
             summary="Criar novo - grupos 1 e 3")
@limiter.limit(get_rate_limit("restrictive"))
async def post_cliente(
    request: Request,
    corpo: Cliente,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1, 3]))
):
    try:
        novo = ClienteDB(nome=corpo.nome, cpf=corpo.cpf, telefone=corpo.telefone)
        db.add(novo); db.commit(); db.refresh(novo)

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="CREATE", recurso="CLIENTE", recurso_id=novo.id_cliente,
            dados_novos=novo, request=request)

        return novo
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cliente/{id}", tags=["Cliente"], status_code=200,
            summary="Editar - grupos 1 e 3")
@limiter.limit(get_rate_limit("restrictive"))
async def put_cliente(
    request: Request,
    id: int,
    corpo: Cliente,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1, 3]))
):
    try:
        c = db.query(ClienteDB).filter(ClienteDB.id_cliente == id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        dados_antigos = c.__dict__.copy()
        c.nome = corpo.nome; c.cpf = corpo.cpf; c.telefone = corpo.telefone
        db.commit(); db.refresh(c)

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="UPDATE", recurso="CLIENTE", recurso_id=c.id_cliente,
            dados_antigos=dados_antigos, dados_novos=c, request=request)

        return c
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cliente/{id}", tags=["Cliente"], status_code=204,
               summary="Excluir - grupo 1")
@limiter.limit(get_rate_limit("critical"))
async def delete_cliente(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        c = db.query(ClienteDB).filter(ClienteDB.id_cliente == id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="DELETE", recurso="CLIENTE", recurso_id=c.id_cliente,
            dados_antigos=c, request=request)

        db.delete(c); db.commit()
        return None
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

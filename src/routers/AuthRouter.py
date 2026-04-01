# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from infra.database import get_db
from infra.orm.models import FuncionarioModel
from infra.security import verify_password, create_access_token

router = APIRouter()

@router.post("/auth/login", tags=["Autenticação"], status_code=200)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login com CPF e senha.
    - username = CPF do funcionário
    - password = senha do funcionário
    """
    # Busca funcionário pelo CPF (username)
    result = await db.execute(
        select(FuncionarioModel).where(FuncionarioModel.cpf == form_data.username)
    )
    funcionario = result.scalars().first()

    # Verifica se existe e se a senha está correta
    if not funcionario or not verify_password(form_data.password, funcionario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Gera o token JWT com os dados do funcionário
    token = create_access_token(data={
        "sub":   funcionario.cpf,
        "nome":  funcionario.nome,
        "grupo": funcionario.grupo,
        "id":    funcionario.id_funcionario
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "nome":         funcionario.nome,
        "grupo":        funcionario.grupo
    }

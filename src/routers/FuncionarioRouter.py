# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from infra.database import get_db
from infra.orm.models import FuncionarioModel
from infra.security import get_password_hash, get_current_user, require_grupo
from domain.entities.Funcionario import Funcionario

router = APIRouter()


@router.get("/funcionario/", tags=["Funcionário"], status_code=200)
async def get_funcionario(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)   # protegida - qualquer grupo logado
):
    result = await db.execute(select(FuncionarioModel))
    funcionarios = result.scalars().all()
    return [
        {
            "id_funcionario": f.id_funcionario,
            "nome":      f.nome,
            "matricula": f.matricula,
            "cpf":       f.cpf,
            "telefone":  f.telefone,
            "grupo":     f.grupo
        }
        for f in funcionarios
    ]


@router.get("/funcionario/{id}", tags=["Funcionário"], status_code=200)
async def get_funcionario_por_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)   # protegida - qualquer grupo logado
):
    result = await db.execute(
        select(FuncionarioModel).where(FuncionarioModel.id_funcionario == id)
    )
    f = result.scalars().first()
    if not f:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return {
        "id_funcionario": f.id_funcionario,
        "nome":      f.nome,
        "matricula": f.matricula,
        "cpf":       f.cpf,
        "telefone":  f.telefone,
        "grupo":     f.grupo
    }


@router.post("/funcionario/", tags=["Funcionário"], status_code=201)
async def post_funcionario(
    corpo: Funcionario,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))   # somente grupo 1 - Admin
):
    result = await db.execute(
        select(FuncionarioModel).where(FuncionarioModel.cpf == corpo.cpf)
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Já existe um funcionário com este CPF")

    novo = FuncionarioModel(
        nome      = corpo.nome,
        matricula = corpo.matricula,
        cpf       = corpo.cpf,
        telefone  = corpo.telefone,
        grupo     = corpo.grupo,
        senha     = get_password_hash(corpo.senha) if corpo.senha else None
    )
    db.add(novo)
    await db.commit()
    await db.refresh(novo)
    return {
        "id_funcionario": novo.id_funcionario,
        "nome":      novo.nome,
        "matricula": novo.matricula,
        "cpf":       novo.cpf,
        "telefone":  novo.telefone,
        "grupo":     novo.grupo
    }


@router.put("/funcionario/{id}", tags=["Funcionário"], status_code=200)
async def put_funcionario(
    id: int,
    corpo: Funcionario,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))   # somente grupo 1 - Admin
):
    result = await db.execute(
        select(FuncionarioModel).where(FuncionarioModel.id_funcionario == id)
    )
    funcionario = result.scalars().first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    if corpo.cpf != funcionario.cpf:
        result_cpf = await db.execute(
            select(FuncionarioModel).where(FuncionarioModel.cpf == corpo.cpf)
        )
        if result_cpf.scalars().first():
            raise HTTPException(status_code=400, detail="Já existe um funcionário com este CPF")

    funcionario.nome      = corpo.nome
    funcionario.matricula = corpo.matricula
    funcionario.cpf       = corpo.cpf
    funcionario.telefone  = corpo.telefone
    funcionario.grupo     = corpo.grupo
    if corpo.senha:
        funcionario.senha = get_password_hash(corpo.senha)

    await db.commit()
    await db.refresh(funcionario)
    return {
        "id_funcionario": funcionario.id_funcionario,
        "nome":      funcionario.nome,
        "matricula": funcionario.matricula,
        "cpf":       funcionario.cpf,
        "telefone":  funcionario.telefone,
        "grupo":     funcionario.grupo
    }


@router.delete("/funcionario/{id}", tags=["Funcionário"], status_code=200)
async def delete_funcionario(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))   # somente grupo 1 - Admin
):
    result = await db.execute(
        select(FuncionarioModel).where(FuncionarioModel.id_funcionario == id)
    )
    funcionario = result.scalars().first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    await db.delete(funcionario)
    await db.commit()
    return {"msg": "Funcionário excluído com sucesso", "id": id}

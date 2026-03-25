# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from infra.database import get_db
from infra.orm.models import FuncionarioModel
from domain.entities.Funcionario import Funcionario

router = APIRouter()


@router.get("/funcionario/", tags=["Funcionário"], status_code=200)
async def get_funcionario(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuncionarioModel))
    funcionarios = result.scalars().all()
    return funcionarios


@router.get("/funcionario/{id}", tags=["Funcionário"], status_code=200)
async def get_funcionario_por_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuncionarioModel).where(FuncionarioModel.id_funcionario == id))
    funcionario = result.scalars().first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return funcionario


@router.post("/funcionario/", tags=["Funcionário"], status_code=201)
async def post_funcionario(corpo: Funcionario, db: AsyncSession = Depends(get_db)):
    novo = FuncionarioModel(
        nome      = corpo.nome,
        matricula = corpo.matricula,
        cpf       = corpo.cpf,
        telefone  = corpo.telefone,
        grupo     = corpo.grupo,
        senha     = corpo.senha
    )
    db.add(novo)
    await db.commit()
    await db.refresh(novo)
    return novo


@router.put("/funcionario/{id}", tags=["Funcionário"], status_code=200)
async def put_funcionario(id: int, corpo: Funcionario, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuncionarioModel).where(FuncionarioModel.id_funcionario == id))
    funcionario = result.scalars().first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    funcionario.nome      = corpo.nome
    funcionario.matricula = corpo.matricula
    funcionario.cpf       = corpo.cpf
    funcionario.telefone  = corpo.telefone
    funcionario.grupo     = corpo.grupo
    funcionario.senha     = corpo.senha

    await db.commit()
    await db.refresh(funcionario)
    return funcionario


@router.delete("/funcionario/{id}", tags=["Funcionário"], status_code=200)
async def delete_funcionario(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuncionarioModel).where(FuncionarioModel.id_funcionario == id))
    funcionario = result.scalars().first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    await db.delete(funcionario)
    await db.commit()
    return {"msg": "Funcionário excluído com sucesso", "id": id}

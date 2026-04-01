# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from infra.database import get_db
from infra.orm.models import ClienteModel
from infra.security import get_current_user, require_grupo
from domain.entities.Cliente import Cliente

router = APIRouter()


@router.get("/cliente/", tags=["Cliente"], status_code=200)
async def get_cliente(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)   # protegida
):
    result = await db.execute(select(ClienteModel))
    return result.scalars().all()


@router.get("/cliente/{id}", tags=["Cliente"], status_code=200)
async def get_cliente_por_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)   # protegida
):
    result = await db.execute(
        select(ClienteModel).where(ClienteModel.id_cliente == id)
    )
    cliente = result.scalars().first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@router.post("/cliente/", tags=["Cliente"], status_code=201)
async def post_cliente(
    corpo: Cliente,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))   # somente grupo 1 - Admin
):
    novo = ClienteModel(nome=corpo.nome, cpf=corpo.cpf, telefone=corpo.telefone)
    db.add(novo)
    await db.commit()
    await db.refresh(novo)
    return novo


@router.put("/cliente/{id}", tags=["Cliente"], status_code=200)
async def put_cliente(
    id: int,
    corpo: Cliente,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))   # somente grupo 1 - Admin
):
    result = await db.execute(
        select(ClienteModel).where(ClienteModel.id_cliente == id)
    )
    cliente = result.scalars().first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente.nome     = corpo.nome
    cliente.cpf      = corpo.cpf
    cliente.telefone = corpo.telefone
    await db.commit()
    await db.refresh(cliente)
    return cliente


@router.delete("/cliente/{id}", tags=["Cliente"], status_code=200)
async def delete_cliente(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))   # somente grupo 1 - Admin
):
    result = await db.execute(
        select(ClienteModel).where(ClienteModel.id_cliente == id)
    )
    cliente = result.scalars().first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    await db.delete(cliente)
    await db.commit()
    return {"msg": "Cliente excluído com sucesso", "id": id}

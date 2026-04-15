# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infra.async_database import get_async_db
from infra.orm.ComandaModel import ComandaModel, ComandaItemModel
from infra.dependencies import get_current_active_user
from domain.schemas.ComandaSchema import (
    ComandaCreate, ComandaResponse, ComandaItemCreate,
    ComandaItemUpdate, ComandaItemResponse
)
from domain.schemas.AuthSchema import FuncionarioAuth

router = APIRouter()


async def _get_comanda_by_numero(numero: int, db: AsyncSession) -> ComandaModel:
    result = await db.execute(select(ComandaModel).where(ComandaModel.numero == numero))
    comanda = result.scalar_one_or_none()
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")
    return comanda


async def _build_response(comanda: ComandaModel, db: AsyncSession) -> ComandaResponse:
    result = await db.execute(
        select(ComandaItemModel).where(ComandaItemModel.comanda_id == comanda.id_comanda)
    )
    itens_db = result.scalars().all()
    itens = [
        ComandaItemResponse(
            id_item=i.id_item,
            comanda_id=i.comanda_id,
            nome_produto=i.nome_produto,
            quantidade=i.quantidade,
            valor_unitario=i.valor_unitario,
            subtotal=round(i.quantidade * i.valor_unitario, 2)
        )
        for i in itens_db
    ]
    return ComandaResponse(
        id_comanda=comanda.id_comanda,
        numero=comanda.numero,
        status=comanda.status,
        data_criacao=comanda.data_criacao,
        itens=itens
    )


# --- Comanda ---

@router.post("/comanda/", tags=["Comanda"], status_code=201,
             summary="Criar nova comanda - protegida")
async def criar_comanda(
    corpo: ComandaCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    existente = await db.execute(select(ComandaModel).where(ComandaModel.numero == corpo.numero))
    if existente.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Já existe uma comanda com este número")

    nova = ComandaModel(numero=corpo.numero, status="aberta")
    db.add(nova)
    await db.commit()
    await db.refresh(nova)
    return await _build_response(nova, db)


@router.get("/comanda/", tags=["Comanda"], status_code=200,
            summary="Listar todas as comandas - protegida")
async def listar_comandas(
    db: AsyncSession = Depends(get_async_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    result = await db.execute(select(ComandaModel))
    comandas = result.scalars().all()
    return [await _build_response(c, db) for c in comandas]


@router.get("/comanda/{numero}", tags=["Comanda"], status_code=200,
            summary="Buscar comanda por número - protegida")
async def buscar_comanda(
    numero: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    comanda = await _get_comanda_by_numero(numero, db)
    return await _build_response(comanda, db)


# --- Itens da Comanda ---

@router.post("/comanda/{numero}/item", tags=["Comanda"], status_code=201,
             summary="Adicionar item à comanda - protegida")
async def adicionar_item(
    numero: int,
    corpo: ComandaItemCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    comanda = await _get_comanda_by_numero(numero, db)

    item = ComandaItemModel(
        comanda_id=comanda.id_comanda,
        nome_produto=corpo.nome_produto,
        quantidade=corpo.quantidade,
        valor_unitario=corpo.valor_unitario
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    return ComandaItemResponse(
        id_item=item.id_item,
        comanda_id=item.comanda_id,
        nome_produto=item.nome_produto,
        quantidade=item.quantidade,
        valor_unitario=item.valor_unitario,
        subtotal=round(item.quantidade * item.valor_unitario, 2)
    )


@router.get("/comanda/{numero}/itens", tags=["Comanda"], status_code=200,
            summary="Listar itens da comanda - protegida")
async def listar_itens(
    numero: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    comanda = await _get_comanda_by_numero(numero, db)
    result = await db.execute(
        select(ComandaItemModel).where(ComandaItemModel.comanda_id == comanda.id_comanda)
    )
    itens = result.scalars().all()
    return [
        ComandaItemResponse(
            id_item=i.id_item,
            comanda_id=i.comanda_id,
            nome_produto=i.nome_produto,
            quantidade=i.quantidade,
            valor_unitario=i.valor_unitario,
            subtotal=round(i.quantidade * i.valor_unitario, 2)
        )
        for i in itens
    ]


@router.put("/comanda/{numero}/item/{item_id}", tags=["Comanda"], status_code=200,
            summary="Editar quantidade de item - protegida")
async def editar_item(
    numero: int,
    item_id: int,
    corpo: ComandaItemUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    comanda = await _get_comanda_by_numero(numero, db)

    result = await db.execute(
        select(ComandaItemModel).where(
            ComandaItemModel.id_item == item_id,
            ComandaItemModel.comanda_id == comanda.id_comanda
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado nesta comanda")

    item.quantidade = corpo.quantidade
    await db.commit()
    await db.refresh(item)

    return ComandaItemResponse(
        id_item=item.id_item,
        comanda_id=item.comanda_id,
        nome_produto=item.nome_produto,
        quantidade=item.quantidade,
        valor_unitario=item.valor_unitario,
        subtotal=round(item.quantidade * item.valor_unitario, 2)
    )


@router.delete("/comanda/{numero}/item/{item_id}", tags=["Comanda"], status_code=204,
               summary="Excluir item da comanda - protegida")
async def excluir_item(
    numero: int,
    item_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    comanda = await _get_comanda_by_numero(numero, db)

    result = await db.execute(
        select(ComandaItemModel).where(
            ComandaItemModel.id_item == item_id,
            ComandaItemModel.comanda_id == comanda.id_comanda
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado nesta comanda")

    await db.delete(item)
    await db.commit()
    return None

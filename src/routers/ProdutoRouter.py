# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from infra.database import get_db
from infra.orm.models import ProdutoModel
from infra.security import get_current_user, require_grupo
from domain.entities.Produto import Produto

router = APIRouter()


# ─── ROTAS PÚBLICAS (sem autenticação) ────────────────────────

@router.get("/produto/", tags=["Produto"], status_code=200)
async def get_produto(db: AsyncSession = Depends(get_db)):
    """Rota pública - qualquer um pode listar produtos"""
    result = await db.execute(select(ProdutoModel))
    produtos = result.scalars().all()
    return [
        {
            "id_produto":     p.id_produto,
            "nome":           p.nome,
            "descricao":      p.descricao,
            "valor_unitario": p.valor_unitario
        }
        for p in produtos
    ]


@router.get("/produto/{id}", tags=["Produto"], status_code=200)
async def get_produto_por_id(id: int, db: AsyncSession = Depends(get_db)):
    """Rota pública - qualquer um pode ver um produto"""
    result = await db.execute(
        select(ProdutoModel).where(ProdutoModel.id_produto == id)
    )
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {
        "id_produto":     p.id_produto,
        "nome":           p.nome,
        "descricao":      p.descricao,
        "valor_unitario": p.valor_unitario
    }


# ─── ROTAS PROTEGIDAS (somente grupo 1 - Admin) ───────────────

@router.post("/produto/", tags=["Produto"], status_code=201)
async def post_produto(
    corpo: Produto,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))
):
    novo = ProdutoModel(
        nome           = corpo.nome,
        descricao      = corpo.descricao,
        foto           = corpo.foto,
        valor_unitario = corpo.valor_unitario
    )
    db.add(novo)
    await db.commit()
    await db.refresh(novo)
    return {
        "id_produto":     novo.id_produto,
        "nome":           novo.nome,
        "descricao":      novo.descricao,
        "valor_unitario": novo.valor_unitario
    }


@router.put("/produto/{id}", tags=["Produto"], status_code=200)
async def put_produto(
    id: int,
    corpo: Produto,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))
):
    result = await db.execute(
        select(ProdutoModel).where(ProdutoModel.id_produto == id)
    )
    produto = result.scalars().first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.nome           = corpo.nome
    produto.descricao      = corpo.descricao
    produto.foto           = corpo.foto
    produto.valor_unitario = corpo.valor_unitario
    await db.commit()
    await db.refresh(produto)
    return {
        "id_produto":     produto.id_produto,
        "nome":           produto.nome,
        "descricao":      produto.descricao,
        "valor_unitario": produto.valor_unitario
    }


@router.delete("/produto/{id}", tags=["Produto"], status_code=200)
async def delete_produto(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_grupo(1))
):
    result = await db.execute(
        select(ProdutoModel).where(ProdutoModel.id_produto == id)
    )
    produto = result.scalars().first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    await db.delete(produto)
    await db.commit()
    return {"msg": "Produto excluído com sucesso", "id": id}

# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi.errors import RateLimitExceeded

from infra.database import get_db
from infra.orm.models import ProdutoModel as ProdutoDB
from infra.dependencies import get_current_active_user, require_group
from infra.rate_limit import limiter, get_rate_limit
from domain.schemas.AuthSchema import FuncionarioAuth
from domain.entities.Produto import Produto
from services.AuditoriaService import AuditoriaService

router = APIRouter()


@router.get("/produto/publico", tags=["Produto"], status_code=200,
            summary="Listar todos sem id e valor - pública")
@limiter.limit(get_rate_limit("light"))
async def get_produto_publico(request: Request, db: Session = Depends(get_db)):
    try:
        produtos = db.query(ProdutoDB).all()
        return [{"nome": p.nome, "descricao": p.descricao} for p in produtos]
    except RateLimitExceeded: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/produto/", tags=["Produto"], status_code=200,
            summary="Listar todos - protegida")
@limiter.limit(get_rate_limit("moderate"))
async def get_produto(
    request: Request,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    try:
        produtos = db.query(ProdutoDB).all()
        return [{"id_produto": p.id_produto, "nome": p.nome,
                 "descricao": p.descricao, "valor_unitario": p.valor_unitario}
                for p in produtos]
    except RateLimitExceeded: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/produto/{id}", tags=["Produto"], status_code=200,
            summary="Listar um - protegida")
@limiter.limit(get_rate_limit("moderate"))
async def get_produto_por_id(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    try:
        p = db.query(ProdutoDB).filter(ProdutoDB.id_produto == id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        return {"id_produto": p.id_produto, "nome": p.nome,
                "descricao": p.descricao, "valor_unitario": p.valor_unitario}
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/produto/", tags=["Produto"], status_code=201,
             summary="Criar novo - grupo 1")
@limiter.limit(get_rate_limit("restrictive"))
async def post_produto(
    request: Request,
    corpo: Produto,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        novo = ProdutoDB(nome=corpo.nome, descricao=corpo.descricao,
                         foto=corpo.foto, valor_unitario=corpo.valor_unitario)
        db.add(novo); db.commit(); db.refresh(novo)

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="CREATE", recurso="PRODUTO", recurso_id=novo.id_produto,
            dados_novos=novo, request=request)

        return {"id_produto": novo.id_produto, "nome": novo.nome,
                "descricao": novo.descricao, "valor_unitario": novo.valor_unitario}
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/produto/{id}", tags=["Produto"], status_code=200,
            summary="Editar - grupo 1")
@limiter.limit(get_rate_limit("restrictive"))
async def put_produto(
    request: Request,
    id: int,
    corpo: Produto,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        p = db.query(ProdutoDB).filter(ProdutoDB.id_produto == id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        dados_antigos = p.__dict__.copy()
        p.nome = corpo.nome; p.descricao = corpo.descricao
        p.foto = corpo.foto; p.valor_unitario = corpo.valor_unitario
        db.commit(); db.refresh(p)

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="UPDATE", recurso="PRODUTO", recurso_id=p.id_produto,
            dados_antigos=dados_antigos, dados_novos=p, request=request)

        return {"id_produto": p.id_produto, "nome": p.nome,
                "descricao": p.descricao, "valor_unitario": p.valor_unitario}
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/produto/{id}", tags=["Produto"], status_code=204,
               summary="Excluir - grupo 1")
@limiter.limit(get_rate_limit("critical"))
async def delete_produto(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        p = db.query(ProdutoDB).filter(ProdutoDB.id_produto == id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="DELETE", recurso="PRODUTO", recurso_id=p.id_produto,
            dados_antigos=p, request=request)

        db.delete(p); db.commit()
        return None
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

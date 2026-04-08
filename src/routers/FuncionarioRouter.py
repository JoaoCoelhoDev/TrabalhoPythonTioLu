# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi.errors import RateLimitExceeded

from infra.database import get_db
from infra.orm.models import FuncionarioModel as FuncionarioDB
from infra.security import get_password_hash
from infra.dependencies import get_current_active_user, require_group
from infra.rate_limit import limiter, get_rate_limit
from domain.schemas.AuthSchema import FuncionarioAuth
from domain.entities.Funcionario import Funcionario
from services.AuditoriaService import AuditoriaService

router = APIRouter()


@router.get("/funcionario/", tags=["Funcionário"], status_code=200,
            summary="Listar todos - grupo 1")
@limiter.limit(get_rate_limit("moderate"))
async def get_funcionario(
    request: Request,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        funcionarios = db.query(FuncionarioDB).all()
        return [{"id": f.id_funcionario, "nome": f.nome, "matricula": f.matricula,
                 "cpf": f.cpf, "telefone": f.telefone, "grupo": f.grupo}
                for f in funcionarios]
    except RateLimitExceeded: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funcionario/{id}", tags=["Funcionário"], status_code=200,
            summary="Listar um - protegida")
@limiter.limit(get_rate_limit("moderate"))
async def get_funcionario_por_id(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(get_current_active_user)
):
    try:
        f = db.query(FuncionarioDB).filter(FuncionarioDB.id_funcionario == id).first()
        if not f:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        return {"id": f.id_funcionario, "nome": f.nome, "matricula": f.matricula,
                "cpf": f.cpf, "telefone": f.telefone, "grupo": f.grupo}
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/funcionario/", tags=["Funcionário"], status_code=201,
             summary="Criar novo - grupo 1")
@limiter.limit(get_rate_limit("restrictive"))
async def post_funcionario(
    request: Request,
    corpo: Funcionario,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        if corpo.grupo not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Grupo inválido. Use 1, 2 ou 3.")

        if db.query(FuncionarioDB).filter(FuncionarioDB.cpf == corpo.cpf).first():
            raise HTTPException(status_code=400, detail="Já existe um funcionário com este CPF")

        novo = FuncionarioDB(
            nome=corpo.nome, matricula=corpo.matricula, cpf=corpo.cpf,
            telefone=corpo.telefone, grupo=corpo.grupo,
            senha=get_password_hash(corpo.senha) if corpo.senha else None
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="CREATE", recurso="FUNCIONARIO", recurso_id=novo.id_funcionario,
            dados_novos=novo, request=request)

        return {"id": novo.id_funcionario, "nome": novo.nome, "matricula": novo.matricula,
                "cpf": novo.cpf, "telefone": novo.telefone, "grupo": novo.grupo}
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/funcionario/{id}", tags=["Funcionário"], status_code=200,
            summary="Editar - grupo 1")
@limiter.limit(get_rate_limit("restrictive"))
async def put_funcionario(
    request: Request,
    id: int,
    corpo: Funcionario,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        f = db.query(FuncionarioDB).filter(FuncionarioDB.id_funcionario == id).first()
        if not f:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")

        if corpo.cpf != f.cpf:
            if db.query(FuncionarioDB).filter(FuncionarioDB.cpf == corpo.cpf).first():
                raise HTTPException(status_code=400, detail="CPF já cadastrado")

        dados_antigos = f.__dict__.copy()

        f.nome = corpo.nome; f.matricula = corpo.matricula
        f.cpf  = corpo.cpf;  f.telefone  = corpo.telefone; f.grupo = corpo.grupo
        if corpo.senha:
            f.senha = get_password_hash(corpo.senha)

        db.commit(); db.refresh(f)

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="UPDATE", recurso="FUNCIONARIO", recurso_id=f.id_funcionario,
            dados_antigos=dados_antigos, dados_novos=f, request=request)

        return {"id": f.id_funcionario, "nome": f.nome, "matricula": f.matricula,
                "cpf": f.cpf, "telefone": f.telefone, "grupo": f.grupo}
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/funcionario/{id}", tags=["Funcionário"], status_code=204,
               summary="Excluir - grupo 1")
@limiter.limit(get_rate_limit("critical"))
async def delete_funcionario(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        f = db.query(FuncionarioDB).filter(FuncionarioDB.id_funcionario == id).first()
        if not f:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        if current_user.id == id:
            raise HTTPException(status_code=400, detail="Não é possível excluir seu próprio usuário")

        AuditoriaService.registrar_acao(db=db, funcionario_id=current_user.id,
            acao="DELETE", recurso="FUNCIONARIO", recurso_id=f.id_funcionario,
            dados_antigos=f, request=request)

        db.delete(f); db.commit()
        return None
    except RateLimitExceeded: raise
    except HTTPException: raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

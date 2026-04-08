# Joao Vitor Coelho de Souza
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from domain.schemas.AuditoriaSchema import AuditoriaResponse
from domain.schemas.AuthSchema import FuncionarioAuth
from infra.orm.AuditoriaModel import AuditoriaDB
from infra.orm.models import FuncionarioModel as FuncionarioDB
from infra.database import get_db
from infra.dependencies import require_group
from infra.rate_limit import limiter, get_rate_limit

router = APIRouter()


@router.get("/auditoria", response_model=List[AuditoriaResponse], tags=["Auditoria"],
            summary="Listar registros de auditoria - grupo 1")
@limiter.limit(get_rate_limit("moderate"))
async def listar_auditoria(
    request: Request,
    funcionario_id: Optional[int] = Query(None),
    acao:           Optional[str] = Query(None, description="Ex: LOGIN,CREATE"),
    recurso:        Optional[str] = Query(None, description="Ex: AUTH,FUNCIONARIO"),
    data_inicio:    Optional[str] = Query(None, description="YYYY-MM-DD"),
    data_fim:       Optional[str] = Query(None, description="YYYY-MM-DD"),
    skip:    int = Query(0,   ge=0),
    limite:  int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    try:
        query = db.query(AuditoriaDB, FuncionarioDB).join(
            FuncionarioDB, FuncionarioDB.id_funcionario == AuditoriaDB.funcionario_id
        )

        if funcionario_id:
            query = query.filter(AuditoriaDB.funcionario_id == funcionario_id)
        if acao:
            acoes = [a.strip().upper() for a in acao.split(",")]
            query = query.filter(AuditoriaDB.acao.in_(acoes))
        if recurso:
            recursos = [r.strip().upper() for r in recurso.split(",")]
            query = query.filter(AuditoriaDB.recurso.in_(recursos))
        if data_inicio:
            query = query.filter(AuditoriaDB.data_hora >= datetime.strptime(data_inicio, "%Y-%m-%d"))
        if data_fim:
            query = query.filter(AuditoriaDB.data_hora <= datetime.strptime(data_fim, "%Y-%m-%d"))

        auditorias = query.order_by(desc(AuditoriaDB.data_hora)).offset(skip).limit(limite).all()

        return [
            AuditoriaResponse(
                id             = a.id,
                funcionario_id = a.funcionario_id,
                funcionario    = {"id": f.id_funcionario, "nome": f.nome, "matricula": f.matricula, "grupo": f.grupo},
                acao           = a.acao,
                recurso        = a.recurso,
                recurso_id     = a.recurso_id,
                dados_antigos  = a.dados_antigos,
                dados_novos    = a.dados_novos,
                ip_address     = a.ip_address,
                user_agent     = a.user_agent,
                data_hora      = a.data_hora,
            )
            for a, f in auditorias
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auditoria/acoes", tags=["Auditoria"],
            summary="Listar ações e recursos disponíveis - grupo 1")
@limiter.limit(get_rate_limit("light"))
async def listar_acoes(
    request: Request,
    db: Session = Depends(get_db),
    current_user: FuncionarioAuth = Depends(require_group([1]))
):
    acoes   = db.query(AuditoriaDB.acao).distinct().all()
    recursos = db.query(AuditoriaDB.recurso).distinct().all()
    return {
        "acoes":    [{"codigo": a[0]} for a in acoes],
        "recursos": [{"codigo": r[0]} for r in recursos],
    }

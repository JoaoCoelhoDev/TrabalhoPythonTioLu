# Joao Vitor Coelho de Souza
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from infra.security import get_current_user
from infra.database import get_db
from infra.orm.models import FuncionarioModel
from domain.schemas.AuthSchema import FuncionarioAuth


def _get_funcionario_auth(token_data: dict, db: Session) -> FuncionarioAuth:
    user_id = token_data.get("id")
    user = db.query(FuncionarioModel).filter(FuncionarioModel.id_funcionario == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    return FuncionarioAuth(
        id=user.id_funcionario,
        nome=user.nome,
        matricula=user.matricula,
        cpf=user.cpf,
        grupo=user.grupo
    )


def get_current_active_user(
    token_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FuncionarioAuth:
    return _get_funcionario_auth(token_data, db)


def require_group(grupos):
    def check(
        token_data: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> FuncionarioAuth:
        user = _get_funcionario_auth(token_data, db)
        allowed = grupos if isinstance(grupos, list) else [grupos]
        if user.grupo not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Apenas grupo {grupos} pode realizar esta operacao."
            )
        return user
    return check

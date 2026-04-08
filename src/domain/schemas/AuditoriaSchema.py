# Joao Vitor Coelho de Souza
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AuditoriaCreate(BaseModel):
    funcionario_id: int
    acao:           str = Field(..., max_length=50)
    recurso:        str = Field(..., max_length=100)
    recurso_id:     Optional[int]  = None
    dados_antigos:  Optional[str]  = None
    dados_novos:    Optional[str]  = None
    ip_address:     Optional[str]  = Field(None, max_length=45)
    user_agent:     Optional[str]  = None

class AuditoriaResponse(BaseModel):
    id:             int
    funcionario_id: int
    funcionario:    Dict[str, Any]
    acao:           str
    recurso:        str
    recurso_id:     Optional[int]  = None
    dados_antigos:  Optional[str]  = None
    dados_novos:    Optional[str]  = None
    ip_address:     Optional[str]  = None
    user_agent:     Optional[str]  = None
    data_hora:      datetime

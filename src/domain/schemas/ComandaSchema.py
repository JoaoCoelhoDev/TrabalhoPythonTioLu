# Joao Vitor Coelho de Souza
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class ComandaCreate(BaseModel):
    numero: int


class ComandaItemCreate(BaseModel):
    nome_produto: str
    quantidade: int
    valor_unitario: float

    @field_validator("quantidade")
    @classmethod
    def quantidade_positiva(cls, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        return v

    @field_validator("valor_unitario")
    @classmethod
    def valor_positivo(cls, v):
        if v <= 0:
            raise ValueError("Valor unitário deve ser maior que zero")
        return v


class ComandaItemUpdate(BaseModel):
    quantidade: int

    @field_validator("quantidade")
    @classmethod
    def quantidade_positiva(cls, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        return v


class ComandaItemResponse(BaseModel):
    id_item: int
    comanda_id: int
    nome_produto: str
    quantidade: int
    valor_unitario: float
    subtotal: float

    model_config = {"from_attributes": True}


class ComandaResponse(BaseModel):
    id_comanda: int
    numero: int
    status: str
    data_criacao: Optional[datetime]
    itens: List[ComandaItemResponse] = []

    model_config = {"from_attributes": True}

# Joao Vitor Coelho de Souza
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from infra.async_database import AsyncBase


class ComandaModel(AsyncBase):
    __tablename__ = "tb_comanda"

    id_comanda   = Column(Integer, primary_key=True, autoincrement=True, index=True)
    numero       = Column(Integer, nullable=False, unique=True, index=True)
    status       = Column(String(20), nullable=False, default="aberta")
    data_criacao = Column(DateTime, server_default=func.now())


class ComandaItemModel(AsyncBase):
    __tablename__ = "tb_comanda_item"

    id_item        = Column(Integer, primary_key=True, autoincrement=True, index=True)
    comanda_id     = Column(Integer, ForeignKey("tb_comanda.id_comanda", ondelete="CASCADE"), nullable=False, index=True)
    nome_produto   = Column(String(100), nullable=False)
    quantidade     = Column(Integer, nullable=False)
    valor_unitario = Column(Float, nullable=False)

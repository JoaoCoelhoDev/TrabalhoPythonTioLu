# Joao Vitor Coelho de Souza
from sqlalchemy import Column, Integer, String, Float, LargeBinary, Index
from infra.database import Base

class FuncionarioModel(Base):
    __tablename__ = "tb_funcionario"

    id_funcionario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome           = Column(String(100), nullable=False)
    matricula      = Column(String(10),  nullable=False)
    cpf            = Column(String(11),  nullable=False, unique=True, index=True)
    telefone       = Column(String(11),  nullable=True)
    grupo          = Column(Integer,     nullable=False)
    senha          = Column(String(200), nullable=True)


class ClienteModel(Base):
    __tablename__ = "tb_cliente"

    id_cliente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome       = Column(String(100), nullable=False)
    cpf        = Column(String(11),  nullable=True, unique=True, index=True)
    telefone   = Column(String(11),  nullable=True)


class ProdutoModel(Base):
    __tablename__ = "tb_produto"

    id_produto     = Column(Integer,     primary_key=True, index=True, autoincrement=True)
    nome           = Column(String(100), nullable=False, index=True)
    descricao      = Column(String(200), nullable=True)
    foto           = Column(LargeBinary, nullable=True)
    valor_unitario = Column(Float,       nullable=False)

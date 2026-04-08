# João Vitor Coelho de Souza
from pydantic import BaseModel

class Cliente(BaseModel):
    id_cliente: int = None
    nome: str
    cpf: str = None
    telefone: str = None

# Joao Vitor Coelho de Souza
# Script para limpar todos os dados do banco (mantém as tabelas)
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from infra.database import SessionLocal
from infra.orm.models import FuncionarioModel, ClienteModel, ProdutoModel
from infra.orm.AuditoriaModel import AuditoriaDB

db = SessionLocal()

db.query(AuditoriaDB).delete()
db.query(FuncionarioModel).delete()
db.query(ClienteModel).delete()
db.query(ProdutoModel).delete()
db.commit()
db.close()

print("Todos os dados foram apagados.")

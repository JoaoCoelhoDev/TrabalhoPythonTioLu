# Joao Vitor Coelho de Souza
# Script para criar o primeiro administrador no banco de dados
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from infra.database import SessionLocal, engine, Base
from infra.orm.models import FuncionarioModel
from infra.orm import AuditoriaModel  # garante que a tabela de auditoria é criada
from infra.security import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

existente = db.query(FuncionarioModel).filter(FuncionarioModel.cpf == "00000000000").first()
if existente:
    print("Usuário admin já existe.")
else:
    admin = FuncionarioModel(
        nome      = "Joao Vitor Coelho de Souza",
        matricula = "ADM001",
        cpf       = "00000000000",
        telefone  = "99999999999",
        grupo     = 1,
        senha     = get_password_hash("admin123")
    )
    db.add(admin)
    db.commit()
    print("Usuário admin criado com sucesso!")
    print("CPF: 00000000000")
    print("Senha: admin123")

db.close()

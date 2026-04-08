# Joao Vitor Coelho de Souza
from dotenv import load_dotenv, find_dotenv
import os

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

# Configurações da API
HOST   = os.getenv("HOST",   "0.0.0.0")
PORT   = os.getenv("PORT",   "8000")
RELOAD = os.getenv("RELOAD", True)

# Configurações JWT
SECRET_KEY                  = os.getenv("SECRET_KEY", "chave_secreta_padrao")
ALGORITHM                   = os.getenv("ALGORITHM",  "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

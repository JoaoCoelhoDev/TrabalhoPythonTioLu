# Joao Vitor Coelho de Souza
from fastapi import FastAPI
from settings import HOST, PORT, RELOAD
import uvicorn

from infra.database import engine, Base
from routers import FuncionarioRouter
from routers import ClienteRouter
from routers import ProdutoRouter

app = FastAPI()

# Cria as tabelas no banco ao iniciar a API
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Rota padrão
@app.get("/", tags=["Root"], status_code=200)
async def root():
    return {
        "detail": "API Pastelaria do Zé",
        "Swagger UI": "http://127.0.0.1:8000/docs",
        "ReDoc": "http://127.0.0.1:8000/redoc"
    }

# Mapeamento das rotas/endpoints
app.include_router(FuncionarioRouter.router)
app.include_router(ClienteRouter.router)
app.include_router(ProdutoRouter.router)

if __name__ == "__main__":
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=RELOAD)

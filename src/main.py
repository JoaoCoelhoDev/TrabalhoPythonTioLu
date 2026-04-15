# Joao Vitor Coelho de Souza

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import HOST, PORT, RELOAD
from infra.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from infra import database
from infra import async_database
import uvicorn

from routers import AuthRouter
from routers import FuncionarioRouter
from routers import ClienteRouter
from routers import ProdutoRouter
from routers import AuditoriaRouter
from routers import HealthRouter
from routers import ComandaRouter
import infra.orm.ComandaModel  # noqa: F401 — registra modelos no AsyncBase.metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API has started")
    await database.cria_tabelas()
    await async_database.cria_tabelas_async()
    yield
    print("API is shutting down")

app = FastAPI(lifespan=lifespan, title="API Pastelaria do Zé")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

@app.get("/", tags=["Root"], status_code=200, summary="Informações da API - pública")
async def root():
    return {"detail": "API Pastelaria do Zé",
            "Swagger UI": "http://127.0.0.1:8000/docs",
            "ReDoc":      "http://127.0.0.1:8000/redoc"}

app.include_router(AuthRouter.router)
app.include_router(FuncionarioRouter.router)
app.include_router(ClienteRouter.router)
app.include_router(ProdutoRouter.router)
app.include_router(AuditoriaRouter.router)
app.include_router(HealthRouter.router)
app.include_router(ComandaRouter.router)

if __name__ == "__main__":
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=RELOAD)

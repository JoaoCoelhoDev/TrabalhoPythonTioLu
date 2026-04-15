# Joao Vitor Coelho de Souza
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./comandas_db.db"

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

AsyncBase = declarative_base()


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


async def cria_tabelas_async():
    async with async_engine.begin() as conn:
        await conn.run_sync(AsyncBase.metadata.create_all)

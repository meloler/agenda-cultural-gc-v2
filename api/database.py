"""
Conexión asíncrona a PostgreSQL para la API FastAPI.

Usa asyncpg como driver y SQLAlchemy 2.0 async engine.
Lee DATABASE_URL del .env y convierte automáticamente el scheme
postgresql:// → postgresql+asyncpg:// si es necesario.
"""

import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno desde .env (raíz del proyecto)
load_dotenv()

# ---------------------------------------------------------------------------
# Engine asíncrono
# ---------------------------------------------------------------------------

_raw_url: str = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin123@localhost:5432/agenda_cultural",
)

# asyncpg requiere el scheme "postgresql+asyncpg://"
DATABASE_URL: str = _raw_url.replace(
    "postgresql://", "postgresql+asyncpg://", 1
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

# Session factory (async)
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Dependency injection para FastAPI
# ---------------------------------------------------------------------------

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield de una sesión asíncrona; se cierra automáticamente al terminar."""
    async with async_session_factory() as session:
        yield session

"""
Configuración de la conexión a PostgreSQL y gestión del engine SQLAlchemy.
Data_Refinery_Agent.
"""

import os

from sqlmodel import Session, SQLModel, create_engine

# Default: PostgreSQL local levantado con docker-compose
DEFAULT_DB_URL = "postgresql://admin:admin123@localhost:5432/agenda_cultural"

engine = create_engine(
    os.getenv("DATABASE_URL", DEFAULT_DB_URL),
    echo=False,  # True para ver SQL en consola (debug)
)


def init_db() -> None:
    """Crea todas las tablas definidas en SQLModel (si no existen).

    Importa app.models para que SQLModel registre la tabla 'evento'
    antes de llamar a create_all.
    """
    import app.models  # noqa: F401 – registro del modelo

    SQLModel.metadata.create_all(engine)
    print("✅ Base de datos inicializada (tablas creadas si no existían).")


def get_session() -> Session:
    """Devuelve una sesión de base de datos."""
    return Session(engine)

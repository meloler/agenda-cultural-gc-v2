"""
Configuración de la conexión a PostgreSQL y gestión del engine SQLAlchemy.
Data_Refinery_Agent.
"""

import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# Cargar las variables de entorno desde el fichero .env
load_dotenv()

# Default: PostgreSQL local levantado con docker-compose
# Offline: Usar SQLite local para evitar problemas de conexión DNS con Supabase
engine = create_engine(
    "sqlite:///local_events.db",
    echo=False,
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

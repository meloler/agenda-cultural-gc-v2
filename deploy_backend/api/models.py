"""
Modelo Evento para la API (contexto asíncrono).

Refleja EXACTAMENTE la tabla 'evento' que ya existe en PostgreSQL.
NO crea ni modifica la tabla — solo la lee.

Separado de app/models.py para evitar imports cruzados entre
el pipeline de scraping (sync) y la API (async).
"""

from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Evento(SQLModel, table=True):
    """Evento cultural de Gran Canaria (read-only desde la API).

    Tabla: 'evento' — creada y poblada por el pipeline de scraping.
    """

    __tablename__ = "evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    lugar: str = "Sin especificar"
    fecha_raw: str = "Sin fecha"
    fecha_iso: Optional[str] = None
    organiza: str = "Desconocido"
    url_venta: str = Field(unique=True, index=True)
    imagen_url: Optional[str] = None
    descripcion: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    estilo: str = "Otros"
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    source_id: Optional[str] = None
    precio_num: Optional[float] = None
    hora: Optional[str] = None
    enriquecido: bool = Field(default=False)

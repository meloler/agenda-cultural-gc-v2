"""
Modelo de datos principal para eventos culturales de Gran Canaria.

Usa SQLModel: combina Pydantic (validación) + SQLAlchemy (ORM) en una sola clase.
- Como modelo Pydantic: se usa en los scrapers para validar datos.
- Como tabla SQL: se persiste directamente en PostgreSQL.

v3 — Scraping de Precisión: eliminada columna 'precio' (texto "Ver web").
     precio_num es la fuente de verdad numérica.
"""

from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Evento(SQLModel, table=True):
    """Evento cultural de Gran Canaria.

    Tabla: 'evento' (nombre automático en snake_case).
    PK: id autoincremental.
    Unique: hash_id (para lógica de upsert robusta).

    Regla: eventos sin fecha_iso son 'Borrador' y no aparecen en el Excel limpio.
    """

    __tablename__ = "evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    lugar: str = "Sin especificar"
    fecha_raw: str = "Sin fecha"
    fecha_iso: Optional[str] = None
    organiza: str = "Desconocido"
    url_venta: str
    hash_id: str = Field(unique=True, index=True)
    imagen_url: Optional[str] = None
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    estilo: str = "Otros"
    # Campos de geolocalización
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    source_id: Optional[str] = None
    # Datos duros extraídos por scraping/IA
    precio_num: Optional[float] = None
    hora: Optional[str] = None
    estado: str = Field(default="upcoming", index=True)
    enriquecido: bool = Field(default=False)

    @property
    def es_borrador(self) -> bool:
        """Evento sin fecha confirmada = borrador, no sale en Excel limpio."""
        return self.fecha_iso is None

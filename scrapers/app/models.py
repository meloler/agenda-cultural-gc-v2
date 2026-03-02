"""
Modelo de datos principal para eventos culturales de Gran Canaria.

Usa SQLModel: combina Pydantic (validación) + SQLAlchemy (ORM) en una sola clase.
- Como modelo Pydantic: se usa en los scrapers para validar datos.
- Como tabla SQL: se persiste directamente en PostgreSQL.

v3 — Scraping de Precisión: eliminada columna 'precio' (texto "Ver web").
     precio_num es la fuente de verdad numérica.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timezone

from sqlalchemy import Column, Text, JSON, DateTime
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
    
    # === CONCEPTUALIZACIÓN EVENT / OCCURRENCE ===
    # Cada fila en esta tabla actúa como EventOccurrence (sesión única).
    # Este event_group_id agrupará lógicamente múltiples sesiones bajo un Evento Canónico master
    # sin tener que romper el pipeline flat actual con JOINs complejos.
    event_group_id: Optional[str] = Field(default=None, index=True)
    
    # === METADATOS DE CALIDAD Y CONFIANZA ===
    # Ejemplo: {"fecha": 1.0, "hora": 0.8, "precio": 0.5, "lugar": 1.0}
    field_confidence: Dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON, nullable=True))
    
    # Prioridad de la fuente (EntradasCanarias=10, Ticketmaster=20, TomaTicket=30, Scrapers=50)
    source_priority: int = Field(default=50)
    
    # Etiquetas analíticas: "ai_description_generated", "improbable_hour_stripped", "fallback_location"
    quality_flags: List[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=True))
    
    # Trazabilidad de vivo/muerto en el crawler
    last_seen_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))

    @property
    def es_borrador(self) -> bool:
        """Evento sin fecha confirmada = borrador, no sale en Excel limpio."""
        return self.fecha_iso is None

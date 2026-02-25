"""
Schemas Pydantic para request/response de la API.

Separados del modelo ORM para controlar exactamente qué se expone
al frontend y cómo se documenta en Swagger.
"""

from __future__ import annotations

import math
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, computed_field

# ---------------------------------------------------------------------------
# Generic pagination wrapper
# ---------------------------------------------------------------------------

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica."""

    items: list[T]
    total: int = Field(description="Total de registros que coinciden con los filtros")
    page: int = Field(description="Página actual (1-indexed)")
    size: int = Field(description="Tamaño de página solicitado")

    @computed_field  # type: ignore[misc]
    @property
    def pages(self) -> int:
        """Número total de páginas."""
        return math.ceil(self.total / self.size) if self.size > 0 else 0


# ---------------------------------------------------------------------------
# Evento — Schemas de respuesta
# ---------------------------------------------------------------------------


class EventoListItem(BaseModel):
    """Versión resumida de un evento para el feed principal."""

    id: int
    nombre: str
    lugar: str
    fecha_iso: Optional[str] = None
    hora: Optional[str] = None
    precio_num: Optional[float] = None
    estilo: str
    imagen_url: Optional[str] = None
    organiza: str

    model_config = {"from_attributes": True}


class EventoRead(BaseModel):
    """Detalle completo de un evento (todos los campos públicos)."""

    id: int
    nombre: str
    lugar: str
    fecha_raw: str
    fecha_iso: Optional[str] = None
    hora: Optional[str] = None
    organiza: str
    url_venta: str
    imagen_url: Optional[str] = None
    descripcion: Optional[str] = None
    estilo: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    precio_num: Optional[float] = None

    model_config = {"from_attributes": True}


class EventoCercano(EventoListItem):
    """Evento con distancia calculada al punto de referencia."""

    distancia_km: float = Field(description="Distancia en km al punto solicitado")


# ---------------------------------------------------------------------------
# Categoría
# ---------------------------------------------------------------------------


class CategoriaCount(BaseModel):
    """Categoría (estilo) con su conteo de eventos activos."""

    nombre: str = Field(description="Nombre de la categoría (estilo)")
    total: int = Field(description="Cantidad de eventos en esta categoría")

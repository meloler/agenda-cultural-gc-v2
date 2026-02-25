"""
Endpoints de eventos — API pública (read-only).

Todos los endpoints filtran automáticamente los borradores
(eventos sin fecha_iso) para que el frontend solo reciba datos limpios.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, literal_column, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from api.database import get_session
from api.models import Evento
from api.schemas import (
    CategoriaCount,
    EventoCercano,
    EventoListItem,
    EventoRead,
    PaginatedResponse,
)

router = APIRouter(prefix="/api", tags=["Eventos"])

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

_CATEGORIAS_VALIDAS: set[str] = {
    "Música",
    "Teatro",
    "Cine",
    "Danza",
    "Humor",
    "Gastronomía",
    "Deporte",
    "Infantil",
    "Formación",
    "Exposición",
    "Carnaval",
    "Otros",
}

# Haversine SQL fragment (distancia en km)
# Usa coordenadas en grados → radianes dentro de la propia fórmula.
_EARTH_RADIUS_KM = 6371.0


def _haversine_sql(lat: float, lon: float):
    """Devuelve una expresión SQL que calcula la distancia Haversine (km).

    Compatible con PostgreSQL math functions (acos, cos, sin, radians).
    """
    return (
        literal_column(str(_EARTH_RADIUS_KM))
        * func.acos(
            func.cos(func.radians(lat))
            * func.cos(func.radians(col(Evento.latitud)))
            * func.cos(
                func.radians(col(Evento.longitud)) - func.radians(lon)
            )
            + func.sin(func.radians(lat))
            * func.sin(func.radians(col(Evento.latitud)))
        )
    )


# ---------------------------------------------------------------------------
# GET /api/eventos/  — Feed principal paginado con filtros
# ---------------------------------------------------------------------------


@router.get(
    "/eventos/",
    response_model=PaginatedResponse[EventoListItem],
    summary="Feed principal de eventos",
    description=(
        "Devuelve eventos confirmados (con fecha) paginados. "
        "Soporta filtros por categoría y rango de fechas."
    ),
)
async def listar_eventos(
    categoria: Optional[str] = Query(
        None,
        description="Filtrar por categoría/estilo (ej: Música, Teatro)",
        examples=["Música"],
    ),
    fecha_inicio: Optional[str] = Query(
        None,
        description="Fecha mínima en formato YYYY-MM-DD",
        examples=["2026-02-24"],
    ),
    fecha_fin: Optional[str] = Query(
        None,
        description="Fecha máxima en formato YYYY-MM-DD",
        examples=["2026-03-01"],
    ),
    page: int = Query(1, ge=1, description="Número de página (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Resultados por página"),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse[EventoListItem]:
    # Base query: solo eventos confirmados
    stmt = select(Evento).where(col(Evento.fecha_iso).is_not(None))

    # Por defecto solo mostrar eventos desde hoy (no pasados)
    effective_inicio = fecha_inicio or str(date.today())

    # Filtros opcionales
    if categoria:
        stmt = stmt.where(col(Evento.estilo) == categoria)
    stmt = stmt.where(col(Evento.fecha_iso) >= effective_inicio)
    if fecha_fin:
        stmt = stmt.where(col(Evento.fecha_iso) <= fecha_fin)

    # Contar total (sin paginación)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(count_stmt)
    total: int = total_result.scalar_one()

    # Paginación + orden
    offset = (page - 1) * size
    stmt = stmt.order_by(col(Evento.fecha_iso).asc()).offset(offset).limit(size)

    result = await session.execute(stmt)
    eventos = result.scalars().all()

    return PaginatedResponse[EventoListItem](
        items=[EventoListItem.model_validate(e) for e in eventos],
        total=total,
        page=page,
        size=size,
    )


# ---------------------------------------------------------------------------
# GET /api/eventos/cercanos  — Proximidad (Haversine)
# ---------------------------------------------------------------------------


@router.get(
    "/eventos/cercanos",
    response_model=list[EventoCercano],
    summary="Eventos cercanos a una ubicación",
    description=(
        "Devuelve eventos ordenados por cercanía usando la fórmula Haversine. "
        "Requiere coordenadas GPS y un radio en km."
    ),
)
async def eventos_cercanos(
    lat: float = Query(
        ...,
        ge=27.5,
        le=28.3,
        description="Latitud del punto de referencia (Gran Canaria: 27.5–28.3)",
        examples=[28.1096],
    ),
    lon: float = Query(
        ...,
        ge=-16.0,
        le=-15.2,
        description="Longitud del punto de referencia (Gran Canaria: -16.0 – -15.2)",
        examples=[-15.4153],
    ),
    radio_km: float = Query(
        10.0,
        ge=0.1,
        le=100.0,
        description="Radio de búsqueda en kilómetros",
    ),
    session: AsyncSession = Depends(get_session),
) -> list[EventoCercano]:
    dist_expr = _haversine_sql(lat, lon).label("distancia_km")

    stmt = (
        select(Evento, dist_expr)
        .where(
            col(Evento.latitud).is_not(None),
            col(Evento.longitud).is_not(None),
            col(Evento.fecha_iso).is_not(None),
        )
        .having(dist_expr <= radio_km)
        .group_by(col(Evento.id))
        .order_by(text("distancia_km ASC"))
        .limit(50)
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [
        EventoCercano(
            **EventoListItem.model_validate(row.Evento).model_dump(),
            distancia_km=round(row.distancia_km, 2),
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/eventos/{evento_id}  — Detalle completo
# ---------------------------------------------------------------------------


@router.get(
    "/eventos/{evento_id}",
    response_model=EventoRead,
    summary="Detalle de un evento",
    description="Devuelve los datos completos de un evento por su ID.",
)
async def detalle_evento(
    evento_id: int,
    session: AsyncSession = Depends(get_session),
) -> EventoRead:
    stmt = select(Evento).where(col(Evento.id) == evento_id)
    result = await session.execute(stmt)
    evento = result.scalar_one_or_none()

    if evento is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    return EventoRead.model_validate(evento)


# ---------------------------------------------------------------------------
# GET /api/categorias  — Categorías con conteo
# ---------------------------------------------------------------------------


@router.get(
    "/categorias",
    response_model=list[CategoriaCount],
    summary="Categorías disponibles con conteo",
    description=(
        "Lista las categorías (estilo) que tienen al menos un evento confirmado, "
        "junto con la cantidad de eventos en cada una."
    ),
)
async def listar_categorias(
    session: AsyncSession = Depends(get_session),
) -> list[CategoriaCount]:
    hoy = str(date.today())
    stmt = (
        select(
            col(Evento.estilo).label("nombre"),
            func.count(col(Evento.id)).label("total"),
        )
        .where(
            col(Evento.fecha_iso).is_not(None),
            col(Evento.fecha_iso) >= hoy,
        )
        .group_by(col(Evento.estilo))
        .order_by(text("total DESC"))
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [CategoriaCount(nombre=row.nombre, total=row.total) for row in rows]

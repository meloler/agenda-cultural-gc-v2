"""
Operaciones CRUD para la tabla de eventos.
v3 — Scraping de Precisión: sin columna 'precio', usa precio_num/hora directos.
"""

from sqlmodel import Session, select

from app.database import get_session
from app.models import Evento


def guardar_eventos_db(eventos: list[Evento]) -> dict[str, int]:
    """Persiste una lista de eventos en PostgreSQL con lógica de Upsert.

    - Si `url_venta` ya existe → ACTUALIZA datos del scraping.
    - Si no existe → INSERTA un nuevo registro.

    Returns:
        Dict con contadores: {"insertados": N, "actualizados": M}.
    """
    insertados = 0
    actualizados = 0

    with get_session() as session:
        for evento in eventos:
            statement = select(Evento).where(Evento.url_venta == evento.url_venta)
            existente = session.exec(statement).first()

            if existente:
                # ACTUALIZAR campos que pueden cambiar
                existente.nombre = evento.nombre
                existente.fecha_raw = evento.fecha_raw
                existente.fecha_iso = evento.fecha_iso
                existente.estilo = evento.estilo
                existente.imagen_url = evento.imagen_url
                existente.descripcion = evento.descripcion
                existente.latitud = evento.latitud
                existente.longitud = evento.longitud
                existente.source_id = evento.source_id
                # Datos duros del scraping de precisión
                existente.precio_num = evento.precio_num
                existente.hora = evento.hora
                # Resetear flag para re-enriquecer con IA si los datos cambiaron
                existente.enriquecido = False
                session.add(existente)
                actualizados += 1
            else:
                nuevo = Evento(
                    nombre=evento.nombre,
                    lugar=evento.lugar,
                    fecha_raw=evento.fecha_raw,
                    fecha_iso=evento.fecha_iso,
                    organiza=evento.organiza,
                    url_venta=evento.url_venta,
                    imagen_url=evento.imagen_url,
                    descripcion=evento.descripcion,
                    estilo=evento.estilo,
                    latitud=evento.latitud,
                    longitud=evento.longitud,
                    source_id=evento.source_id,
                    precio_num=evento.precio_num,
                    hora=evento.hora,
                    enriquecido=False,
                )
                session.add(nuevo)
                insertados += 1

        session.commit()

    stats = {"insertados": insertados, "actualizados": actualizados}
    print(f"💾 DB: {insertados} insertados, {actualizados} actualizados.")
    return stats

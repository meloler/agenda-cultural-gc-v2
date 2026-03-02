"""
Operaciones CRUD para la tabla de eventos.
v3 — Scraping de Precisión: sin columna 'precio', usa precio_num/hora directos.
"""

import hashlib
from datetime import datetime, timezone
from sqlmodel import Session, select

from app.database import get_session
from app.models import Evento
from app.geocoder import _normalizar


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
            # Generar hash determinista para identificar de forma única a este evento/sesión
            titulo_norm = _normalizar(evento.nombre)
            lugar_norm = _normalizar(evento.lugar) if evento.lugar else ""
            hora_n = str(evento.hora).strip() if evento.hora else ""
            
            raw_id = f"{evento.organiza}|{titulo_norm}|{evento.fecha_iso}|{hora_n}|{lugar_norm}"
            hash_str = hashlib.sha256(raw_id.encode('utf-8')).hexdigest()
            evento.hash_id = hash_str

            statement = select(Evento).where(Evento.hash_id == evento.hash_id)
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
                existente.lugar = evento.lugar
                existente.url_venta = evento.url_venta
                # Resetear flag para re-enriquecer con IA si los datos cambiaron
                existente.enriquecido = False
                existente.last_seen_at = datetime.now(timezone.utc)
                
                # Actualizar también group id y flags si las pasa el scraper
                if evento.event_group_id: existente.event_group_id = evento.event_group_id
                if evento.quality_flags: existente.quality_flags = evento.quality_flags
                if evento.field_confidence: existente.field_confidence = evento.field_confidence
                
                session.add(existente)
                actualizados += 1
            else:
                evento.last_seen_at = datetime.now(timezone.utc)
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
                    hash_id=evento.hash_id,
                    enriquecido=False,
                    event_group_id=evento.event_group_id,
                    field_confidence=evento.field_confidence,
                    source_priority=evento.source_priority,
                    quality_flags=evento.quality_flags,
                    last_seen_at=evento.last_seen_at,
                )
                session.add(nuevo)
                insertados += 1

        session.commit()

    stats = {"insertados": insertados, "actualizados": actualizados}
    print(f"💾 DB: {insertados} insertados, {actualizados} actualizados.")
    return stats

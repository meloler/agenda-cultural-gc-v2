"""
Scraper para EntradasCanarias.com – Deep Scraping de Precisión.

URL: https://entradascanarias.com/

Estructura DOM (validada 2026-02-26):
  - Secciones: "Destacados" y "Conciertos" con tarjetas de evento
  - Cada tarjeta: h5 (nombre), ubicación (texto con 📍), fecha (día + mes en badges)
  - Categoría: StaticText (Conciertos, Otros, Festivales, etc.)
  - Imagen: src de la tarjeta
  - Botón "Cargar más" para paginación
  - ⚠️ Incluye eventos de VARIAS ISLAS (Tenerife, Lanzarote)
  - El scraper filtra solo eventos de Gran Canaria.

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, limpiar_texto


# Ubicaciones válidas para Gran Canaria
UBICACIONES_GC = [
    "las palmas", "gran canaria", "telde", "arucas", "gáldar", "galdar",
    "agüimes", "aguimes", "ingenio", "santa lucía", "santa lucia",
    "san bartolomé", "san bartolome", "mogán", "mogan", "teror", "firgas",
    "valsequillo", "tejeda", "artenara", "agaete", "moya", "guía", "guia",
    "santa brígida", "santa brigida", "vega de san mateo", "valleseco",
    "maspalomas", "playa del inglés", "playa del ingles", "vecindario",
    "puerto rico", "arguineguín", "arguineguin", "arinaga", "el puertillo",
    "tarajalillo", "infecar", "gc arena", "sala faro", "canarias en vivo",
    "imaginario", "paraninfo", "sotano analogico", "la juntadera",
    "taurito",
]

# Ubicaciones que NO son Gran Canaria (otras islas, península)
EXCLUSIONES = [
    "tenerife", "lanzarote", "fuerteventura", "la palma", "la gomera",
    "el hierro", "arrecife", "adeje", "la laguna", "santa cruz de tenerife",
    "diferentes ciudades",
]


def _es_gran_canaria(texto_ubicacion: str) -> bool:
    """Verifica si la ubicación corresponde a Gran Canaria."""
    if not texto_ubicacion:
        return False
    t = texto_ubicacion.lower()

    # Si explícitamente menciona otra isla → rechazar
    if any(ex in t for ex in EXCLUSIONES):
        return False

    # Si menciona un municipio/lugar de GC → aceptar
    if any(m in t for m in UBICACIONES_GC):
        return True

    return False


MESES_MAP = {
    "ene": "01", "feb": "02", "mar": "03", "abr": "04",
    "may": "05", "jun": "06", "jul": "07", "ago": "08",
    "sep": "09", "oct": "10", "nov": "11", "dic": "12",
}


def _parsear_fecha_badge(dia: str, mes_abrev: str) -> str | None:
    """Convierte día + mes abreviado en fecha ISO."""
    try:
        mes = MESES_MAP.get(mes_abrev.lower()[:3])
        if not mes:
            return None
        dia_num = dia.strip().zfill(2)
        return f"2026-{mes}-{dia_num}"
    except Exception:
        return None


async def scrape_entradas_canarias(page: Page) -> list[Evento]:
    """Scraper para EntradasCanarias.com con filtro geográfico Gran Canaria.

    Fase 1: Carga la página y hace click en "Cargar más" para obtener todos los eventos.
    Fase 2: Extrae datos de las tarjetas con JS.
    Fase 3: Filtra por ubicación y enriquece con deep scraping.
    """
    print("🏝️ EntradasCanarias.com...")
    eventos_raw: list[dict] = []

    try:
        # === FASE 1: Fetch desde APIs ===
        api_current = "https://12bwlcduo0.execute-api.eu-west-1.amazonaws.com/events/current-events"
        api_slider = "https://12bwlcduo0.execute-api.eu-west-1.amazonaws.com/events/slider-events"
        
        try:
            resp_curr = await page.request.get(api_current, timeout=15000)
            data_curr = await resp_curr.json() if resp_curr.ok else []
        except Exception as e:
            print(f"      [DEBUG] Error fetching current-events: {e}")
            data_curr = []
            
        try:
            resp_slid = await page.request.get(api_slider, timeout=15000)
            data_slid = await resp_slid.json() if resp_slid.ok else []
        except Exception as e:
            print(f"      [DEBUG] Error fetching slider-events: {e}")
            data_slid = []
            
        seen_keys = set()
        
        # Procesar current-events
        for item in data_curr:
            try:
                nombre = item.get("title", "")
                slug = item.get("slug", "")
                if not nombre or not slug: 
                    continue
                
                url_full = item.get("url") or f"https://ventas.entradascanarias.com/events/{slug}"
                
                sessions = item.get("sessions", [])
                venue = item.get("venue", "")
                master_id = item.get("masterId", "")
                
                # Filtro Geográfico general del item
                loc_str = f"{item.get('province', '')} {item.get('city', '')} {venue}".lower()
                if not _es_gran_canaria(loc_str):
                    continue
                    
                lugar = limpiar_texto(venue) or "Gran Canaria"

                if not sessions:
                    # Fallback si no hay sessions, aunque es raro
                    sessions = [{"date": ""}]

                for sess in sessions:
                    date_str = sess.get("date", "")
                    fecha_iso_val = None
                    hora_val = None
                    sess_id = sess.get("id", "")
                    if date_str:
                        from dateutil.parser import isoparse
                        from zoneinfo import ZoneInfo
                        try:
                            dt = isoparse(date_str)
                            if dt.tzinfo is not None:
                                dt = dt.astimezone(ZoneInfo("Atlantic/Canary"))
                            fecha_iso_val = dt.date().isoformat()
                            hora_val = dt.strftime("%H:%M")
                        except Exception:
                            pass

                    # Para deduplicar internamente (masterId + fecha + hora o slug + fecha + hora + venue)
                    dup_key = f"{master_id}_{fecha_iso_val}_{hora_val}" if master_id and fecha_iso_val else f"{slug}_{fecha_iso_val}_{hora_val}_{venue}"
                    if dup_key in seen_keys:
                        continue
                    seen_keys.add(dup_key)
                    
                    eventos_raw.append({
                        "nombre": limpiar_texto(nombre),
                        "url_full": url_full,
                        "img_card": _validar_imagen(item.get("imageUrl")),
                        "lugar": lugar,
                        "precio_api": item.get("minPrice"),
                        "fecha_raw": date_str or "Sin fecha",
                        "fecha_iso": fecha_iso_val,
                        "hora_api": hora_val,
                        "source_id": f"EC|{master_id or slug}|{sess_id}",
                    })
            except Exception:
                continue
                
        # Procesar slider-events
        for item in data_slid:
            try:
                nombre = item.get("eventTitle", "")
                url_full = item.get("eventUrl", "")
                venue = item.get("eventLocation", "")
                date_str = item.get("eventDate", "")
                
                if not nombre or not url_full: 
                    continue
                
                dup_key = f"{nombre}_{venue}"
                if dup_key in seen_keys:
                    continue
                seen_keys.add(dup_key)
                
                loc_str = venue.lower()
                if not _es_gran_canaria(loc_str):
                    continue
                    
                lugar = limpiar_texto(venue) or "Gran Canaria"
                
                eventos_raw.append({
                    "nombre": limpiar_texto(nombre),
                    "url_full": url_full,
                    "img_card": _validar_imagen(item.get("imageUrl")),
                    "lugar": lugar,
                    "precio_api": None,
                    "fecha_raw": date_str or "Sin fecha",
                    "fecha_iso": None,
                })
            except Exception:
                continue

        print(f"   -> {len(eventos_raw)} eventos de Gran Canaria (filtrados vía API)")

        # === FASE 3: Deep Scraping (solo si tenemos URL individual) ===
        print(f"   -> Procesando {len(eventos_raw)} eventos de EntradasCanarias...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            # Si tenemos URL individual, hacer deep scraping
            if raw["url_full"] and "entradascanarias.com" in raw["url_full"] and raw["url_full"] != "https://entradascanarias.com/":
                try:
                    detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
                    imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]
                    
                    # Las sesiones API son más fiables por cada pase horario que la página individual (que puede tener múltiples pasados)
                    fecha_iso = raw["fecha_iso"] or detalle["fecha_iso"]
                    fecha_raw = raw["fecha_raw"] or detalle.get("fecha_raw")
                    hora = raw.get("hora_api") or detalle["hora"]
                    
                    precio = detalle["precio_num"] if detalle["precio_num"] is not None else raw.get("precio_api")
                    descripcion = detalle["descripcion"]
                except Exception:
                    imagen_final = raw["img_card"]
                    fecha_iso = raw["fecha_iso"]
                    fecha_raw = raw["fecha_raw"]
                    precio = raw.get("precio_api")
                    hora = raw.get("hora_api")
                    descripcion = None
            else:
                imagen_final = raw["img_card"]
                fecha_iso = raw["fecha_iso"]
                fecha_raw = raw["fecha_raw"]
                precio = raw.get("precio_api")
                hora = raw.get("hora_api")
                descripcion = None

            eventos.append(
                Evento(
                    nombre=raw["nombre"],
                    lugar=raw["lugar"],
                    fecha_raw=fecha_raw or "Sin fecha",
                    fecha_iso=fecha_iso,
                    precio_num=precio,
                    hora=hora,
                    organiza="EntradasCanarias",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=descripcion,
                    estilo=categorizar_pro(raw["nombre"], "EntradasCanarias"),
                    source_id=raw.get("source_id"),
                )
            )

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        con_img = sum(1 for e in eventos if e.imagen_url)
        print(f"   -> EntradasCanarias: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} img:{con_img})")

    except Exception as e:
        print(f"   ❌ Error EntradasCanarias: {e}")

    return eventos if "eventos" in dir() else []

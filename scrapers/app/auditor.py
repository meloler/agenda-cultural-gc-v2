"""
Auditor "Detective" — Análisis profundo de precisión de datos.

v2 – Deep Scraping Edition:
  - Busca recintos específicos cuando el lugar es genérico ("Gran Canaria").
  - Usa título, URL y descripción como pistas para detectar el venue real.
  - **NUEVO:** Deep Scrape con Playwright para Tomaticket/Tickety cuando las
    heurísticas de texto no encuentran nada.
  - Limpia basura: nombres que son solo números, idénticos al lugar, etc.
  - Corrige precios absurdos (> 300 = error de parser, no precio real).
  - Se ejecuta ANTES del enricher (IA) y ANTES del geocoder.

Estrategia de detección (5 capas):
  1. Extraer recinto del título: "Origen Sala Scala" → "Sala Scala"
  2. Extraer recinto de la descripción: "en el salón de actos" → directo
  3. Extraer recinto de la URL (dominio): "teatroperezgaldos.es" → "Teatro Pérez Galdós"
  4. Patrones regex: "Calle ...", "Campus ...", "Edificio ..."
  5. Deep Scrape (Playwright): visita la URL y scrape selectores de venue
"""

import asyncio
import re
from sqlmodel import select

from app.database import get_session
from app.geocoder import es_lugar_generico, _normalizar
from app.models import Evento

# ─────────────────────────────────────────────────────────────────────
# Mapa de recintos extraíbles del título o la descripción
# Se buscan como subcadenas normalizadas.
# ─────────────────────────────────────────────────────────────────────
RECINTOS_CONOCIDOS: list[tuple[str, str]] = [
    # (patrón normalizado a buscar, nombre canónico a asignar)
    # ── Teatros ──
    ("teatro cuyas",                 "Teatro Cuyás"),
    ("teatro guiniguada",            "Teatro Guiniguada"),
    ("teatro perez galdos",          "Teatro Pérez Galdós"),
    ("sala insular de teatro",       "Sala Insular de Teatro"),
    # ── Auditorios / Salas ──
    ("auditorio alfredo kraus",      "Auditorio Alfredo Kraus"),
    ("auditorio a. kraus",           "Auditorio Alfredo Kraus"),
    ("auditorio kraus",              "Auditorio Alfredo Kraus"),
    ("alfredo kraus",                "Auditorio Alfredo Kraus"),
    ("sala scala",                   "Sala Scala"),
    ("sala miller",                  "Sala Miller"),
    ("edificio miller",              "Edificio Miller"),
    ("gran canaria arena",           "Gran Canaria Arena"),
    # ── Centros culturales ──
    ("cicca",                        "CICCA"),
    ("casa de colon",                "Casa de Colón"),
    ("museo elder",                  "Museo Elder"),
    ("caam",                         "CAAM"),
    ("centro atlantico de arte",     "CAAM"),
    ("gabinete literario",           "Gabinete Literario"),
    ("casa africa",                  "Casa África"),
    # ── Ocio / conciertos ──
    ("paper club",                   "Paper Club"),
    ("the paper club",               "The Paper Club"),
    ("canarias en vivo",             "Canarias en Vivo"),
    ("la azotea",                    "La Azotea"),
    ("el sotano",                    "El Sótano"),
    # ── Parques / plazas ──
    ("parque santa catalina",        "Parque Santa Catalina"),
    ("parque san telmo",             "Parque San Telmo"),
    ("parque doramas",               "Parque Doramas"),
    ("plaza de la musica",           "Plaza de la Música"),
    ("plaza de las ranas",           "Plaza de las Ranas"),
    # ── Universidad ──
    ("campus del obelisco",          "Campus del Obelisco"),
    ("campus obelisco",              "Campus del Obelisco"),
    ("facultad de humanidades",      "Facultad de Humanidades ULPGC"),
    # ── Deportivos ──
    ("estadio de gran canaria",      "Estadio de Gran Canaria"),
    ("estadio gran canaria",         "Estadio de Gran Canaria"),
    # ── Recintos especiales ──
    ("infecar",                      "INFECAR"),
    ("recinto ferial",               "Recinto Ferial INFECAR"),
    ("centro penitenciario",         "Centro Penitenciario Las Palmas"),
    ("palmitos park",                "Palmitos Park"),
    ("aqualand",                     "Aqualand Maspalomas"),
    ("holidayworld",                 "HolidayWorld Maspalomas"),
]

# Mapa de dominios → recintos (cuando la URL delata el venue)
DOMINIO_A_RECINTO: dict[str, str] = {
    "teatroperezgaldos.es":     "Teatro Pérez Galdós",
    "auditorioalfredokraus.es": "Auditorio Alfredo Kraus",
    "teatroguiniguada.es":      "Teatro Guiniguada",
    "cicca.es":                 "CICCA",
    "teatrocuyas.com":          "Teatro Cuyás",
    "salaescala.com":           "Sala Scala",
    "salamiller.es":            "Sala Miller",
    "grancanariaarena.com":     "Gran Canaria Arena",
}

from app.utils.parsers import RE_DIRECCION, RE_NOMBRE_BASURA


# ─────────────────────────────────────────────────────────────────────
# Capas 1-4: Detección heurística (sin red)
# ─────────────────────────────────────────────────────────────────────
def _detectar_recinto_en_texto(texto: str) -> str | None:
    """Busca un recinto conocido dentro de un texto (título, descripción)."""
    if not texto:
        return None

    texto_norm = _normalizar(texto)

    for patron, nombre_canonico in RECINTOS_CONOCIDOS:
        if patron in texto_norm:
            return nombre_canonico

    return None


def _detectar_recinto_en_url(url: str) -> str | None:
    """Extrae el recinto a partir del dominio de la URL."""
    if not url:
        return None

    url_lower = url.lower()
    for dominio, recinto in DOMINIO_A_RECINTO.items():
        if dominio in url_lower:
            return recinto

    return None


def _detectar_direccion_en_texto(texto: str) -> str | None:
    """Busca referencias a direcciones/campus/salones en la descripción."""
    if not texto:
        return None

    match = RE_DIRECCION.search(texto)
    if match:
        direccion = match.group(1).strip()
        if len(direccion) > 5:
            return direccion

    return None


def _detectar_lugar_real(evento: "Evento") -> str | None:
    """Intenta detectar el recinto real usando heurísticas (capas 1-4).

    Capas (en orden de prioridad):
      1. Recinto conocido en el título
      2. Recinto conocido en la descripción
      3. Dominio de la URL
      4. Dirección/campus/salón en la descripción
    """
    # Capa 1: título
    recinto = _detectar_recinto_en_texto(evento.nombre)
    if recinto:
        return recinto

    # Capa 2: descripción
    recinto = _detectar_recinto_en_texto(evento.descripcion)
    if recinto:
        return recinto

    # Capa 3: URL
    recinto = _detectar_recinto_en_url(evento.url_venta)
    if recinto:
        return recinto

    # Capa 4: dirección literal
    direccion = _detectar_direccion_en_texto(evento.descripcion)
    if direccion:
        return direccion

    return None


# ─────────────────────────────────────────────────────────────────────
# Capa 5: Deep Scrape con Playwright (visitar la URL del evento)
# ─────────────────────────────────────────────────────────────────────

# Selectores confirmados por fuente para la ubicación/venue
SELECTORES_VENUE: dict[str, list[str]] = {
    "tomaticket": [
        ".nombre-recinto",           # <div class="nombre-recinto">Sala Scala</div>
        ".place-name",
        ".venue-name",
        "[class*='recinto']",
        "[class*='venue']",
    ],
    "tickety": [
        "address",                   # <address>Teatro Cuyás, Las Palmas</address>
        ".event-location",
        ".venue",
        "[class*='location']",
        "[class*='venue']",
    ],
}


def _identificar_fuente(url: str) -> str | None:
    """Identifica si una URL pertenece a Tomaticket o Tickety."""
    if not url:
        return None
    url_lower = url.lower()
    if "tomaticket" in url_lower:
        return "tomaticket"
    if "tickety" in url_lower:
        return "tickety"
    return None


async def _deep_scrape_venue(url: str) -> str | None:
    """Visita la URL del evento con Playwright y extrae el nombre del venue.

    Solo se activa para URLs de Tomaticket y Tickety.
    Lee selectores CSS confirmados; si encuentra texto válido, lo retorna.
    """
    fuente = _identificar_fuente(url)
    if not fuente:
        return None

    selectores = SELECTORES_VENUE.get(fuente, [])
    if not selectores:
        return None

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)  # Esperar JS dinámico

                for selector in selectores:
                    try:
                        el = page.locator(selector).first
                        if await el.count() > 0:
                            texto = (await el.text_content() or "").strip()
                            # Validar que no sea genérico
                            if texto and len(texto) > 2 and not es_lugar_generico(texto):
                                print(f"      🔎 Deep Scrape [{fuente}]: '{texto}'")
                                await browser.close()
                                return texto
                    except Exception:
                        continue

            except Exception as e:
                print(f"      ⚠️ Deep Scrape error ({url[:50]}): {e}")
            finally:
                await browser.close()

    except ImportError:
        print("      ⚠️ Playwright no disponible para Deep Scrape")
    except Exception as e:
        print(f"      ⚠️ Deep Scrape fallo general: {e}")

    return None


# ─────────────────────────────────────────────────────────────────────
# Validadores de basura
# ─────────────────────────────────────────────────────────────────────
def _es_basura(evento: "Evento") -> bool:
    """Detecta si un evento es basura y debería eliminarse.

    Criterios:
      - Nombre es solo un número (ej: "2")
      - Nombre es vacío o solo whitespace
      - Nombre es idéntico al lugar (ej: nombre="Cicca", lugar="CICCA")
      - Nombre tiene menos de 3 caracteres
    """
    nombre = (evento.nombre or "").strip()

    # Nombre vacío o muy corto
    if len(nombre) < 3:
        return True

    # Nombre es solo números/puntuación
    if RE_NOMBRE_BASURA.match(nombre):
        return True

    # Nombre idéntico al lugar (error de scraping)
    nombre_norm = _normalizar(nombre)
    lugar_norm = _normalizar(evento.lugar)
    if nombre_norm and lugar_norm and nombre_norm == lugar_norm:
        return True

    return False


def _precio_absurdo(precio: float | None) -> bool:
    """Detecta precios absurdos (> 300€ es casi seguro un error de parser).

    El parser suele confundir años (2025, 2026) con precios.
    Pero 300€ ya es el máximo razonable para un evento en GC.
    """
    if precio is None:
        return False
    return precio > 300


# ─────────────────────────────────────────────────────────────────────
# Pipeline: auditar todos los eventos (SYNC wrapper + ASYNC deep scrape)
# ─────────────────────────────────────────────────────────────────────
async def _auditar_eventos_async() -> dict[str, int]:
    """Versión async de la auditoría — necesaria para Deep Scrape."""
    print("\n" + "=" * 60)
    print("🔍 AUDITORÍA DE PRECISIÓN (Detective v2)")
    print("=" * 60)

    stats = {
        "total": 0,
        "lugares_corregidos": 0,
        "deep_scrape_hits": 0,
        "basura_eliminada": 0,
        "precios_corregidos": 0,
    }

    with get_session() as session:
        todos = list(session.exec(select(Evento)).all())
        stats["total"] = len(todos)
        print(f"   📊 Eventos a auditar: {stats['total']}")

        eliminados_ids: list[int] = []
        # Eventos que necesitan deep scrape (lugar genérico + heurísticas fallaron)
        pendientes_deep: list["Evento"] = []

        for evento in todos:
            # ── Paso 1: ¿Es basura? ──
            if _es_basura(evento):
                print(f"      🗑️ Basura: '{evento.nombre}' (id={evento.id})")
                eliminados_ids.append(evento.id)
                stats["basura_eliminada"] += 1
                continue

            # ── Paso 2: ¿Lugar genérico? Intentar corregir con heurísticas ──
            if es_lugar_generico(evento.lugar):
                lugar_real = _detectar_lugar_real(evento)
                if lugar_real:
                    lugar_anterior = evento.lugar
                    evento.lugar = lugar_real
                    evento.latitud = None
                    evento.longitud = None
                    session.add(evento)
                    stats["lugares_corregidos"] += 1
                    print(f"      📍 '{evento.nombre[:45]}': "
                          f"'{lugar_anterior}' → '{evento.lugar}'")
                else:
                    # Heurísticas no encontraron nada → candidato a Deep Scrape
                    pendientes_deep.append(evento)

            # ── Paso 3: ¿Precio absurdo (> 300)? ──
            if _precio_absurdo(evento.precio_num):
                print(f"      💰 Precio corregido: '{evento.nombre[:40]}' "
                      f"{evento.precio_num} → NULL (parser error)")
                evento.precio_num = None
                session.add(evento)
                stats["precios_corregidos"] += 1

        # ── Paso 4: Deep Scrape para los que aún son genéricos ──
        if pendientes_deep:
            print(f"\n   🔎 Deep Scraping {len(pendientes_deep)} eventos con lugar genérico...")

            for evento in pendientes_deep:
                url = evento.url_venta
                fuente = _identificar_fuente(url)
                if not fuente:
                    continue  # Solo deep-scrapeamos Tomaticket/Tickety

                venue = await _deep_scrape_venue(url)
                if venue:
                    lugar_anterior = evento.lugar
                    evento.lugar = venue
                    evento.latitud = None
                    evento.longitud = None
                    session.add(evento)
                    stats["deep_scrape_hits"] += 1
                    stats["lugares_corregidos"] += 1
                    print(f"      🎯 Deep: '{evento.nombre[:40]}': "
                          f"'{lugar_anterior}' → '{venue}'")

        # Eliminar basura en bloque
        if eliminados_ids:
            for eid in eliminados_ids:
                obj = session.get(Evento, eid)
                if obj:
                    session.delete(obj)

        session.commit()

    print(f"\n   📊 AUDITORÍA COMPLETADA:")
    print(f"      Total auditados:    {stats['total']}")
    print(f"      Lugares corregidos: {stats['lugares_corregidos']}")
    print(f"        (de los cuales Deep Scrape: {stats['deep_scrape_hits']})")
    print(f"      Basura eliminada:   {stats['basura_eliminada']}")
    print(f"      Precios corregidos: {stats['precios_corregidos']}")
    print("=" * 60)

    return stats


async def auditar_eventos() -> dict[str, int]:
    """Audita y corrige todos los eventos en la DB.

    Función async porque incluye Deep Scrape con Playwright.
    Se debe llamar con `await auditar_eventos()` desde main.py.
    """
    return await _auditar_eventos_async()

"""
Scraper para Entradium.com – Gran Canaria.

URL: https://entradium.com/es/search

Estrategia:
  1. Submit del formulario de búsqueda (POST) con términos de Gran Canaria.
     El parámetro de URL ?q= se ignora; hay que rellenar #search_q y enviar.
  2. Pre-filtro por slug de URL: si contiene keywords GC → aceptar sin esperar
     deep scraping; si contiene exclusiones de otras islas → descartar.
  3. Deep scraping de fichas individuales con enriquecer_evento().
  4. Filtro geográfico final sobre el lugar extraído del deep scraping.

Búsquedas: "las palmas", "gran canaria", "telde", "vecindario", "arucas".
           (Cada búsqueda devuelve 32 resultados; se deduplicá por URL.)

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, limpiar_texto

# ──────────────────────────────────────────────────────────────────────────────
# Constantes geográficas
# ──────────────────────────────────────────────────────────────────────────────

TERMINOS_GC = [
    "las palmas",
    "gran canaria",
    "telde",
    "vecindario",
    "arucas",
]

# Palabras en el SLUG que confirman Gran Canaria sin necesidad de deep scraping
SLUG_GC = [
    "las-palmas", "gran-canaria", "canarias-en-vivo",
    "telde", "vecindario", "arucas", "agaete",
    "maspalomas", "ingenio", "aguimes",
]

# Palabras en el lugar extraído que confirman GC
MUNICIPIOS_GC = [
    "las palmas", "gran canaria", "telde", "arucas", "gáldar", "galdar",
    "agüimes", "aguimes", "ingenio", "santa lucía", "santa lucia",
    "san bartolomé", "san bartolome", "mogán", "mogan", "teror", "firgas",
    "valsequillo", "tejeda", "artenara", "agaete", "moya", "guía", "guia",
    "santa brígida", "santa brigida", "vega de san mateo", "valleseco",
    "maspalomas", "playa del inglés", "playa del ingles", "vecindario",
    "puerto rico", "arguineguín", "arguineguin", "arinaga",
    "infecar", "gc arena", "canarias en vivo",
]

# Palabras en el slug o lugar que descartan (otras islas / península)
EXCLUSIONES_SLUG = [
    "sevilla", "madrid", "barcelona", "valencia", "bilbao", "granada",
    "malaga", "cordoba", "cadiz", "murcia", "alicante", "castellon",
    "tenerife", "lanzarote", "fuerteventura", "la-palma", "la-gomera",
    "el-hierro", "arrecife", "adeje", "la-laguna",
]

EXCLUSIONES_LUGAR = [
    "tenerife", "lanzarote", "fuerteventura", "la palma", "la gomera",
    "el hierro", "arrecife", "adeje", "la laguna", "santa cruz de tenerife",
    "sevilla", "madrid", "barcelona", "valencia",
]


def _slug_es_gc(slug: str) -> bool | None:
    """
    Analiza el slug de la URL del evento.
    Retorna True (es GC), False (NO es GC) o None (no se puede determinar).
    """
    s = slug.lower()
    if any(ex in s for ex in EXCLUSIONES_SLUG):
        return False
    if any(kw in s for kw in SLUG_GC):
        return True
    return None


def _lugar_es_gc(lugar: str) -> bool:
    """
    True si el lugar enriquecido NO pertenece explícitamente a otra ciudad.
    Lógica invertida: los eventos vienen de búsquedas GC, así que solo
    descartamos si el venue menciona claramente otra isla o península.
    """
    if not lugar:
        return True  # sin lugar → beneficio de la duda (viene de búsqueda GC)
    t = lugar.lower()
    return not any(ex in t for ex in EXCLUSIONES_LUGAR)


# ──────────────────────────────────────────────────────────────────────────────
# Scraper principal
# ──────────────────────────────────────────────────────────────────────────────

async def _buscar_termino(page: Page, termino: str) -> list[str]:
    """
    Navega a /es/search, rellena el formulario y devuelve la lista de URLs
    de eventos encontrados.
    """
    try:
        await page.goto(
            "https://entradium.com/es/search",
            wait_until="networkidle",
            timeout=30000,
        )
        await page.fill("#search_q", termino)
        await page.press("#search_q", "Enter")
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(0.8)

        urls = await page.evaluate("""() =>
            Array.from(document.querySelectorAll("a[href*='/es/events/']"))
                .map(a => a.href)
        """)
        return list(dict.fromkeys(urls))  # conservar orden, sin duplicados
    except Exception as e:
        print(f"   [Entradium] Error buscando '{termino}': {e}")
        return []


async def scrape_entradium(page: Page) -> list[Evento]:
    """
    Scraper para Entradium.com filtrando eventos de Gran Canaria.

    Fase 1 – Recopilación: submit del formulario por cada término GC.
    Fase 2 – Pre-filtro:   descarta slugs de otras ciudades; acepta slugs GC.
    Fase 3 – Deep scraping: visita cada ficha para obtener lugar exacto.
    Fase 4 – Filtro final:  acepta solo eventos con lugar en Gran Canaria.
    """
    print("[Entradium] Iniciando...")

    await page.set_extra_http_headers({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9",
    })

    # ── Fase 1: Recopilación de URLs ──────────────────────────────────────────
    seen_urls: set[str] = set()
    candidatos: list[dict] = []  # {url, slug, termino}

    for termino in TERMINOS_GC:
        urls = await _buscar_termino(page, termino)
        nuevas = 0
        for url in urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            slug = url.split("/es/events/")[-1].rstrip("/")
            candidatos.append({"url": url, "slug": slug, "termino": termino})
            nuevas += 1
        print(f"   -> '{termino}': {len(urls)} resultados ({nuevas} nuevos)")

    # ── Fase 2: Pre-filtro por slug ───────────────────────────────────────────
    para_deep: list[dict] = []
    pre_aceptados: list[dict] = []   # slug confirma GC
    descartados = 0

    for c in candidatos:
        verdict = _slug_es_gc(c["slug"])
        if verdict is False:
            descartados += 1
        elif verdict is True:
            pre_aceptados.append(c)
        else:
            para_deep.append(c)  # slug ambiguo → necesita deep scraping

    print(
        f"   -> {len(candidatos)} candidatos | "
        f"slug-GC: {len(pre_aceptados)} | "
        f"ambiguos: {len(para_deep)} | "
        f"descartados: {descartados}"
    )

    todos_para_procesar = pre_aceptados + para_deep

    # ── Fase 3 & 4: Deep scraping + filtro geográfico ─────────────────────────
    eventos: list[Evento] = []
    seen_texts: set[str] = set()

    for c in todos_para_procesar:
        url_ev = c["url"]
        nombre_slug = limpiar_texto(c["slug"].replace("-", " "))

        try:
            detalle = await enriquecer_evento(page, url_ev, nombre_slug, seen_texts)
        except Exception as e:
            print(f"   [Entradium] deep error {c['slug']}: {e}")
            detalle = {
                "imagen_url": None, "fecha_iso": None, "fecha_raw": None,
                "hora": None, "precio_num": None, "descripcion": None,
                "lugar_deep": None, "nombre_deep": None,
            }

        nombre_final = detalle.get("nombre_deep") or nombre_slug
        lugar_final = detalle.get("lugar_deep") or ""

        # Filtro geográfico: descartar solo si el venue menciona otra ciudad
        if not _lugar_es_gc(lugar_final):
            continue

        lugar_salida = lugar_final or "Gran Canaria"

        imagen_final = _validar_imagen(detalle["imagen_url"])

        eventos.append(
            Evento(
                nombre=nombre_final,
                lugar=lugar_salida,
                fecha_raw=limpiar_texto(detalle.get("fecha_raw") or "Sin fecha"),
                fecha_iso=detalle["fecha_iso"],
                precio_num=detalle["precio_num"],
                hora=detalle["hora"],
                organiza="Entradium",
                url_venta=url_ev,
                imagen_url=imagen_final,
                descripcion=detalle["descripcion"],
                estilo=categorizar_pro(nombre_final, "Entradium"),
            )
        )

    # Log de calidad
    con_precio = sum(1 for e in eventos if e.precio_num is not None)
    con_fecha  = sum(1 for e in eventos if e.fecha_iso)
    con_hora   = sum(1 for e in eventos if e.hora)
    con_img    = sum(1 for e in eventos if e.imagen_url)
    print(
        f"   -> Entradium: {len(eventos)} eventos GC "
        f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} img:{con_img})"
    )

    return eventos

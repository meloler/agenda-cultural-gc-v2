"""
Scraper para Entrées.es (búsqueda Gran Canaria) – Deep Scraping de Precisión.

URL: https://entrees.es/busqueda/gran-canaria

Estructura DOM (validada 2026-02-26):
  - Tarjetas con imagen, badge de fecha (mes + día), nombre (h3), ubicación (📍)
  - Badge de ciudad al fondo de cada tarjeta (ej: "Gran Canaria", "Las Palmas de Gran Canaria")
  - ⚠️ MEZCLA EVENTOS DE TODA ESPAÑA: Bilbao, A Coruña, etc.
  - El scraper DEBE filtrar estrictamente por ubicación Gran Canaria.

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, limpiar_texto, normalizar_fecha


# Municipios y términos válidos para filtrar Gran Canaria
UBICACIONES_GC = [
    "gran canaria", "las palmas", "telde", "arucas", "gáldar", "galdar",
    "agüimes", "aguimes", "ingenio", "santa lucía", "santa lucia",
    "san bartolomé", "san bartolome", "mogán", "mogan", "teror", "firgas",
    "valsequillo", "tejeda", "artenara", "agaete", "moya", "guía", "guia",
    "santa brígida", "santa brigida", "vega de san mateo", "valleseco",
    "maspalomas", "playa del inglés", "playa del ingles", "vecindario",
    "puerto rico", "arguineguín", "arguineguin", "arinaga", "el puertillo",
    "tarajalillo", "infecar", "gc arena",
]


def _es_ubicacion_gc(texto: str) -> bool:
    """Verifica si la ubicación es de Gran Canaria."""
    if not texto:
        return False
    t = texto.lower()
    return any(m in t for m in UBICACIONES_GC)


async def scrape_entrees(page: Page) -> list[Evento]:
    """Scraper para Entrées.es – búsqueda Gran Canaria con filtro geográfico estricto.

    Fase 1: Extrae tarjetas de eventos con scroll para cargar más.
    Fase 2: Filtra solo los de Gran Canaria.
    Fase 3: Deep scraping de cada ficha.
    """
    print("🎪 Entrées.es...")
    eventos_raw: list[dict] = []

    try:
        # === FASE 1: Carga de la página de búsqueda ===
        await page.goto(
            "https://entrees.es/busqueda/gran-canaria",
            wait_until="domcontentloaded",
            timeout=25000,
        )

        # Esperar a que carguen las tarjetas
        try:
            await page.wait_for_selector("a[href*='/evento/'], a[href*='/entradas/']", timeout=10000)
        except Exception:
            pass

        # Scroll para cargar más tarjetas
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)

        # Extraer datos de las tarjetas
        items = await page.evaluate("""
            () => {
                const results = [];
                const cards = document.querySelectorAll('a[href*="/evento/"], a[href*="/entradas/"]');
                const seen = new Set();
                
                for (const card of cards) {
                    const url = card.href;
                    if (!url || seen.has(url)) continue;
                    seen.add(url);
                    
                    const text = card.textContent || '';
                    const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                    
                    // Nombre: buscar h3, h2, o el texto más largo
                    const h3 = card.querySelector('h3, h2, [class*="title"]');
                    let nombre = h3 ? h3.textContent.trim() : '';
                    if (!nombre && lines.length > 0) {
                        nombre = lines.reduce((a, b) => a.length > b.length ? a : b, '');
                    }
                    
                    // Ubicación: texto con icono de pin
                    let ubicacion = '';
                    const locEl = card.querySelector('[class*="location"], [class*="lugar"], [class*="venue"]');
                    if (locEl) {
                        ubicacion = locEl.textContent.trim();
                    }
                    // También buscar texto completo para ubicación
                    const fullText = text.toLowerCase();
                    
                    // Imagen
                    const img = card.querySelector('img');
                    const imgSrc = img ? (img.getAttribute('data-image') || img.src || img.dataset.src) : null;
                    
                    // Badge de ciudad (suele estar al fondo de la tarjeta)
                    const badges = card.querySelectorAll('[class*="badge"], [class*="city"], [class*="tag"]');
                    let ciudad = '';
                    badges.forEach(b => {
                        const bt = b.textContent.trim();
                        if (bt.length > 2 && bt.length < 50) {
                            ciudad += ' ' + bt;
                        }
                    });
                    
                    results.push({
                        nombre: nombre,
                        url: url,
                        ubicacion: ubicacion,
                        ciudad: ciudad,
                        fullText: fullText.substring(0, 600),
                        img: imgSrc,
                    });
                }
                return results;
            }
        """)

        print(f"   -> {len(items)} tarjetas totales en Entrées.es")

        # === FASE 2: Filtro geográfico estricto ===
        for item in items:
            nombre = limpiar_texto(item.get("nombre", ""))
            url = item.get("url", "")
            ubicacion = item.get("ubicacion", "")
            ciudad = item.get("ciudad", "")
            texto_completo = item.get("fullText", "")
            img = _validar_imagen(item.get("img"))

            if not nombre or not url:
                continue

            # Verificar que es Gran Canaria en ubicación, ciudad o texto completo
            es_gc = (
                _es_ubicacion_gc(ubicacion)
                or _es_ubicacion_gc(ciudad)
                or _es_ubicacion_gc(texto_completo)
            )

            if not es_gc:
                continue

            # Determinar lugar más específico
            lugar = limpiar_texto(ubicacion) if ubicacion else "Gran Canaria"

            eventos_raw.append({
                "nombre": nombre,
                "url_full": url,
                "img_card": img,
                "lugar": lugar,
            })

        print(f"   -> {len(eventos_raw)} eventos en Gran Canaria (filtrados)")

        # === FASE 3: Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos de Entrées.es...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
            imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]

            eventos.append(
                Evento(
                    nombre=raw["nombre"],
                    lugar=raw["lugar"],
                    fecha_raw=detalle.get("fecha_raw") or "Sin fecha",
                    fecha_iso=detalle["fecha_iso"],
                    precio_num=detalle["precio_num"],
                    hora=detalle["hora"],
                    organiza="Entrées.es",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], "Entrées.es"),
                )
            )

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        con_img = sum(1 for e in eventos if e.imagen_url)
        print(f"   -> Entrées.es: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} img:{con_img})")

    except Exception as e:
        print(f"   ❌ Error Entrées.es: {e}")

    return eventos if "eventos" in dir() else []

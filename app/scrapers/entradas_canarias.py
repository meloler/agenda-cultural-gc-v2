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
        # === FASE 1: Carga completa con paginación ===
        await page.goto(
            "https://entradascanarias.com/",
            wait_until="domcontentloaded",
            timeout=25000,
        )

        # Esperar a que carguen los eventos
        await asyncio.sleep(3)

        # Click en "Cargar más" varias veces para obtener todos los eventos
        for _ in range(5):
            try:
                btn = await page.query_selector("button:has-text('Cargar más'), button:has-text('cargar más')")
                if btn:
                    visible = await btn.is_visible()
                    if visible:
                        await btn.click()
                        await asyncio.sleep(2)
                    else:
                        break
                else:
                    break
            except Exception:
                break

        # Scroll adicional
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

        # === FASE 2: Extracción con JS ===
        items = await page.evaluate("""
            () => {
                const results = [];
                // Buscar todas las tarjetas de evento (divs con h5 que tienen nombre)
                const headings = document.querySelectorAll('h5');
                const seen = new Set();
                
                for (const h5 of headings) {
                    const nombre = h5.textContent.trim();
                    if (!nombre || nombre.length < 3 || seen.has(nombre)) continue;
                    seen.add(nombre);
                    
                    // Buscar el contenedor padre
                    let container = h5.closest('div[class*="card"], div[class*="evento"], a, div');
                    if (!container) continue;
                    
                    // Recoger texto completo del contenedor (incluye ubicación, fecha, etc.)
                    const fullText = container.textContent || '';
                    
                    // Buscar enlace
                    let link = container.closest('a');
                    if (!link) link = container.querySelector('a');
                    let url = link ? link.href : '';
                    
                    // Buscar botón "Comprar entradas"
                    if (!url) {
                        const btn = container.querySelector('a[href*="entradas"], button');
                        if (btn && btn.href) url = btn.href;
                    }
                    
                    // Imagen
                    const img = container.querySelector('img');
                    const imgSrc = img ? (img.src || img.dataset.src) : null;
                    
                    // Extraer líneas de texto para parsear fecha y ubicación
                    const lines = fullText.split('\\n').map(l => l.trim()).filter(l => l);
                    
                    results.push({
                        nombre: nombre,
                        url: url,
                        fullText: fullText.substring(0, 500),
                        lines: lines.slice(0, 10),
                        img: imgSrc,
                    });
                }
                return results;
            }
        """)

        print(f"   -> {len(items)} tarjetas totales en EntradasCanarias")

        # Procesar y filtrar
        for item in items:
            nombre = limpiar_texto(item.get("nombre", ""))
            url = item.get("url", "")
            texto = item.get("fullText", "")
            lines = item.get("lines", [])
            img = _validar_imagen(item.get("img"))

            if not nombre or nombre.upper() in ["DESTACADOS", "CONCIERTOS", "FESTIVALES", "OTROS", "FIESTAS Y CLUBS", "TEATRO"]:
                continue

            # Extraer ubicación del texto
            ubicacion = ""
            for line in lines:
                if any(x in line.lower() for x in ["recintos", "ciudades"]):
                    continue
                if any(c in line for c in ["📍", "Palmas", "Telde", "Gran Canaria", "Maspalomas", "Infecar"]):
                    ubicacion = line.strip().lstrip("📍 ").strip()
                    break

            # Si no encontramos ubicación explícita, buscar en texto completo
            if not ubicacion:
                for loc in UBICACIONES_GC:
                    if loc in texto.lower():
                        ubicacion = loc.title()
                        break

            # Filtro geográfico
            es_gc = _es_gran_canaria(texto)
            if not es_gc:
                continue

            # Parsear fecha del badge
            fecha_iso = None
            fecha_raw = "Sin fecha"
            for i, line in enumerate(lines):
                if line.isdigit() and len(line) <= 2 and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if len(next_line) == 3 and next_line.isalpha():
                        fecha_iso = _parsear_fecha_badge(line, next_line)
                        fecha_raw = f"{line} {next_line}"
                        break
                if "varias fechas" in line.lower():
                    fecha_raw = "Varias fechas"
                    break

            lugar = limpiar_texto(ubicacion) if ubicacion else "Gran Canaria"

            eventos_raw.append({
                "nombre": nombre,
                "url_full": url if url else f"https://entradascanarias.com/",
                "img_card": img,
                "lugar": lugar,
                "fecha_iso": fecha_iso,
                "fecha_raw": fecha_raw,
            })

        print(f"   -> {len(eventos_raw)} eventos de Gran Canaria (filtrados)")

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
                    fecha_iso = detalle["fecha_iso"] or raw["fecha_iso"]
                    fecha_raw = detalle.get("fecha_raw") or raw["fecha_raw"]
                    precio = detalle["precio_num"]
                    hora = detalle["hora"]
                    descripcion = detalle["descripcion"]
                except Exception:
                    imagen_final = raw["img_card"]
                    fecha_iso = raw["fecha_iso"]
                    fecha_raw = raw["fecha_raw"]
                    precio = None
                    hora = None
                    descripcion = None
            else:
                imagen_final = raw["img_card"]
                fecha_iso = raw["fecha_iso"]
                fecha_raw = raw["fecha_raw"]
                precio = None
                hora = None
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

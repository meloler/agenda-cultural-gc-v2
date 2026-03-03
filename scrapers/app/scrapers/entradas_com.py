"""
Scraper para Entradas.com (búsqueda Gran Canaria) – Deep Scraping de Precisión.

URL: https://www.entradas.com/search/?affiliate=EES&searchterm=Gran+canaria

Estructura DOM (validada 2026-02-26):
  - Resultados en listado con 18 items
  - Cada resultado: h2/h3 (nombre), fecha texto, precio ("desde X €"), imagen
  - Ubicación: texto plano con "Las Palmas de Gran Canaria"
  - Algunos eventos tienen múltiples sub-entradas (abonos, días individuales)

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio
import re

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, limpiar_texto, normalizar_fecha


# Municipios de Gran Canaria para validar ubicación
MUNICIPIOS_GC = [
    "las palmas", "gran canaria", "telde", "arucas", "gáldar", "galdar",
    "agüimes", "aguimes", "ingenio", "santa lucía", "santa lucia",
    "san bartolomé", "san bartolome", "mogán", "mogan", "teror", "firgas",
    "valsequillo", "tejeda", "artenara", "agaete", "moya", "guía", "guia",
    "santa brígida", "santa brigida", "vega de san mateo", "valleseco",
    "maspalomas", "playa del inglés", "playa del ingles", "vecindario",
    "infecar", "gc arena", "puerto rico",
]


def _es_gran_canaria(texto_ubicacion: str) -> bool:
    """Verifica si la ubicación corresponde a Gran Canaria."""
    if not texto_ubicacion:
        return False
    t = texto_ubicacion.lower()
    return any(m in t for m in MUNICIPIOS_GC)


async def scrape_entradas_com(page: Page) -> list[Evento]:
    """Scraper para Entradas.com – búsqueda Gran Canaria (Deep Scraping de Precisión).

    Fase 1: Extrae la lista de resultados de búsqueda.
    Fase 2: Navega a cada ficha para enriquecer con todos los datos.
    """
    print("🎟️ Entradas.com...")
    eventos_raw: list[dict] = []

    try:
        # === FASE 1: Recopilación de resultados ===
        # Intentar cargar con un User-Agent real para evitar ERR_HTTP2_PROTOCOL_ERROR
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9"
        }
        await page.context.set_extra_http_headers(headers)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                await page.goto(
                    "https://www.entradas.com/search/?affiliate=EES&searchterm=Gran+canaria",
                    wait_until="load",
                    timeout=30000,
                )
                break
            except Exception as e:
                err_msg = str(e)
                print(f"   ⚠️ Error cargando Entradas.com (intento {attempt+1}/{max_retries}): {err_msg.split(':')[0]}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    if "ERR_HTTP2_PROTOCOL_ERROR" in err_msg:
                        try:
                            print("      [Estrategia Fallback] Descargando HTML vía API_request puro...")
                            resp = await page.request.get(
                                "https://www.entradas.com/search/?affiliate=EES&searchterm=Gran+canaria",
                                timeout=30000,
                                headers=headers
                            )
                            if resp.ok:
                                html = await resp.text()
                                await page.set_content(html, wait_until="load", timeout=15000)
                                break
                        except Exception as inner_e:
                            print(f"      [Fallback falló]: {inner_e}")
                else:
                    print(f"   ❌ Cancelando Entradas.com tras {max_retries} intentos.")
                    return []

        # Esperar a que carguen los resultados
        try:
            await page.wait_for_selector(".searchResultItem, .search-result-item, .productItem", timeout=10000)
        except Exception:
            pass

        # Scroll para cargar todo
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

        # Extraer resultados usando evaluación JS para mayor precisión
        items = await page.evaluate("""
            () => {
                const results = [];
                // Buscar todos los bloques de resultado que tengan h2 o h3 con enlace
                const headings = document.querySelectorAll('h2 a, h3 a');
                const seen = new Set();
                
                for (const h of headings) {
                    const url = h.href;
                    if (!url || seen.has(url)) continue;
                    if (url.includes('/search/') || url.includes('/info/')) continue;
                    seen.add(url);
                    
                    const nombre = h.textContent.trim();
                    if (!nombre || nombre.length < 3) continue;
                    
                    // Buscar el contenedor padre (resultado)
                    let container = h.closest('.searchResultItem, .productItem, [class*="result"], tr, div');
                    let texto_completo = container ? container.textContent : '';
                    
                    // Buscar imagen
                    let img = container ? container.querySelector('img') : null;
                    let img_src = img ? (img.src || img.dataset.src) : null;
                    
                    // Buscar precio
                    let precio_text = '';
                    if (container) {
                        const precio_el = container.querySelector('[class*="price"], [class*="precio"]');
                        if (precio_el) precio_text = precio_el.textContent.trim();
                    }
                    
                    results.push({
                        nombre: nombre,
                        url: url,
                        texto: texto_completo.substring(0, 500),
                        img: img_src,
                        precio_text: precio_text,
                    });
                }
                return results;
            }
        """)

        print(f"   -> {len(items)} resultados detectados en Entradas.com")

        for item in items:
            nombre = limpiar_texto(item.get("nombre", ""))
            url = item.get("url", "")
            texto = item.get("texto", "").lower()
            img = _validar_imagen(item.get("img"))

            if not nombre or not url:
                continue

            # Filtro de ubicación: solo Gran Canaria
            if not _es_gran_canaria(texto):
                continue

            # Intentar parsear precio del texto de búsqueda
            precio_text = item.get("precio_text", "")
            precio_num = None
            if precio_text:
                match = re.search(r'(\d+[.,]?\d*)\s*€', precio_text)
                if match:
                    try:
                        precio_num = float(match.group(1).replace(",", "."))
                    except ValueError:
                        pass

            eventos_raw.append({
                "nombre": nombre,
                "url_full": url,
                "img_card": img,
                "precio_num": precio_num,
            })

        # === FASE 2: Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos de Entradas.com...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)

            imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]

            # Precio: usar el de la búsqueda si deep scraping no encontró
            precio = detalle["precio_num"]
            if precio is None and raw["precio_num"] is not None:
                precio = raw["precio_num"]

            eventos.append(
                Evento(
                    nombre=detalle.get("nombre_deep") or raw["nombre"],
                    lugar=detalle.get("lugar_deep") or "Las Palmas de Gran Canaria",  # P0-E: venue del deep scrape
                    fecha_raw=detalle.get("fecha_raw") or "Sin fecha",
                    fecha_iso=detalle["fecha_iso"],
                    precio_num=precio,
                    hora=detalle["hora"],
                    organiza="Entradas.com",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], "Entradas.com"),
                )
            )

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        con_img = sum(1 for e in eventos if e.imagen_url)
        print(f"   -> Entradas.com: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} img:{con_img})")

    except Exception as e:
        print(f"   ❌ Error Entradas.com: {e}")

    return eventos if "eventos" in dir() else []

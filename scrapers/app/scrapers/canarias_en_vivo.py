"""
Scraper para CanariasEnVivo.com – Sala de conciertos en Las Palmas.

URL: https://www.canariasenvivo.com/event?tags=%5B165%5D&prevent_redirect=True

Estructura DOM (validada 2026-03-27):
  - Plataforma: Odoo (schema.org microdata)
  - Eventos programados con paginación (/event/page/2?...)
  - Cada evento: <article itemtype="http://schema.org/Event"> dentro de un <a>
  - Fecha: <meta itemprop="startDate" content="2026-03-27T22:00:00">  ← muy preciso
  - Título: <h5 class="card-title"><span>...</span></h5>
  - Ubicación: texto junto a icono .fa-map-marker
  - Imagen: background-image en .o_record_cover_image  
  - Categorías: <span class="badge">
  - Todos los eventos son en "Canarias en Vivo", Las Palmas de Gran Canaria.

Nota: esta web es la propia sala, así que todos los eventos son de Gran Canaria.
      Los títulos suelen incluir " en Canarias en Vivo - Concierto en Las Palmas"
      que limpiamos para que el deduplicador fuzzy los matchee con otros scrapers.

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio
import re
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

from playwright.async_api import Page

from app.models import Evento
from app.utils.text_processing import categorizar_pro, limpiar_texto
from app.utils.parsers import _parsear_precio, _validar_imagen


# Sufijos redundantes en los títulos de canariasenvivo.com
_TITLE_SUFFIXES = [
    " en canarias en vivo - concierto en las palmas",
    " en canarias en vivo - festival en las palmas",
    " en canarias en vivo concierto en las palmas",
    " en canarias en vivo",
    " - concierto en las palmas",
    " - festival en las palmas",
    " concierto en las palmas",
    " canarias en vivo",
]


def _limpiar_titulo(titulo: str) -> str:
    """Quita las coletillas redundantes para que el deduplicador fuzzy funcione."""
    t = titulo.strip()
    low = t.lower()
    for suffix in _TITLE_SUFFIXES:
        if low.endswith(suffix):
            t = t[: len(t) - len(suffix)].strip()
            low = t.lower()
    # Quitar guiones/espacios finales residuales
    t = t.rstrip(" -–—")
    return t


def _parsear_fecha_iso_odoo(start_date_str: str) -> tuple[str | None, str | None]:
    """Parsea la fecha ISO de Odoo (meta itemprop=startDate).
    
    Formato esperado: '2026-03-27T22:00:00' o '2026-03-27T22:00:00+00:00'
    Devuelve (fecha_iso, hora) ajustados a hora canaria.
    """
    if not start_date_str:
        return None, None
    try:
        # Intentamos parsear ISO con timezone
        dt = datetime.fromisoformat(start_date_str)
        # Si no tiene tzinfo, asumimos UTC (Odoo suele guardar en UTC)
        if dt.tzinfo is None:
            from zoneinfo import ZoneInfo
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        # Convertir a hora canaria
        dt_canaria = dt.astimezone(ZoneInfo("Atlantic/Canary"))
        fecha_iso = dt_canaria.date().isoformat()
        hora = dt_canaria.strftime("%H:%M")
        return fecha_iso, hora
    except Exception:
        return None, None


async def scrape_canarias_en_vivo(page: Page) -> list[Evento]:
    """Extrae eventos de CanariasEnVivo.com con soporte de paginación."""
    print("🎸 CanariasEnVivo.com...")
    eventos: list[Evento] = []
    seen_urls: set[str] = set()

    base_url = "https://www.canariasenvivo.com/event"
    # URL con filtro de "Lista de precios" (tag 165) que muestra todos los que tienen precio
    # Usamos date=scheduled para solo eventos futuros
    page_urls = [
        f"{base_url}?tags=%5B165%5D&prevent_redirect=True&date=scheduled",
    ]

    try:
        page_num = 1
        max_pages = 5  # Seguridad: máximo 5 páginas

        while page_num <= max_pages:
            if page_num == 1:
                url = page_urls[0]
            else:
                url = f"{base_url}/page/{page_num}?tags=%5B165%5D&prevent_redirect=True&search=&date=scheduled&type=all&country=all"

            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)

            # Scroll para lazy load
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(0.3)

            # Extraer eventos con JS (usa schema.org microdata de Odoo)
            items_raw = await page.evaluate("""
                () => {
                    const results = [];
                    // Cada evento es un <a> que contiene un <article itemtype="schema.org/Event">
                    const eventLinks = document.querySelectorAll('a.text-reset[href*="/event/"]');
                    
                    for (const link of eventLinks) {
                        const article = link.querySelector('article[itemtype*="Event"]');
                        if (!article) continue;
                        
                        const href = link.href || '';
                        
                        // Título: h5.card-title span
                        const titleEl = article.querySelector('h5.card-title span, h5 span');
                        const titulo = titleEl ? titleEl.textContent.trim() : '';
                        
                        // Fecha ISO precisa: <meta itemprop="startDate">
                        const dateMeta = article.querySelector('meta[itemprop="startDate"]');
                        const startDate = dateMeta ? dateMeta.getAttribute('content') : '';
                        
                        // Ubicación: texto junto a icono de mapa
                        const locationEl = article.querySelector('.text-truncate');
                        let ubicacion = '';
                        if (locationEl) {
                            ubicacion = locationEl.textContent.trim();
                        }
                        
                        // Imagen: background-image en .o_record_cover_image
                        const coverEl = article.querySelector('.o_record_cover_image');
                        let imagenUrl = '';
                        if (coverEl) {
                            const style = coverEl.getAttribute('style') || '';
                            const urlMatch = style.match(/url\\(['"]?([^'"\\)]+)['"]?\\)/);
                            if (urlMatch) {
                                imagenUrl = urlMatch[1];
                            }
                        }
                        
                        // Tags/categorías
                        const badges = article.querySelectorAll('span.badge');
                        const tags = [];
                        for (const badge of badges) {
                            const text = badge.textContent.trim();
                            if (text) tags.push(text);
                        }
                        
                        // Fecha visual (mes abreviado + día) como fallback
                        const dateContainer = article.querySelector('.o_wevent_event_date');
                        let fechaVisual = '';
                        if (dateContainer) {
                            fechaVisual = dateContainer.textContent.trim();
                        }
                        
                        if (titulo) {
                            results.push({
                                titulo,
                                href,
                                startDate,
                                ubicacion,
                                imagenUrl: imagenUrl.startsWith('/') 
                                    ? 'https://www.canariasenvivo.com' + imagenUrl 
                                    : imagenUrl,
                                tags,
                                fechaVisual,
                            });
                        }
                    }
                    return results;
                }
            """)

            if not items_raw:
                break  # No más eventos, parar paginación

            for item in items_raw:
                href = item.get("href", "")
                # Normalizar URL (quitar /register si existe)
                href_clean = re.sub(r'/register/?$', '/', href)
                if not href_clean.endswith('/'):
                    href_clean += '/'

                if href_clean in seen_urls:
                    continue
                seen_urls.add(href_clean)

                # Título limpio
                titulo_raw = limpiar_texto(item.get("titulo", ""))
                if not titulo_raw or len(titulo_raw) < 3:
                    continue
                titulo = _limpiar_titulo(titulo_raw)

                # Fecha + Hora desde meta[itemprop=startDate] (muy preciso)
                fecha_iso, hora = _parsear_fecha_iso_odoo(item.get("startDate", ""))

                # Ubicación
                ubicacion_raw = limpiar_texto(item.get("ubicacion", ""))
                # Todos los eventos son en la sala "Canarias en Vivo" en Las Palmas
                if ubicacion_raw:
                    # Si solo dice "Las Palmas de Gran Canaria, España", usar el nombre de la sala
                    if "las palmas" in ubicacion_raw.lower() and "canarias en vivo" not in ubicacion_raw.lower():
                        lugar = "Canarias en Vivo, Las Palmas de Gran Canaria"
                    else:
                        lugar = ubicacion_raw
                else:
                    lugar = "Canarias en Vivo, Las Palmas de Gran Canaria"

                # Imagen
                imagen_url = _validar_imagen(item.get("imagenUrl", ""))

                # La categoría la asigna el clasificador de IA (classifier.py)
                # que usa título + descripción completa para mayor precisión
                estilo = "Otros"

                eventos.append(
                    Evento(
                        nombre=titulo,
                        lugar=lugar[:200],
                        fecha_raw=item.get("startDate", "Sin fecha")[:100],
                        fecha_iso=fecha_iso,
                        precio_num=None,  # Precio se obtiene del deep scraping en detalle
                        hora=hora,
                        organiza="CanariasEnVivo",
                        url_venta=href,
                        imagen_url=imagen_url,
                        estilo=estilo,
                    )
                )

            # Comprobar si hay siguiente página
            has_next = await page.evaluate(f"""
                () => {{
                    const nextLinks = document.querySelectorAll('a[href*="/event/page/"]');
                    for (const a of nextLinks) {{
                        if (a.href.includes('/page/{page_num + 1}')) return true;
                    }}
                    return false;
                }}
            """)

            if not has_next:
                break
            page_num += 1

        # === Deep Scraping: obtener precio y descripción de cada evento ===
        print(f"   -> {len(eventos)} eventos encontrados. Enriqueciendo con detalles...")

        for i, ev in enumerate(eventos):
            try:
                await page.goto(ev.url_venta, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(1)

                detalle = await page.evaluate("""
                    () => {
                        const result = { precio_raw: '', descripcion: '', direccion: '' };
                        
                        // Descripción: contenido principal del evento
                        const descEl = document.querySelector('.o_wevent_event_subtitle, .o_wevent_event .oe_structure, .o_wevent_event_main');
                        if (descEl) {
                            result.descripcion = descEl.textContent.trim().substring(0, 1000);
                        }
                        
                        // Precio: buscar en todo el texto de la página
                        const pageText = document.body.innerText || '';
                        
                        // Buscar patrones de precio
                        const precioPatterns = [
                            /(\d+)\s*€/,
                            /€\s*(\d+)/,
                            /(\d+)\s*euros/i,
                            /entradas?\s*(\d+)\s*€/i,
                            /(\d+[.,]\d+)\s*€/,
                        ];
                        for (const pattern of precioPatterns) {
                            const m = pageText.match(pattern);
                            if (m) {
                                result.precio_raw = m[0];
                                break;
                            }
                        }
                        
                        // Dirección: buscar enlace de Google Maps
                        const mapLink = document.querySelector('a[href*="maps.google"], a[href*="google.com/maps"]');
                        if (mapLink) {
                            result.direccion = mapLink.textContent.trim() || mapLink.href;
                        }
                        
                        return result;
                    }
                """)

                # Parsear precio del detalle
                if detalle.get("precio_raw"):
                    precio = _parsear_precio(detalle["precio_raw"])
                    if precio is not None:
                        ev.precio_num = precio

                # Descripción
                desc = limpiar_texto(detalle.get("descripcion", ""))
                if desc and len(desc) > 20:
                    ev.descripcion = desc[:800]

            except Exception as e:
                # Si falla el deep scraping de un evento, no pasa nada
                pass

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        con_img = sum(1 for e in eventos if e.imagen_url)
        con_desc = sum(1 for e in eventos if e.descripcion)
        print(
            f"   -> CanariasEnVivo: {len(eventos)} eventos "
            f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} "
            f"img:{con_img} desc:{con_desc})"
        )

    except Exception as e:
        print(f"   ❌ Error CanariasEnVivo: {e}")

    return eventos

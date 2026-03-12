"""
Scraper para SalanProducciones.com – Conciertos en Canarias.

URL: https://www.salanproducciones.com/proximos-conciertos/

Estructura DOM (validada 2026-03-11):
  - Listado en /proximos-conciertos/ con tarjetas Elementor
  - Cada tarjeta: imagen cartel, título (h3 a), link "COMPRAR ENTRADAS"
  - Fichas individuales: Elementor con datos en headings y texto libre
  - Algunas fichas incluyen JSON-LD tipo MusicEvent (datos estructurados)

⚠️ Salán organiza conciertos en TODA ESPAÑA (Bilbao, Tenerife, Gran Canaria...).
   Se filtran solo los conciertos en Gran Canaria.

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio
import json
import re

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import (
    _extraer_json_ld,
    extraer_datos_duros,
    extraer_parrafos,
    _validar_imagen,
)
from app.utils.text_processing import categorizar_pro, limpiar_texto
from app.utils.parsers import _parsear_fecha, _parsear_hora, _parsear_precio


# ─────────────────────────────────────────────────────────────────────
# Filtro geográfico: solo Gran Canaria
# ─────────────────────────────────────────────────────────────────────
_GC_KEYWORDS = [
    "gran canaria", "las palmas", "telde", "gáldar", "galdar",
    "arucas", "agüimes", "aguimes", "ingenio", "maspalomas",
    "playa del inglés", "playa del ingles", "vecindario",
    "santa lucía", "santa lucia", "san bartolomé", "san bartolome",
    "teror", "firgas", "moya", "guía", "guia", "mogán", "mogan",
    "sala insular", "teatro cuyás", "teatro cuyas",
    "auditorio alfredo kraus", "gran canaria arena", "infecar",
    "teatro pérez galdós", "teatro perez galdos",
    "teatro guiniguada", "cicca", "miller", "juan ramón jiménez",
    "juan ramon jimenez", "parque san juan",
]


def _es_gran_canaria(titulo: str, location_text: str = "") -> bool:
    """Determina si un concierto es en Gran Canaria por su título y/o location."""
    combined = f"{titulo} {location_text}".lower()
    return any(kw in combined for kw in _GC_KEYWORDS)


async def _extraer_article_jsonld(page: Page) -> dict | None:
    """Extrae datePublished del JSON-LD Article (Yoast SEO).
    
    Salán Producciones usa el schema Article incluso para eventos,
    y pone la fecha real del evento en datePublished.
    Solo lo usamos como fallback cuando no hay MusicEvent/Event.
    """
    try:
        scripts = page.locator("script[type='application/ld+json']")
        count = await scripts.count()
        for i in range(count):
            try:
                text = await scripts.nth(i).inner_text(timeout=2000)
                data = json.loads(text)
                
                # Manejar @graph de Yoast
                if isinstance(data, dict) and "@graph" in data:
                    for item in data["@graph"]:
                        if isinstance(item, dict) and item.get("@type") in (
                            "Article", "BlogPosting", "WebPage",
                        ):
                            if item.get("datePublished"):
                                return item
                
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") in (
                            "Article", "BlogPosting",
                        ):
                            if item.get("datePublished"):
                                return item
                elif isinstance(data, dict):
                    if data.get("@type") in ("Article", "BlogPosting"):
                        if data.get("datePublished"):
                            return data
            except Exception:
                continue
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────
# Scraper principal
# ─────────────────────────────────────────────────────────────────────
async def scrape_salan_producciones(page: Page) -> list[Evento]:
    """Scraper para SalanProducciones.com – conciertos en Gran Canaria.

    Fase 1: Extrae links del listado /proximos-conciertos/.
    Fase 2: Filtra solo conciertos en Gran Canaria.
    Fase 3: Deep scraping de fichas individuales (JSON-LD → DOM fallback).
    """
    print("🤘 SalanProducciones.com...")
    eventos: list[Evento] = []

    try:
        # === FASE 1: Carga del listado ===
        await page.goto(
            "https://www.salanproducciones.com/proximos-conciertos/",
            wait_until="domcontentloaded",
            timeout=25000,
        )
        await asyncio.sleep(2)

        # Scroll para cargar lazy-loaded content
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

        # Extraer tarjetas con JS
        items = await page.evaluate("""
            () => {
                const results = [];
                const seen = new Set();

                // Elementor posts grid
                const posts = document.querySelectorAll('.elementor-post, article.elementor-post');
                for (const post of posts) {
                    const titleEl = post.querySelector('.elementor-post__title a, h3 a');
                    if (!titleEl) continue;
                    
                    let url = titleEl.href;
                    if (!url || seen.has(url)) continue;
                    seen.add(url);
                    
                    const nombre = titleEl.textContent.trim();
                    const imgEl = post.querySelector('.elementor-post__thumbnail img, img');
                    const img = imgEl ? (imgEl.src || imgEl.dataset.src) : null;
                    
                    results.push({ nombre, url, img });
                }

                // Fallback: si Elementor cambió de estructura, buscar links directos
                if (results.length === 0) {
                    const links = document.querySelectorAll('a[href*="salanproducciones.com/"]');
                    for (const link of links) {
                        const url = link.href;
                        // Filtrar la propia página de listado y links genéricos
                        if (!url || seen.has(url)) continue;
                        if (url.includes('/proximos-conciertos') || 
                            url.includes('/contacto') || 
                            url.includes('/sobre-nosotros') ||
                            url.includes('/conciertos-anteriores') ||
                            url.includes('/category/') ||
                            url.includes('/tag/') ||
                            url === 'https://www.salanproducciones.com/' ||
                            url === 'https://www.salanproducciones.com') continue;
                        seen.add(url);
                        
                        const nombre = link.textContent.trim();
                        if (!nombre || nombre.length < 3 || 
                            nombre.toUpperCase() === 'COMPRAR ENTRADAS' ||
                            nombre.toUpperCase().includes('COMPRAR ENTRADAS')) continue;
                        
                        const imgEl = link.querySelector('img');
                        const img = imgEl ? (imgEl.src || imgEl.dataset.src) : null;
                        
                        results.push({ nombre, url, img });
                    }
                }
                
                return results;
            }
        """)

        print(f"   -> {len(items)} conciertos detectados en SalanProducciones")

        if not items:
            print("   ⚠️ SalanProducciones: 0 tarjetas detectadas. ¿Cambio de DOM?")
            return []

        # === FASE 2: Filtro geográfico + Deep scraping ===
        # Pre-filtrar por título (rápido, sin navegar)
        items_gc = []
        items_desconocido = []
        filtrados_fuera_gc = 0

        for item in items:
            nombre = item.get("nombre", "")
            if _es_gran_canaria(nombre):
                items_gc.append(item)
            else:
                # Si el título no indica GC explícitamente,
                # podría ser GC (ej: "Ana Curra" sin " – Gran Canaria")
                # → deep scrape para confirmar
                items_desconocido.append(item)

        if filtrados_fuera_gc := len(items) - len(items_gc) - len(items_desconocido):
            pass  # Contado abajo

        print(f"   -> {len(items_gc)} confirman Gran Canaria por título, "
              f"{len(items_desconocido)} requieren verificación")

        # Combinar: primero los seguros, luego los que necesitan verificar
        items_a_procesar = items_gc + items_desconocido
        seen_texts: set[str] = set()
        descartados_geo = 0

        for item in items_a_procesar:
            nombre_raw = limpiar_texto(item.get("nombre", ""))
            url = item.get("url", "")
            img_card = _validar_imagen(item.get("img"))

            if not nombre_raw or len(nombre_raw) < 3:
                continue

            # === FASE 3: Deep scraping de cada ficha ===
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(1.5)

                # 1️⃣ Intentar JSON-LD MusicEvent/Event (fuente más fiable)
                ld_data = await _extraer_json_ld(page)
                
                # 1b️⃣ Fallback: extraer datePublished del JSON-LD Article
                #     Salán usa Article (Yoast SEO) con fecha del evento en datePublished
                ld_article = None
                if not ld_data:
                    ld_article = await _extraer_article_jsonld(page)
                
                titulo_final = nombre_raw
                lugar = None
                fecha_iso = None
                fecha_raw = None
                hora = None
                precio_num = None
                descripcion = None
                imagen_url = img_card
                url_venta = url

                if ld_data:
                    print(f"      [JSON-LD] Encontrado schema '{ld_data.get('@type', '?')}'")
                    
                    # Nombre del JSON-LD
                    ld_name = ld_data.get("name", "")
                    if ld_name and len(ld_name) > 3:
                        titulo_final = limpiar_texto(ld_name)
                    
                    # Fecha + Hora
                    start_date = ld_data.get("startDate", "")
                    if start_date:
                        fecha_raw = str(start_date)
                        fecha_iso = _parsear_fecha(start_date)
                        hora = _parsear_hora(start_date)
                    
                    # Lugar (location)
                    location = ld_data.get("location")
                    if location:
                        if isinstance(location, list):
                            location = location[0] if location else None
                        if isinstance(location, dict):
                            venue = location.get("name", "")
                            address = location.get("address", "")
                            if isinstance(address, dict):
                                address = address.get("addressLocality", "")
                            lugar = f"{venue}" if venue else str(address)
                            # Verificación geográfica con JSON-LD
                            if not _es_gran_canaria(nombre_raw, f"{venue} {address}"):
                                print(f"      ❌ Descartado (no GC): {nombre_raw} → {venue}, {address}")
                                descartados_geo += 1
                                continue
                        elif isinstance(location, str):
                            lugar = location
                    
                    # Precio (offers)
                    offers = ld_data.get("offers")
                    if offers:
                        if isinstance(offers, list):
                            offers = offers[0]
                        if isinstance(offers, dict):
                            price = offers.get("price") or offers.get("lowPrice")
                            if price is not None:
                                try:
                                    precio_num = float(price)
                                except (ValueError, TypeError):
                                    pass
                            # URL de compra de la oferta
                            offer_url = offers.get("url")
                            if offer_url and offer_url.startswith("http"):
                                url_venta = offer_url
                    
                    # Imagen del JSON-LD
                    ld_image = ld_data.get("image")
                    if isinstance(ld_image, list):
                        ld_image = ld_image[0] if ld_image else None
                    if isinstance(ld_image, dict):
                        ld_image = ld_image.get("url")
                    if ld_image:
                        ld_image = _validar_imagen(str(ld_image))
                        if ld_image:
                            imagen_url = ld_image

                # 1c️⃣ Extraer fecha del Article JSON-LD si MusicEvent no la tenía
                if not fecha_iso and ld_article:
                    art_date = ld_article.get("datePublished", "")
                    if art_date:
                        fecha_raw = str(art_date)
                        fecha_iso = _parsear_fecha(art_date)
                        if not hora:
                            hora = _parsear_hora(art_date)

                # 2️⃣ Extracción específica de widgets Elementor
                #    Salán usa widgets Elementor con lugar y precio en texto visible
                if not lugar or precio_num is None:
                    try:
                        widget_data = await page.evaluate("""
                            () => {
                                const result = {venue: null, price: null, allText: ''};
                                
                                // Recopilar TODO el texto de widgets (excluyendo header/nav/footer)
                                const mainContent = document.querySelector('.elementor-location-single, .site-main, main, article, .entry-content');
                                if (!mainContent) return result;
                                
                                const widgets = mainContent.querySelectorAll('.elementor-widget');
                                const texts = [];
                                
                                for (const w of widgets) {
                                    const text = w.textContent.trim();
                                    if (!text || text.length < 2) continue;
                                    texts.push(text);
                                    
                                    // Detectar venues conocidos
                                    const lower = text.toLowerCase();
                                    if (!result.venue && (
                                        lower.includes('teatro') || lower.includes('auditorio') || 
                                        lower.includes('sala ') || lower.includes('arena') || 
                                        lower.includes('parque') || lower.includes('recinto') ||
                                        lower.includes('pabellón') || lower.includes('pabellon')
                                    ) && text.length < 100 && !lower.includes('comprar')) {
                                        result.venue = text;
                                    }
                                    
                                    // Detectar precio (ej: "35 €", "20 €")
                                    const priceMatch = text.match(/^[ ]*([0-9]+(?:[.,][0-9]+)?)[ ]*\u20ac[ ]*$/);
                                    if (priceMatch && !result.price) {
                                        result.price = text;
                                    }
                                }
                                
                                result.allText = texts.join('\\n');
                                return result;
                            }
                        """)
                        
                        if widget_data:
                            if not lugar and widget_data.get("venue"):
                                lugar = limpiar_texto(widget_data["venue"])
                            if precio_num is None and widget_data.get("price"):
                                precio_num = _parsear_precio(widget_data["price"])
                            # Fecha/hora fallback desde texto de widgets
                            all_text = widget_data.get("allText", "")
                            if not fecha_iso and all_text:
                                fecha_iso = _parsear_fecha(all_text[:2000])
                            if not hora and all_text:
                                hora = _parsear_hora(all_text[:2000])
                    except Exception:
                        pass

                # 3️⃣ Fallback DOM genérico (si aún faltan datos)
                if not fecha_iso or not hora or precio_num is None or not lugar:
                    datos_dom = await extraer_datos_duros(page, url)

                    if not fecha_iso and datos_dom["fecha_iso"]:
                        fecha_iso = datos_dom["fecha_iso"]
                    if not fecha_raw and datos_dom["fecha_raw"]:
                        fecha_raw = datos_dom["fecha_raw"]
                    if not hora and datos_dom["hora"]:
                        hora = datos_dom["hora"]
                    if precio_num is None and datos_dom["precio_num"] is not None:
                        precio_num = datos_dom["precio_num"]
                    if not lugar and datos_dom.get("venue_name"):
                        # Solo aceptamos si es corto y no tiene basura 
                        ven = str(datos_dom["venue_name"])
                        if len(ven) < 50 and "INICIO" not in ven.upper() and "CONCIERTO" not in ven.upper():
                            lugar = ven

                # Verificación geográfica final (para items sin JSON-LD location)
                if item in items_desconocido and not _es_gran_canaria(
                    nombre_raw, f"{lugar or ''} {descripcion or ''}"
                ):
                    print(f"      ❌ Descartado (no GC): {nombre_raw} → {lugar or 'sin lugar'}")
                    descartados_geo += 1
                    continue

                # 4️⃣ Descripción
                desc_selectors = [
                    ".elementor-text-editor",
                    ".entry-content",
                    "article",
                ]
                for desc_sel in desc_selectors:
                    text = await extraer_parrafos(page, desc_sel)
                    if text and len(text) > 30:
                        fingerprint = text[:200].strip()
                        if fingerprint not in seen_texts:
                            seen_texts.add(fingerprint)
                            descripcion = text
                            break
                            
                # Fallback: Extraer directo de los <p> si Elementor cambia de markup
                if not descripcion:
                    try:
                        all_p = page.locator("p, h2, h3")
                        count = await all_p.count()
                        clean_lines = []
                        for i in range(count):
                            texto = (await all_p.nth(i).inner_text(timeout=1000)).strip()
                            # Filtrar paja (botones, cookies, etc)
                            t_lower = texto.lower()
                            if texto and len(texto) > 15 and "comprar" not in t_lower and "suscríbete" not in t_lower and "salán producciones" not in t_lower and "inicio" not in t_lower and "aviso legal" not in t_lower and "cookie" not in t_lower and "almacenamos" not in t_lower and "nuestros socios" not in t_lower:
                                clean_lines.append(texto)
                        if clean_lines:
                            combined = "\n\n".join(clean_lines)
                            seen_texts.add(combined[:200].strip())
                            descripcion = combined
                    except Exception as e:
                        pass


                # 5️⃣ Imagen: og:image como prioridad si no la tenemos
                if not imagen_url:
                    try:
                        og = page.locator("meta[property='og:image']").first
                        if await og.count() > 0:
                            img_content = await og.get_attribute("content")
                            imagen_url = _validar_imagen(img_content)
                    except Exception:
                        pass

                # 6️⃣ URL de compra: buscar link externo a ticketera
                if url_venta == url:
                    try:
                        buy_links = await page.evaluate("""
                            () => {
                                const links = document.querySelectorAll('a.elementor-button-link, a[href*="tickety"], a[href*="tureservaonline"], a[href*="seetickets"], a[href*="entradas"]');
                                for (const link of links) {
                                    const href = link.href;
                                    if (href && !href.includes('salanproducciones.com') && href.startsWith('http')) {
                                        return href;
                                    }
                                }
                                return null;
                            }
                        """)
                        if buy_links:
                            url_venta = buy_links
                    except Exception:
                        pass

                # Lugar por defecto si no se encontró nada
                if not lugar:
                    lugar = "Gran Canaria"

                # Log de datos extraídos
                if fecha_iso:
                    print(f"      ✅ {titulo_final[:50]}: {fecha_iso} {hora or '?'} | {lugar} | {precio_num}€")
                else:
                    print(f"      ⚠️ {titulo_final[:50]}: sin fecha | {lugar} | {precio_num}€")

                eventos.append(
                    Evento(
                        nombre=titulo_final,
                        lugar=lugar or "Gran Canaria",
                        fecha_raw=limpiar_texto(str(fecha_raw or "Sin fecha"))[:100],
                        fecha_iso=fecha_iso,
                        precio_num=precio_num,
                        hora=hora,
                        organiza="Salan Producciones",
                        url_venta=url_venta,
                        imagen_url=imagen_url,
                        descripcion=descripcion,
                        estilo=categorizar_pro(titulo_final, "Salan Producciones"),
                    )
                )

            except Exception as e:
                print(f"      ⚠️ Error procesando '{nombre_raw[:40]}': {e}")
                continue

        # Log de calidad
        if descartados_geo:
            print(f"   -> {descartados_geo} conciertos descartados (fuera de Gran Canaria)")

        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        con_img = sum(1 for e in eventos if e.imagen_url)
        print(f"   -> SalanProducciones: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} img:{con_img})")

    except Exception as e:
        print(f"   ❌ Error SalanProducciones: {e}")

    return eventos

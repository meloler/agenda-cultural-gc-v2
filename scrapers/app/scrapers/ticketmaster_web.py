"""
Scraper web para Ticketmaster.es usando Playwright – con Deep Scraping de Precisión v4.
Busca eventos de Gran Canaria y entra en cada ficha para datos completos.
"""

import asyncio

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, limpiar_texto, normalizar_fecha


async def scrape_ticketmaster_web(page: Page) -> list[Evento]:
    """Scraper de Ticketmaster.es vía navegador + Deep Scraping de Precisión."""
    print("🔥 Ticketmaster (Web Scraper)...")
    eventos_raw: list[dict] = []

    try:
        await page.goto(
            "https://www.ticketmaster.es/search?q=gran%20canaria",
            wait_until="domcontentloaded",
            timeout=25000,
        )

        selectors_to_try = [
            "[data-testid='event-list-item']",
            ".event-listing__item",
            "a[href*='/event/']",
            "a[href*='/activity/']",
            ".search-results a[href*='ticketmaster']",
            "li[class*='event']",
            ".mu-card",
        ]

        cards_selector = None
        for sel in selectors_to_try:
            try:
                await page.wait_for_selector(sel, timeout=5000)
                cards_selector = sel
                print(f"   -> Selector encontrado: {sel}")
                break
            except Exception:
                continue

        if not cards_selector:
            print("   ⚠️ Ningún selector estándar encontrado. Probando fallback...")
            cards_selector = "a[href*='/event/'], a[href*='/activity/']"

        # Scroll para lazy loading
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

        cards = await page.query_selector_all(cards_selector)
        seen: set[str] = set()

        print(f"   -> {len(cards)} cards detectadas en Ticketmaster.es")

        for card in cards:
            try:
                href = await card.get_attribute("href")
                if not href:
                    link = await card.query_selector("a[href]")
                    if link:
                        href = await link.get_attribute("href")
                if not href:
                    continue

                url_full = href if href.startswith("http") else f"https://www.ticketmaster.es{href}"

                if url_full in seen:
                    continue
                seen.add(url_full)

                # Nombre del evento
                nombre = ""
                for name_sel in ["h3", "h2", "[class*='title']", "[class*='name']", "span"]:
                    el = await card.query_selector(name_sel)
                    if el:
                        nombre = await el.inner_text()
                        nombre = limpiar_texto(nombre)
                        if nombre and len(nombre) > 3:
                            break

                if not nombre or len(nombre) < 3:
                    raw_text = await card.inner_text()
                    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
                    nombre = lines[0] if lines else "Evento Ticketmaster"

                nombre = limpiar_texto(nombre)

                # Fecha de la card
                fecha_card = None
                for date_sel in ["[class*='date']", "[class*='fecha']", "time", "[datetime]"]:
                    el = await card.query_selector(date_sel)
                    if el:
                        fecha_card = await el.inner_text()
                        fecha_card = limpiar_texto(fecha_card)
                        if fecha_card:
                            break

                # Lugar
                lugar = "Gran Canaria"
                for venue_sel in ["[class*='venue']", "[class*='location']"]:
                    el = await card.query_selector(venue_sel)
                    if el:
                        lugar = await el.inner_text()
                        lugar = limpiar_texto(lugar)
                        if lugar:
                            break

                # Imagen de la card
                img_card = None
                img = await card.query_selector("img")
                if img:
                    img_src = await img.get_attribute("src") or await img.get_attribute("data-src")
                    img_card = _validar_imagen(img_src)

                eventos_raw.append({
                    "nombre": nombre,
                    "lugar": lugar,
                    "fecha_card": fecha_card,
                    "url_full": url_full,
                    "img_card": img_card,
                })
            except Exception:
                continue

        # === Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos de Ticketmaster...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
            imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]

            # Fecha: deep scrape > card
            fecha_iso = detalle["fecha_iso"]
            fecha_raw = detalle.get("fecha_raw")
            if not fecha_iso and raw.get("fecha_card"):
                fecha_iso = normalizar_fecha(raw["fecha_card"])
                fecha_raw = raw["fecha_card"]

            eventos.append(
                Evento(
                    nombre=detalle.get("nombre_deep") or raw["nombre"],
                    lugar=raw["lugar"],
                    fecha_raw=fecha_raw or "Sin fecha",
                    fecha_iso=fecha_iso,
                    precio_num=detalle["precio_num"],
                    hora=detalle["hora"],
                    organiza="Ticketmaster",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], "Ticketmaster"),
                )
            )

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        print(f"   -> Ticketmaster Web: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora})")

    except Exception as e:
        print(f"   ❌ Error Ticketmaster Web: {e}")

    return eventos if "eventos" in dir() else []

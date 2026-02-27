"""
Scraper para Tickety (Gran Canaria) – con Deep Scraping de Precisión v4.
Soporta infinite scroll y entra en cada ficha para datos completos.
"""

import asyncio

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, limpiar_texto


async def scrape_tickety(page: Page) -> list[Evento]:
    """Scraper para Tickety con infinite scroll + deep scraping de precisión."""
    print("🎫 Tickety...")
    eventos_raw: list[dict] = []

    try:
        loaded = False
        for attempt in range(3):
            try:
                await page.goto(
                    "https://tickety.es/search/gran%20canaria",
                    wait_until="networkidle",
                    timeout=20000,
                )
                loaded = True
                break
            except Exception as e:
                print(f"   ⚠️ Reintento {attempt+1}/3 al cargar Tickety: {e}")
                await asyncio.sleep(2)
        
        if not loaded:
            raise Exception("No se pudo cargar la página principal de Tickety")

        # Scroll para cargar más eventos (infinite scroll)
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)

        cards = await page.query_selector_all("a[href*='/event/']")
        seen: set[str] = set()

        for card in cards:
            try:
                url = await card.get_attribute("href")
                if not url or url in seen:
                    continue
                seen.add(url)

                url_clean = url if url.startswith("http") else f"https://tickety.es{url}"

                raw = await card.inner_text()
                lines = [line.strip() for line in raw.split("\n") if line.strip()]
                if not lines:
                    continue

                nombre = lines[0]
                if len(nombre) < 15 and any(c.isdigit() for c in nombre):
                    nombre = lines[1] if len(lines) > 1 else "Evento"

                # Imagen de la card
                img_el = await card.query_selector("img")
                img_card = None
                if img_el:
                    img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src")
                    img_card = _validar_imagen(img_src)

                eventos_raw.append({
                    "nombre": limpiar_texto(nombre),
                    "url_full": url_clean,
                    "img_card": img_card,
                })
            except Exception:
                continue

        # === Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos de Tickety...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
            imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]
            nombre_final = detalle.get("nombre_deep") or raw["nombre"]

            eventos.append(
                Evento(
                    nombre=nombre_final,
                    lugar="Gran Canaria",
                    fecha_raw=detalle.get("fecha_raw") or "Sin fecha",
                    fecha_iso=detalle["fecha_iso"],
                    precio_num=detalle["precio_num"],
                    hora=detalle["hora"],
                    organiza="Tickety",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], "Tickety"),
                )
            )

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        print(f"   -> Tickety: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora})")

    except Exception as e:
        print(f"   ❌ Error Tickety: {e}")

    return eventos if "eventos" in dir() else []

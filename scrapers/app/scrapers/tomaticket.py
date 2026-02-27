"""
Scraper para Tomaticket (Gran Canaria) – con Deep Scraping de Precisión v4.
Entra en la ficha de cada evento para extraer descripción, imagen, precio, fecha y hora.

Selectores DOM validados (2026-02-18):
  - Cards: a.eventtt con h2 (nombre), .fecha (fecha card)
  - Ficha: #BotonExterno (precio), p.fecha-info (fecha + hora)
  - Imagen: og:image puede ser eNULL → filtrar y usar alternativas

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import (
    categorizar_pro,
    inferir_nombre,
    limpiar_texto,
    normalizar_fecha,
)


async def scrape_tomaticket(page: Page) -> list[Evento]:
    """Scraper para Tomaticket – Gran Canaria (Deep Scraping de Precisión v4).

    Fase 1: Extrae la lista de URLs desde la página principal.
    Fase 2: Navega a cada ficha para enriquecer con todos los datos.
    """
    print("🍅 Tomaticket...")
    eventos_raw: list[dict] = []

    try:
        # === FASE 1: Recopilación de URLs ===
        await page.goto(
            "https://www.tomaticket.es/es-es/gran-canaria",
            wait_until="domcontentloaded",
            timeout=20000,
        )

        try:
            await page.wait_for_selector("a.eventtt", timeout=15000)
        except Exception:
            pass

        # Scroll dinámico para cargar más eventos (lazy loading)
        prev_count = 0
        paciencia = 0
        for _ in range(15):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
            cards_count = await page.locator("a.eventtt").count()
            if cards_count == prev_count:
                paciencia += 1
                if paciencia >= 2:  # Si tras 2 scrolls no hay nuevos, parar
                    break
            else:
                paciencia = 0
            prev_count = cards_count

        cards = await page.query_selector_all("a.eventtt")
        seen: set[str] = set()

        print(f"   -> {len(cards)} cards detectadas en Tomaticket")

        for card in cards:
            try:
                url = await card.get_attribute("href")
                if not url:
                    continue

                url_full = (
                    f"https://www.tomaticket.es{url}"
                    if url.startswith("/")
                    else f"https://www.tomaticket.es/es-es/{url}"
                ).split("?")[0]

                if url_full in seen:
                    continue
                seen.add(url_full)

                # Nombre
                h2 = await card.query_selector("h2")
                nombre = await h2.inner_text() if h2 else inferir_nombre(url)

                # Fecha de la card (puede ser mala, deep scrape la mejorará)
                fecha_el = await card.query_selector(".fecha")
                fecha_card = await fecha_el.inner_text() if fecha_el else None

                # Imagen de la card (fallback si la ficha no tiene)
                img_el = await card.query_selector("img")
                img_card = None
                if img_el:
                    img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src")
                    # Validar inmediatamente la imagen de la card
                    img_card = _validar_imagen(img_src)

                eventos_raw.append({
                    "nombre": limpiar_texto(nombre),
                    "fecha_card": fecha_card,
                    "url_full": url_full,
                    "img_card": img_card,
                })
            except Exception:
                continue

        # === FASE 2: Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos...")

        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)

            # Imagen: deep scrape > card, pero SIEMPRE validar contra NULL
            imagen_final = _validar_imagen(detalle["imagen_url"])
            if not imagen_final:
                imagen_final = raw["img_card"]  # Ya fue validada en fase 1
            # Doble check final
            imagen_final = _validar_imagen(imagen_final)

            # Fecha: deep scrape > card
            fecha_iso = detalle["fecha_iso"]
            fecha_raw = detalle.get("fecha_raw")
            if not fecha_iso and raw["fecha_card"]:
                fecha_iso = normalizar_fecha(raw["fecha_card"])
                fecha_raw = raw["fecha_card"]

            eventos.append(
                Evento(
                    nombre=detalle.get("nombre_deep") or raw["nombre"],
                    lugar="Gran Canaria",
                    fecha_raw=limpiar_texto(fecha_raw or raw.get("fecha_card") or "Sin fecha"),
                    fecha_iso=fecha_iso,
                    precio_num=detalle["precio_num"],
                    hora=detalle["hora"],
                    organiza="Tomaticket",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], "Tomaticket"),
                )
            )

        # Log resumen de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        con_img = sum(1 for e in eventos if e.imagen_url)
        print(f"   -> Tomaticket: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} img:{con_img})")

    except Exception as e:
        print(f"   ❌ Error Tomaticket: {e}")
        return eventos if "eventos" in dir() else []

    return eventos

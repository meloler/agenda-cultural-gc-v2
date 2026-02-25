"""
Scrapers para sitios institucionales: CICCA y Teatro Guiniguada.
Con Deep Scraping de Precisión v4: extrae precio, fecha, hora, descripción e imagen.

Nota: www.cicca.es puede estar caído (ERR_NAME_NOT_RESOLVED observado 2026-02-18).
"""

import re

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, inferir_nombre, limpiar_texto


async def scrape_cicca(page: Page) -> list[Evento]:
    """Scraper para CICCA – Fundación La Caja de Canarias (Deep Scraping de Precisión)."""
    print("🏛️ CICCA...")
    eventos_raw: list[dict] = []

    try:
        await page.goto(
            "https://www.fundacionlacajadecanarias.es/agenda-cultural/",
            wait_until="networkidle",
            timeout=20000,
        )

        cards = await page.query_selector_all("article")

        for card in cards:
            try:
                link = await card.query_selector("a")
                url = await link.get_attribute("href") if link else ""
                if not url:
                    continue

                tit = await card.query_selector("h2, h3")
                nombre = await tit.inner_text() if tit else ""
                if not nombre:
                    nombre = inferir_nombre(url)
                nombre = limpiar_texto(nombre)

                img_el = await card.query_selector("img")
                img_card = None
                if img_el:
                    img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src")
                    img_card = _validar_imagen(img_src)

                eventos_raw.append({
                    "nombre": nombre,
                    "url_full": url,
                    "img_card": img_card,
                })
            except Exception:
                continue

        # === Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos de CICCA...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
            imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]

            eventos.append(
                Evento(
                    nombre=raw["nombre"],
                    lugar="CICCA",
                    fecha_raw=detalle.get("fecha_raw") or "Sin fecha",
                    fecha_iso=detalle["fecha_iso"],
                    precio_num=detalle["precio_num"],
                    hora=detalle["hora"],
                    organiza="CICCA",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], "CICCA"),
                )
            )

    except Exception as e:
        print(f"   ❌ Error CICCA: {e}")

    print(f"   -> CICCA: {len(eventos_raw)} eventos enriquecidos.")
    return eventos if "eventos" in dir() else []


async def scrape_guiniguada(page: Page) -> list[Evento]:
    """Scraper para Teatro Guiniguada (Gobierno de Canarias) – Deep Scraping de Precisión."""
    print("🎬 Teatro Guiniguada...")
    eventos_raw: list[dict] = []

    try:
        url_base = "https://www3.gobiernodecanarias.org/cultura/ocio/teatroguiniguada/eventos/"
        await page.goto(url_base, wait_until="domcontentloaded", timeout=20000)

        links = await page.query_selector_all("a[href*='/eventos/']")
        seen: set[str] = set()

        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or href in seen:
                    continue
                if "/category/" in href or "/tag/" in href:
                    continue
                seen.add(href)

                nombre = await link.inner_text()
                nombre = limpiar_texto(nombre)

                if not nombre or len(nombre) < 4 or "leer" in nombre.lower():
                    if len(href.split("/")) > 4:
                        nombre = inferir_nombre(href)
                    else:
                        continue

                if re.match(r"^\d[\d\s]+$", nombre):
                    continue

                img_el = await link.query_selector("img")
                img_card = None
                if img_el:
                    img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src")
                    img_card = _validar_imagen(img_src)

                eventos_raw.append({
                    "nombre": nombre,
                    "url_full": href,
                    "img_card": img_card,
                })
            except Exception:
                continue

        # === Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos de T. Guiniguada...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
            imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]

            eventos.append(
                Evento(
                    nombre=raw["nombre"],
                    lugar="Teatro Guiniguada",
                    fecha_raw=detalle.get("fecha_raw") or "Sin fecha",
                    fecha_iso=detalle["fecha_iso"],
                    precio_num=detalle["precio_num"],
                    hora=detalle["hora"],
                    organiza="Teatro Guiniguada",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], "Teatro Guiniguada"),
                )
            )

    except Exception as e:
        print(f"   ❌ Error Teatro Guiniguada: {e}")

    print(f"   -> Teatro Guiniguada: {len(eventos_raw)} eventos enriquecidos.")
    return eventos if "eventos" in dir() else []

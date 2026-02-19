"""
Scraper para sitios de cultura canaria (Auditorio Alfredo Kraus, Teatro Pérez Galdós).
Con Deep Scraping de Precisión v4: extrae descripción, imagen, precio, fecha y hora.

DOM validado (2026-02-18):
  - /programacion tiene enlaces a /evento/{slug}/{id}
  - Ficha contiene: Fecha ("26 de febrero de 2026"), Horario ("20:00 h")
  - Precio NO está en estas webs → se extrae de Janto si hay enlace
"""

import asyncio

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, inferir_nombre, limpiar_texto


async def scrape_cultura_canaria(page: Page, url_base: str, recinto: str) -> list[Evento]:
    """Scraper genérico para webs de cultura canaria con enlaces a /evento/.

    Fase 1: Recopila URLs desde /programacion.
    Fase 2: Deep scrape de cada ficha (precio, fecha, hora, descripción, imagen).
    """
    print(f"🎭 {recinto}...")
    eventos_raw: list[dict] = []

    try:
        await page.goto(
            f"{url_base}/programacion",
            wait_until="networkidle",
            timeout=20000,
        )

        links = await page.query_selector_all("a[href*='/evento/']")
        seen: set[str] = set()

        print(f"   -> {len(links)} enlaces detectados en {recinto}")

        for link in links:
            try:
                href = await link.get_attribute("href")
                if not href or href in seen:
                    continue
                seen.add(href)

                url_full = href if href.startswith("http") else f"{url_base}{href}"

                nombre = await link.inner_text()
                nombre = limpiar_texto(nombre)

                if not nombre or len(nombre) < 3 or nombre.lower() in ["imagen", "ver más", "entradas"]:
                    nombre = await link.get_attribute("title")
                    if not nombre:
                        nombre = inferir_nombre(href)

                nombre = limpiar_texto(nombre)

                # Imagen de la card (fallback)
                img_el = await link.query_selector("img")
                img_card = None
                if img_el:
                    img_src = await img_el.get_attribute("src") or await img_el.get_attribute("data-src")
                    img_card = _validar_imagen(img_src)

                eventos_raw.append({
                    "nombre": nombre,
                    "url_full": url_full,
                    "img_card": img_card,
                })
            except Exception:
                continue

        # === FASE 2: Deep Scraping de Precisión ===
        print(f"   -> Iniciando deep scraping de {len(eventos_raw)} eventos de {recinto}...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
            
            # Imagen: validar y usar fallback
            imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]

            eventos.append(
                Evento(
                    nombre=raw["nombre"],
                    lugar=recinto,
                    fecha_raw=detalle.get("fecha_raw") or "Sin fecha",
                    fecha_iso=detalle["fecha_iso"],
                    precio_num=detalle["precio_num"],
                    hora=detalle["hora"],
                    organiza=recinto,
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=detalle["descripcion"],
                    estilo=categorizar_pro(raw["nombre"], recinto),
                )
            )

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        print(f"   -> {recinto}: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora})")

    except Exception as e:
        print(f"   ❌ Error {recinto}: {e}")

    return eventos if "eventos" in dir() else []

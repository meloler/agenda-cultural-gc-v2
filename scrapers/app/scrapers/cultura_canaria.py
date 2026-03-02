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
        import json
        seen: set[str] = set()
        page_num = 1
        
        while page_num <= 5:
            api_url = f"{url_base}/eventos/0?page={page_num}"
            try:
                await page.goto(api_url, wait_until="domcontentloaded", timeout=15000)
                body_text = await page.inner_text("body", timeout=5000)
                data = json.loads(body_text)
            except Exception as e:
                print(f"      [DEBUG] Fin de paginación o error en API: {e}")
                break
            
            items = data.get("data", data) if isinstance(data, dict) else data
            if not isinstance(items, list) or len(items) == 0:
                break
                
            for item in items:
                try:
                    nombre = item.get("title", "")
                    
                    # URL local del evento
                    url_full = item.get("url")
                    if not url_full:
                        slug = item.get("slug")
                        id_evento = item.get("id")
                        if slug and id_evento:
                            url_full = f"{url_base}/evento/{slug}/{id_evento}"
                        elif slug:
                            url_full = f"{url_base}/evento/{slug}"
                    
                    # A veces la URL viene relativa
                    if url_full and url_full.startswith("/"):
                        url_full = f"{url_base}{url_full}"
                        
                    if not url_full or url_full in seen:
                        continue
                    seen.add(url_full)
                    
                    # Imagen
                    img_card = item.get("image") or item.get("image_url") or item.get("poster")
                    if isinstance(img_card, str):
                        if img_card.startswith("/"):
                            img_card = f"{url_base}{img_card}"
                        img_card = _validar_imagen(img_card)
                    
                    eventos_raw.append({
                        "nombre": limpiar_texto(nombre) or inferir_nombre(url_full),
                        "url_full": url_full,
                        "img_card": img_card,
                    })
                except Exception:
                    continue
                    
            page_num += 1

        print(f"   -> {len(eventos_raw)} enlaces detectados en {recinto} (vía API)")

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

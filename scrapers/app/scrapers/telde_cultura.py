"""
Scraper para TeldeCultura.org – Agenda cultural municipal de Telde.

URL: https://teldecultura.org/

Estructura DOM (validada 2026-02-26):
  - Grid de tarjetas (article o div)
  - Cada tarjeta: imagen, título (h2/texto), fecha rango (dd.mm.yyyy-dd.mm.yyyy),
    hora, botón "Entrada libre"
  - ⚠️ Muchos registros son cursos/talleres de LARGA DURACIÓN (ej: 01.10.2024-30.06.2026)
  - El scraper filtra: solo incluye eventos puntuales (rango ≤ 30 días)
    o eventos cuya fecha de fin es futura.

Requiere una instancia de Playwright Page ya abierta.
"""

import asyncio
import re
from datetime import datetime, timedelta

from playwright.async_api import Page

from app.models import Evento
from app.scrapers._enrichment import enriquecer_evento, _validar_imagen
from app.utils.text_processing import categorizar_pro, limpiar_texto


def _parsear_fecha_telde(fecha_texto: str) -> tuple[str | None, str | None, bool]:
    """Parsea fechas de TeldeCultura.

    Formatos:
      - "01.10.2024-30.06.2026" (rango)
      - "15.03.2026" (fecha única)
      - "Todo el día"

    Returns:
        (fecha_inicio_iso, fecha_fin_iso, es_curso)
    """
    if not fecha_texto:
        return None, None, False

    # Limpiar
    texto = fecha_texto.strip()

    # Formato rango: dd.mm.yyyy-dd.mm.yyyy
    match_rango = re.search(r'(\d{2})\.(\d{2})\.(\d{4})\s*-\s*(\d{2})\.(\d{2})\.(\d{4})', texto)
    if match_rango:
        d1, m1, y1, d2, m2, y2 = match_rango.groups()
        fecha_inicio = f"{y1}-{m1}-{d1}"
        fecha_fin = f"{y2}-{m2}-{d2}"

        try:
            dt_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            dt_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
            duracion = (dt_fin - dt_inicio).days

            # Si dura más de 30 días, es probablemente un curso/taller
            es_curso = duracion > 30
            return fecha_inicio, fecha_fin, es_curso
        except ValueError:
            return fecha_inicio, fecha_fin, False

    # Formato único: dd.mm.yyyy
    match_unico = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', texto)
    if match_unico:
        d, m, y = match_unico.groups()
        fecha = f"{y}-{m}-{d}"
        return fecha, fecha, False

    return None, None, False


def _parsear_hora_telde(hora_texto: str) -> str | None:
    """Extrae hora de TeldeCultura."""
    if not hora_texto:
        return None

    if "todo el" in hora_texto.lower():
        return None

    match = re.search(r'(\d{1,2})[:.hH](\d{2})', hora_texto)
    if match:
        h, m = match.groups()
        return f"{int(h):02d}:{m}"
    return None


async def scrape_telde_cultura(page: Page) -> list[Evento]:
    """Scraper para TeldeCultura.org – eventos culturales de Telde.

    Fase 1: Extrae tarjetas de la agenda.
    Fase 2: Filtra cursos de larga duración (> 30 días).
    Fase 3: Deep scraping de fichas individuales.
    """
    print("🏘️ TeldeCultura.org...")
    eventos_raw: list[dict] = []

    try:
        # === FASE 1: Carga de la agenda ===
        await page.goto(
            "https://teldecultura.org/",
            wait_until="domcontentloaded",
            timeout=25000,
        )

        # Esperar contenido
        await asyncio.sleep(3)

        # Scroll para cargar más
        for _ in range(3):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

        # Extraer tarjetas con JS
        items = await page.evaluate("""
            () => {
                const results = [];
                // Buscar artículos o divs con contenido de evento
                const containers = document.querySelectorAll('article, .event-card, .card, .evento');
                
                // Si no hay articles, buscar por estructura alternativa
                let cards = containers.length > 0 ? containers :
                    document.querySelectorAll('div[class*="event"], div[class*="actividad"]');
                
                // Fallback: buscar por la estructura visible (título + fecha)
                if (cards.length === 0) {
                    const allLinks = document.querySelectorAll('a[href]');
                    for (const link of allLinks) {
                        const text = link.textContent.trim();
                        // Buscar enlaces que contengan fechas (formato dd.mm.yyyy)
                        if (/\d{2}\.\d{2}\.\d{4}/.test(text) && text.length > 20) {
                            results.push({
                                nombre: '',
                                url: link.href,
                                fullText: text.substring(0, 500),
                                img: null,
                            });
                        }
                    }
                    return results;
                }
                
                const seen = new Set();
                for (const card of cards) {
                    const text = card.textContent || '';
                    
                    // Buscar enlace principal
                    const link = card.querySelector('a[href]');
                    const url = link ? link.href : '';
                    if (url && seen.has(url)) continue;
                    if (url) seen.add(url);
                    
                    // Nombre: buscar h1, h2, h3 o título
                    const heading = card.querySelector('h1, h2, h3, h4, [class*="title"]');
                    let nombre = heading ? heading.textContent.trim() : '';
                    
                    // Imagen
                    const img = card.querySelector('img');
                    const imgSrc = img ? (img.src || img.dataset.src) : null;
                    
                    results.push({
                        nombre: nombre,
                        url: url || '',
                        fullText: text.substring(0, 500),
                        img: imgSrc,
                    });
                }
                return results;
            }
        """)

        print(f"   -> {len(items)} tarjetas detectadas en TeldeCultura")

        hoy = datetime.now().strftime("%Y-%m-%d")
        cursos_filtrados = 0

        for item in items:
            nombre = limpiar_texto(item.get("nombre", ""))
            url = item.get("url", "")
            texto = item.get("fullText", "")
            img = _validar_imagen(item.get("img"))

            # Si no tenemos nombre, intentar extraerlo del texto
            if not nombre:
                lines = [l.strip() for l in texto.split("\n") if l.strip() and len(l.strip()) > 5]
                if lines:
                    # Buscar la línea más larga que no sea fecha
                    for line in lines:
                        if not re.match(r'^\d{2}\.\d{2}', line) and len(line) > 5:
                            nombre = limpiar_texto(line)
                            break

            if not nombre or len(nombre) < 4:
                continue

            # Parsear fecha
            fecha_inicio, fecha_fin, es_curso = _parsear_fecha_telde(texto)

            # Filtrar cursos de larga duración
            if es_curso:
                # Solo incluir si la fecha de fin es futura Y si podemos
                # usar la fecha de fin como referencia
                if fecha_fin and fecha_fin >= hoy:
                    # Para cursos, usamos la fecha de fin como referencia
                    # pero los marcamos como "Curso/Taller"
                    cursos_filtrados += 1
                    continue
                else:
                    continue

            # Fecha ISO a usar
            fecha_iso = fecha_inicio
            if fecha_iso and fecha_iso < hoy:
                # Si la fecha de inicio es pasada pero la fecha fin es futura,
                # considerar como evento activo
                if fecha_fin and fecha_fin >= hoy:
                    fecha_iso = None  # No tiene fecha puntual clara
                else:
                    continue  # Evento completamente pasado

            fecha_raw_text = texto[:100] if texto else "Sin fecha"

            # Parsear hora
            hora = _parsear_hora_telde(texto)

            # Verificar si es "Entrada libre"
            es_gratis = "entrada libre" in texto.lower() or "gratis" in texto.lower()

            eventos_raw.append({
                "nombre": nombre,
                "url_full": url if url else "https://teldecultura.org/",
                "img_card": img,
                "fecha_iso": fecha_iso,
                "fecha_raw": fecha_raw_text,
                "hora": hora,
                "es_gratis": es_gratis,
            })

        if cursos_filtrados:
            print(f"   -> {cursos_filtrados} cursos/talleres de larga duración filtrados")

        # === FASE 3: Deep Scraping (si hay URL individual) ===
        print(f"   -> Procesando {len(eventos_raw)} eventos de TeldeCultura...")
        eventos: list[Evento] = []
        seen_texts: set[str] = set()

        for raw in eventos_raw:
            # Si tenemos URL individual, hacer deep scraping
            if raw["url_full"] and raw["url_full"] != "https://teldecultura.org/":
                try:
                    detalle = await enriquecer_evento(page, raw["url_full"], raw["nombre"], seen_texts)
                    imagen_final = _validar_imagen(detalle["imagen_url"]) or raw["img_card"]
                    fecha_iso = detalle["fecha_iso"] or raw["fecha_iso"]
                    fecha_raw = detalle.get("fecha_raw") or raw["fecha_raw"]
                    precio = detalle["precio_num"]
                    hora = detalle["hora"] or raw["hora"]
                    descripcion = detalle["descripcion"]
                except Exception:
                    imagen_final = raw["img_card"]
                    fecha_iso = raw["fecha_iso"]
                    fecha_raw = raw["fecha_raw"]
                    precio = 0.0 if raw["es_gratis"] else None
                    hora = raw["hora"]
                    descripcion = None
            else:
                imagen_final = raw["img_card"]
                fecha_iso = raw["fecha_iso"]
                fecha_raw = raw["fecha_raw"]
                precio = 0.0 if raw["es_gratis"] else None
                hora = raw["hora"]
                descripcion = None

            # Si es "Entrada libre" y no se encontró precio
            if raw["es_gratis"] and precio is None:
                precio = 0.0

            eventos.append(
                Evento(
                    nombre=raw["nombre"],
                    lugar="Telde",
                    fecha_raw=limpiar_texto(str(fecha_raw or "Sin fecha"))[:100],
                    fecha_iso=fecha_iso,
                    precio_num=precio,
                    hora=hora,
                    organiza="TeldeCultura",
                    url_venta=raw["url_full"],
                    imagen_url=imagen_final,
                    descripcion=descripcion,
                    estilo=categorizar_pro(raw["nombre"], "TeldeCultura"),
                )
            )

        # Log de calidad
        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        con_hora = sum(1 for e in eventos if e.hora)
        con_img = sum(1 for e in eventos if e.imagen_url)
        print(f"   -> TeldeCultura: {len(eventos)} eventos "
              f"(precio:{con_precio} fecha:{con_fecha} hora:{con_hora} img:{con_img})")

    except Exception as e:
        print(f"   ❌ Error TeldeCultura: {e}")

    return eventos if "eventos" in dir() else []

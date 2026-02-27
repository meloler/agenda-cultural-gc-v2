"""
Utilidades compartidas de enriquecimiento para todos los scrapers.
v4 – Scraping de Precisión (DOM-validado): extrae DATOS DUROS (precio, fecha, hora)
además de descripción e imagen.

Estrategia por capas:
  1. JSON-LD (schema.org)  — fuente más fiable
  2. Selectores por dominio — VALIDADOS contra DOM real
  3. Regex sobre texto visible — fallback universal

Selectores validados por inspección directa del DOM (2026-02-18):
  - Tomaticket: precio en #BotonExterno ("DESDE: 30 €"), fecha en p.fecha-info
  - Auditorio/Teatro Galdós: fecha/hora en texto visible de la ficha
  - Janto (ticketing): precio detrás de múltiples clics, intentamos extraer de tablas
"""

import json
import re
from urllib.parse import urlparse

from playwright.async_api import Page

from app.utils.text_processing import limpiar_texto

# ─────────────────────────────────────────────────────────────────────
# Blacklist de paja
# ─────────────────────────────────────────────────────────────────────
BLACKLIST = [
    "condiciones de compra", "condiciones generales",
    "política de privacidad", "aviso legal",
    "cambios o devoluciones", "cambios ni devoluciones",
    "cookies", "copyright", "newsletter", "suscríbete",
    "términos y condiciones", "protección de datos",
    "ley orgánica", "responsabilidad del organizador",
    "footer", "síguenos en", "todos los derechos",
    "barra libre", "mayores de 18",
]

GENERIC_TITLES = [
    "entradas para los mejores eventos", "entradas para", 
    "tickets for the best events", "tickets for",
    "compra tus entradas", "anuncio genérico", "entradas",
    "abono", "bono", "agenda gc", "inicio -", "entrees", "tomaticket", "tickety"
]

def es_titulo_generico(titulo: str) -> bool:
    """Detecta si un título es propaganda genérica del portal en lugar de un evento."""
    if not titulo:
        return True
    t = titulo.lower().strip()
    if len(t) < 3:
        return True
    return any(g in t for g in GENERIC_TITLES)


# ─────────────────────────────────────────────────────────────────────
# Regex patterns compilados
# ─────────────────────────────────────────────────────────────────────
RE_PRECIO = re.compile(
    r'(\d+[.,]?\d*)\s*€|€\s*(\d+[.,]?\d*)|(\d+[.,]?\d*)\s*euros',
    re.IGNORECASE,
)
RE_DESDE = re.compile(r'desde[:\s]+(\d+[.,]?\d*)', re.IGNORECASE)
RE_RANGO = re.compile(r'(\d+[.,]?\d*)\s*[-–—]\s*(\d+[.,]?\d*)\s*€', re.IGNORECASE)
RE_HORA = re.compile(
    r'(?:^|[\s,;(T])(\d{1,2})[:.hH](\d{2})(?:\s*(?:h|hrs?|horas?))?(?:\b|$)',
    re.IGNORECASE,
)
RE_FECHA_ISO = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
RE_FECHA_DMY_SLASH = re.compile(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})')
RE_FECHA_DMY_TEXT = re.compile(
    r'(\d{1,2})\s*(?:de\s+)?(?:del?\s+)?'
    r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|'
    r'septiembre|octubre|noviembre|diciembre)'
    r'(?:\s+(?:de\s+)?(\d{4}))?',
    re.IGNORECASE,
)
RE_A_LAS = re.compile(r'a\s+las?\s+(\d{1,2})[:.hH](\d{2})', re.IGNORECASE)

MESES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
}


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────
def es_paja(texto: str) -> bool:
    """Devuelve True si el texto parece boilerplate legal/footer/promo."""
    texto_lower = texto.lower()
    hits = sum(1 for kw in BLACKLIST if kw in texto_lower)
    return hits >= 2


def _detectar_dominio(url: str) -> str:
    """Detecta el dominio del evento."""
    domain = urlparse(url).netloc.lower()
    if "tomaticket" in domain:
        return "tomaticket"
    if "auditorioalfredokraus" in domain:
        return "auditorio"
    if "teatroperezgaldos" in domain:
        return "teatro_galdos"
    if "guiniguada" in domain or "gobiernodecanarias" in domain:
        return "guiniguada"
    if "fundacionlacajadecanarias" in domain:
        return "cicca"
    if "tickety" in domain:
        return "tickety"
    if "ticketmaster" in domain:
        return "ticketmaster"
    if "janto" in domain:
        return "janto"
    if "entrees" in domain:
        return "entrees"
    if "entradascanarias" in domain:
        return "entradascanarias"
    if "entradas.com" in domain:
        return "entradas_com"
    if "teldecultura" in domain:
        return "teldecultura"
    return "generico"


def _parsear_precio(texto: str) -> float | None:
    """Extrae el precio numérico más bajo de un texto."""
    if not texto:
        return None
    texto = texto.replace(",", ".")
    # "Gratis", "Gratuito"
    if any(kw in texto.lower() for kw in ["gratis", "gratuito", "entrada libre", "free"]):
        return 0.0

    precios: list[float] = []
    # "Desde 25€"
    for m in RE_DESDE.finditer(texto):
        try:
            precios.append(float(m.group(1)))
        except ValueError:
            pass
    # "15-30€" (rangos)
    for m in RE_RANGO.finditer(texto):
        try:
            precios.append(float(m.group(1)))
            precios.append(float(m.group(2)))
        except ValueError:
            pass
    for m in RE_PRECIO.finditer(texto):
        val = m.group(1) or m.group(2) or m.group(3)
        if val:
            try:
                precios.append(float(val))
            except ValueError:
                pass
    return min(precios) if precios else None


def _parsear_fecha(texto: str) -> str | None:
    """Extrae fecha ISO (YYYY-MM-DD) de un texto."""
    if not texto:
        return None
    # ISO directo: 2026-02-14
    m = RE_FECHA_ISO.search(texto)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # dd/mm/yyyy o dd/mm/yy o dd-mm-yyyy
    m = RE_FECHA_DMY_SLASH.search(texto)
    if m:
        dia, mes, anio = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
        if len(anio) == 2:
            anio = "20" + anio # asume 20xx
        return f"{anio}-{mes}-{dia}"
    # "14 de febrero 2026"
    m = RE_FECHA_DMY_TEXT.search(texto)
    if m:
        dia = m.group(1).zfill(2)
        mes = MESES.get(m.group(2).lower())
        if mes:
            anio = m.group(3) or "2026"
            return f"{anio}-{mes}-{dia}"
    return None


def _parsear_hora(texto: str) -> str | None:
    """Extrae hora HH:MM de un texto."""
    if not texto:
        return None
        
    hora_final = None
    # "a las 19:30"
    m = RE_A_LAS.search(texto)
    if m:
        h, mins = int(m.group(1)), m.group(2)
        if 0 <= h <= 23:
            hora_final = f"{h:02d}:{mins}"
            
    if not hora_final:
        # "19:30h", "20.00", "T20:00:00"
        m = RE_HORA.search(texto)
        if m:
            h, mins = int(m.group(1)), m.group(2)
            if 0 <= h <= 23:
                hora_final = f"{h:02d}:{mins}"

    if hora_final == "22:33":
        return None  # Entrées sentinel hour for unpublished/generic
        
    if hora_final == "00:00" and "T00:00" in texto:
        return None  # Default ISO hour without real time meaning
        
    # Descartar extraña hora 12:00 genérica frecuente de Entrées si proviene de un default JSON (aunque difícil de asegurar, 12:00 al mediodía sí puede ser válido. Nos fijamos en "T12:00:00" o similar).
    if hora_final == "12:00" and ("T12:00:00" in texto or "T00:00:00" in texto):
        return None
        
    if hora_final == "10:31" and "10:31" in texto: 
        # A veces Ticketmaster/otros meten 10.31€ como precio y se toma como hora.
        # Mejor ignorar horas locas sacadas de céntimos.
        # Wait, just to be safe.
        pass

    return hora_final


def _validar_imagen(url: str | None) -> str | None:
    """Filtra URLs de imagen inválidas."""
    if not url:
        return None
    url_upper = url.upper()
    # Filtrar eNULL, NULL, placeholder, etc.
    if any(x in url_upper for x in ["NULL", "PLACEHOLDER", "NOIMAGE", "DEFAULT"]):
        return None
    if not url.startswith("http"):
        return None
    if len(url) < 20:
        return None
    return url


# ─────────────────────────────────────────────────────────────────────
# Extracción de JSON-LD
# ─────────────────────────────────────────────────────────────────────
async def _extraer_json_ld(page: Page) -> dict | None:
    """Extrae datos de schema.org JSON-LD si existen."""
    try:
        scripts = page.locator("script[type='application/ld+json']")
        count = await scripts.count()
        for i in range(count):
            try:
                text = await scripts.nth(i).inner_text(timeout=2000)
                data = json.loads(text)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") in (
                            "Event", "MusicEvent", "TheaterEvent", "Festival",
                        ):
                            return item
                elif isinstance(data, dict):
                    if data.get("@type") in ("Event", "MusicEvent", "TheaterEvent", "Festival"):
                        return data
            except Exception:
                continue
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────
# Tomaticket: extracción específica con selectores DOM validados
# ─────────────────────────────────────────────────────────────────────
async def _extraer_tomaticket(page: Page, result: dict) -> dict:
    """Selectores DOM validados por inspección directa (2026-02-18).
    
    - Precio: #BotonExterno contiene "COMPRAR ENTRADAS - DESDE: 30 €"
    - Fecha/Hora: p.fecha-info contiene "10/03/2026 a las 19:30"
    - También puede contener "Varias Fechas" → capturar la primera
    """
    # PRECIO: #BotonExterno
    if result["precio_num"] is None:
        try:
            boton = page.locator("#BotonExterno").first
            if await boton.count() > 0:
                text = await boton.inner_text(timeout=3000)
                print(f"      [TOMATICKET] BotonExterno: '{text[:80]}'")
                # "COMPRAR ENTRADAS - DESDE: 30 €" or "COMPRAR ENTRADAS - 15,00 €"
                precio = _parsear_precio(text)
                if precio is not None:
                    result["precio_num"] = precio
        except Exception:
            pass

    # Fallback precio: búsqueda en botones de compra genéricos
    if result["precio_num"] is None:
        for sel in ["a.btn-compra", ".boton-compra", "a[href*='entradas'] span",
                     ".event-price", "[class*='price']", "[class*='precio']"]:
            try:
                loc = page.locator(sel).first
                if await loc.count() > 0:
                    text = await loc.inner_text(timeout=2000)
                    precio = _parsear_precio(text)
                    if precio is not None:
                        result["precio_num"] = precio
                        break
            except Exception:
                continue

    # FECHA + HORA: p.fecha-info ("10/03/2026 a las 19:30")
    if result["fecha_iso"] is None:
        try:
            fecha_el = page.locator("p.fecha-info").first
            if await fecha_el.count() > 0:
                text = await fecha_el.inner_text(timeout=2000)
                print(f"      [TOMATICKET] fecha-info: '{text[:80]}'")
                result["fecha_raw"] = text.strip()
                fecha = _parsear_fecha(text)
                if fecha:
                    result["fecha_iso"] = fecha
                hora = _parsear_hora(text)
                if hora and not result["hora"]:
                    result["hora"] = hora
        except Exception:
            pass

    # Fallback fecha: texto visible con patrones DD/MM/YYYY
    if result["fecha_iso"] is None:
        for sel in [".event-date", ".date", ".fecha", "[class*='date']",
                    "[class*='fecha']", ".info-date"]:
            try:
                loc = page.locator(sel).first
                if await loc.count() > 0:
                    text = await loc.inner_text(timeout=2000)
                    fecha = _parsear_fecha(text)
                    if fecha:
                        result["fecha_iso"] = fecha
                        result["fecha_raw"] = text.strip()
                        if not result["hora"]:
                            result["hora"] = _parsear_hora(text)
                        break
            except Exception:
                continue

    return result


# ─────────────────────────────────────────────────────────────────────
# Auditorio / Teatro Galdós: extracción DOM validada
# ─────────────────────────────────────────────────────────────────────
async def _extraer_cultura_canaria(page: Page, result: dict) -> dict:
    """Selectores DOM validados (2026-02-18).
    
    Estructura visible de la ficha:
      Fecha: "26 de febrero de 2026"
      Horario: "20:00 h"
      Sala: "Sala Sinfónica"
    
    NO hay precio en estas webs → se intenta sacar de Janto si hay enlace.
    """
    try:
        # Extraer TODO el texto visible del cuerpo principal
        body_text = await page.inner_text("body", timeout=5000)
        body_section = body_text[:3000]  # Solo la parte superior

        # FECHA: buscar "DD de MONTH de YYYY" en el cuerpo
        if result["fecha_iso"] is None:
            fecha = _parsear_fecha(body_section)
            if fecha:
                result["fecha_iso"] = fecha
                # Extraer la fecha raw del texto
                m = RE_FECHA_DMY_TEXT.search(body_section)
                if m:
                    result["fecha_raw"] = m.group(0)

        # HORA: buscar "HH:MM h" o "HH:MM" en el cuerpo
        if result["hora"] is None:
            hora = _parsear_hora(body_section)
            if hora:
                result["hora"] = hora

        # PRECIO: intentar encontrar enlace a Janto y navegar
        if result["precio_num"] is None:
            try:
                janto_link = page.locator("a[href*='janto']").first
                if await janto_link.count() > 0:
                    janto_url = await janto_link.get_attribute("href")
                    if janto_url:
                        result = await _intentar_janto(page, janto_url, result)
            except Exception:
                pass

    except Exception as e:
        print(f"      [CULTURA_CANARIA] Error: {e}")

    return result


async def _intentar_janto(page: Page, janto_url: str, result: dict) -> dict:
    """Intenta extraer precio de la plataforma Janto (ticketing).
    
    Janto es muy dinámico (PHP + iframes). Intentamos:
    1. Navegar a la URL de Janto
    2. Buscar texto con € en la tabla de precios
    3. Si no, buscar en el body text visible
    """
    try:
        print(f"      [JANTO] Intentando: {janto_url[:80]}...")
        await page.goto(janto_url, wait_until="domcontentloaded", timeout=10000)
        await page.wait_for_timeout(2000)

        # Buscar precios en la página de Janto
        body_text = await page.inner_text("body", timeout=5000)
        precio = _parsear_precio(body_text[:3000])
        if precio is not None:
            result["precio_num"] = precio
            print(f"      [JANTO] Precio encontrado: {precio}€")
        else:
            # Intentar clickear "Seleccionar" si existe
            try:
                sel_btn = page.locator("button:has-text('Seleccionar'), a:has-text('Seleccionar'), input[value*='Seleccionar']").first
                if await sel_btn.count() > 0:
                    await sel_btn.click(timeout=3000)
                    await page.wait_for_timeout(2000)
                    body_text2 = await page.inner_text("body", timeout=5000)
                    precio2 = _parsear_precio(body_text2[:3000])
                    if precio2 is not None:
                        result["precio_num"] = precio2
                        print(f"      [JANTO] Precio (post-click): {precio2}€")
            except Exception:
                pass

    except Exception as e:
        print(f"      [JANTO] Error: {e}")

    return result


# ─────────────────────────────────────────────────────────────────────
# extraer_datos_duros — el corazón de Scraping de Precisión v4
# ─────────────────────────────────────────────────────────────────────
async def extraer_datos_duros(page: Page, url: str) -> dict:
    """Extrae precio, fecha y hora de la ficha del evento.

    Capas:
      1. JSON-LD (schema.org)
      2. Selectores CSS específicos por dominio (VALIDADOS contra DOM)
      3. Texto visible de la página (regex)

    Returns:
        {"precio_num": float|None, "fecha_iso": str|None,
         "hora": str|None, "fecha_raw": str|None}
    """
    result = {"precio_num": None, "fecha_iso": None, "hora": None, "fecha_raw": None}
    dominio = _detectar_dominio(url)

    # === CAPA 1: JSON-LD ===
    ld = await _extraer_json_ld(page)
    if ld:
        # Precio
        offers = ld.get("offers")
        if offers:
            if isinstance(offers, list):
                offers = offers[0]
            if isinstance(offers, dict):
                price = offers.get("price") or offers.get("lowPrice")
                if price is not None:
                    try:
                        result["precio_num"] = float(price)
                    except (ValueError, TypeError):
                        pass
        # Fecha + Hora
        start = ld.get("startDate") or ""
        if start:
            result["fecha_raw"] = str(start)
            result["fecha_iso"] = _parsear_fecha(start)
            result["hora"] = _parsear_hora(start)

        # Imagen del JSON-LD (validar)
        ld_image = ld.get("image")
        if isinstance(ld_image, list):
            ld_image = ld_image[0] if ld_image else None
        if isinstance(ld_image, dict):
            ld_image = ld_image.get("url")

    # === CAPA 2: Selectores DOM-validados por dominio ===
    if dominio == "tomaticket":
        result = await _extraer_tomaticket(page, result)
    elif dominio in ("auditorio", "teatro_galdos"):
        result = await _extraer_cultura_canaria(page, result)
    else:
        # Selectores genéricos para otros dominios
        # -- PRECIO --
        if result["precio_num"] is None:
            price_selectors = {
                "tickety": [".event-price", "[class*='price']", "[class*='precio']",
                            "button:has-text('€')", "span:has-text('€')"],
                "ticketmaster": [".event-price", "[class*='price']", "[data-testid*='price']"],
                "guiniguada": [".precio", "[class*='price']", "[class*='tarifa']"],
                "cicca": [".precio", "[class*='price']", "[class*='tarifa']"],
                "generico": [".price", ".precio", "[class*='price']", "[class*='precio']"],
            }
            sels = price_selectors.get(dominio, price_selectors["generico"])
            for sel in sels:
                try:
                    loc = page.locator(sel).first
                    if await loc.count() > 0:
                        text = await loc.inner_text(timeout=2000)
                        precio = _parsear_precio(text)
                        if precio is not None:
                            result["precio_num"] = precio
                            break
                except Exception:
                    continue

        # -- FECHA (selectores genéricos) --
        if result["fecha_iso"] is None:
            # <time datetime="...">
            try:
                time_els = page.locator("time[datetime]")
                count = await time_els.count()
                for i in range(min(count, 5)):
                    dt = await time_els.nth(i).get_attribute("datetime")
                    if dt:
                        fecha = _parsear_fecha(dt)
                        if fecha:
                            result["fecha_iso"] = fecha
                            result["fecha_raw"] = dt
                            if not result["hora"]:
                                result["hora"] = _parsear_hora(dt)
                            break
            except Exception:
                pass

        if result["fecha_iso"] is None:
            date_selectors = {
                "tickety": [".date", ".fecha", "[class*='date']"],
                "ticketmaster": ["[class*='date']", "time", "[datetime]"],
                "guiniguada": [".fecha", "[class*='date']", ".event-date"],
                "cicca": [".fecha", "[class*='date']", ".event-date"],
                "generico": [".event-date", ".date", ".fecha",
                             "[class*='date']", "[class*='fecha']"],
            }
            sels = date_selectors.get(dominio, date_selectors["generico"])
            for sel in sels:
                try:
                    loc = page.locator(sel).first
                    if await loc.count() > 0:
                        text = await loc.inner_text(timeout=2000)
                        text = limpiar_texto(text)
                        fecha = _parsear_fecha(text)
                        if fecha:
                            result["fecha_iso"] = fecha
                            result["fecha_raw"] = text
                            if not result["hora"]:
                                result["hora"] = _parsear_hora(text)
                            break
                except Exception:
                    continue

    # === CAPA 3: Regex sobre contenido visible ===
    try:
        body_text = await page.inner_text("body", timeout=3000)
        body_text_limpio = body_text[:5000]  # Limitar para no procesar footer

        # Precio fallback
        if result["precio_num"] is None:
            result["precio_num"] = _parsear_precio(body_text_limpio)

        # Fecha fallback
        if result["fecha_iso"] is None:
            fecha = _parsear_fecha(body_text_limpio)
            if fecha:
                result["fecha_iso"] = fecha

        # Hora fallback
        if result["hora"] is None:
            result["hora"] = _parsear_hora(body_text_limpio)
    except Exception:
        pass

    return result


# ─────────────────────────────────────────────────────────────────────
# Descripción
# ─────────────────────────────────────────────────────────────────────
async def extraer_parrafos(page: Page, container_sel: str) -> str:
    """Extrae y une párrafos dentro de un contenedor, filtrando paja."""
    lines: list[str] = []
    try:
        container = page.locator(container_sel).first
        if await container.count() == 0:
            return ""

        parrafos = container.locator("p, li, span")
        count = await parrafos.count()

        if count > 0:
            for i in range(count):
                try:
                    texto = await parrafos.nth(i).inner_text(timeout=1000)
                    texto = limpiar_texto(texto)
                    if texto and len(texto) > 5 and not es_paja(texto):
                        lines.append(texto)
                except Exception:
                    continue
        else:
            texto = await container.inner_text(timeout=3000)
            texto = limpiar_texto(texto)
            if texto and not es_paja(texto):
                lines.append(texto)
    except Exception:
        pass

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# Función principal de deep scraping
# ─────────────────────────────────────────────────────────────────────
async def enriquecer_evento(
    page: Page,
    url: str,
    nombre: str,
    seen_texts: set[str],
) -> dict:
    """Deep scrape genérico: navega a la URL del evento y extrae todo.

    Returns:
        Dict: {"descripcion", "imagen_url", "precio_num", "fecha_iso",
               "hora", "fecha_raw"}
    """
    detalle = {
        "descripcion": None,
        "imagen_url": None,
        "precio_num": None,
        "fecha_iso": None,
        "hora": None,
        "fecha_raw": None,
        "nombre_deep": None,
    }

    # Guardar la URL original para poder volver (en caso de Janto navigation)
    original_url = url

    try:
        print(f"   -> Enriqueciendo: {nombre[:60]}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        except Exception as nav_err:
            print(f"      [DEBUG] Navegación lenta ({nav_err.__class__.__name__}), "
                  "capturando contenido parcial...")
        await page.wait_for_timeout(1500)

        # === DATOS DUROS (precio, fecha, hora) ===
        datos = await extraer_datos_duros(page, url)
        detalle["precio_num"] = datos["precio_num"]
        detalle["fecha_iso"] = datos["fecha_iso"]
        detalle["hora"] = datos["hora"]
        detalle["fecha_raw"] = datos["fecha_raw"]

        if datos["precio_num"] is not None:
            print(f"      [PRECIO] {datos['precio_num']}€")
        if datos["fecha_iso"]:
            print(f"      [FECHA]  {datos['fecha_iso']}")
        if datos["hora"]:
            print(f"      [HORA]   {datos['hora']}")

        # Buscar el nombre real (h1) sin truncar
        try:
            h1 = page.locator("h1").first
            if await h1.count() > 0:
                h1_text = await h1.inner_text(timeout=2000)
                if h1_text and len(h1_text.strip()) > 5:
                    nombre_posible = h1_text.strip()
                    if not es_titulo_generico(nombre_posible):
                        detalle["nombre_deep"] = nombre_posible
                    else:
                        print(f"      ⚠️ Título H1 ignorado por ser genérico: '{nombre_posible}'")
        except Exception:
            pass

        # Si Janto navigation changed the URL, go back to original for desc/image
        current_url = page.url
        if "janto" in current_url.lower() and "janto" not in original_url.lower():
            try:
                await page.goto(original_url, wait_until="domcontentloaded", timeout=10000)
                await page.wait_for_timeout(1000)
            except Exception:
                pass

        # === DESCRIPCIÓN ===
        desc_selectors = [
            "div[itemprop='description']",
            "div.description",
            ".event-description",
            "#event-description",
            ".entry-content",
            "article .content",
            "article",
            "[class*='description']:not([class*='condition'])",
            ".detail-text",
            ".info-event",
            ".content-detail",
            ".field-body",
            ".texto",
            ".cuerpo",
        ]

        for desc_sel in desc_selectors:
            texto = await extraer_parrafos(page, desc_sel)
            if texto and len(texto) > 30 and not es_paja(texto):
                fingerprint = texto[:200].strip()
                if fingerprint not in seen_texts:
                    seen_texts.add(fingerprint)
                    detalle["descripcion"] = texto
                    break

        # Fallback: párrafos sueltos
        if not detalle["descripcion"]:
            try:
                all_p = page.locator("main p, .container p, .content p, section p, article p")
                count = await all_p.count()
                clean_lines: list[str] = []
                for i in range(min(count, 30)):
                    try:
                        texto = await all_p.nth(i).inner_text(timeout=1000)
                        texto = limpiar_texto(texto)
                        if texto and len(texto) > 20 and not es_paja(texto):
                            clean_lines.append(texto)
                    except Exception:
                        continue
                if clean_lines:
                    combined = "\n".join(clean_lines)
                    fingerprint = combined[:200].strip()
                    if fingerprint not in seen_texts:
                        seen_texts.add(fingerprint)
                        detalle["descripcion"] = combined
            except Exception:
                pass

        # === IMAGEN ===
        # Prioridad 1: og:image (validada)
        try:
            og = page.locator("meta[property='og:image']").first
            if await og.count() > 0:
                img_content = await og.get_attribute("content")
                img_content = _validar_imagen(img_content)
                if img_content:
                    detalle["imagen_url"] = img_content
        except Exception:
            pass

        # Prioridad 2: imagen principal visible (ignora og:image si era NULL)
        if not detalle["imagen_url"]:
            for img_sel in [
                ".event-image img", ".detail-image img",
                "[class*='poster'] img", "[class*='cartel'] img",
                ".main-image img", ".entry-content img",
                "article img", "img[class*='event']",
                ".contenido img", ".imagen img",
                # Tomaticket: imagen principal del evento
                "img[src*='tomaticket.com/eventos']",
                "img[src*='tomaticket.com/images/eventos']",
            ]:
                try:
                    img_loc = page.locator(img_sel).first
                    if await img_loc.count() > 0:
                        src = await img_loc.get_attribute("src") or \
                              await img_loc.get_attribute("data-src")
                        src = _validar_imagen(src)
                        if src and "logo" not in src.lower():
                            detalle["imagen_url"] = src
                            break
                except Exception:
                    continue

        # Prioridad 3: cualquier imagen grande (>200px) que no sea logo
        if not detalle["imagen_url"]:
            try:
                all_imgs = page.locator("img")
                img_count = await all_imgs.count()
                for i in range(min(img_count, 15)):
                    try:
                        img = all_imgs.nth(i)
                        src = await img.get_attribute("src")
                        src = _validar_imagen(src)
                        if not src or "logo" in src.lower() or "icon" in src.lower():
                            continue
                        # Check natural dimensions
                        width = await img.evaluate("el => el.naturalWidth || el.width")
                        if width and int(width) > 200:
                            detalle["imagen_url"] = src
                            break
                    except Exception:
                        continue
            except Exception:
                pass

    except Exception as e:
        print(f"      ⚠️ Error enriqueciendo '{nombre[:40]}': {e}")

    return detalle

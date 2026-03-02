import re
import datetime
from app.utils.text_processing import limpiar_texto

__all__ = [
    '_parsear_precio', '_parsear_fecha', '_parsear_hora', '_validar_imagen',
    'es_paja', 'es_titulo_generico',
    'RE_PRECIO', 'RE_DESDE', 'RE_RANGO', 'RE_FECHA_ISO', 'RE_FECHA_DMY_SLASH', 
    'RE_FECHA_DMY_TEXT', 'RE_HORA', 'RE_A_LAS', 'RE_HORA_SHORT', 'MESES',
    'RE_DIRECCION', 'RE_NOMBRE_BASURA'
]

# Regex compilados (extraídos de _enrichment.py para testabilidad pura)
RE_PRECIO = re.compile(r'(?:€|EUR|euros|€)\s*(\d+[.,]?\d*)|(\d+[.,]?\d*)\s*(?:€|EUR|euros|€)', re.I)
RE_DESDE = re.compile(r'(?:desde|a partir de|precio)\s*:?\s*(\d+[.,]?\d*)', re.I)
RE_RANGO = re.compile(r'(\d+[.,]?\d*)\s*(?:-|al|y)\s*(\d+[.,]?\d*)\s*(?:€|EUR|euros|€)', re.I)

RE_FECHA_ISO = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
RE_FECHA_DMY_SLASH = re.compile(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})')
RE_FECHA_DMY_TEXT = re.compile(r'(\d{1,2})\s+de\s+(\w+)\s+(20\d{2})?', re.I)

RE_HORA = re.compile(
    r'(?:^|[\s,;(T])([012]?\d)[:.hH]([0-5]\d)(?:\s*(?:h|hrs?|horas?))?(?!\s*(?:€|euros|%|[$]))(?:\b|$)',
    re.I,
)
RE_A_LAS = re.compile(r'a\s+las?\s+([012]?\d)[:.hH]([0-5]\d)', re.I)
RE_HORA_SHORT = re.compile(
    r'(?:^|[\s,;(T])(\d{1,2})(?:\s*(?:h|hrs|horas))(?!\s*(?:€|euros|%|[$]))(?:\b|$)',
    re.I,
)

RE_DIRECCION = re.compile(
    r'(?:en\s+(?:el|la|los|las)\s+)?'
    r'((?:Calle|C/|Avda\.?|Avenida|Plaza|Paseo|Campus|Salón de actos|Edificio)\s+[^.,:;\n]{3,60})',
    re.IGNORECASE,
)
RE_NOMBRE_BASURA = re.compile(r'^[\d\s\-.,;:]+$')

MESES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06',
    'julio': '07', 'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
    'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
    'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
}

def _parsear_precio(texto: str) -> float | None:
    if not texto: return None
    val = None
    m = RE_RANGO.search(texto)
    if m: val = float(m.group(1).replace(",", "."))
    else:
        m = RE_DESDE.search(texto)
        if m: val = float(m.group(1).replace(",", "."))
        else:
            m = RE_PRECIO.search(texto)
            if m:
                v_str = m.group(1) or m.group(2)
                if v_str:
                    val = float(v_str.replace(",", "."))
    
    if val is not None and val < 500.0:
        return val
        
    # Si no se encontró ningún precio numérico, comprobar si dice "gratis"
    t_lower = texto.lower()
    if any(kw in t_lower for kw in ["gratis", "gratuito", "entrada libre", "free"]):
        return 0.0
        
    return None

def _parsear_fecha(texto: str) -> str | None:
    if not texto: return None
    # ISO: 2026-02-14
    m = RE_FECHA_ISO.search(texto)
    if m: return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # DMY: 14/02/2026
    m = RE_FECHA_DMY_SLASH.search(texto)
    if m:
        dia, mes, anio = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
        if len(anio) == 2: anio = "20" + anio
        return f"{anio}-{mes}-{dia}"
    # Range Text: 1 al 10 de Mayo
    m = re.search(r'(\d{1,2})\s+(?:al|y|de|a)\s+(\d{1,2})\s+de\s+(\w+)\s+(20\d{2})?', texto, re.I)
    if m:
        dia = m.group(1).zfill(2)
        mes = MESES.get(m.group(3).lower())
        if mes:
            anio = m.group(4) or "2026"
            return f"{anio}-{mes}-{dia}"
    # Standard Text: 14 de febrero
    m = re.search(r'(\d{1,2})\s*(?:de\s+)?(\w+)\s*(?:de\s+)?(20\d{2})?', texto, re.I)
    if m:
        dia = m.group(1).zfill(2)
        mes_name = m.group(2).lower()
        mes = MESES.get(mes_name) or (MESES.get(mes_name[:3]) if len(mes_name) > 3 else None)
        if mes:
            anio = m.group(3) or "2026"
            return f"{anio}-{mes}-{dia}"
    return None

def _parsear_hora(texto: str) -> str | None:
    if not texto: return None
    hora_final = None
    m = RE_A_LAS.search(texto)
    if m:
        h, m_int = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= m_int <= 59:
            hora_final = f"{h:02d}:{m_int:02d}"
    if not hora_final:
        m = RE_HORA.search(texto)
        if m:
            h, m_int = int(m.group(1)), int(m.group(2))
            if 0 <= h <= 23 and 0 <= m_int <= 59:
                hora_final = f"{h:02d}:{m_int:02d}"
    if not hora_final:
        m = RE_HORA_SHORT.search(texto)
        if m:
            h = int(m.group(1))
            if 0 <= h <= 23:
                hora_final = f"{h:02d}:00"

    if not hora_final: return None
    
    # Improbables
    improbables = {"10:31", "12:04", "05:00", "06:00", "07:00", "08:00", "12:00", "22:33", "00:00"}
    if hora_final in improbables: return None
    return hora_final

def _validar_imagen(url: str) -> str | None:
    if not url: return None
    u = str(url).strip()
    if any(x in u.lower() for x in ["data:image", "transparent.gif", "placeholder", "empty.png"]):
        return None
    # 15 chars for short domains, filters sh.ort
    if len(u) < 15 or not u.startswith("http"): return None
    return u


# ─────────────────────────────────────────────────────────────────────
# Blacklist de paja y títulos genéricos
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

def es_paja(texto: str) -> bool:
    """Devuelve True si el texto parece boilerplate legal/footer/promo."""
    texto_lower = (texto or "").lower()
    hits = sum(1 for kw in BLACKLIST if kw in texto_lower)
    return hits >= 2

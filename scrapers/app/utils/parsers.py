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
RE_FECHA_DMY_TEXT = re.compile(r'(\d{1,2})\s+de\s+(\w+)(?:\s+(?:de\s+)?(20\d{2}))?', re.I)

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


# ─────────────────────────────────────────────────────────────────────
# Helpers de fecha (P0-A fix)
# ─────────────────────────────────────────────────────────────────────
def _anio_inferido(mes: str, dia: str) -> str:
    """Infiere el año más probable cuando el texto de la página no lo indica.

    Regla: si la fecha (mes-dia) ya pasó hace más de 30 días, asumimos
    que es del año siguiente.  Si no, asumimos el año corriente.
    """
    hoy = datetime.date.today()
    try:
        candidata = datetime.date(hoy.year, int(mes), int(dia))
    except ValueError:
        return str(hoy.year)
    if candidata < hoy - datetime.timedelta(days=30):
        return str(hoy.year + 1)
    return str(hoy.year)


def _fecha_valida(fecha_iso: str) -> bool:
    """Verifica que una fecha ISO sea parseable y razonable (2024-2030)."""
    try:
        dt = datetime.datetime.strptime(fecha_iso, "%Y-%m-%d")
        return 2024 <= dt.year <= 2030
    except ValueError:
        return False


def _parsear_fecha(texto: str) -> str | None:
    """Parsea una fecha desde texto con validación estricta de rango.

    Capas (en orden de prioridad):
      1. ISO:  2026-02-14
      2. DMY Slash:  14/02/2026  (con validación anti-teléfono)
      3. Rango textual:  1 al 10 de Mayo 2026
      4. Texto estándar:  14 de febrero de 2026
    """
    if not texto:
        return None

    # 1) ISO: 2026-02-14
    m = RE_FECHA_ISO.search(texto)
    if m:
        fecha = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        if _fecha_valida(fecha):
            return fecha

    # 2) DMY Slash: 14/02/2026 — con validación de rangos (anti-teléfono, anti-basura)
    m = RE_FECHA_DMY_SLASH.search(texto)
    if m:
        dia_raw, mes_raw, anio_raw = m.group(1), m.group(2), m.group(3)
        dia = dia_raw.zfill(2)
        mes = mes_raw.zfill(2)
        anio = anio_raw
        if len(anio) == 2:
            anio = "20" + anio
        # Validar rangos crudos ANTES de construir la fecha
        try:
            if 1 <= int(dia_raw) <= 31 and 1 <= int(mes_raw) <= 12 and 2024 <= int(anio) <= 2030:
                fecha = f"{anio}-{mes}-{dia}"
                if _fecha_valida(fecha):
                    return fecha
        except ValueError:
            pass

    # 3) Rango textual: "1 al 10 de Mayo 2026"
    m = re.search(
        r'(\d{1,2})\s+(?:al|y|de|a)\s+(\d{1,2})\s+de\s+(\w+)\s+(20\d{2})?',
        texto, re.I,
    )
    if m:
        dia = m.group(1).zfill(2)
        mes = MESES.get(m.group(3).lower())
        if mes:
            anio = m.group(4) or _anio_inferido(mes, dia)
            fecha = f"{anio}-{mes}-{dia}"
            if _fecha_valida(fecha):
                return fecha

    # 4) Texto estándar: "14 de febrero de 2026" / "14 febrero"
    m = RE_FECHA_DMY_TEXT.search(texto)
    if m:
        dia = m.group(1).zfill(2)
        mes_name = m.group(2).lower()
        mes = MESES.get(mes_name) or (MESES.get(mes_name[:3]) if len(mes_name) > 3 else None)
        if mes:
            anio = m.group(3) or _anio_inferido(mes, dia)
            fecha = f"{anio}-{mes}-{dia}"
            if _fecha_valida(fecha):
                return fecha

    return None


def _parsear_hora(texto: str) -> str | None:
    """Parsea una hora desde texto.

    P0-B fix: blacklist reducida — ya NO descarta 12:00, 00:00, 22:33
    que son horas legítimas (matinés, nochevieja, sesiones nocturnas).
    Solo se descartan horas de madrugada (05-08h) que casi nunca son
    eventos culturales y suelen ser residuos de timestamps del servidor.
    """
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

    # P0-B fix: blacklist mínima — solo horas de madrugada servicial
    # que suelen ser timestamps del servidor, no horas de evento.
    improbables_madrugada = {"05:00", "06:00", "07:00"}
    if hora_final in improbables_madrugada:
        return None
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
    "abono", "bono", "agenda gc", "inicio -", "entrees", "tomaticket", "tickety",
    "comprar entradas", "eventos en gran canaria", "inicio - entradascanarias",
]

# Palabras sueltas que son categorías, no títulos de eventos
_CATEGORIA_WORDS = {
    "música", "musica", "teatro", "cine", "danza", "deporte",
    "cultura", "humor", "arte", "concierto", "festival",
    "espectáculo", "espectaculo", "evento", "eventos",
    "exposición", "exposicion", "charla", "conferencia",
}

def es_titulo_generico(titulo: str) -> bool:
    """Detecta si un título es propaganda genérica del portal en lugar de un evento."""
    if not titulo:
        return True
    t = titulo.lower().strip()
    if len(t) < 3:
        return True
    # Una sola palabra que es una categoría → genérico
    if t in _CATEGORIA_WORDS:
        return True
    return any(g in t for g in GENERIC_TITLES)

def es_paja(texto: str) -> bool:
    """Devuelve True si el texto parece boilerplate legal/footer/promo."""
    texto_lower = (texto or "").lower()
    hits = sum(1 for kw in BLACKLIST if kw in texto_lower)
    return hits >= 2

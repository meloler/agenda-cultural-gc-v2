"""
Utilidades de procesamiento de texto para limpieza y categorización de eventos.
Extraído de main.py por Data_Refinery_Agent.
"""

import re
from urllib.parse import unquote


def limpiar_texto(texto: str) -> str:
    """Limpia espacios extra y caracteres invisibles."""
    if not texto:
        return ""
    return re.sub(r'\s+', ' ', texto).strip().replace('\u200b', '')


def inferir_nombre(url: str) -> str:
    """Convierte '/evento/lago-de-cisnes/123' en 'Lago De Cisnes'."""
    try:
        if not url:
            return "Evento Cultural"
        partes = [p for p in url.split('/') if p and not p.isdigit() and len(p) > 2]
        if not partes:
            return "Evento Cultural"
        slug = partes[-1]
        slug = unquote(slug)
        slug = re.sub(r'^\d+-', '', slug)
        slug = slug.replace('-', ' ').replace('_', ' ')
        return slug.title()
    except Exception:
        return "Evento Cultural"


def normalizar_fecha(fecha_texto: str) -> str | None:
    """Convierte texto de fecha a formato ISO (YYYY-MM-DD)."""
    meses = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
        'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12',
    }
    try:
        match = re.search(r'(\d{1,2})\s+(?:de\s+)?([a-zA-Z]+)', fecha_texto.lower())
        if match:
            dia = match.group(1).zfill(2)
            mes = meses.get(match.group(2)[:3], '01')
            return f"2026-{mes}-{dia}"
        return None
    except Exception:
        return None


def categorizar_pro(nombre: str, organiza: str) -> str:
    """Categoriza eventos según keywords en nombre/organizador."""
    if organiza in ["Auditorio A. Kraus", "Teatro Pérez Galdós", "CICCA", "Teatro Guiniguada"]:
        return "Cultura/Teatro"
    n = nombre.lower()
    if any(x in n for x in ['concierto', 'festival', 'live', 'musica', 'banda', 'rock', 'jazz']):
        return 'Música'
    if any(x in n for x in ['carnaval', 'gala', 'reina', 'drag']):
        return 'Carnaval'
    if any(x in n for x in ['humor', 'monologo', 'comedia']):
        return 'Humor'
    return 'Otros'

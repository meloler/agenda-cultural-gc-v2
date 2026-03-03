"""
Utilidades de procesamiento de texto para limpieza y categorización de eventos.
Extraído de main.py por Data_Refinery_Agent.
"""

import re
import pandas as pd
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
    """Convierte texto de fecha a formato ISO (YYYY-MM-DD).
    
    P0-A fix: año inferido dinámicamente (no hardcodeado).
    """
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
            mes = meses.get(match.group(2)[:3], None)
            if not mes:
                return None
            # Inferir año dinámicamente
            from datetime import date, timedelta
            hoy = date.today()
            try:
                candidata = date(hoy.year, int(mes), int(dia))
            except ValueError:
                return None
            anio = hoy.year + 1 if candidata < hoy - timedelta(days=30) else hoy.year
            return f"{anio}-{mes}-{dia}"
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


def normalizar_titulo_export(t: str) -> str:
    if pd.isna(t) or not t: return ""
    t = str(t).strip()
    # Quitar sufijos geográficos redundantes (" en Gran Canaria", " | Las Palmas de Gran Canaria")
    pattern = r'(?i)\s*[-|/,]*\s*(?:en\s+)?(?:las palmas de gran canaria|las palmas|gran canaria|islas canarias|canarias|telde|infecar)\b\s*$'
    t = re.sub(pattern, '', t)
    # Limpiar separadores colgantes por si acaso
    t = re.sub(r'(?i)\s+[-|/,]\s*$', '', t)
    return t.strip()


def limpiar_lugar(lugar: str) -> str | None:
    l = (lugar or "").strip()
    if not l: return None
    # Lista masiva de frases narrativas para evitar escapes
    leak_tokens = ["paseo nocturno", "prepárate", "descubre", "que no olvidarás", "la cara más natural", "calle y los", "plaza y", "disfruta", "sumérgete", "vive la experiencia", "te esperamos", "no te pierdas", "aventura", "te invitamos", "https://", "conoce al autor", "abierto al público", "te imaginas", "asombroso", "fantástico", "reservando", "incluye", "taquilla", "entrada libre"]
    if len(l) > 150: return None  # Don't kill legit 70-150 char places
    if any(tok in l.lower() for tok in leak_tokens): return None
    
    # Resolver Alias
    import unicodedata
    low = l.lower()
    norm = unicodedata.normalize("NFKD", low).encode('ASCII', 'ignore').decode('ASCII')
    
    if "kraus" in norm or "auditorio alfredo" in norm:
        return "Auditorio Alfredo Kraus"
    if "galdos" in norm and "perez" in norm:
        return "Teatro Pérez Galdós"
    if "guiniguada" in norm:
        return "Teatro Guiniguada"
    if "cicca" in norm:
        return "Fundación CICCA"
    if "cuyas" in norm:
        return "Teatro Cuyás"
    if "victor jara" in norm:
        return "Teatro Víctor Jara"
    if "gran canaria arena" in norm or "gc arena" in norm:
        return "Gran Canaria Arena"
    if "infecar" in norm:
        return "INFECAR"
    if "estadio de gran canaria" in norm:
        return "Estadio de Gran Canaria"
        
    return l or None

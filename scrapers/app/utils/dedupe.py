import re
import unicodedata
from app.utils.text_processing import normalizar_titulo_export, limpiar_lugar

def _simplify_title(t: str) -> str:
    if not t: return ""
    t = normalizar_titulo_export(t).lower()
    # Remove noise words (longer first to avoid partial matches)
    noise = ["en concierto", "concierto de", "concierto", "live", "gira", " en "]
    for n in noise:
        t = t.replace(n, " ")
    
    # Normalize and remove non-alnum
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r'[^a-z0-9]', '', t)
    return t.strip()

def _simplify_place(p: str) -> str:
    if not p: return ""
    # Use our alias resolver first
    p_clean = limpiar_lugar(p) or p
    p_clean = unicodedata.normalize("NFKD", p_clean).encode("ascii", "ignore").decode("ascii")
    p_clean = re.sub(r'[^a-z0-9]', '', p_clean.lower())
    return p_clean

def generate_occurrence_key(nombre: str, fecha: str, lugar: str) -> str:
    """Generates a key for cross-source occurrence matching."""
    name_key = _simplify_title(nombre)
    place_key = _simplify_place(lugar)
    return f"{name_key}|{fecha}|{place_key}"

def resolve_cross_source_duplicates(eventos):
    """
    Groups events from different sources using event_group_id.
    Logic: Same normalized title, date and venue = Same physical event.
    """
    groups = {}
    next_group_id = 1
    
    for ev in eventos:
        key = generate_occurrence_key(ev.nombre, ev.fecha_iso, ev.lugar)
        if key not in groups:
            groups[key] = f"group_{next_group_id}"
            next_group_id += 1
        
        ev.event_group_id = groups[key]
    
    return eventos

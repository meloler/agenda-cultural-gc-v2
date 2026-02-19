"""
GIS_Specialist – Módulo de geolocalización para eventos de Gran Canaria.

v3 – Alta precisión + búsqueda agresiva:
  - Coordenadas validadas con Google Maps.
  - Normalización Unicode (sin tildes, sin mayúsculas).
  - Nominatim con cascada de queries + contexto geográfico.

Estrategia por capas:
  1. Diccionario de coordenadas fijas  — recintos conocidos (instantáneo, sin API)
  2. Geopy + Nominatim (agresivo)     — 3 queries con contexto creciente
  3. Fallback                         — centro de Las Palmas de Gran Canaria

IMPORTANTE: latitud/longitud siempre se devuelven como float para evitar
bugs en los enlaces de Google Maps.
"""

import time
import unicodedata
from typing import Optional

from sqlmodel import select

from app.database import get_session
from app.models import Evento

# ─────────────────────────────────────────────────────────────────────
# Normalización de texto (quitar tildes, minúsculas)
# ─────────────────────────────────────────────────────────────────────
def _normalizar(texto: str) -> str:
    """Normaliza un nombre de lugar: minúsculas, sin tildes, sin puntuación extra."""
    if not texto:
        return ""
    # Minúsculas
    texto = texto.lower().strip()
    # Quitar tildes: "pérez" → "perez", "cuyás" → "cuyas"
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


# ─────────────────────────────────────────────────────────────────────
# CAPA 1: Diccionario de coordenadas fijas (alta precisión Google Maps)
# ─────────────────────────────────────────────────────────────────────
# Formato: (latitud, longitud)
# TODAS las claves están normalizadas (sin tildes, minúsculas).
COORDS_FIJAS: dict[str, tuple[float, float]] = {
    # ── Recintos culturales principales (ALTA PRECISIÓN Google Maps) ──
    "teatro guiniguada":                (28.1030,   -15.4160),
    "auditorio alfredo kraus":          (28.1300,   -15.4470),
    "auditorio a. kraus":               (28.1300,   -15.4470),
    "auditorio kraus":                  (28.1300,   -15.4470),
    "alfredo kraus":                    (28.1300,   -15.4470),
    "teatro perez galdos":              (28.1020,   -15.4130),
    "cicca":                            (28.1040,   -15.4150),
    "teatro cuyas":                     (28.106512, -15.418036),
    "sala scala":                       (28.0938,   -15.4168),
    "gran canaria arena":               (28.1137,   -15.4449),
    "edificio miller":                  (28.1396,   -15.4305),

    # ── Espacios municipales / culturales ──
    "museo elder":                      (28.1325,   -15.4345),
    "elder":                            (28.1325,   -15.4345),
    "centro atlantico de arte moderno": (28.1000,   -15.4145),
    "caam":                             (28.1000,   -15.4145),
    "casa de colon":                    (28.1003,   -15.4155),
    "castillo de mata":                 (28.1058,   -15.4195),
    "centro penitenciario las palmas":  (28.083,    -15.400),
    "casa africa":                      (28.1010,   -15.4148),
    "gabinete literario":               (28.1077,   -15.4165),

    # ── Parques y plazas ──
    "parque santa catalina":            (28.1340,   -15.4320),
    "parque san telmo":                 (28.1140,   -15.4270),
    "parque doramas":                   (28.1185,   -15.4295),
    "plaza de la musica":               (28.1310,   -15.4475),
    "plaza de las ranas":               (28.1060,   -15.4165),
    "plaza del pilar":                  (28.1000,   -15.4140),

    # ── Espacios INFECAR / Ferial ──
    "recinto ferial":                   (28.0860,   -15.4530),
    "infecar":                          (28.0860,   -15.4530),

    # ── Salas de conciertos y ocio ──
    "sala miller":                      (28.1335,   -15.4340),
    "paper club":                       (28.1145,   -15.4275),
    "the paper club":                   (28.1145,   -15.4275),
    "la azotea":                        (28.1120,   -15.4250),
    "el sotano":                        (28.1098,   -15.4230),
    "sala insular de teatro":           (28.1008,   -15.4142),
    "canarias en vivo":                 (28.1125,   -15.4310),  # Calle Matagalpa 6
    "calle matagalpa":                  (28.1125,   -15.4310),

    # ── Universidad / Campus ──
    "campus obelisco":                  (28.1020,   -15.4180),
    "campus del obelisco":              (28.1020,   -15.4180),
    "campus universitario de tafira":   (28.0700,   -15.4530),
    "ulpgc":                            (28.0700,   -15.4530),
    "facultad de humanidades":          (28.1020,   -15.4180),
    "salon de actos del edificio de humanidades": (28.1020, -15.4180),

    # ── Deportivos / Grandes recintos ──
    "estadio de gran canaria":          (28.1000,   -15.4560),
    "estadio gran canaria":             (28.1000,   -15.4560),

    # ── Municipios (centros urbanos) ──
    "las palmas de gran canaria":       (28.1235,   -15.4363),
    "las palmas":                       (28.1235,   -15.4363),
    "telde":                            (27.9945,   -15.4165),
    "arucas":                           (28.1200,   -15.5230),
    "galdar":                           (28.1470,   -15.6500),
    "aguimes":                          (27.9060,   -15.4450),
    "ingenio":                          (27.9160,   -15.4360),
    "santa lucia de tirajana":          (27.9120,   -15.5410),
    "san bartolome de tirajana":        (27.9245,   -15.5730),
    "maspalomas":                       (27.7600,   -15.5860),
    "playa del ingles":                 (27.7580,   -15.5730),
    "mogan":                            (27.8850,   -15.7620),
    "puerto de mogan":                  (27.8170,   -15.7660),
    "teror":                            (28.0590,   -15.5470),
    "firgas":                           (28.1070,   -15.5620),
    "valsequillo":                      (27.9830,   -15.4970),
    "vecindario":                       (27.8420,   -15.4380),
    "santa brigida":                    (28.0310,   -15.4720),
    "vega de san mateo":                (28.0100,   -15.5290),
    "artenara":                         (28.0195,   -15.6450),
    "tejeda":                           (27.9945,   -15.6140),
    "moya":                             (28.1115,   -15.5820),
    "guia":                             (28.1390,   -15.6350),
    "san nicolas":                      (27.9870,   -15.7810),
    "agaete":                           (28.1000,   -15.6990),
    "puerto de la luz":                 (28.1400,   -15.4250),

    # ── Genéricos (fallback municipal) ──
    "gran canaria":                     (28.1235,   -15.4363),
}

# Centro de Las Palmas de Gran Canaria (fallback final)
FALLBACK_COORDS = (28.1235, -15.4363)

# Lugares considerados "genéricos" (la IA debería refinar estos)
LUGARES_GENERICOS = {
    "gran canaria", "las palmas", "las palmas de gran canaria",
    "españa", "espana", "canarias", "islas canarias",
    "sin especificar", "",
}


# ─────────────────────────────────────────────────────────────────────
# CAPA 1: Búsqueda en diccionario (coincidencia normalizada)
# ─────────────────────────────────────────────────────────────────────
def _buscar_en_diccionario(lugar: str) -> Optional[tuple[float, float]]:
    """Busca coincidencia normalizada (sin tildes, minúsculas) en el diccionario."""
    lugar_norm = _normalizar(lugar)

    if not lugar_norm:
        return None

    # Coincidencia exacta normalizada
    if lugar_norm in COORDS_FIJAS:
        return COORDS_FIJAS[lugar_norm]

    # Coincidencia parcial: "Auditorio A. Kraus" contiene o está contenido
    for clave, coords in COORDS_FIJAS.items():
        if clave in lugar_norm or lugar_norm in clave:
            return coords

    return None


def es_lugar_generico(lugar: str) -> bool:
    """Devuelve True si el lugar es genérico y debería ser refinado por la IA."""
    return _normalizar(lugar) in LUGARES_GENERICOS


# ─────────────────────────────────────────────────────────────────────
# CAPA 2: Geopy + Nominatim AGRESIVO (cascada de queries)
# ─────────────────────────────────────────────────────────────────────
def _buscar_con_nominatim(lugar: str) -> Optional[tuple[float, float]]:
    """Usa geopy/Nominatim con búsqueda agresiva en cascada.

    Prueba 3 queries en orden:
      1. "{lugar}, Las Palmas de Gran Canaria, España"
      2. "{lugar}, Gran Canaria, España"
      3. "{lugar}, Canarias, España"

    Valida que las coords estén dentro del bounding box de Gran Canaria.
    Siempre devuelve float para evitar bugs en enlaces de Google Maps.
    """
    try:
        from geopy.geocoders import Nominatim

        geocoder = Nominatim(
            user_agent="agenda_cultural_gc_v5",
            timeout=5,
        )

        queries = [
            f"{lugar}, Las Palmas de Gran Canaria, España",
            f"{lugar}, Gran Canaria, España",
            f"{lugar}, Canarias, España",
        ]

        for query in queries:
            try:
                location = geocoder.geocode(query)
            except Exception:
                continue

            if location:
                lat, lon = float(location.latitude), float(location.longitude)
                # Validar bounding box de Gran Canaria
                if 27.5 < lat < 28.3 and -16.0 < lon < -15.2:
                    print(f"      📍 Nominatim: '{lugar}' → ({lat:.4f}, {lon:.4f})")
                    return (lat, lon)

            time.sleep(1.1)  # Respetar rate limit entre queries

        # Ninguna query dio resultado válido
        return None

    except ImportError:
        print("      ⚠️ geopy no instalado. Usando solo diccionario fijo.")
    except Exception as e:
        print(f"      ⚠️ Nominatim error: {e}")

    return None


# ─────────────────────────────────────────────────────────────────────
# Función principal: geolocalizar un lugar
# ─────────────────────────────────────────────────────────────────────
def geolocalizar_lugar(lugar: str) -> tuple[float, float]:
    """Resuelve un nombre de lugar a (latitud, longitud).

    Siempre devuelve una tupla de floats.

    Capas:
      1. Normalizar nombre (sin tildes, minúsculas)
      2. Diccionario fijo de recintos/municipios de Gran Canaria
      3. Nominatim agresivo (3 queries con contexto creciente)
      4. Fallback: centro de Las Palmas de Gran Canaria
    """
    if not lugar or lugar.strip() == "Sin especificar":
        return FALLBACK_COORDS

    # Capa 1: diccionario (con normalización)
    coords = _buscar_en_diccionario(lugar)
    if coords:
        return (float(coords[0]), float(coords[1]))

    # Capa 2: Nominatim agresivo
    coords = _buscar_con_nominatim(lugar)
    if coords:
        return (float(coords[0]), float(coords[1]))

    # Capa 3: fallback
    print(f"      📍 Sin coords para '{lugar}' → usando fallback LPGC")
    return FALLBACK_COORDS


# ─────────────────────────────────────────────────────────────────────
# Pipeline: geolocalizar todos los eventos en la DB
# ─────────────────────────────────────────────────────────────────────
def geolocalizar_eventos() -> dict[str, int]:
    """Rellena latitud/longitud para todos los eventos en la DB.

    Solo procesa eventos que aún no tienen coordenadas.
    Incluye rate-limiting para Nominatim (1 req/seg).

    Returns:
        Dict con estadísticas.
    """
    print("\n🌍 GEOLOCALIZACIÓN DE EVENTOS...")
    print("-" * 40)

    stats = {"procesados": 0, "diccionario": 0, "nominatim": 0, "fallback": 0}

    # Cache para evitar re-geocodificar el mismo lugar
    cache: dict[str, tuple[float, float]] = {}

    with get_session() as session:
        # Solo eventos sin coordenadas
        statement = select(Evento).where(
            (Evento.latitud == None) | (Evento.longitud == None)  # noqa: E711
        )
        eventos = list(session.exec(statement).all())

        if not eventos:
            print("   ✅ Todos los eventos ya tienen coordenadas.")
            return stats

        print(f"   📌 {len(eventos)} eventos sin coordenadas.")

        for evento in eventos:
            lugar = (evento.lugar or "").strip()
            lugar_norm = _normalizar(lugar)

            if lugar_norm in cache:
                lat, lon = cache[lugar_norm]
            else:
                # Intentar diccionario primero
                coords_dict = _buscar_en_diccionario(lugar)
                if coords_dict:
                    lat, lon = coords_dict
                    stats["diccionario"] += 1
                else:
                    # Nominatim (con rate-limiting)
                    coords_nom = _buscar_con_nominatim(lugar)
                    if coords_nom:
                        lat, lon = coords_nom
                        stats["nominatim"] += 1
                        time.sleep(1.1)  # Respetar rate limit de Nominatim
                    else:
                        lat, lon = FALLBACK_COORDS
                        stats["fallback"] += 1

                cache[lugar_norm] = (lat, lon)

            # ── FLOAT EXPLÍCITO en el punto de escritura a DB ──
            # Esto GARANTIZA que evento.latitud/longitud son float
            # y los f-strings de Google Maps nunca se corrompen.
            evento.latitud = float(lat)
            evento.longitud = float(lon)
            session.add(evento)
            stats["procesados"] += 1

        session.commit()

    print(f"\n   📊 Geolocalización completada:")
    print(f"      Procesados:  {stats['procesados']}")
    print(f"      Diccionario: {stats['diccionario']}")
    print(f"      Nominatim:   {stats['nominatim']}")
    print(f"      Fallback:    {stats['fallback']}")

    return stats

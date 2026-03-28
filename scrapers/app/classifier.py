"""
Clasificador inteligente de eventos culturales.

Dual-mode:
  1. LOCAL (default): Clasificación por keywords expandida — sin API, sin coste.
  2. LLM (opcional): Usa Gemini o OpenAI para clasificar por descripción.
     Activar con CLASSIFIER_MODE=llm y GEMINI_API_KEY o OPENAI_API_KEY en .env.

Categorías posibles:
  Música, Teatro, Cine, Danza, Humor, Gastronomía, Deporte, Infantil,
  Formación, Exposición, Carnaval, Otros.
"""

import json
import os
from collections import defaultdict

from openai import OpenAI
import httpx
from sqlmodel import select

from app.database import get_session
from app.models import Evento

# ─────────────────────────────────────────────────────────────────────
# Categorías válidas
# ─────────────────────────────────────────────────────────────────────
CATEGORIAS_VALIDAS = [
    "Música", "Teatro", "Cine", "Danza", "Humor",
    "Gastronomía", "Deporte", "Infantil", "Formación",
    "Exposición", "Carnaval", "Fiesta", "Otros",
]

# ─────────────────────────────────────────────────────────────────────
# Keywords expandidas para clasificación local
# ─────────────────────────────────────────────────────────────────────
_KEYWORDS: dict[str, list[str]] = {
    "Música": [
        "concierto", "concert", "festival", "live", "música", "musica",
        "banda", "rock", "jazz", "pop", "reggae", "rap", "hip hop",
        "sinfón", "orquesta", "ópera", "opera", "recital", "acústico",
        "dj", "techno", "electrónica", "session", "jam", "tour",
        "unplugged", "gira", "canta", "cantante", "coral", "coro",
        "guitarra", "piano", "violín", "flamenco", "salsa", "bachata",
        "reggaeton", "trap", "indie", "metal", "punk", "blues",
        "gospel", "folk", "son cubano", "timba", "bolero", "fado",
    ],
    "Teatro": [
        "teatro", "obra", "escena", "dramaturgia", "monólogo",
        "representación", "compañía", "cia", "cía", "actor", "actriz",
        "tragedia", "comedia dramática", "puesta en escena",
        "sainete", "zarzuela", "musical", "shakespear", "impro",
        "microteatro", "performance", "escénic",
    ],
    "Cine": [
        "cine", "película", "film", "cortometraje", "documental",
        "proyección", "rodaje", "director", "cinema", "cineforum",
        "cine-forum", "largometraje", "animación", "aula de cine",
    ],
    "Danza": [
        "danza", "ballet", "baile", "bailar", "coreografía",
        "contemporánea", "folclore", "folclor", "hip-hop dance",
        "breakdance", "tango", "vals", "sevillanas",
    ],
    "Humor": [
        "humor", "comedia", "monólogo", "stand up", "stand-up",
        "standup", "risa", "cómico", "comedy", "parodia", "sketch",
        "improvisación cómica",
    ],
    "Gastronomía": [
        "gastro", "cocina", "culinari", "cata", "vino", "cerveza",
        "maridaje", "degustación", "showcooking", "food", "chef",
        "tapas", "menú", "receta", "barista", "queso", "aceite",
    ],
    "Deporte": [
        "deporte", "triatlón", "maratón", "carrera", "running",
        "surf", "yoga", "fitness", "torneo", "campeonato",
        "liga", "partido", "fútbol", "basket", "baloncesto",
        "natación", "ciclismo", "senderismo", "trail", "cross",
        "paddle", "tenis", "lucha canaria", "vela",
    ],
    "Infantil": [
        "infantil", "niños", "niñas", "familiar", "familia",
        "títeres", "marioneta", "payaso", "cuentacuentos",
        "cuenta cuento", "bebé", "baby", "kids", "peque",
        "animación infantil", "parque",
    ],
    "Formación": [
        "taller", "curso", "formación", "masterclass", "master class",
        "seminario", "charla", "conferencia", "ponencia", "coloquio",
        "debate", "mesa redonda", "workshop", "congreso", "simposio",
        "clase magistral", "aula", "academia", "aprendizaje",
        "bootcamp", "webinar", "jornada",
    ],
    "Exposición": [
        "exposición", "exposicion", "muestra", "exhibición",
        "galería", "museo", "instalación artística", "retrospectiva",
        "pintura", "escultura", "fotografía", "arte contemporáneo",
        "arte urbano", "artes plásticas", "vernissage",
    ],
    "Carnaval": [
        "carnaval", "gala", "reina", "drag", "murga", "comparsa",
        "cabalgata", "chirigota", "mogollón",
    ],
    "Fiesta": [
        "fiesta", "party", "parties", "after", "verbena", "baile popular",
        "nochevieja", "fin de año", "nochebuena", "halloween", "carnaval party",
        "universitari", "erasmus", "rave", "discoteca", "club", "noche de",
        "celebración", "celebracion", "cumpleaños", "bodas", "gala de",
        "regularización", "regularizacion", "fila 0", "copa", "copas",
        "open bar", "botellón", "botellon", "dj set", "sala de fiestas",
    ],
}


def _clasificar_local(nombre: str, descripcion: str | None, organiza: str) -> str:
    """Clasifica un evento usando keywords expandidas sobre nombre + descripción."""
    texto = f"{nombre} {descripcion or ''}".lower()
    nombre_low = nombre.lower()

    # Puntuación por categoría: contar cuántas keywords coinciden
    scores: dict[str, int] = defaultdict(int)

    for categoria, keywords in _KEYWORDS.items():
        for kw in keywords:
            if kw in texto:
                # Keywords en el nombre pesan 3x, en descripción 1x
                if kw in nombre_low:
                    scores[categoria] += 3
                else:
                    scores[categoria] += 1

    if not scores:
        return "Otros"

    # Categoría con mayor puntuación
    mejor = max(scores, key=scores.get)
    return mejor


# ─────────────────────────────────────────────────────────────────────
# Clasificación con LLM (OpenAI Responses API / Gemini)
# ─────────────────────────────────────────────────────────────────────
_LLM_PROMPT = """Eres un clasificador experto de eventos culturales y de ocio en Gran Canaria.
Clasifica cada evento en UNA SOLA categoría basándote en el título y la descripción.

Categorías y sus criterios:
- Música: conciertos, recitales, festivales de música, actuaciones de bandas, DJs en contexto musical
- Teatro: obras teatrales, monólogos dramáticos, piezas escénicas, musicales
- Cine: proyecciones, ciclos de cine, documentales, cortometrajes
- Danza: ballet, danza contemporánea, flamenco, espectáculos de baile
- Humor: stand-up, comedy, monólogos de humor, espectáculos cómicos
- Gastronomía: catas, showcooking, ferias de alimentación, eventos culinarios
- Deporte: competiciones, carreras, torneos, actividades deportivas
- Infantil: actividades para niños y familias, cuentacuentos, teatro infantil
- Formación: talleres, cursos, conferencias, seminarios, charlas
- Exposición: exposiciones de arte, instalaciones, muestras, inauguraciones
- Carnaval: galas de carnaval, elecciones de reina, murgas, comparsas
- Fiesta: fiestas nocturnas, parties universitarias, eventos de discoteca, verbenas, celebraciones con open bar o DJ de fiesta, eventos de regularización
- Otros: cualquier evento que no encaje claramente en las categorías anteriores

IMPORTANTE: Usa el contexto completo del título y descripción. "Bach íntimo" es Música aunque sea en un teatro.
Responde SOLO con un JSON array donde cada elemento tiene "id" y "categoria". Sin markdown.

Eventos:
{eventos_json}
"""


async def _clasificar_lote_openai(lote: list[dict], api_key: str, model: str) -> dict[int, str]:
    """Envía un lote de eventos a OpenAI (Responses API) y devuelve {{id: categoria}}."""
    resultado: dict[int, str] = {}

    eventos_para_prompt = [
        {"id": e["id"], "nombre": e["nombre"], "descripcion": (e["descripcion"] or "")[:300]}
        for e in lote
    ]

    prompt = _LLM_PROMPT.format(
        eventos_json=json.dumps(eventos_para_prompt, ensure_ascii=False),
    )

    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un clasificador de eventos culturales. Responde solo con JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        text = resp.choices[0].message.content or ""
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        clasificaciones = json.loads(text)

        for item in clasificaciones:
            cat = item.get("categoria", "Otros")
            if cat not in CATEGORIAS_VALIDAS:
                cat = "Otros"
            resultado[item["id"]] = cat

    except Exception as e:
        print(f"      ⚠️ Error OpenAI: {e}")

    return resultado


async def _clasificar_lote_gemini(lote: list[dict], api_key: str) -> dict[int, str]:
    """Envía un lote de eventos a Gemini y devuelve {{id: categoria}}."""
    resultado: dict[int, str] = {}

    eventos_para_prompt = [
        {"id": e["id"], "nombre": e["nombre"], "descripcion": (e["descripcion"] or "")[:300]}
        for e in lote
    ]

    prompt = _LLM_PROMPT.format(
        eventos_json=json.dumps(eventos_para_prompt, ensure_ascii=False),
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        clasificaciones = json.loads(text)

        for item in clasificaciones:
            cat = item.get("categoria", "Otros")
            if cat not in CATEGORIAS_VALIDAS:
                cat = "Otros"
            resultado[item["id"]] = cat

    except Exception as e:
        print(f"      ⚠️ Error Gemini: {e}")

    return resultado


# ─────────────────────────────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────────────────────────────
BATCH_SIZE = 15  # Eventos por lote para LLM


async def categorizar_eventos() -> dict[str, int]:
    """Clasifica TODOS los eventos usando IA (título + descripción) o keywords como fallback.

    Modo se determina por variables de entorno:
      - CLASSIFIER_MODE=llm  + GEMINI_API_KEY → usa Gemini (recomendado, gratis)
      - CLASSIFIER_MODE=llm  + OPENAI_API_KEY → usa OpenAI
      - (default) → clasificación local por keywords

    A diferencia de versiones anteriores, reclasifica TODOS los eventos en cada
    ejecución para corregir pre-clasificaciones incorrectas del scraper.

    Returns:
        Dict con estadísticas: {"procesados": N, "reclasificados": M, "modo": str}
    """
    print("\n" + "=" * 60)
    print("🏷️  CLASIFICACIÓN INTELIGENTE DE EVENTOS (IA para todos)")
    print("=" * 60)

    mode = os.getenv("CLASSIFIER_MODE", "local").lower()
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if mode == "llm" and openai_key:
        print(f"   🤖 Modo: OpenAI Chat API ({openai_model})")
        llm_fn = lambda lote: _clasificar_lote_openai(lote, openai_key, openai_model)
    elif mode == "llm" and gemini_key:
        print("   🤖 Modo: Gemini API (gemini-2.0-flash)")
        llm_fn = lambda lote: _clasificar_lote_gemini(lote, gemini_key)
    else:
        if mode == "llm":
            print("   ⚠️ CLASSIFIER_MODE=llm pero no hay GEMINI_API_KEY ni OPENAI_API_KEY.")
            print("   ↪ Usando clasificación local por keywords.")
        else:
            print("   📝 Modo: Clasificación local (keywords expandidas)")
        llm_fn = None

    stats = {"procesados": 0, "reclasificados": 0, "modo": "local" if not llm_fn else "llm"}

    with get_session() as session:
        # Reclasificar TODOS los eventos, no solo los "Otros"
        # Esto corrige pre-clasificaciones incorrectas del scraper
        statement = select(Evento)
        todos_eventos: list[Evento] = list(session.exec(statement).all())
        eventos_otros = todos_eventos  # alias para compatibilidad con el código siguiente
        print(f"   📊 Total eventos a clasificar: {len(eventos_otros)}")

        if not eventos_otros:
            print("   ✨ No hay eventos en la base de datos.")
            print("=" * 60)
            return stats

        if llm_fn:
            # === Modo LLM: procesar en lotes ===
            lotes = [
                eventos_otros[i:i + BATCH_SIZE]
                for i in range(0, len(eventos_otros), BATCH_SIZE)
            ]
            print(f"   📦 Procesando en {len(lotes)} lotes de hasta {BATCH_SIZE} eventos...")

            for idx, lote in enumerate(lotes):
                print(f"\n   🔄 Lote {idx + 1}/{len(lotes)} ({len(lote)} eventos)...")

                lote_dicts = [
                    {"id": e.id, "nombre": e.nombre, "descripcion": e.descripcion}
                    for e in lote
                ]
                clasificaciones = await llm_fn(lote_dicts)

                for evento in lote:
                    stats["procesados"] += 1
                    nueva_cat = clasificaciones.get(evento.id)
                    if nueva_cat and nueva_cat != "Otros":
                        print(f"      [{nueva_cat}] {evento.nombre[:50]}")
                        evento.estilo = nueva_cat
                        session.add(evento)
                        stats["reclasificados"] += 1
                    else:
                        print(f"      [Otros] {evento.nombre[:50]}")

        else:
            # === Modo local: keywords ===
            for evento in eventos_otros:
                stats["procesados"] += 1
                nueva_cat = _clasificar_local(evento.nombre, evento.descripcion, evento.organiza)

                if nueva_cat != "Otros":
                    print(f"      [{nueva_cat}] {evento.nombre[:60]}")
                    evento.estilo = nueva_cat
                    session.add(evento)
                    stats["reclasificados"] += 1

        session.commit()

    # Resumen
    print(f"\n   📊 RESUMEN DE CLASIFICACIÓN:")
    print(f"      Modo:             {stats['modo']}")
    print(f"      Procesados:       {stats['procesados']}")
    print(f"      Reclasificados:   {stats['reclasificados']}")
    restantes = stats["procesados"] - stats["reclasificados"]
    print(f"      Siguen en 'Otros': {restantes}")
    print("=" * 60)

    return stats

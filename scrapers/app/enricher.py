"""
Enriquecedor de eventos con IA (OpenAI Responses API / Gemini).

v4 – Precisión + Geolocalización:
  - La IA edita la descripción de forma editorial (3 párrafos).
  - La IA extrae precio_num y hora SOLO como fallback si el scraper no los encontró.
  - NUEVO: La IA detecta el recinto específico cuando el campo 'lugar' es genérico
    ("Gran Canaria", "Las Palmas") y devuelve `lugar_corregido`.
"""

import json
import os

from openai import OpenAI
import httpx
from sqlmodel import select

from app.database import get_session
from app.geocoder import es_lugar_generico
from app.models import Evento

# ─────────────────────────────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────────────────────────────
BATCH_SIZE = 10

SYSTEM_PROMPT = """Eres el editor jefe de una agenda cultural digital de Gran Canaria.
Tu trabajo es enriquecer fichas de eventos para que sean atractivas y útiles al público.

Para cada evento recibirás: id, nombre, descripcion_raw, lugar_actual, precio_num_actual, hora_actual.

Debes devolver SOLO un JSON array. Cada elemento debe tener:
- "id": (int) el id del evento
- "descripcion_limpia": (string) Un resumen editorial de exactamente 3 párrafos cortos (máx 500 chars total).
  - Párrafo 1: Qué es el evento y por qué es especial.
  - Párrafo 2: Detalles prácticos (lugar, artistas, programa).
  - Párrafo 3: Llamada a la acción o dato curioso.
  - Si la descripción original es buena, resúmela manteniendo lo esencial.
  - Si tiene "paja" (condiciones legales, textos genéricos de compra), ignórala y redacta algo coherente.
  - Si no hay descripción, genera una breve y atractiva basada en el nombre del evento.
  - Marca con "[Generado por IA]" al final SOLO si has inventado la descripción sin datos reales.
  - Escribe siempre en español.
- "precio_num": (float|null) Solo si encuentras un precio en la descripción que NO esté ya en precio_num_actual. Ejemplos: "Desde 25€" → 25.0, "Gratuito" → 0.0, sin precio → null.
- "hora": (string|null) Solo si encuentras una hora en la descripción que NO esté ya en hora_actual. Formato HH:MM (24h). Si no la ves → null.
- "lugar_corregido": (string|null) MUY IMPORTANTE: Analiza cuidadosamente el nombre y la descripción del evento.
  Si el campo 'lugar_actual' es GENÉRICO (como "Gran Canaria", "Las Palmas", "Las Palmas de Gran Canaria", "España"),
  EXTRAE el nombre del recinto, sala o espacio ESPECÍFICO donde se celebra el evento.
  Ejemplos:
    - "Origen Sala Scala" con lugar="Gran Canaria" → lugar_corregido="Sala Scala"
    - "Concierto en el Auditorio" con lugar="Las Palmas" → lugar_corregido="Auditorio Alfredo Kraus"
    - "Stand-up Comedy Teatro Cuyás" con lugar="Gran Canaria" → lugar_corregido="Teatro Cuyás"
    - "Festival Parque Santa Catalina" con lugar="Las Palmas" → lugar_corregido="Parque Santa Catalina"
    - "Gran Canaria Arena Live" con lugar="Gran Canaria" → lugar_corregido="Gran Canaria Arena"
  Si no puedes determinar un lugar más específico, devuelve null.
  Si el lugar_actual ya es específico (ej: "Teatro Guiniguada"), devuelve null.

IMPORTANTE: NO uses markdown. NO expliques nada fuera del JSON. Solo el array JSON puro."""

USER_PROMPT_TEMPLATE = """Eventos a procesar:
{eventos_json}"""


# ─────────────────────────────────────────────────────────────────────
# Llamadas a LLM
# ─────────────────────────────────────────────────────────────────────
async def _llamar_openai(lote: list[dict], api_key: str, model: str) -> list[dict]:
    """Envía un lote a OpenAI (Responses API) y devuelve la lista de enriquecimientos."""
    prompt_input = USER_PROMPT_TEMPLATE.format(
        eventos_json=json.dumps(lote, ensure_ascii=False)
    )

    try:
        client = OpenAI(api_key=api_key)
        resp = client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            input=prompt_input,
        )

        text = resp.output_text
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)

    except Exception as e:
        print(f"      ⚠️ Error OpenAI: {e}")
        return []


async def _llamar_gemini(lote: list[dict], api_key: str) -> list[dict]:
    """Envía un lote a Gemini y devuelve la lista de enriquecimientos."""
    full_prompt = SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE.format(
        eventos_json=json.dumps(lote, ensure_ascii=False)
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)

    except Exception as e:
        print(f"      ⚠️ Error Gemini: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────────────────────────────
async def enriquecer_eventos() -> dict[str, int]:
    """Enriquece eventos con IA: edita descripciones, corrige lugares, extrae precio/hora.

    Solo procesa eventos donde enriquecido == False.
    """
    print("\n" + "=" * 60)
    print("✨ ENRIQUECIMIENTO EDITORIAL CON IA")
    print("=" * 60)

    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if openai_key:
        provider = "openai"
        print(f"   🤖 Proveedor: OpenAI Responses API ({openai_model})")
    elif gemini_key:
        provider = "gemini"
        print(f"   🤖 Proveedor: Gemini (gemini-2.0-flash)")
    else:
        print("   ⚠️ No se encontró OPENAI_API_KEY ni GEMINI_API_KEY.")
        print("   ↪ Saltando enriquecimiento con IA.")
        print("=" * 60)
        return {"procesados": 0, "enriquecidos": 0, "lugares_corregidos": 0, "sin_api": True}

    stats = {"procesados": 0, "enriquecidos": 0, "lugares_corregidos": 0, "sin_api": False}

    with get_session() as session:
        statement = select(Evento).where(Evento.enriquecido == False)  # noqa: E712
        pendientes: list[Evento] = list(session.exec(statement).all())

        print(f"   📊 Eventos pendientes de enriquecimiento: {len(pendientes)}")

        if not pendientes:
            print("   ✨ Todos los eventos ya fueron enriquecidos previamente.")
            print("=" * 60)
            return stats

        lotes = [
            pendientes[i:i + BATCH_SIZE]
            for i in range(0, len(pendientes), BATCH_SIZE)
        ]
        print(f"   📦 Procesando en {len(lotes)} lotes de hasta {BATCH_SIZE} eventos...")

        for idx, lote in enumerate(lotes):
            print(f"\n   🔄 Lote {idx + 1}/{len(lotes)} ({len(lote)} eventos)...")

            # Preparar datos para la IA (incluye lugar_actual para que refine)
            lote_dicts = [
                {
                    "id": e.id,
                    "nombre": e.nombre,
                    "descripcion_raw": (e.descripcion or "")[:600],
                    "lugar_actual": e.lugar,
                    "precio_num_actual": e.precio_num,
                    "hora_actual": e.hora,
                }
                for e in lote
            ]

            # Llamar al LLM
            if provider == "openai":
                resultados = await _llamar_openai(lote_dicts, openai_key, openai_model)
            else:
                resultados = await _llamar_gemini(lote_dicts, gemini_key)

            # Mapear resultados por id
            resultados_map = {r["id"]: r for r in resultados}

            for evento in lote:
                stats["procesados"] += 1
                enriquecimiento = resultados_map.get(evento.id)

                if not enriquecimiento:
                    evento.enriquecido = True
                    session.add(evento)
                    continue

                # Aplicar descripción limpia
                desc_limpia = enriquecimiento.get("descripcion_limpia")
                if desc_limpia and len(desc_limpia) > 20:
                    evento.descripcion = desc_limpia
                    stats["enriquecidos"] += 1
                    tag = "📝" if "[Generado por IA]" not in desc_limpia else "🤖"
                    print(f"      {tag} {evento.nombre[:55]} → {len(desc_limpia)} chars")

                # Lugar corregido: solo si el actual es genérico y la IA propone algo
                lugar_corregido = enriquecimiento.get("lugar_corregido")
                if lugar_corregido and isinstance(lugar_corregido, str) and len(lugar_corregido) > 2:
                    # Solo aplicar si el lugar actual es genérico
                    if es_lugar_generico(evento.lugar):
                        lugar_anterior = evento.lugar
                        evento.lugar = lugar_corregido.strip()
                        # Resetear coordenadas para que el geocoder las recalcule
                        evento.latitud = None
                        evento.longitud = None
                        stats["lugares_corregidos"] += 1
                        print(f"      📍 {evento.nombre[:40]}: "
                              f"'{lugar_anterior}' → '{evento.lugar}'")

                # Precio: IA como FALLBACK (solo si scraper no encontró)
                if evento.precio_num is None:
                    precio_num = enriquecimiento.get("precio_num")
                    if precio_num is not None:
                        try:
                            evento.precio_num = float(precio_num)
                            print(f"      💰 {evento.nombre[:40]} → {evento.precio_num}€ (IA)")
                        except (ValueError, TypeError):
                            pass

                # Hora: IA como FALLBACK (solo si scraper no encontró)
                if evento.hora is None:
                    hora = enriquecimiento.get("hora")
                    if hora and isinstance(hora, str) and ":" in hora:
                        evento.hora = hora
                        print(f"      🕐 {evento.nombre[:40]} → {evento.hora} (IA)")

                evento.enriquecido = True
                session.add(evento)

        session.commit()

    # Resumen
    print(f"\n   📊 RESUMEN DE ENRIQUECIMIENTO:")
    print(f"      Procesados:         {stats['procesados']}")
    print(f"      Enriquecidos:       {stats['enriquecidos']}")
    print(f"      Lugares corregidos: {stats['lugares_corregidos']}")
    sin_cambio = stats["procesados"] - stats["enriquecidos"]
    print(f"      Sin cambios:        {sin_cambio}")
    print("=" * 60)

    return stats

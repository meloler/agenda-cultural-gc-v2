"""
Limpieza y deduplicación inteligente de eventos en la base de datos.

Utiliza rapidfuzz para comparación fuzzy de nombres y aplica reglas
de fusión para consolidar duplicados cross-fuente.
"""

from collections import defaultdict

from rapidfuzz import fuzz
from sqlmodel import Session, select

from app.database import get_session
from app.models import Evento
from app.geocoder import _normalizar
from app.scrapers._enrichment import es_titulo_generico

# Prioridad de fuentes: a menor índice, mayor fiabilidad del dato.
# Los eventos de fuentes prioritarias se preservan como "maestros".
PRIORIDAD_FUENTE: dict[str, int] = {
    "Auditorio A. Kraus": 1,
    "Teatro Pérez Galdós": 2,
    "CICCA": 3,
    "Teatro Guiniguada": 4,
    "Ticketmaster": 5,
    "Tomaticket": 6,
    "Tickety": 7,
}

# Umbral de similitud por encima del cual dos nombres se consideran el mismo evento
UMBRAL_SIMILITUD = 90


def _puntuacion_maestro(evento: Evento) -> tuple[int, int]:
    """Calcula la puntuación de un evento para decidir el maestro.

    Retorna una tupla (prioridad_fuente, longitud_descripcion) que se usa
    para ordenar: menor prioridad numérica + mayor descripción = mejor candidato.

    La tupla se ordena con: prioridad ASC (fuente mejor), desc_len DESC (más contenido).
    """
    prioridad = PRIORIDAD_FUENTE.get(evento.organiza, 99)
    desc_len = len(evento.descripcion) if evento.descripcion else 0
    # Negamos desc_len para que al ordenar ASC, la más larga quede primero
    return (prioridad, -desc_len)


def ejecutar_limpieza_db() -> dict[str, int]:
    """Analiza la tabla de eventos y detecta/fusiona duplicados cross-fuente.

    Algoritmo:
        1. Extrae todos los eventos y los agrupa por `(fecha_iso, hora, lugar_norm)`.
        2. Dentro de cada grupo, compara nombres con `token_set_ratio`.
        3. Si similitud > UMBRAL_SIMILITUD → fusiona:
           - Maestro: fuente prioritaria + descripción más larga.
           - Duplicados: se eliminan de la DB.

    Returns:
        Dict con estadísticas: {"grupos_analizados", "duplicados_eliminados", "maestros_enriquecidos"}.
    """
    print("\n" + "=" * 60)
    print("🧹 LIMPIEZA DE DUPLICADOS (Cross-Fuente)")
    print("=" * 60)

    stats = {
        "grupos_analizados": 0,
        "duplicados_eliminados": 0,
        "maestros_enriquecidos": 0,
    }

    with get_session() as session:
        # Cargar todos los eventos
        todos: list[Evento] = list(session.exec(select(Evento)).all())
        print(f"   📊 Total eventos en DB: {len(todos)}")

        # Agrupar por fecha_iso, hora y lugar_norm
        grupos: dict[tuple, list[Evento]] = defaultdict(list)
        for ev in todos:
            # Excluir los títulos genéricos de los clusters fuzzy para no absorber válidos
            if es_titulo_generico(ev.nombre):
                continue
            hora_fija = ev.hora if ev.hora else ""
            lugar_norm = _normalizar(ev.lugar) if ev.lugar else ""
            grupo_key = (ev.fecha_iso, hora_fija, lugar_norm)
            grupos[grupo_key].append(ev)

        llaves_grupo = list(grupos.keys())

        print(f"   📅 Grupos únicos de fecha: {len(llaves_grupo)}")
        print("-" * 60)

        ids_a_eliminar: list[int] = []
        maestros_a_actualizar: list[tuple[int, dict]] = []

        for llave in llaves_grupo:
            grupo = grupos[llave]
            if len(grupo) < 2:
                continue

            stats["grupos_analizados"] += 1

            # Comparar todos los pares dentro del grupo
            procesados: set[int] = set()

            for i, ev_a in enumerate(grupo):
                if ev_a.id in procesados:
                    continue

                # Cluster de duplicados para este evento
                cluster: list[Evento] = [ev_a]

                for j in range(i + 1, len(grupo)):
                    ev_b = grupo[j]
                    if ev_b.id in procesados:
                        continue

                    similitud = fuzz.token_set_ratio(
                        ev_a.nombre.lower(),
                        ev_b.nombre.lower(),
                    )

                    if similitud >= UMBRAL_SIMILITUD:
                        cluster.append(ev_b)

                # Solo procesar si hay duplicados reales
                if len(cluster) < 2:
                    continue

                # Marcar todo el cluster como procesado
                for ev in cluster:
                    procesados.add(ev.id)

                # Determinar el maestro: menor prioridad + mayor descripción
                cluster.sort(key=_puntuacion_maestro)
                maestro = cluster[0]
                duplicados = cluster[1:]

                # Log del cluster encontrado
                fecha_label = llave[0] or "Sin fecha"
                hora_label = llave[1] or "Sin hora"
                print(f"\n   🔗 Cluster detectado [{fecha_label} {hora_label}]:")
                print(f"      ⭐ MAESTRO: [{maestro.organiza}] {maestro.nombre}")
                desc_len = len(maestro.descripcion) if maestro.descripcion else 0
                print(f"         Descripción: {desc_len} chars | URL: {maestro.url_venta}")

                for dup in duplicados:
                    dup_desc_len = len(dup.descripcion) if dup.descripcion else 0
                    print(f"      ❌ DUPLICADO: [{dup.organiza}] {dup.nombre}")
                    print(f"         Descripción: {dup_desc_len} chars | URL: {dup.url_venta}")
                    sim = fuzz.token_set_ratio(maestro.nombre.lower(), dup.nombre.lower())
                    print(f"         Similitud: {sim}%")

                # Enriquecer maestro con datos de los duplicados
                enriquecido = False

                for dup in duplicados:
                    # Si el duplicado tiene mejor descripción, copiarla al maestro
                    dup_desc_len = len(dup.descripcion) if dup.descripcion else 0
                    maestro_desc_len = len(maestro.descripcion) if maestro.descripcion else 0
                    if dup_desc_len > maestro_desc_len:
                        maestro.descripcion = dup.descripcion
                        enriquecido = True
                        print(f"      📝 Descripción mejorada con datos de [{dup.organiza}]")

                    # Si el maestro no tiene imagen pero el duplicado sí
                    if not maestro.imagen_url and dup.imagen_url:
                        maestro.imagen_url = dup.imagen_url
                        enriquecido = True
                        print(f"      🖼️ Imagen tomada de [{dup.organiza}]")

                    # Registrar para eliminación
                    ids_a_eliminar.append(dup.id)

                if enriquecido:
                    session.add(maestro)
                    stats["maestros_enriquecidos"] += 1

                stats["duplicados_eliminados"] += len(duplicados)

        # === APLICAR CAMBIOS ===
        print("\n" + "-" * 60)

        if ids_a_eliminar:
            print(f"   🗑️ Eliminando {len(ids_a_eliminar)} duplicados de la DB...")
            for eid in ids_a_eliminar:
                ev = session.get(Evento, eid)
                if ev:
                    session.delete(ev)

            session.commit()
            print(f"   ✅ Limpieza aplicada exitosamente.")
        else:
            print(f"   ✨ No se encontraron duplicados. La DB está limpia.")

    # Resumen final
    print(f"\n   📊 RESUMEN DE LIMPIEZA:")
    print(f"      Grupos de fecha analizados: {stats['grupos_analizados']}")
    print(f"      Duplicados eliminados:      {stats['duplicados_eliminados']}")
    print(f"      Maestros enriquecidos:      {stats['maestros_enriquecidos']}")
    print("=" * 60)

    return stats

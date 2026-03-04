"""
Orquestador principal – Agenda Cultural de Gran Canaria v5.1.
Pipeline de Precisión: Scrapers → Auditor (Deep) → IA → GIS → Sanitize → Excel.

Regla: eventos sin fecha_iso son 'Borrador' y no aparecen en el Excel limpio.
"""

import asyncio
import time
from datetime import datetime, date
import pandas as pd
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from sqlmodel import select as sql_select
from rapidfuzz import fuzz

# Módulos de la aplicación
from app.models import Evento
from app.utils.observability import generar_reporte_observabilidad
from app.auditor import auditar_eventos
from app.classifier import categorizar_eventos
from app.cleaner import ejecutar_limpieza_db
from app.crud import guardar_eventos_db
from app.database import init_db, get_session
from app.enricher import enriquecer_eventos
from app.geocoder import geolocalizar_eventos, _normalizar, es_lugar_generico
from app.scrapers._enrichment import es_titulo_generico

# Scrapers
from app.scrapers.ticketmaster import scrape_ticketmaster_api
from app.scrapers.ticketmaster_web import scrape_ticketmaster_web
from app.scrapers.tomaticket import scrape_tomaticket
from app.scrapers.cultura_canaria import scrape_cultura_canaria
from app.scrapers.tickety import scrape_tickety
from app.scrapers.institucional import scrape_cicca, scrape_guiniguada
from app.scrapers.entradas_com import scrape_entradas_com
from app.scrapers.entrees import scrape_entrees
from app.scrapers.entradas_canarias import scrape_entradas_canarias
from app.scrapers.telde_cultura import scrape_telde_cultura


async def _scrape_ticketmaster_smart(page) -> list[Evento]:
    """Prueba la API primero; si falla o está vacía, usa Web."""
    eventos = await scrape_ticketmaster_api()
    if not eventos:
        print("   🌐 Ticketmaster Fallback: Usando Web Scraper...")
        eventos = await scrape_ticketmaster_web(page)
    return eventos


async def run_all_scrapers() -> list[Evento]:
    """Ejecuta todos los scrapers en paralelo y recopila resultados."""
    all_eventos: list[Evento] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Crear páginas independientes
        page_ticketmaster = await browser.new_page()
        page_auditorio = await browser.new_page()
        page_galdos = await browser.new_page()
        page_cicca = await browser.new_page()
        page_guiniguada = await browser.new_page()
        page_tomaticket = await browser.new_page()
        page_tickety = await browser.new_page()
        page_entradas_com = await browser.new_page()
        page_entrees = await browser.new_page()
        page_entradas_canarias = await browser.new_page()
        page_telde = await browser.new_page()

        # Lanzar en paralelo
        results = await asyncio.gather(
            _scrape_ticketmaster_smart(page_ticketmaster),
            scrape_cultura_canaria(page_auditorio, "https://auditorioalfredokraus.es", "Auditorio A. Kraus"),
            scrape_cultura_canaria(page_galdos, "https://teatroperezgaldos.es", "Teatro Pérez Galdós"),
            scrape_cicca(page_cicca),
            scrape_guiniguada(page_guiniguada),
            scrape_tomaticket(page_tomaticket),
            scrape_tickety(page_tickety),
            scrape_entradas_com(page_entradas_com),
            scrape_entrees(page_entrees),
            scrape_entradas_canarias(page_entradas_canarias),
            scrape_telde_cultura(page_telde),
            return_exceptions=True,
        )

        await browser.close()

    scraper_names = [
        "Ticketmaster Web", "Auditorio A. Kraus", "Teatro Pérez Galdós",
        "CICCA", "Teatro Guiniguada", "Tomaticket", "Tickety",
        "Entradas.com", "Entrées.es", "EntradasCanarias", "TeldeCultura",
    ]

    fallos_scraper = 0

    for name, result in zip(scraper_names, results):
        if isinstance(result, Exception):
            print(f"   🚨 ALERTA DevOps: {name} falló críticamente (Exception): {result}")
            fallos_scraper += 1
        elif isinstance(result, list):
            if len(result) == 0:
                print(f"   🚨 ALERTA DevOps: {name} extrajo 0 eventos. (¿Cambio de DOM o IP bloqueada?)")
            all_eventos.extend(result)
        else:
            print(f"   ⚠️ {name} devolvió un resultado inesperado: {type(result)}")
            fallos_scraper += 1

    error_ratio = (fallos_scraper / len(scraper_names)) * 100
    if error_ratio > 30:
        print(f"\n🔥 ALERTA DevOps: Ratio de error excepcionalmente alto: {error_ratio:.1f}% de las fuentes fracasaron.\n")

    return all_eventos


def generar_enlace_mapa_seguro(row):
    """
    Genera un enlace de Google Maps estándar y seguro.
    Filtra coordenadas que no estén en Canarias (Lat 27-29) para evitar errores.
    """
    lat = row.get("latitud")
    lon = row.get("longitud")
    
    if lat is None or lon is None:
        return ""

    try:
        lat_f = float(lat)
        lon_f = float(lon)
        
        # Filtro de Seguridad Geográfica:
        # Canarias está aprox entre Lat 27.0 y 29.5
        # Si la latitud es 128 (bug anterior) o 0, se descarta.
        if not (27.0 < lat_f < 30.0): 
            return "" 

        # Formato Estándar Google Maps (Universal)
        return f"https://www.google.com/maps?q={lat_f},{lon_f}"
        
    except (ValueError, TypeError):
        return ""


async def main():
    """Punto de entrada principal."""
    start_time = time.time()
    load_dotenv()

    print("=" * 60)
    print("START: AGENDA CULTURAL GC - v5.1 (Pipeline de Precision + Deep Scrape)")
    print("=" * 60)

    # 1. Inicializar DB
    init_db()

    # 2. Scraping
    todos = await run_all_scrapers()

    if not todos:
        print("\n❌ No se encontraron eventos.")
        return

    # 3. Guardar en DB (Upsert)
    guardar_eventos_db(todos)
    print("🗄️ Base de datos actualizada (Sincronización completada)")

    # 4. Limpieza básica en DB
    ejecutar_limpieza_db()

    # 4b. Marcar eventos pasados como "past" en lugar de eliminarlos
    actualizar_estado_eventos()

    # 5. Auditoría (Detective v2) - Aquí es donde se arreglan los "Gran Canaria"
    await auditar_eventos()

    import os
    # 6. Clasificación IA
    if os.getenv("SKIP_AI", "false").lower() == "true":
        print("\n⏩ Saltando Clasificación y Enriquecimiento IA (Modo Test)")
    else:
        await categorizar_eventos()

        # 7. Enriquecimiento IA
        await enriquecer_eventos()

    # 8. Geolocalización (GIS)
    geolocalizar_eventos()

    # === Generar Excel desde la DB ===
    print("\n📊 Generando Excel Final...")
    with get_session() as session:
        todos_db = list(session.exec(sql_select(Evento)).all())

    if not todos_db:
        print("\n❌ No hay eventos en la DB tras la limpieza.")
        return

    df = pd.DataFrame([e.model_dump() for e in todos_db])

    # Filtros de exclusión (Redes sociales)
    df = df[~df["nombre"].str.contains("Youtube|Facebook|Instagram", case=False, na=False)]
    df = df[~df["url_venta"].str.contains("youtube|facebook|twitter", case=False, na=False)]

    # ===================================================================
    # SANITIZACIÓN DE DATOS (v5.1 Fixes)
    # ===================================================================
    pre_sanitize = len(df)

    # 1️⃣ Títulos basura: len < 3 (ej: "Dr.", "2", "A") y patrones irregulares
    import re
    def es_titulo_basura(t: str) -> bool:
        t = (t or "").strip()
        low = t.lower()
        if low in {"ext", "nan", "none", "null", ""}: return True
        if len(t) < 2: return True  # titles like "BEBE" or "UB40", "O" are allowed
        if len(t) >= 110: return True
        if re.search(r"\b\d{3}\b.*\b\d{3}\b", t): return True
        if t.endswith("..."): return True
        return False

    # En vez de eliminarlos, los mandamos a 'Borradores' (staging) para no publicarlos
    df.loc[df["nombre"].apply(es_titulo_basura), "fecha_iso"] = None

    # 1.2️⃣ Canonical Title Normalizer (User-Facing)
    from app.utils.text_processing import normalizar_titulo_export, limpiar_lugar

    df["nombre"] = df["nombre"].apply(normalizar_titulo_export)

    # 1.5️⃣ Sanitización y Alias Resolution de lugar
    df["lugar"] = df["lugar"].apply(limpiar_lugar)

    # 2️⃣ Precios absurdos: > 300€ se consideran error de año (2025/2026)
    # Convertimos a numérico forzoso por si acaso
    df["precio_num"] = pd.to_numeric(df["precio_num"], errors='coerce')
    df.loc[df["precio_num"] > 300, "precio_num"] = None

    # 2.2️⃣ QA Gate: Hora vacía (solo en eventos confirmados)
    # Nota: muchos eventos culturales (exposiciones, ferias) no tienen hora fija.
    # Umbral alto (25%) para no bloquear; solo se alerta para monitoreo.
    df_conf = df[df["fecha_iso"].notna()]
    if len(df_conf) > 0:
        vacias = df_conf["hora"].isna() | (df_conf["hora"].astype(str).str.strip() == "") | (df_conf["hora"].astype(str).str.lower().isin(["nan", "none", "<na>"]))
        pct_hora_vacia = vacias.mean() * 100
        print(f"   📊 QA Hora vacía en confirmados: {pct_hora_vacia:.1f}%")
        if pct_hora_vacia > 25.0:
            print(f"\n🔥 ALERTA DevOps: hora vacía en confirmados {pct_hora_vacia:.1f}% > 25%. Revisar scrapers de hora.")

    # 2.5️⃣ QA Gate: Títulos genéricos (P0)
    df["_es_generico_titulo"] = df["nombre"].apply(lambda x: es_titulo_generico(str(x)))
    if len(df) > 0:
        generic_count = df["_es_generico_titulo"].sum()
        generic_ratio = (generic_count / len(df)) * 100
        if generic_count > 0:
            print(f"   📊 QA Títulos Genéricos detectados: {generic_count} ({generic_ratio:.1f}%)")
        if generic_ratio > 5.0:
            print(f"\n🔥 ALERTA P0 DevOps FULL STOP: Demasiados títulos genéricos ({generic_ratio:.1f}% > 5%). Abortando exportación para no corromper Excel/DB.\n")
            return
            
    # En vez de eliminarlos, los mandamos a 'Borradores'
    df.loc[df["_es_generico_titulo"], "fecha_iso"] = None

    # 2.8️⃣ Política temporal: Recortar pasados (agenda es futura)
    today_iso = date.today().isoformat()
    df = df[(df["fecha_iso"].isna()) | (df["fecha_iso"] >= today_iso)]

    # 3️⃣ Smart Deduplication V3 (2-Phase Cross-Source)
    # P0-C fix: clave broad sin lugar/hora (varían entre fuentes)
    df["_titulo_norm"] = df["nombre"].apply(lambda x: _normalizar(str(x)))
    df["_lugar_norm"] = df["lugar"].apply(lambda x: _normalizar(str(x)) if pd.notna(x) else "")
    df["_hora_norm"] = df["hora"].fillna("")
    df["_es_generico_lugar"] = df["lugar"].apply(lambda x: es_lugar_generico(str(x)))
    df["_len_desc"] = df["descripcion"].str.len().fillna(0)

    df = df.sort_values(
        by=["_titulo_norm", "_es_generico_lugar", "_len_desc"],
        ascending=[True, True, False] # False (Específico) primero, luego Desc más larga
    )
    
    # 3.1️⃣ Dedupe SAME-SOURCE estricto (misma fuente, misma URL/sesión, misma fecha/hora)
    df = df.drop_duplicates(subset=["organiza", "url_venta", "fecha_iso", "_hora_norm"], keep="first")
    
    # 3.5️⃣ Dedupe CROSS-SOURCE en 2 fases (P0-C fix)
    PREF = {"Ticketmaster": 100, "EntradasCanarias": 90, "Tickety": 80, "Tomaticket": 70, "CICCA": 65, "Teatro Guiniguada": 65, "Entrées.es": 40}

    def quality_score(r):
        s = PREF.get(r["organiza"], 50)
        s += 10 if pd.notna(r["hora"]) and str(r["hora"]).strip() else 0
        s += 10 if pd.notna(r["precio_num"]) else 0
        # P0-C fix: premiar lugar ESPECÍFICO (+20) vs genérico (+2) vs vacío (+0)
        if pd.notna(r["lugar"]) and str(r["lugar"]).strip():
            if not es_lugar_generico(str(r["lugar"])):
                s += 20  # Lugar específico = mucho más valioso
            else:
                s += 2   # "Gran Canaria" es apenas mejor que nada
        # Premiar descripción larga (hasta +10)
        desc_len = len(str(r.get("descripcion", "") or ""))
        s += min(desc_len // 100, 10)
        return s

    def normalizar_titulo(t: str) -> str:
        """Normaliza título para deduplicación cross-source.
        
        P1-C fix: stopwords ordenadas de mayor a menor, sin eliminar
        'tour'/'concierto'/'gira' que son parte de la identidad del evento.
        """
        if pd.isna(t) or not t: return ""
        import unicodedata
        t = str(t).lower().strip()
        t = unicodedata.normalize("NFKD", t)
        t = "".join(c for c in t if not unicodedata.combining(c))
        # Normalizar '&' → 'y' para evitar falsos negativos (Fito & → Fito y)
        t = t.replace("&", "y")
        # Stopwords ordenadas de mayor a menor longitud (evita matches parciales)
        stopwords = sorted([
            "en las palmas de gran canaria", "en gran canaria", "en las palmas",
            "entradas para", "tickets for",
            "25/26", "2025", "2026",
        ], key=len, reverse=True)
        for w in stopwords:
            t = t.replace(w, "")
        t = re.sub(r'[^a-z0-9\s]', '', t)
        return re.sub(r'\s+', ' ', t).strip()

    def _hora_to_minutes(hora: str) -> int:
        """Convierte '20:30' a minutos desde medianoche. '' → -999."""
        try:
            if not hora or hora in ("", "nan", "None", "<NA>"):
                return -999
            parts = str(hora).split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return -999

    df["_canon"] = df["nombre"].apply(normalizar_titulo)
    df["_score"] = df.apply(quality_score, axis=1)
    
    # ─── Fase 1: Fuzzy clustering por fecha + título similar (≥82%) ───
    FUZZY_THRESHOLD = 82  # ratio mínimo para considerar mismo evento
    
    def _fuzzy_cluster(canons: list[str]) -> list[int]:
        """Asigna un cluster_id a cada canon.
        
        Usa max(ratio, token_set_ratio) para detectar casos donde un título
        es subconjunto de otro (ej: 'Carles Sans' vs 'Carles Sans - Por Fin Me Voy').
        """
        clusters = []  # list of (cluster_id, representative_canon)
        assignments = []
        for canon in canons:
            matched = False
            for cid, rep in clusters:
                # token_set_ratio detecta subconjuntos de tokens
                score = max(fuzz.ratio(canon, rep), fuzz.token_set_ratio(canon, rep))
                if score >= FUZZY_THRESHOLD:
                    assignments.append(cid)
                    matched = True
                    break
            if not matched:
                new_id = len(clusters)
                clusters.append((new_id, canon))
                assignments.append(new_id)
        return assignments
    
    # Agrupar por fecha, luego fuzzy-cluster dentro de cada fecha
    df["_fuzzy_group"] = -1
    global_group = 0
    for fecha, fecha_group in df.groupby("fecha_iso", sort=False):
        canons = fecha_group["_canon"].tolist()
        local_clusters = _fuzzy_cluster(canons)
        for idx, local_cid in zip(fecha_group.index, local_clusters):
            df.loc[idx, "_fuzzy_group"] = global_group + local_cid
        global_group += max(local_clusters, default=-1) + 1
    
    # Aggregate sources for traceability
    grouped_sources = df.groupby("_fuzzy_group")["organiza"].apply(
        lambda x: " + ".join(sorted(set(x)))
    ).reset_index(name="merged_from_sources")
    
    # Fase 2: Dentro de cada fuzzy-group, sub-agrupar por distancia horaria
    # Si dos filas difieren en ≥2h, son sesiones distintas (matinée vs noche)
    # PERO: si comparten el MISMO lugar concreto → fusionar siempre (misma función)
    # PERO: registros con lugar genérico fuerzan merge (su hora no es fiable)
    keep_indices = []
    for fuzzy_gid, group in df.groupby("_fuzzy_group", sort=False):
        if len(group) == 1:
            keep_indices.append(group.index[0])
            continue
        
        # Detectar si todos los registros del grupo comparten un lugar concreto
        lugares = group["lugar"].apply(lambda x: str(x).strip().lower() if pd.notna(x) else "").tolist()
        lugares_concretos = [l for l in lugares if l and not es_lugar_generico(l)]
        # Si hay ≥2 registros con el mismo lugar concreto, fusionar todo el grupo
        mismo_lugar = (len(lugares_concretos) >= 2 and len(set(lugares_concretos)) == 1)
        
        if mismo_lugar:
            # Mismo evento, distintas funciones → quedarnos con el mejor
            best_idx = max(group.index, key=lambda i: df.loc[i, "_score"])
            keep_indices.append(best_idx)
            continue
        
        # Sub-agrupar por cercanía horaria (±2h = mismo evento)
        subgroups = []  # list of {"indices": [...], "horas": [...]}
        for idx, row in group.iterrows():
            hora_min = _hora_to_minutes(str(row["_hora_norm"]))
            # Fix duplicados residuales: lugar genérico → hora desconocida
            # para que siempre se fusione con otros registros del mismo evento
            if es_lugar_generico(str(row.get("lugar", ""))):
                hora_min = -999
            matched = False
            for sg in subgroups:
                # -999 (sin hora o genérico) siempre se agrupa con cualquiera
                if hora_min == -999 or any(
                    h == -999 or abs(hora_min - h) < 120 for h in sg["horas"]
                ):
                    sg["indices"].append(idx)
                    sg["horas"].append(hora_min)
                    matched = True
                    break
            if not matched:
                subgroups.append({"indices": [idx], "horas": [hora_min]})
        
        # De cada sub-grupo, quedarnos con el de mayor score
        for sg in subgroups:
            best_idx = max(sg["indices"], key=lambda i: df.loc[i, "_score"])
            keep_indices.append(best_idx)
    
    df = df.loc[keep_indices]
    
    # Unir la trazabilidad de fuentes combinadas
    df = df.merge(grouped_sources, on="_fuzzy_group", how="left")

    # ─── QA Gates reforzados (P0-F) ───
    # QA: Ratio de eventos sin fecha_iso (demasiados borradores = scraper roto)
    total_pre_split = len(df)
    sin_fecha_count = df["fecha_iso"].isna().sum()
    if total_pre_split > 0:
        pct_sin_fecha = (sin_fecha_count / total_pre_split) * 100
        print(f"   📊 QA fecha_iso vacía: {sin_fecha_count} ({pct_sin_fecha:.1f}%)")
        if pct_sin_fecha > 40:
            raise RuntimeError(
                f"QA FAIL: {pct_sin_fecha:.1f}% de eventos SIN fecha_iso > 40%. "
                f"Probable fallo masivo de parseo de fechas. Abortando."
            )

    # QA: Demasiados lugares genéricos
    genericos_count = df["lugar"].apply(lambda x: es_lugar_generico(str(x))).sum()
    if total_pre_split > 0:
        pct_generico = (genericos_count / total_pre_split) * 100
        print(f"   📊 QA Lugares Genéricos: {genericos_count} ({pct_generico:.1f}%)")
        if pct_generico > 60:
            print(f"\n🔥 ALERTA P0: {pct_generico:.1f}% de lugares son genéricos. "
                  f"Revisión manual recomendada antes de publicar.")

    # QA: Detección de lote basura (título repetido > 5 veces)
    nombre_counts = df["nombre"].value_counts()
    if len(nombre_counts) > 0:
        max_reps = nombre_counts.iloc[0]
        nombre_top = nombre_counts.index[0]
        if max_reps > 5:
            print(f"   🚨 QA ALERTA: Título '{nombre_top}' aparece {max_reps} veces. "
                  f"Probable scraper enloquecido.")
            if max_reps > 15:
                raise RuntimeError(
                    f"QA FAIL: '{nombre_top}' repetido {max_reps} veces. "
                    f"Abortando exportación."
                )

    df = df.drop(columns=["_titulo_norm", "_lugar_norm", "_hora_norm", "_es_generico_lugar", "_len_desc", "_es_generico_titulo", "_canon", "_score"])

    post_sanitize = len(df)
    if pre_sanitize != post_sanitize:
        eliminados = pre_sanitize - post_sanitize
        drop_ratio = (eliminados / pre_sanitize) * 100
        print(f"   🧹 Sanitización: {pre_sanitize} → {post_sanitize} eventos (-{eliminados} eliminados)")
        if drop_ratio >= 60:
            print(f"   🚨 ALERTA DevOps: Caída repentina de calidad. Más del {drop_ratio:.1f}% de los datos se eliminó.")

    # 4️⃣ Generación de Mapa Seguro
    df["ver_mapa"] = df.apply(generar_enlace_mapa_seguro, axis=1)

    # === Exportación UX (P2) ===
    # 1. Precio desconocido -> "Consultar" (en DB quedará Null transparentemente por script de upload)
    df["precio_num"] = df["precio_num"].fillna("Consultar")
    # 2. Hora desconocida -> "Hora por confirmar"
    df["hora"] = df["hora"].replace(["", "nan", "None", "<NA>", "NaN"], pd.NA).fillna("Hora por confirmar")
    # 3. Lugar por defecto -> "Recinto por confirmar" (mejor que "Sin especificar")
    df["lugar"] = df["lugar"].replace(["Sin especificar", None, "", "nan", "NaN"], "Recinto por confirmar")
    # 4. Imagen inválida: Limpieza extrema (rechazar data URIs o paths rotos)
    def clean_img_ux(url):
        u = str(url).strip()
        if not u.startswith("http") or len(u) < 15:
            return None
        return u
    df["imagen_url"] = df["imagen_url"].apply(clean_img_ux)

    # === Split Confirmados vs Borradores ===
    df_confirmados = df[df["fecha_iso"].notna()].copy()
    df_borradores = df[df["fecha_iso"].isna()].copy()

    df_confirmados = df_confirmados.sort_values(by="fecha_iso", na_position="last")

    columnas_excel = {
        "nombre": "Evento",
        "lugar": "Lugar",
        "fecha_iso": "Fecha",
        "hora": "Hora",
        "precio_num": "Precio (€)",
        "estilo": "Categoría",
        "organiza": "Fuente",
        "url_venta": "URL",
        "imagen_url": "Imagen",
        "descripcion": "Descripción",
        "ver_mapa": "Ver en Mapa",
        "merged_from_sources": "Fuentes Combinadas",
    }

    # Excel Final Limpio
    filename_limpia = "agenda_cultural_LIMPIA.xlsx"
    df_export = df_confirmados[list(columnas_excel.keys())].rename(columns=columnas_excel)
    df_export.to_excel(filename_limpia, index=False)
    
    print(f"\n✅ EXCEL GENERADO: {filename_limpia}")
    print(f"   📅 Eventos confirmados: {len(df_confirmados)}")
    
    if len(df_borradores) > 0:
        filename_borradores = "agenda_cultural_BORRADORES.xlsx"
        df_borr_export = df_borradores[list(columnas_excel.keys())].rename(columns=columnas_excel)
        df_borr_export.to_excel(filename_borradores, index=False)
        print(f"   ⚠️ Eventos sin fecha (Borradores): {len(df_borradores)}")

    # 10. Reporte Final de Observabilidad (KPIs & Regression Logs)
    elapsed_time = time.time() - start_time
    generar_reporte_observabilidad(df_confirmados, df_borradores, elapsed_time)


def actualizar_estado_eventos():
    """Marca como 'past' los eventos con fecha_iso anterior a hoy para conservar el histórico."""
    hoy = str(date.today())
    print(f"\n🏷️ Actualizando estado a 'past' para eventos anteriores a {hoy}...")
    with get_session() as session:
        pasados = list(session.exec(
            sql_select(Evento).where(
                Evento.fecha_iso < hoy, 
                Evento.fecha_iso.is_not(None), 
                Evento.estado != "past"
            )
        ).all())
        if pasados:
            for ev in pasados:
                ev.estado = "past"
                session.add(ev)
            session.commit()
            print(f"   ✅ {len(pasados)} eventos marcados como 'past' (Histórico conservado).")
        else:
            print("   ✨ No hay eventos para actualizar. Todo al día.")


if __name__ == "__main__":
    asyncio.run(main())
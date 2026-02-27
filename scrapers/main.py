"""
Orquestador principal – Agenda Cultural de Gran Canaria v5.1.
Pipeline de Precisión: Scrapers → Auditor (Deep) → IA → GIS → Sanitize → Excel.

Regla: eventos sin fecha_iso son 'Borrador' y no aparecen en el Excel limpio.
"""

import asyncio
from datetime import datetime, date
import pandas as pd
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from sqlmodel import select as sql_select

# Módulos de la aplicación
from app.models import Evento
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
    def es_titulo_basura(t) -> bool:
        t = (str(t) if pd.notna(t) else "").strip()
        low = t.lower()
        if low in {"ext", "nan", "none", "null", ""}: return True
        if len(t) <= 4: return True
        if len(t) >= 110: return True
        if re.search(r"\b\d{3}\b.*\b\d{3}\b", t): return True
        if t.endswith("..."): return True
        return False

    df = df[~df["nombre"].apply(es_titulo_basura)]

    # 1.5️⃣ Sanitización de lugar
    def limpiar_lugar(lugar) -> str | None:
        l = (str(lugar) if pd.notna(lugar) else "").strip()
        if not l: return None
        leak_tokens = ["paseo nocturno", "prepárate", "descubre", "que no olvidarás", "la cara más natural", "calle y los"]
        if len(l) > 70: return None
        if any(tok in l.lower() for tok in leak_tokens): return None
        return l or None

    df["lugar"] = df["lugar"].apply(limpiar_lugar)

    # 2️⃣ Precios absurdos: > 300€ se consideran error de año (2025/2026)
    # Convertimos a numérico forzoso por si acaso
    df["precio_num"] = pd.to_numeric(df["precio_num"], errors='coerce')
    df.loc[df["precio_num"] > 300, "precio_num"] = None

    # 2.2️⃣ QA Gate: Hora vacía
    pct_hora_vacia = df["hora"].isna().mean() * 100
    if len(df) > 0 and pct_hora_vacia > 25.0:
        print(f"\n🔥 ALERTA P0 DevOps FULL STOP: Demasiados eventos sin hora ({pct_hora_vacia:.1f}% > 25%). Abortando exportación.\n")
        return

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
            
    # Limpiamos preventivamente los que hayan pasado (si <= 5%)
    df = df[~df["_es_generico_titulo"]]

    # 2.8️⃣ Política temporal: Recortar pasados (agenda es futura)
    today_iso = date.today().isoformat()
    df = df[(df["fecha_iso"].isna()) | (df["fecha_iso"] >= today_iso)]

    # 3️⃣ Smart Deduplication V2 (Clave compuesta)
    # Priorizamos: 1. Lugar Específico, 2. Descripción más larga
    df["_titulo_norm"] = df["nombre"].apply(lambda x: _normalizar(str(x)))
    df["_lugar_norm"] = df["lugar"].apply(lambda x: _normalizar(str(x)) if pd.notna(x) else "")
    df["_hora_norm"] = df["hora"].fillna("")
    df["_es_generico_lugar"] = df["lugar"].apply(lambda x: es_lugar_generico(str(x)))
    df["_len_desc"] = df["descripcion"].str.len().fillna(0)

    df = df.sort_values(
        by=["_titulo_norm", "_es_generico_lugar", "_len_desc"],
        ascending=[True, True, False] # False (Específico) primero, luego Desc más larga
    )
    
    # Clave fuerte para evitar fusionar eventos distintos el mismo día
    df = df.drop_duplicates(subset=["_titulo_norm", "fecha_iso", "_lugar_norm", "_hora_norm"], keep="first")

    # 3.5️⃣ Deduplicación de consolidación multi-fuente (canonical+fecha)
    PREF = {"Ticketmaster": 100, "EntradasCanarias": 90, "Tickety": 80, "Tomaticket": 70, "CICCA": 65, "Teatro Guiniguada": 65, "Entrées.es": 40}

    def quality_score(r):
        s = PREF.get(r["organiza"], 50)
        s += 10 if pd.notna(r["hora"]) and str(r["hora"]).strip() else 0
        s += 10 if pd.notna(r["precio_num"]) else 0
        s += 10 if pd.notna(r["lugar"]) and str(r["lugar"]).strip() else 0
        return s

    df["_canon"] = df["nombre"].apply(lambda x: _normalizar(str(x)))
    df["_score"] = df.apply(quality_score, axis=1)
    df = df.sort_values(["_canon", "fecha_iso", "_score"], ascending=[True, True, False])
    df = df.drop_duplicates(subset=["_canon", "fecha_iso"], keep="first")

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

    # === Exportación ===
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
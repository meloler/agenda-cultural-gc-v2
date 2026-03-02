import json
import os
from datetime import datetime
import pandas as pd

METRICS_FILE = "run_metrics.json"

def generar_reporte_observabilidad(df_confirmados: pd.DataFrame, df_borradores: pd.DataFrame, elapsed_time: float):
    """
    Genera un log estructurado (KPIs) y comprueba regresiones respecto a la corrida anterior.
    """
    total_confirmados = len(df_confirmados)
    total_borradores = len(df_borradores)
    total_eventos = total_confirmados + total_borradores

    if total_eventos == 0:
        print("\n📊 OBSERVABILITY: No hay eventos para analizar.")
        return

    # Distribución por fuente (combinada)
    df_all = pd.concat([df_confirmados, df_borradores])
    source_counts = df_all["organiza"].value_counts().to_dict()

    # Cálculo avanzado de vacíos en confirmados (hora, precio)
    if total_confirmados > 0:
        hora_vacia_count = df_confirmados["hora"].isin(["Hora por confirmar", None, ""]).sum()
        precio_vacio_count = df_confirmados["precio_num"].isin(["Consultar", None, ""]).sum()
        
        pct_hora_vacia = (hora_vacia_count / total_confirmados) * 100
        pct_precio_vacio = (precio_vacio_count / total_confirmados) * 100
    else:
        pct_hora_vacia = 0.0
        pct_precio_vacio = 0.0

    current_metrics = {
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed_time, 2),
        "total_eventos": total_eventos,
        "totales_confirmados": total_confirmados,
        "totales_borradores": total_borradores,
        "pct_hora_vacia_en_conf": round(pct_hora_vacia, 2),
        "pct_precio_vacio_en_conf": round(pct_precio_vacio, 2),
        "distribucion_fuentes": source_counts
    }

    print("\n" + "="*50)
    print("📈 OBSERVABILITY & REGRESSION REPORT")
    print("="*50)
    print(f"⏱️  Tiempo ejecución: {current_metrics['elapsed_seconds']}s")
    print(f"📦 Total Eventos:   {current_metrics['total_eventos']} ({current_metrics['totales_confirmados']} confirmados, {current_metrics['totales_borradores']} borradores)")
    print(f"🕒 Faltan Horas:    {current_metrics['pct_hora_vacia_en_conf']}%")
    print(f"💰 Faltan Precios:  {current_metrics['pct_precio_vacio_en_conf']}%")
    print("\n📊 Origen de Datos:")
    for k, v in source_counts.items():
        print(f"   - {k}: {v}")

    # Comprobar Regresiones si existe run_metrics anterior
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                prev_metrics = json.load(f)
            
            print("\n🔍 ANÁLISIS DE REGRESIONES:")
            diff_total = current_metrics["total_eventos"] - prev_metrics.get("total_eventos", 0)
            if diff_total < 0:
                print(f"   🚨 ALERTA: Caída de volumen total ({diff_total} eventos). Posible fallo en scraper.")
            else:
                print(f"   ✅ Volumen estacional: {diff_total:+} eventos frente a iteración anterior.")

            diff_hora = current_metrics["pct_hora_vacia_en_conf"] - prev_metrics.get("pct_hora_vacia_en_conf", 0)
            if diff_hora > 5.0:
                print(f"   🚨 ALERTA: Degradación extrema de calidad. Horas vacías suben un {diff_hora:+}%")
            else:
                print(f"   ✅ Calidad Hora QA: estable ({diff_hora:+}%)")

            for src in current_metrics["distribucion_fuentes"].keys():
                prev_src = prev_metrics.get("distribucion_fuentes", {}).get(src, 0)
                curr_src = current_metrics["distribucion_fuentes"].get(src, 0)
                if curr_src == 0 and prev_src > 5:
                     print(f"   💀 CRÍTICO: Fuente '{src}' ha colapsado a 0. ¡Revisar urgente!")
                elif curr_src < (prev_src * 0.4):
                     print(f"   ⚠️ WARNING: Caída >60% en '{src}' ({prev_src} -> {curr_src}).")

        except Exception as e:
            print(f"   ⚠️ Error leyendo métricas previas: {e}")
    else:
        print("\n🔍 ANÁLISIS DE REGRESIONES: No hay histórico anterior.")

    # Guardar estado actual
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(current_metrics, f, indent=4)
        
    print("\n💾 [INFO] Métricas estructuradas guardadas en run_metrics.json")
    print("="*50 + "\n")

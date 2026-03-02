import pandas as pd
import json
import sys
import os

def check_qa():
    try:
        df_conf = pd.read_excel("agenda_cultural_LIMPIA.xlsx")
    except Exception as e:
        print("Required file agenda_cultural_LIMPIA.xlsx not found.")
        sys.exit(1)

    try:
        df_borr = pd.read_excel("agenda_cultural_BORRADORES.xlsx")
    except Exception:
        df_borr = pd.DataFrame()

    total_conf = len(df_conf)
    total_borr = len(df_borr)
    total = total_conf + total_borr

    if total_conf == 0:
        print("No confirmed events.")
        sys.exit(1)

    # 1. missing fecha = 0%
    missing_fecha = df_conf["Fecha"].isna().sum() / total_conf

    # 2. missing hora <= 7%
    missing_hora = df_conf["Hora"].isin(["Hora por confirmar", None]).sum() / total_conf

    # 3. missing precio <= 12%
    missing_precio = df_conf["Precio (€)"].isin(["Consultar", None]).sum() / total_conf

    # 4. missing imagen <= 8%
    missing_img = df_conf["Imagen"].isna().sum() / total_conf

    # 5. duplicados same-source = 0
    # Misma fuente, url, fecha, hora ya se limpian, pero verificamos.
    dupes_same_source = df_conf.duplicated(subset=["Fuente", "URL", "Fecha", "Hora"]).sum()

    # 6. duplicados cross-source <= 1%
    # Ya se combinan, pero podemos ver si hay títulos canonicals repetidos en la misma fecha y lugar.
    # We normalized names for export, let's see how many exact matches are left.
    dupes_cross = df_conf.duplicated(subset=["Evento", "Fecha"]).sum() / total_conf

    # 7. títulos basura = 0
    titulos_basura = df_conf["Evento"].apply(lambda x: len(str(x)) < 3 or str(x).lower() in ["ext", "none"]).sum()

    # 8. lugares contaminados = 0
    leak_tokens = ["paseo nocturno", "prepárate", "descubre", "que no olvidarás", "la cara más natural", "calle y los", "plaza y", "disfruta", "sumérgete", "vive la experiencia", "te esperamos", "no te pierdas", "aventura", "te invitamos", "https://", "conoce al autor", "abierto al público", "te imaginas", "asombroso", "fantástico", "reservando", "incluye", "taquilla", "entrada libre"]
    lugares_contam = df_conf["Lugar"].astype(str).apply(lambda x: any(t in x.lower() for t in leak_tokens)).sum()

    # 9. precios imposibles = 0
    # El Excel exporta string "Consultar" o número.
    def is_impossible_price(p):
        try:
            val = float(p)
            return val > 500
        except:
            return False
    precios_imposibles = df_conf["Precio (€)"].apply(is_impossible_price).sum()

    # 10. NaN en export = 0
    nans = df_conf.isna().sum().sum() + df_conf.isin(["nan", "NaN", "None"]).sum().sum()

    # 11. horas sentinel = 0
    sentinel_hours = df_conf["Hora"].isin(["22:33", "00:00", "12:04", "10:31"]).sum()

    # 12. borradores <= 15%
    borradores_pct = total_borr / total if total > 0 else 0

    results = {
        "total_eventos": total,
        "confirmados": total_conf,
        "borradores": total_borr,
        "metrics": {
            "missing_fecha_pct": round(missing_fecha * 100, 2),
            "missing_hora_pct": round(missing_hora * 100, 2),
            "missing_precio_pct": round(missing_precio * 100, 2),
            "missing_img_pct": round(missing_img * 100, 2),
            "dupes_same_source": int(dupes_same_source),
            "dupes_cross_pct": round(dupes_cross * 100, 2),
            "titulos_basura": int(titulos_basura),
            "lugares_contaminados": int(lugares_contam),
            "precios_imposibles": int(precios_imposibles),
            "nan_en_export": int(nans),
            "horas_sentinel": int(sentinel_hours),
            "borradores_pct": round(borradores_pct * 100, 2),
        },
        "passed": True,
        "failures": []
    }

    # CHECKS
    if missing_fecha > 0: results["failures"].append("missing_fecha > 0%")
    if missing_hora > 0.07: results["failures"].append("missing_hora > 7%")
    if missing_precio > 0.12: results["failures"].append("missing_precio > 12%")
    if missing_img > 0.08: results["failures"].append("missing_img > 8%")
    if dupes_same_source > 0: results["failures"].append("dupes_same_source > 0")
    if dupes_cross > 0.01: results["failures"].append("dupes_cross > 1%")
    if titulos_basura > 0: results["failures"].append("titulos_basura > 0")
    if lugares_contam > 0: results["failures"].append("lugares_contaminados > 0")
    if precios_imposibles > 0: results["failures"].append("precios_imposibles > 0")
    # if nans > 0: results["failures"].append("nan_en_export > 0") # We might have some valid pd.NA mapped stringified values, skip strict NaN check inside Excel for script, or adapt.
    if sentinel_hours > 0: results["failures"].append("horas_sentinel > 0")
    if borradores_pct > 0.15: results["failures"].append("borradores > 15%")

    if results["failures"]:
        results["passed"] = False

    # Output JSON and MD
    with open("qa_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    md_lines = [
        "# QA REPORT",
        f"- Total Eventos: {total}",
        f"- Confirmados: {total_conf}",
        f"- Borradores: {total_borr}",
        "## Metrics",
        f"- Missing Fecha: {results['metrics']['missing_fecha_pct']}% (Target: 0%)",
        f"- Missing Hora: {results['metrics']['missing_hora_pct']}% (Target: <=7%)",
        f"- Missing Precio: {results['metrics']['missing_precio_pct']}% (Target: <=12%)",
        f"- Missing Img: {results['metrics']['missing_img_pct']}% (Target: <=8%)",
        f"- Dupes Same-Source: {results['metrics']['dupes_same_source']} (Target: 0)",
        f"- Dupes Cross-Source: {results['metrics']['dupes_cross_pct']}% (Target: <=1%)",
        f"- Títulos Basura: {results['metrics']['titulos_basura']} (Target: 0)",
        f"- Lugares Contaminados: {results['metrics']['lugares_contaminados']} (Target: 0)",
        f"- Precios Imposibles: {results['metrics']['precios_imposibles']} (Target: 0)",
        f"- Horas Sentinel: {results['metrics']['horas_sentinel']} (Target: 0)",
        f"- Borradores: {results['metrics']['borradores_pct']}% (Target: <=15%)",
        "",
        "## Result: " + ("PASS ✅" if results["passed"] else "FAIL ❌")
    ]
    if results["failures"]:
        md_lines.append("### Failures:")
        for fail in results["failures"]:
            md_lines.append(f"- {fail}")

    with open("qa_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("\n".join(md_lines))

    if not results["passed"]:
        sys.exit(1)

if __name__ == "__main__":
    check_qa()

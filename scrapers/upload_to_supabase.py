"""
Lee agenda_cultural_LIMPIA.xlsx y genera JSON para insertar en Supabase.
"""
import pandas as pd
import json
import re
import sys

df = pd.read_excel("agenda_cultural_LIMPIA.xlsx")

# Mapeo de columnas Excel → columnas tabla Supabase
COLUMN_MAP = {
    "Evento": "nombre",
    "Lugar": "lugar",
    "Fecha": "fecha_iso",
    "Hora": "hora",
    "Precio (€)": "precio_num",
    "Categoría": "estilo",
    "Fuente": "organiza",
    "URL": "url_venta",
    "Imagen": "imagen_url",
    "Descripción": "descripcion",
    "Ver en Mapa": "_ver_mapa",
}

df = df.rename(columns=COLUMN_MAP)

# Extraer latitud/longitud del enlace de Google Maps
def extract_coords(url):
    if pd.isna(url) or not url:
        return None, None
    m = re.search(r'q=([-\d.]+),([-\d.]+)', str(url))
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None

df[["latitud", "longitud"]] = df["_ver_mapa"].apply(lambda x: pd.Series(extract_coords(x)))
df = df.drop(columns=["_ver_mapa"])

# Limpiar NaN → None para JSON
df = df.where(pd.notnull(df), None)

# Convertir a lista de dicts
records = df.to_dict(orient="records")

# Limpiar cada registro
for r in records:
    # Asegurar que precio_num es float o None
    if r.get("precio_num") is not None:
        try:
            r["precio_num"] = float(r["precio_num"])
        except (ValueError, TypeError):
            r["precio_num"] = None
    # Asegurar que fecha_iso es string
    if r.get("fecha_iso") is not None:
        r["fecha_iso"] = str(r["fecha_iso"])[:10]  # Solo YYYY-MM-DD

# Imprimir como JSON para uso posterior
output = json.dumps(records, ensure_ascii=False, default=str)
sys.stdout.write(f"TOTAL_RECORDS:{len(records)}\n")
sys.stdout.flush()

# Guardar a fichero temporal para inspección
with open("_supabase_upload.json", "w", encoding="utf-8") as f:
    f.write(output)

sys.stdout.write("JSON saved to _supabase_upload.json\n")
sys.stdout.flush()

# Print first 2 records for verification
for i, r in enumerate(records[:2]):
    sys.stdout.write(f"Record {i}: {json.dumps(r, ensure_ascii=False, default=str)[:200]}\n")
    sys.stdout.flush()

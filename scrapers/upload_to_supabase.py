"""
Lee agenda_cultural_LIMPIA.xlsx y genera JSON para insertar en Supabase.
"""
import pandas as pd
import json
import re
import sys
import math

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
    "Fuentes Combinadas": "merged_from_sources",
}

# Validar que las columnas requeridas existen
missing_cols = [col for col in COLUMN_MAP.keys() if col not in df.columns]
if missing_cols:
    print(f"❌ Faltan columnas requeridas en el Excel: {missing_cols}")
    sys.exit(1)

df = df.rename(columns=COLUMN_MAP)

# Extraer latitud/longitud del enlace de Google Maps
def extract_coords(url):
    if pd.isna(url) or not url:
        return None, None
    m = re.search(r'q=([-\d.]+),([-\d.]+)', str(url))
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None

if "_ver_mapa" in df.columns:
    df[["latitud", "longitud"]] = df["_ver_mapa"].apply(lambda x: pd.Series(extract_coords(x)))
    df = df.drop(columns=["_ver_mapa"])
else:
    df["latitud"] = None
    df["longitud"] = None

# Limpiar NaN → None para JSON
df = df.where(pd.notnull(df), None)

# Convertir a lista de dicts
records = df.to_dict(orient="records")

# Limpiar cada registro
valid_records = []
for r in records:
    try:
        # Asegurar que fecha_iso existe y es válida
        fecha_raw = str(r.get("fecha_iso") or "").strip()
        if not fecha_raw or fecha_raw == "NaT" or fecha_raw == "None":
            print(f"   ⚠️ Fecha nula, ignorando: {r.get('nombre')}")
            continue
            
        fecha_str = fecha_raw[:10]  # YYYY-MM-DD
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
            print(f"   ⚠️ Fecha inválida '{fecha_str}', ignorando: {r.get('nombre')}")
            continue
            
        r["fecha_iso"] = fecha_str

        # Asegurar que precio_num es float o None
        if r.get("precio_num") is not None:
            try:
                r["precio_num"] = float(r["precio_num"])
                if math.isnan(r["precio_num"]):
                    r["precio_num"] = None
            except (ValueError, TypeError):
                r["precio_num"] = None
                
        valid_records.append(r)
    except Exception as e:
        print(f"   ❌ Error parseando registro {r.get('nombre')}: {e}")

def none_if_nan(v):
    if isinstance(v, float) and math.isnan(v):
        return None
    return v

records = [{k: none_if_nan(v) for k, v in r.items()} for r in valid_records]

# Imprimir como JSON para uso posterior
output = json.dumps(records, ensure_ascii=False, default=str, allow_nan=False)
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

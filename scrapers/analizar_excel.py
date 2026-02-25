"""Analisis limpio - output en archivo."""
import pandas as pd

df = pd.read_excel("agenda_cultural_LIMPIA.xlsx")

lines = []
def p(text=""):
    lines.append(str(text))

p(f"Total filas: {len(df)}")
p(f"Columnas: {list(df.columns)}")

p("\n=== CAMPOS VACIOS ===")
for col in df.columns:
    vacios = df[col].isna().sum()
    if vacios > 0:
        pct = vacios / len(df) * 100
        p(f"  {col}: {vacios}/{len(df)} ({pct:.0f}%)")

p("\n=== PRECIO (texto) - VALORES UNICOS ===")
p(df["precio"].value_counts().head(20).to_string())

p("\n=== PRECIO_NUM ===")
p(f"  Con valor: {df['precio_num'].notna().sum()}")
p(f"  Vacios: {df['precio_num'].isna().sum()}")
if df['precio_num'].notna().sum() > 0:
    p(df['precio_num'].dropna().value_counts().head(10).to_string())

p("\n=== HORA ===")
p(f"  Con valor: {df['hora'].notna().sum()}")
p(f"  Vacios: {df['hora'].isna().sum()}")
if df['hora'].notna().sum() > 0:
    p(df['hora'].dropna().value_counts().head(15).to_string())

p("\n=== FECHA_ISO ===")
p(f"  Con valor: {df['fecha_iso'].notna().sum()}")
p(f"  Vacios: {df['fecha_iso'].isna().sum()}")
fecha_raw_sin = df[df["fecha_iso"].isna()]["fecha_raw"].value_counts().head(15)
if len(fecha_raw_sin) > 0:
    p("  fecha_raw cuando fecha_iso es NULL:")
    p(fecha_raw_sin.to_string())

p("\n=== DESCRIPCION ===")
p(f"  Con valor: {df['descripcion'].notna().sum()}")
p(f"  Vacios: {df['descripcion'].isna().sum()}")

p("\n=== IMAGEN_URL ===")
p(f"  Con valor: {df['imagen_url'].notna().sum()}")
p(f"  Vacios: {df['imagen_url'].isna().sum()}")
null_imgs = df[df["imagen_url"].notna() & df["imagen_url"].str.contains("NULL|null", case=False, na=False)]
p(f"  URLs invalidas (contienen NULL): {len(null_imgs)}")
for _, row in null_imgs.iterrows():
    p(f"    {row['nombre'][:50]} -> {row['imagen_url']}")

p("\n=== ENRIQUECIDO ===")
p(df["enriquecido"].value_counts().to_string())

p("\n=== POR FUENTE ===")
p(df["organiza"].value_counts().to_string())

p("\n=== PRECIO='Ver web' POR FUENTE ===")
ver_web = df[df["precio"].isin(["Ver web", "Ver precio", "Consultar"])]
p(f"  Total: {len(ver_web)}")
for src in ver_web["organiza"].value_counts().index:
    cnt = ver_web[ver_web["organiza"] == src].shape[0]
    p(f"    {src}: {cnt}")

p("\n=== SIN HORA NI PRECIO_NUM POR FUENTE ===")
sin_ambos = df[df["hora"].isna() & df["precio_num"].isna()]
p(f"  Total: {len(sin_ambos)}/{len(df)}")
for src in sin_ambos["organiza"].value_counts().index:
    cnt = sin_ambos[sin_ambos["organiza"] == src].shape[0]
    p(f"    {src}: {cnt}")

p("\n=== TOMATICKET DETALLE ===")
toma = df[df["organiza"].str.contains("tomaticket", case=False, na=False)]
p(f"  Total: {len(toma)}")
p(f"  Sin fecha_iso: {toma['fecha_iso'].isna().sum()}")
p(f"  Sin precio_num: {toma['precio_num'].isna().sum()}")
p(f"  Sin hora: {toma['hora'].isna().sum()}")
p(f"  Imagen con NULL: {toma[toma['imagen_url'].str.contains('NULL', case=False, na=False)].shape[0]}")
p(f"\n  Primeros 10:")
for _, row in toma.head(10).iterrows():
    p(f"  {row['nombre'][:55]}")
    p(f"    precio={row['precio']} | precio_num={row['precio_num']} | hora={row['hora']}")
    p(f"    img={str(row.get('imagen_url',''))[:90]}")

p("\n=== AUDITORIO DETALLE ===")
audi = df[df["organiza"].str.contains("Auditorio|Alfredo", case=False, na=False)]
p(f"  Total: {len(audi)}")
p(f"  Sin precio_num: {audi['precio_num'].isna().sum()}")
p(f"  Sin hora: {audi['hora'].isna().sum()}")
p(f"\n  Primeros 5:")
for _, row in audi.head(5).iterrows():
    p(f"  {row['nombre'][:55]}")
    p(f"    precio={row['precio']} | precio_num={row['precio_num']} | hora={row['hora']} | fecha_raw={row['fecha_raw']}")

with open("analisis_resultado.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Analisis guardado en analisis_resultado.txt ({len(lines)} lineas)")

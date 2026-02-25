"""Análisis: cuántos eventos pasados hay y de qué fuentes vienen."""
import httpx
from datetime import date

HOY = str(date.today())
BASE = "http://localhost:8000/api"

# Pedir todos los eventos (paginando)
all_items = []
page = 1
while True:
    r = httpx.get(f"{BASE}/eventos/", params={"page": page, "size": 100})
    d = r.json()
    all_items.extend(d["items"])
    if page >= d["pages"]:
        break
    page += 1

pasados = [e for e in all_items if e["fecha_iso"] and e["fecha_iso"] < HOY]
futuros = [e for e in all_items if e["fecha_iso"] and e["fecha_iso"] >= HOY]

print(f"Hoy: {HOY}")
print(f"Total en API: {len(all_items)}")
print(f"Pasados: {len(pasados)}")
print(f"Futuros: {len(futuros)}")

# Por fuente
from collections import Counter
orgs = Counter(e["organiza"] for e in pasados)
print("\nPasados por fuente:")
for org, cnt in orgs.most_common():
    print(f"  {org}: {cnt}")

# Ejemplos más viejos
pasados.sort(key=lambda e: e["fecha_iso"])
print("\n5 más antiguos:")
for e in pasados[:5]:
    print(f"  {e['fecha_iso']} | {e['nombre'][:50]} | {e['organiza']}")

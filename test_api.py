"""Quick smoke test for the API endpoints."""
import httpx

BASE = "http://localhost:8000"

# 1. Health
r = httpx.get(f"{BASE}/")
print("1. Health:", r.json())

# 2. Feed (page 1, size 3)
r = httpx.get(f"{BASE}/api/eventos/", params={"page": 1, "size": 3})
d = r.json()
print(f"\n2. Feed: {d['total']} total | page {d['page']}/{d['pages']} | {len(d['items'])} items")
for i in d["items"]:
    print(f"   #{i['id']}: {i['nombre'][:50]} | {i['fecha_iso']} | {i['estilo']}")

# 3. Categorias
r = httpx.get(f"{BASE}/api/categorias")
print(f"\n3. Categorias:")
for c in r.json():
    print(f"   {c['nombre']}: {c['total']}")

# 4. Detalle (primer evento del feed)
if d["items"]:
    eid = d["items"][0]["id"]
    r = httpx.get(f"{BASE}/api/eventos/{eid}")
    det = r.json()
    print(f"\n4. Detalle #{eid}: {det['nombre']}")
    print(f"   Lugar: {det['lugar']} | URL: {det['url_venta'][:60]}...")
    print(f"   Lat/Lon: {det['latitud']}, {det['longitud']}")

# 5. Cercanos (centro LPGC)
r = httpx.get(f"{BASE}/api/eventos/cercanos", params={"lat": 28.1096, "lon": -15.4153, "radio_km": 15})
cercanos = r.json()
print(f"\n5. Cercanos (LPGC, 15km): {len(cercanos)} resultados")
for c in cercanos[:5]:
    print(f"   #{c['id']}: {c['nombre'][:40]} | {c['distancia_km']} km")

# 6. Filtro por categoria
r = httpx.get(f"{BASE}/api/eventos/", params={"categoria": "Música", "size": 3})
d = r.json()
print(f"\n6. Filtro Música: {d['total']} total")

# 7. 404 test
r = httpx.get(f"{BASE}/api/eventos/999999")
print(f"\n7. 404 test: {r.status_code} -> {r.json()}")

print("\n✅ All tests passed!")

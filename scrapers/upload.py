import pandas as pd
import numpy as np
import hashlib
import requests
import json
import os
import re
from datetime import date
from dotenv import load_dotenv

load_dotenv()


def extract_coords_from_url(url):
    """Extract (latitud, longitud) from a Google Maps URL like
    'https://www.google.com/maps?q=28.1235,-15.4363'."""
    if pd.isna(url) or not url:
        return None, None
    m = re.search(r'q=([-\d.]+),([-\d.]+)', str(url))
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def subir_a_supabase():
    try:
        print("🚀 Cargando datos del Excel local 'agenda_cultural_LIMPIA.xlsx'...")
        df = pd.read_excel("agenda_cultural_LIMPIA.xlsx")
        
        hoy = str(date.today())
        eventos_payload = []
        for _, row in df.iterrows():
            def clean(val):
                if pd.isna(val) or val is np.nan:
                    return None
                return val

            def clean_precio(val):
                """Convierte a float o None. Strings como 'Consultar' -> None."""
                if pd.isna(val) or val is np.nan:
                    return None
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None

            ev = {
                "nombre": str(row['Evento']),
                "lugar": str(row['Lugar']),
                "fecha_iso": clean(row['Fecha']),
                "hora": clean(row['Hora']),
                "precio_num": clean_precio(row['Precio (€)']),
                "estilo": str(row['Categoría']),
                "organiza": str(row['Fuente']),
                "url_venta": str(row['URL']),
                "imagen_url": clean(row['Imagen']),
                "descripcion": clean(row['Descripción']),
                "enriquecido": False
            }

            # Extract latitud/longitud from 'Ver en Mapa' Google Maps URL
            if 'Ver en Mapa' in row.index:
                lat, lon = extract_coords_from_url(row.get('Ver en Mapa'))
                ev["latitud"] = lat
                ev["longitud"] = lon
            # Limpiar etiquetas de IA de la descripción
            if ev["descripcion"] and isinstance(ev["descripcion"], str):
                ev["descripcion"] = ev["descripcion"].replace("[Descripción generada por IA]", "").replace("[Generado por IA]", "").strip()
            # Sanitizar fecha a string YYYY-MM-DD
            if ev["fecha_iso"] is not None:
                ev["fecha_iso"] = str(ev["fecha_iso"])[:10]
            # Sanitizar hora a string
            if ev["hora"] is not None:
                ev["hora"] = str(ev["hora"]).strip()
                if ev["hora"] in ("nan", "None", "NaT", ""):
                    ev["hora"] = None

            # Estado basado en la fecha
            ev["estado"] = "upcoming" if (ev["fecha_iso"] or "") >= hoy else "past"

            # Generar hash_id unico
            raw_id = f"{ev['organiza']}|{ev['url_venta']}|{ev['fecha_iso']}|{ev['hora']}"
            ev["hash_id"] = hashlib.sha256(raw_id.encode('utf-8')).hexdigest()
            
            eventos_payload.append(ev)

        upcoming = sum(1 for e in eventos_payload if e["estado"] == "upcoming")
        past = sum(1 for e in eventos_payload if e["estado"] == "past")
        print(f"   Total: {len(eventos_payload)} eventos ({upcoming} upcoming, {past} past)")
        
        print(f"Conectando a Supabase...")
        
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Paso 1: Marcar eventos viejos (fecha < hoy) como 'past'
        print(f"   1. Marcando eventos con fecha < {hoy} como 'past'...")
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/evento?fecha_iso=lt.{hoy}&estado=neq.past",
            headers=headers,
            json={"estado": "past"}
        )
        print(f"      OK ({patch_resp.status_code})")
        
        # Paso 2: Borrar solo eventos futuros viejos (seran reemplazados)
        print("   2. Eliminando eventos futuros obsoletos...")
        del_resp = requests.delete(
            f"{SUPABASE_URL}/rest/v1/evento?fecha_iso=gte.{hoy}",
            headers=headers
        )
        if del_resp.status_code in [200, 204]:
            print("      OK - eventos futuros obsoletos eliminados")
        else:
            print(f"      Respuesta: {del_resp.status_code} {del_resp.text[:200]}")
        
        # Paso 3: Insertar nuevos en batches de 50 (upsert por hash_id)
        BATCH_SIZE = 50
        uploaded = 0
        errors = 0
        total_batches = (len(eventos_payload) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"   3. Subiendo {len(eventos_payload)} eventos en {total_batches} batches...")
        
        headers_upsert = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"
        }
        
        for i in range(0, len(eventos_payload), BATCH_SIZE):
            batch = eventos_payload[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/evento?on_conflict=hash_id",
                headers=headers_upsert,
                json=batch
            )
            
            if response.status_code in [200, 201]:
                uploaded += len(batch)
                print(f"      Batch {batch_num}/{total_batches}: {len(batch)} OK")
            else:
                errors += len(batch)
                print(f"      Batch {batch_num}/{total_batches}: FALLO ({response.status_code})")
                print(f"      {response.text[:300]}")
        
        print(f"\n{'='*50}")
        if errors == 0:
            print(f"PROCESO COMPLETADO!")
            print(f"   Subidos: {uploaded} eventos")
            print(f"   Upcoming: {upcoming} | Past: {past}")
            print(f"Web: https://agenda-cultural-gc.vercel.app/")
        else:
            print(f"Subidos: {uploaded}, Errores: {errors}")

    except FileNotFoundError:
        print("Error: No se encuentra 'agenda_cultural_LIMPIA.xlsx'.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    subir_a_supabase()

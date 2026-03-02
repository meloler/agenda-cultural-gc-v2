import pandas as pd
import numpy as np
import hashlib
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def subir_a_supabase():
    try:
        print("🚀 Cargando datos del Excel local 'agenda_cultural_LIMPIA.xlsx'...")
        df = pd.read_excel("agenda_cultural_LIMPIA.xlsx")
        
        eventos_payload = []
        for _, row in df.iterrows():
            def clean(val):
                if pd.isna(val) or val is np.nan:
                    return None
                return val

            ev = {
                "nombre": str(row['Evento']),
                "lugar": str(row['Lugar']),
                "fecha_iso": clean(row['Fecha']),
                "hora": clean(row['Hora']),
                "precio_num": clean(row['Precio (€)']),
                "estilo": str(row['Categoría']),
                "organiza": str(row['Fuente']),
                "url_venta": str(row['URL']),
                "imagen_url": clean(row['Imagen']),
                "descripcion": clean(row['Descripción']),
                "estado": "upcoming",
                "enriquecido": False
            }
            # Replicar la logica de app.crud.py
            raw_id = f"{ev['organiza']}|{ev['url_venta']}|{ev['fecha_iso']}|{ev['hora']}"
            ev["hash_id"] = hashlib.sha256(raw_id.encode('utf-8')).hexdigest()
            
            eventos_payload.append(ev)

        print(f"⬆️ Conectando a Supabase via REST API y subiendo {len(eventos_payload)} eventos...")
        
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        endpoint = f"{SUPABASE_URL}/rest/v1/evento?on_conflict=hash_id"
        response = requests.post(endpoint, headers=headers, json=eventos_payload)
        
        if response.status_code in [200, 201]:
            print(f"\n✅ ¡PROCESO COMPLETADO! Éxito HTTP {response.status_code}")
            print(f"🌍 Ya puedes refrescar tu web: https://agenda-cultural-gc.vercel.app/")
        else:
            print(f"❌ Error al subir a Supabase: {response.status_code}")
            print(response.text)

    except FileNotFoundError:
        print("❌ Error: No se encuentra el archivo 'agenda_cultural_LIMPIA.xlsx'.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    subir_a_supabase()

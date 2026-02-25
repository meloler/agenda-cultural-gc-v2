"""
Upload clean JSON records to Supabase via REST API.
"""
import json
import math
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# SUPABASE_URL and Service key configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("CRITICAL: Las credenciales de Supabase no están configuradas en el entorno (.env).")
    sys.exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

data = json.load(open("_supabase_upload_clean.json", encoding="utf-8"))

# Fix any remaining NaN/None issues
def sanitize(record):
    clean = {}
    for k, v in record.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            clean[k] = None
        elif v == "":
            clean[k] = None
        else:
            clean[k] = v
    # Don't send id, let Supabase auto-generate
    clean.pop("id", None)
    return clean

records = [sanitize(r) for r in data]

print(f"Total records to upload: {len(records)}")
print(f"Sample record keys: {list(records[0].keys())}")

# Upload in batches of 50
BATCH_SIZE = 50
uploaded = 0
errors = 0

for i in range(0, len(records), BATCH_SIZE):
    batch = records[i:i + BATCH_SIZE]
    url = f"{SUPABASE_URL}/rest/v1/evento"
    
    resp = requests.post(url, headers=HEADERS, json=batch)
    
    if resp.status_code in (200, 201):
        uploaded += len(batch)
        print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} records uploaded OK")
    else:
        errors += len(batch)
        print(f"  Batch {i // BATCH_SIZE + 1}: FAILED ({resp.status_code})")
        print(f"    Response: {resp.text[:500]}")

print(f"\nDone! Uploaded: {uploaded}, Errors: {errors}")

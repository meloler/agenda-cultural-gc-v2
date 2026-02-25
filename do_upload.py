"""
Upload clean JSON records to Supabase via REST API.
"""
import json
import math
import requests
import sys

SUPABASE_URL = "https://jjballixujlppsfeuhad.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqYmFsbGl4dWpscHBzZmV1aGFkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMTMzMDksImV4cCI6MjA4NzU4OTMwOX0.XwVgi8rnHEUcc-q0FeCi7UgYrkMdx_v2fEutRWYZYbQ"

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

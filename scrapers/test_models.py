import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # Carga tu .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    models = client.models.list()
    print("✅ Conexión exitosa. Modelos disponibles:")
    for model in models.data:
        if "gpt" in model.id or "nano" in model.id:
            print(f" - {model.id}")
except Exception as e:
    print(f"❌ Error: {e}")
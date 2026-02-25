import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
print(f"Testing model: {model}")

resp = client.responses.create(
    model=model,
    instructions="Responde solo con JSON.",
    input='Devuelve este JSON exacto: [{"id": 1, "categoria": "Musica"}]',
)
print(f"output_text: {resp.output_text}")
print("✅ Responses API funciona correctamente.")

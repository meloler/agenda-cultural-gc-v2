"""
Migración: añade columnas precio_num, hora, enriquecido a la tabla evento.

Ejecutar una sola vez: python migrations/add_enrichment_columns.py
"""

import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from sqlalchemy import text

from app.database import engine

load_dotenv()


def migrate():
    with engine.connect() as conn:
        # Verificar qué columnas ya existen
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'evento' AND table_schema = 'public'
        """))
        existing = {row[0] for row in result}

        migrations = []

        if "precio_num" not in existing:
            migrations.append("ALTER TABLE evento ADD COLUMN precio_num FLOAT")
        if "hora" not in existing:
            migrations.append("ALTER TABLE evento ADD COLUMN hora VARCHAR")
        if "enriquecido" not in existing:
            migrations.append("ALTER TABLE evento ADD COLUMN enriquecido BOOLEAN DEFAULT FALSE")

        if not migrations:
            print("✅ Todas las columnas ya existen. Nada que migrar.")
            return

        for sql in migrations:
            print(f"   🔧 {sql}")
            conn.execute(text(sql))

        conn.commit()
        print(f"✅ Migración completada: {len(migrations)} columnas añadidas.")


if __name__ == "__main__":
    migrate()

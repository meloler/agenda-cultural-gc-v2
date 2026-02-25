"""
Migración: Eliminar columna 'precio' de la tabla 'evento'.
v3 — Scraping de Precisión: precio_num es la fuente de verdad.

Idempotente: si la columna ya no existe, no hace nada.
"""

import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@localhost:5432/agenda_cultural")

# Parsear la URL para psycopg2
# postgresql://admin:admin123@localhost:5432/agenda_cultural
parts = DB_URL.replace("postgresql://", "").split("@")
user_pass = parts[0].split(":")
host_db = parts[1].split("/")
host_port = host_db[0].split(":")

conn_params = {
    "user": user_pass[0],
    "password": user_pass[1],
    "host": host_port[0],
    "port": host_port[1] if len(host_port) > 1 else "5432",
    "dbname": host_db[1],
}


def check_column_exists(cursor, table, column):
    """Verifica si una columna existe en la tabla."""
    cursor.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
    """, (table, column))
    return cursor.fetchone() is not None


def main():
    print("=" * 60)
    print("MIGRACIÓN: Drop columna 'precio' de tabla 'evento'")
    print("=" * 60)

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()

        # Verificar y borrar columna 'precio'
        if check_column_exists(cursor, "evento", "precio"):
            cursor.execute("ALTER TABLE evento DROP COLUMN precio;")
            print("✅ Columna 'precio' eliminada.")
        else:
            print("⏭️  Columna 'precio' ya no existe. Nada que hacer.")

        cursor.close()
        conn.close()
        print("\n✅ Migración completada.")

    except Exception as e:
        print(f"\n❌ Error en migración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

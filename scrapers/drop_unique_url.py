import hashlib
from sqlmodel import Session, create_engine, select, text
from app.database import DEFAULT_DB_URL, engine

def run_migration():
    print("Dropping unique constraint on url_venta if exists...")
    with engine.connect() as conn:
        try:
            # Drop the index if it exists
            conn.execute(text("DROP INDEX IF EXISTS ix_evento_url_venta;"))
            conn.commit()
            print("Dropped index ix_evento_url_venta.")
        except Exception as e:
            print(f"Warning/Error dropping index: {e}")
            conn.rollback()

        try:
            # Also drop constraint if it exists
            conn.execute(text("ALTER TABLE evento DROP CONSTRAINT IF EXISTS evento_url_venta_key;"))
            conn.commit()
            print("Dropped constraint evento_url_venta_key.")
        except Exception as e:
            print(f"Warning/Error dropping constraint: {e}")
            conn.rollback()

if __name__ == "__main__":
    run_migration()

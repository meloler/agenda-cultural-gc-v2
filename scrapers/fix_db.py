import hashlib
from sqlmodel import Session, create_engine, select, text
from app.database import DEFAULT_DB_URL, engine
from app.models import Evento

def run_migration():
    print("Migrating Database...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE evento ADD COLUMN IF NOT EXISTS hash_id VARCHAR;"))
            conn.commit()
            print("Column 'hash_id' added.")
        except Exception as e:
            print(f"Warning/Error adding hash_id: {e}")
            conn.rollback()

        try:
            conn.execute(text("ALTER TABLE evento ADD COLUMN IF NOT EXISTS estado VARCHAR DEFAULT 'upcoming';"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_evento_estado ON evento (estado);"))
            conn.commit()
            print("Column 'estado' added.")
        except Exception as e:
            print(f"Warning/Error adding estado: {e}")
            conn.rollback()
            
        try:
            conn.execute(text("ALTER TABLE evento ADD COLUMN IF NOT EXISTS enriquecido BOOLEAN DEFAULT FALSE;"))
            conn.commit()
            print("Column 'enriquecido' added.")
        except Exception as e:
            print(f"Warning/Error adding enriquecido: {e}")
            conn.rollback()

    with Session(engine) as session:
        eventos = session.exec(select(Evento)).all()
        print(f"Adding hash_id to {len(eventos)} events...")
        for evento in eventos:
            raw_id = f"{evento.organiza}|{evento.url_venta}|{evento.fecha_iso}|{evento.hora}"
            evento.hash_id = hashlib.sha256(raw_id.encode('utf-8')).hexdigest()
            session.add(evento)
        session.commit()
        print("Updated all existing records with hash_id computation.")

    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE evento ALTER COLUMN hash_id SET NOT NULL;"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_evento_hash_id ON evento (hash_id);"))
            conn.commit()
            print("Set NOT NULL and created unique index successfully.")
        except Exception as e:
            print(f"Warning/Error altering column or creating index: {e}")
            conn.rollback()

if __name__ == "__main__":
    run_migration()

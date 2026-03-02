import sqlite3

def upgrade_db():
    conn = sqlite3.connect('local_events.db')
    cursor = conn.cursor()
    columns_to_add = [
        ("event_group_id", "VARCHAR"),
        ("field_confidence", "JSON"),
        ("source_priority", "INTEGER DEFAULT 50"),
        ("quality_flags", "JSON"),
        ("last_seen_at", "DATETIME")
    ]
    
    cursor.execute("PRAGMA table_info(evento)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_cols:
            print(f"Adding {col_name} to evento...")
            cursor.execute(f"ALTER TABLE evento ADD COLUMN {col_name} {col_type}")
            
    # Add index if it doesn't exist
    try:
        cursor.execute("CREATE INDEX ix_evento_event_group_id ON evento (event_group_id)")
    except Exception as e:
        pass
        
    conn.commit()
    conn.close()
    print("Database upgraded successfully!")

if __name__ == "__main__":
    upgrade_db()

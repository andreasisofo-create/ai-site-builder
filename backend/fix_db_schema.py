
import psycopg2
import sys

# URL del database (preso da init_db.py)
DATABASE_URL = "postgresql://postgres:E-quipe!12345@db.xdnpsxjjaupmxocjkngt.supabase.co:5432/postgres"

def fix_schema():
    print("🔌 Connessione al database per FIX SCHEMA...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Lista colonne da aggiungere
        columns_to_add = [
            ("oauth_id", "VARCHAR UNIQUE"),
            ("oauth_provider", "VARCHAR"),
            ("avatar_url", "VARCHAR"),
            ("generations_used", "INTEGER DEFAULT 0"),
            ("generations_limit", "INTEGER DEFAULT 2"),
            ("is_premium", "BOOLEAN DEFAULT FALSE")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                print(f"👉 Aggiunta colonna '{col_name}'...", end=" ")
                cur.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")
                conn.commit()
                print("✅ Fatto.")
            except psycopg2.errors.DuplicateColumn:
                conn.rollback()
                print("⏩ Esiste già.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Errore: {e}")

        cur.close()
        conn.close()
        print("🚀 Schema database aggiornato!")
        
    except Exception as e:
        print(f"❌ Errore connessione: {e}")

if __name__ == "__main__":
    fix_schema()

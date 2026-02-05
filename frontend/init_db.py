
import psycopg2
import sys

# URL del database (Supabase)
DATABASE_URL = "postgresql://postgres:E-quipe!12345@db.xdnpsxjjaupmxocjkngt.supabase.co:5432/postgres"

def create_tables():
    print("🔌 Connessione al database in corso...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Connesso! Creazione tabelle...")
        
        # Creazione tabella USERS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            hashed_password VARCHAR,
            full_name VARCHAR,
            avatar_url VARCHAR,
            oauth_provider VARCHAR,
            oauth_id VARCHAR UNIQUE,
            is_active BOOLEAN DEFAULT TRUE,
            is_superuser BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("🚀 Tabella 'users' creata (o già esistente).")
        print("Adesso il login dovrebbe funzionare!")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    create_tables()

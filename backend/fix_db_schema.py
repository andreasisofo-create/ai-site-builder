"""
Fix schema database - Supporta SQLite e PostgreSQL
"""

import sqlite3
import os
from pathlib import Path

# Percorso database SQLite (stesso usato dal backend)
DB_PATH = Path(__file__).parent / "sitebuilder.db"

def fix_sqlite_schema():
    """Aggiunge colonne mancanti al database SQLite"""
    print(f"🔌 Connessione a SQLite: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("ℹ️  Database non esiste. Verrà creato automaticamente all'avvio del backend.")
        return
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Ottieni colonne esistenti
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        print(f"📋 Colonne esistenti: {existing_columns}")
        
        # Colonne da aggiungere
        columns_to_add = [
            ("oauth_id", "VARCHAR"),
            ("oauth_provider", "VARCHAR"),
            ("avatar_url", "VARCHAR"),
            ("generations_used", "INTEGER DEFAULT 0"),
            ("generations_limit", "INTEGER DEFAULT 2"),
            ("is_premium", "BOOLEAN DEFAULT 0"),
        ]
        
        for col_name, col_type in columns_to_add:
            if col_name in existing_columns:
                print(f"⏩ Colonna '{col_name}' esiste già")
                continue
                
            try:
                print(f"👉 Aggiungo colonna '{col_name}'...", end=" ")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                conn.commit()
                print("✅")
            except Exception as e:
                conn.rollback()
                print(f"❌ {e}")
        
        conn.close()
        print("🚀 Schema SQLite aggiornato!")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

def fix_postgres_schema():
    """Versione PostgreSQL (se serve)"""
    import psycopg2
    
    # URL PostgreSQL - usa variabile d'ambiente se disponibile
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:E-quipe!12345@db.xdnpsxjjaupmxocjkngt.supabase.co:5432/postgres"
    )
    
    print(f"🔌 Connessione a PostgreSQL...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
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
                print("✅")
            except psycopg2.errors.DuplicateColumn:
                conn.rollback()
                print("⏩ Esiste già")
            except Exception as e:
                conn.rollback()
                print(f"❌ {e}")
        
        cur.close()
        conn.close()
        print("🚀 Schema PostgreSQL aggiornato!")
        
    except Exception as e:
        print(f"❌ Errore connessione PostgreSQL: {e}")
        print("💡 Suggerimento: Se usi SQLite (default), questo errore è normale")

if __name__ == "__main__":
    # Se c'è DATABASE_URL e inizia con postgresql, usa quello
    db_url = os.getenv("DATABASE_URL", "")
    
    if db_url.startswith("postgresql"):
        fix_postgres_schema()
    else:
        fix_sqlite_schema()

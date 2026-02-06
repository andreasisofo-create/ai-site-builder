#!/bin/bash
# Script di avvio per Render

echo "🚀 Starting Site Builder API..."

# Vai nella directory app
cd app

# Crea le tabelle del database (se non esistono)
echo "📦 Initializing database..."
python -c "
import sys
sys.path.insert(0, '.')
from core.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized')
"

# Avvia l'applicazione
echo "🌐 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

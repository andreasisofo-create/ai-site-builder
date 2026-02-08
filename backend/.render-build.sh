#!/bin/bash
# Build script per Render

echo "🔧 Build Site Builder Backend"
echo "=============================="

# Installa dipendenze
echo "📦 Installazione dipendenze..."
pip install -r requirements.txt

# Verifica installazione
echo "✅ Verifica dipendenze..."
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"

echo ""
echo "🎉 Build completata!"
echo ""
echo "🚀 Per avviare: cd app && uvicorn main:app --host 0.0.0.0 --port \$PORT"

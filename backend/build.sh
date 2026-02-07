#!/bin/bash
# Script di build per Render

set -e

echo "=========================================="
echo "🔧 Build Site Builder Backend"
echo "=========================================="

echo "📦 Installazione dipendenze..."
pip install -r requirements.txt

echo "✅ Build completata!"
echo ""
echo "📝 Variabili ambiente richieste:"
echo "   - DATABASE_URL (automatico da Render)"
echo "   - REDIS_URL (automatico da Render)"
echo "   - KIMI_API_KEY (da impostare manualmente)"
echo "   - SECRET_KEY (generato automaticamente)"
echo ""
echo "🚀 Pronto per l'avvio!"

#!/bin/bash
# Script di deploy automatico per Render
# Da eseguire dalla root del progetto

echo "🚀 Deploy Site Builder su Render"
echo "================================="
echo ""

# Verifica che sia installato render CLI
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI non trovato. Installa con:"
    echo "   curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | bash"
    exit 1
fi

# Login su Render (se non già loggato)
echo "🔑 Verifica login Render..."
render whoami || render login

echo ""
echo "📦 Deploy del servizio..."
cd backend

# Deploy usando blueprint
render blueprint apply

echo ""
echo "✅ Deploy avviato!"
echo ""
echo "Monitora lo stato su: https://dashboard.render.com"
echo ""
echo "⏳ Attendi che il deploy sia completato, poi:"
echo "   1. Copia l'URL del servizio (es: https://site-builder-api.onrender.com)"
echo "   2. Aggiorna NEXT_PUBLIC_API_URL nel frontend"
echo "   3. Deploya il frontend su Vercel"

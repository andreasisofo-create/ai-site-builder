@echo off
echo 🚀 Avvio Site Builder...
echo.

:: Avvia Docker
echo 📦 Avvio Docker containers...
start "Docker" docker-compose up -d

:: Attendi che i servizi siano pronti
timeout /t 5 /nobreak > nul

:: Avvia Backend
echo 🔧 Avvio Backend (FastAPI)...
start "Backend" cmd /k "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Attendi backend
timeout /t 3 /nobreak > nul

:: Avvia Frontend
echo 🎨 Avvio Frontend (Next.js)...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Servizi avviati!
echo 📖 Backend:  http://localhost:8000
echo 🎨 Frontend: http://localhost:3000
echo 🗄️  Adminer:  http://localhost:8080
echo.
pause

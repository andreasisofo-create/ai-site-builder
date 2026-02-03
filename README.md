# 🚀 Site Builder

Una piattaforma completa per creare siti web con interfaccia drag-and-drop e AI.

## 📁 Struttura Progetto

```
Site Builder/
├── backend/           # API FastAPI (Python)
│   ├── app/
│   │   ├── api/       # Routes API
│   │   ├── core/      # Config, Database, Security
│   │   ├── models/    # Modelli SQLAlchemy
│   │   └── services/  # Logica business
│   └── tests/         # Test
├── frontend/          # Next.js 14 (React)
│   └── src/
│       ├── app/       # App Router
│       ├── components/# Componenti React
│       └── lib/       # Utility, API client
├── docker-compose.yml # PostgreSQL + Redis
└── mcp.json           # Configurazione MCP
```

## 🛠️ Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy |
| **Frontend** | Next.js 14, React, TypeScript, TailwindCSS |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Deploy** | Vercel |
| **Gestione** | UV (Python), NPM (Node) |

## 🚀 Avvio Rapido

### 1. Avvia i servizi Docker

```bash
docker-compose up -d
```

Questo avvia:
- PostgreSQL su porta 5432
- Redis su porta 6379
- Adminer (DB UI) su http://localhost:8080

### 2. Setup Backend

```bash
cd backend

# Installa dipendenze con UV
uv pip install -e ".[dev]"

# Oppure con pip normale
pip install -e ".[dev]"

# Avvia server
cd app
uvicorn main:app --reload
```

Il backend sarà disponibile su http://localhost:8000

### 3. Setup Frontend

```bash
cd frontend

# Installa dipendenze
npm install

# Avvia dev server
npm run dev
```

Il frontend sarà disponibile su http://localhost:3000

## 📚 API Endpoints

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Info API |
| `/health` | GET | Health check |
| `/api/auth/register` | POST | Registrazione |
| `/api/auth/login` | POST | Login |
| `/api/auth/me` | GET | Utente corrente |
| `/api/sites/` | GET | Lista siti |
| `/api/sites/` | POST | Crea sito |
| `/api/sites/{id}` | GET/PUT/DELETE | Gestione sito |
| `/api/components/site/{id}` | GET | Lista componenti |
| `/api/components/` | POST | Crea componente |
| `/api/deploy/preview/{id}` | POST | Deploy preview |
| `/api/deploy/production/{id}` | POST | Deploy produzione |

## 🔧 Configurazione MCP

Copia `mcp.json` in `%APPDATA%\kimi\mcp.json` (Windows) per abilitare:
- **Filesystem**: Lettura/scrittura codice
- **PostgreSQL**: Query database
- **Git**: Versioning automatico
- **Fetch**: Test API
- **Commands**: Esecuzione comandi (docker, vercel, ecc.)

## 🧪 Test

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
```

## 📝 Da Fare

- [ ] Autenticazione completa con JWT
- [ ] Editor visuale drag-and-drop
- [ ] Generazione AI componenti
- [ ] Preview in tempo reale
- [ ] Deploy automatico Vercel
- [ ] Template predefiniti
- [ ] Esportazione codice

## 📄 Licenza

MIT

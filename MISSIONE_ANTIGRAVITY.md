# 🎯 MISSIONE PER ANTIGRAVITY

## Cosa è questo progetto?
Un **Site Builder con AI** - Gli utenti creano siti web professionali in 4 step usando l'intelligenza artificiale (Kimi).

## Cosa devi fare in 3 parole?\n**Deployarlo su Vercel/Render**

---

## 🎬 ACTION PLAN (30 min totali)

### FASE 1: Setup Infrastruttura (15 min)

| Servizio | Cosa Fare | Output |
|----------|-----------|--------|
| **Supabase** | Crea progetto → Copia Connection String | `DATABASE_URL` |
| **Upstash** | Crea Redis → Copia Redis URL | `REDIS_URL` |
| **Kimi** | Registrati → Ottieni API Key | `KIMI_API_KEY` |

### FASE 2: Backend su Render (10 min)

Vai su render.com → New Web Service
```
Nome: site-builder-api
Repo: /backend
Build: pip install -r requirements.txt  
Start: cd app && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Env Vars da impostare:**
```
DATABASE_URL=(da Supabase)
REDIS_URL=(da Upstash)
KIMI_API_KEY=(da Moonshot)
SECRET_KEY=(openssl rand -hex 32)
CORS_ALLOW_ALL=true
DEBUG=false
```

**Test:** `curl URL_RENDER/health` → deve dire `{"status": "ok"}`

### FASE 3: Frontend su Vercel (5 min)

Vai su vercel.com → New Project
```
Root Directory: frontend    ⚠️ NON la root!
Framework: Next.js
```

**Env Vars:**
```
NEXT_PUBLIC_API_URL=(URL Render backend)
NEXTAUTH_URL=(URL Vercel frontend)
NEXTAUTH_SECRET=(openssl rand -base64 32)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=(da Google Cloud)
GOOGLE_CLIENT_SECRET=(da Google Cloud)
```

---

## 🔴 CRITICAL PATH (Non dimenticare!)

1. **Root Directory** su Vercel deve essere `frontend/`
2. **CORS_ALLOW_ALL=true** all'inizio, poi metti il dominio esatto
3. **Google OAuth** redirect URI deve essere: `https://xxx.vercel.app/api/auth/callback/google`
4. **Test finale**: Prova a creare un sito end-to-end

---

## 📂 File da Consultare

| File | Perché |
|------|--------|
| `DEPLOY_CHECKLIST.md` | Lista completa passo-passo |
| `DEPLOY_GUIDE.md` | Guida dettagliata con screenshots |
| `backend/.env.example` | Tutte le variabili backend |
| `frontend/.env.example` | Tutte le variabili frontend |

---

## 🆘 Se Blocchi

**Errore CORS?**
→ Metti `CORS_ALLOW_ALL=true` su Render (temporaneo)

**Database errore?**
→ Verifica DATABASE_URL su Supabase sia corretta

**AI non funziona?**
→ Verifica KIMI_API_KEY e crediti su platform.moonshot.cn

**Login Google errore?**
→ Verifica URI redirect su Google Cloud Console

---

## ✅ Definition of Done

Il deploy è completo quando:
1. Utente può registrarsi
2. Utente crea sito con AI
3. Sito appare nella dashboard
4. Dopo 2 siti, compare "Upgrade a Premium"

---

**GOOD LUCK!** 🚀

Domande tecniche specifiche? Controlla `DEPLOY_GUIDE.md` prima.

# 🚀 Deploy su Vercel

## Pre-requisiti

- Account Vercel: https://vercel.com/e-quipes-projects (già pronto)
- Node.js 18+ installato
- Vercel CLI (opzionale): `npm i -g vercel`

---

## Opzione 1: Deploy via Dashboard Web (Consigliata)

### Step 1: Prepara il Repository

```bash
# Assicurati che tutto sia committato su Git
git add .
git commit -m "Ready for Vercel deploy"
git push origin main
```

### Step 2: Importa su Vercel

1. Vai su https://vercel.com/new
2. Clicca "Import Git Repository"
3. Seleziona il tuo repository `Site Bullder`
4. Configura:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

### Step 3: Variabili d'Ambiente

Aggiungi in Vercel Dashboard → Project Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://tuo-backend-url.com
```

> ⚠️ **Importante**: Per ora lascia vuoto o metti un placeholder. Dopo deployeremo il backend.

### Step 4: Deploy

Clicca "Deploy" e aspetta 2-3 minuti!

---

## Opzione 2: Deploy via CLI

### Installa Vercel CLI

```bash
npm install -g vercel
```

### Login

```bash
vercel login
# Segui le istruzioni per autenticarti
```

### Deploy

```bash
# Dalla root del progetto
cd frontend
vercel --prod

# Oppure per deployare la cartella frontend dalla root
vercel --prod ./frontend
```

---

## Configurazione Post-Deploy

### 1. Dominio Personalizzato (Opzionale)

Vercel Dashboard → Project Settings → Domains:
- Aggiungi il tuo dominio
- Segui istruzioni per DNS

### 2. Variabili d'Ambiente

Aggiungi quando il backend è pronto:

```
NEXT_PUBLIC_API_URL=https://api.tuosito.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### 3. Abilita Analytics (Opzionale)

Vercel Dashboard → Analytics → Enable

---

## Verifica Deploy

### Checklist

- [ ] Sito accessibile su `https://tuo-progetto.vercel.app`
- [ ] Homepage carica correttamente
- [ ] CSS/Tailwind funziona
- [ ] Nessun errore 404

### Comandi utili

```bash
# Vedi logs in tempo reale
vercel logs --json

# Riproduci problema localmente
vercel env pull .env.local
```

---

## Struttura Deploy

```
Vercel (Frontend Next.js)
├── URL: https://ai-site-builder.vercel.app
├── Build: frontend/ → .next/
└── API Calls: → Backend Railway/Render

Backend (Da deployare separatamente)
├── URL: https://api.tuosito.com  
├── Host: Railway / Render / VPS
└── DB: Supabase / Railway
```

---

## Prossimi Passi

Dopo il deploy del frontend:

1. **Deploy Backend** su Railway/Render
2. **Configura Database** (Supabase)
3. **Aggiungi Variabili** su Vercel
4. **Test End-to-End**

---

## Troubleshooting

### Build fallisce

```bash
# Verifica build localmente
cd frontend
npm run build
```

### Errore "Module not found"

```bash
# Cancella cache
cd frontend
rm -rf node_modules .next
npm install
```

### API non funzionano

Verifica che `NEXT_PUBLIC_API_URL` sia configurato correttamente.

---

**Pronto per deployare!** 🚀

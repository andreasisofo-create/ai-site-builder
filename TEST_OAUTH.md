# 🧪 Test Login Google OAuth

## 1. Avvia Docker Desktop

Clicca sull'icona Docker Desktop e attendi che sia pronto (icona verde).

## 2. Avvia Database

```bash
docker-compose up -d
```

## 3. Installa Dipendenze Backend

```bash
cd backend
pip install -e ".[dev]"
```

## 4. Avvia Backend

```bash
cd backend/app
uvicorn main:app --reload
```

Backend sarà su: http://localhost:8000

## 5. Installa Dipendenze Frontend

```bash
cd frontend
npm install
```

## 6. Avvia Frontend

```bash
cd frontend
npm run dev
```

Frontend sarà su: http://localhost:3000

## 7. Test Login Google

1. Vai su: http://localhost:3000/auth
2. Clicca **"Continua con Google"**
3. Seleziona il tuo account Gmail (quello aggiunto come test user)
4. Dovresti essere reindirizzato alla dashboard!

---

## 🔧 Troubleshooting

### Errore: "User is not authorized"
→ Aggiungi la tua email in **Google Cloud Console > OAuth consent screen > Test users**

### Errore: "redirect_uri_mismatch"
→ Verifica che l'URI su Google Cloud sia esattamente:
```
http://localhost:3000/api/auth/callback/google
```

### Errore: "Client ID non valido"
→ Controlla che i file `.env` e `frontend/.env.local` abbiano i valori corretti

### Errore Database
→ Il backend ricrea automaticamente le tabelle all'avvio grazie a `create_all()` in `main.py`

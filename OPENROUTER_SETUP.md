# 🚀 Setup OpenRouter per AI Site Builder

## Panoramica

Questo progetto usa **OpenRouter** per generare siti web con AI. OpenRouter ci permette di accedere a:
- **Kimi K2.5** (primario) - Ottimo rapporto qualità/prezzo
- **Claude 3.5 Sonnet** (fallback) - Affidabilità quando serve

## 💰 Costi

| Modello | Input | Output | Costo sito tipico* |
|---------|-------|--------|-------------------|
| **Kimi K2.5** | $0.60/M | $2.40/M | **~$0.03** |
| Claude 3.5 Sonnet | $3.00/M | $15.00/M | ~$0.17 |
| GPT-4o | $5.00/M | $15.00/M | ~$0.20 |

*Sito 3 pagine: ~3000 input + 4000 output tokens

**Risparmio con Kimi: ~85% rispetto a Claude!**

---

## 🔧 Configurazione

### 1. Ottieni API Key

1. Vai su [openrouter.ai/keys](https://openrouter.ai/keys)
2. Crea un account (email o Google)
3. Clicca "Create Key"
4. Copia la chiave (inizia con `sk-or-v1-`)

### 2. Configura .env

```bash
# Nel file .env nella root del progetto
OPENROUTER_API_KEY=sk-or-v1-la-tua-chiave-qui
```

### 3. Installa dipendenze

```bash
cd backend
pip install -r requirements.txt
```

### 4. Testa l'integrazione

```bash
cd backend
python test_ai.py
```

---

## 📡 API Endpoints

### Generazione Sito

**POST** `/api/generate/website`

```json
{
  "business_name": "Ristorante Da Mario",
  "business_description": "Ristorante italiano nel centro di Roma...",
  "sections": ["hero", "about", "menu", "contact", "footer"],
  "style_preferences": {
    "primary_color": "#dc2626",
    "mood": "elegant, traditional"
  }
}
```

**Risposta:**
```json
{
  "success": true,
  "html_content": "<!DOCTYPE html>...</html>",
  "model_used": "moonshot-ai/kimi-k2.5",
  "tokens_input": 3100,
  "tokens_output": 4200,
  "cost_usd": 0.0125,
  "generation_time_ms": 45000
}
```

### Test Rapido

**POST** `/api/generate/test`

Endpoint di test con dati predefiniti.

---

## 🎨 Personalizzazione

### Modelli disponibili

Modifica in `.env`:

```bash
# Modelli supportati
AI_MODEL_PRIMARY=moonshot-ai/kimi-k2.5
AI_MODEL_FALLBACK=anthropic/claude-3.5-sonnet

# Alternative (vedi openrouter.ai/docs/models)
# AI_MODEL_PRIMARY=anthropic/claude-3-opus
# AI_MODEL_PRIMARY=openai/gpt-4o
# AI_MODEL_PRIMARY=google/gemini-pro-1.5
```

### Parametri generazione

```bash
AI_MAX_TOKENS=8000        # Lunghezza max output
AI_TEMPERATURE=0.7        # Creatività (0.0-1.0)
```

---

## 🛡️ Fallback Automatico

Se Kimi K2.5 fallisce (rate limit, downtime), il sistema automaticamente:
1. Riprova con Claude 3.5 Sonnet
2. Logga l'evento
3. Ritorna il risultato

**Tu paghi ~13 centesimi in più, ma il cliente riceve sempre il sito.**

---

## 📊 Monitoring

Ogni generazione traccia:
- Modello usato
- Token consumati
- Costo USD
- Tempo di generazione

Query database per analytics:
```sql
SELECT 
  model_used,
  COUNT(*) as total_generations,
  SUM(cost_usd) as total_cost,
  AVG(generation_time_ms) as avg_time
FROM generation_logs
GROUP BY model_used;
```

---

## 💡 Best Practices

1. **Cache risultati**: Non rigenerare stesso input
2. **Rate limiting**: Max 5 generazioni/min per utente
3. **Timeout**: 120 secondi max per generazione
4. **Sanitizzazione**: HTML sempre pulito prima di salvare

---

## 🔥 Troubleshooting

### "API key non valida"
- Verifica che inizi con `sk-or-v1-`
- Controlla non ci siano spazi

### "Rate limit exceeded"
- Aspetta 1 minuto
- Considera upgrade piano OpenRouter

### "Modello non trovato"
- Verifica nome modello su openrouter.ai/docs/models
- Kimi K2.5: `moonshot-ai/kimi-k2.5`

### Timeout
- Aumenta timeout in `ai_service.py` (default: 120s)
- Verifica connessione internet

---

## 📚 Risorse

- [OpenRouter Docs](https://openrouter.ai/docs)
- [Modelli disponibili](https://openrouter.ai/models)
- [Pricing](https://openrouter.ai/models)
- [Kimi K2.5](https://platform.moonshot.cn)

---

Pronto! Ora puoi generare siti web con AI 🚀

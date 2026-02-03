"""
Test API Diretta Kimi (Moonshot) - Usa il tuo abbonamento
Endpoint: https://api.moonshot.cn/v1
"""
import asyncio
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

import httpx


async def test_kimi_direct():
    """Test generazione con API diretta Kimi."""
    
    print("🚀 Test API Diretta Kimi (Moonshot)")
    print("=" * 50)
    
    # Verifica API key
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ ERRORE: KIMI_API_KEY non trovata!")
        return
    
    masked = api_key[:10] + "..." + api_key[-10:]
    print(f"✅ API Key Kimi: {masked}")
    
    # Header per Kimi
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prompt di sistema
    system_prompt = """You are an expert frontend developer specializing in Tailwind CSS.
Generate complete, production-ready HTML5 websites.

RULES:
1. Use semantic HTML5 with inline Tailwind CSS classes
2. Include Tailwind CDN: https://cdn.tailwindcss.com
3. Mobile-first responsive design
4. Include meta tags for SEO
5. Use placeholder images from placehold.co
6. Add smooth scroll navigation and mobile menu
7. Professional, modern design
8. Return ONLY HTML code between ```html and ``` tags"""

    # Prompt utente
    user_prompt = """Create a website for:

BUSINESS: Ristorante Da Mario
DESCRIPTION: Ristorante italiano autentico nel centro di Milano dal 1985. 
Specialità pasta fresca fatta in casa, pizza napoletana e pesce fresco.
Atmosfera elegante ma accogliente, perfetto per cene romantiche e cene di lavoro.

SECTIONS TO INCLUDE:
- Hero: Grande immagine ristorante, titolo "Ristorante Da Mario", tagline "L'autentica cucina italiana dal 1985", bottone "Prenota Ora"
- About: Storia del ristorante, chef, filosofia
- Menu: Antipasti, Primi, Secondi, Dolci (placeholder)
- Galleria: Grid di 6 immagini placeholder
- Contatti: Indirizzo Milano, telefono, email, form prenotazione
- Footer: Orari, social links, copyright

STYLE: Elegant, warm, traditional Italian, premium feel
COLORS: Deep red (#8B1a1a), Gold (#d4af37), Cream (#faf8f3)

Generate complete HTML file now."""

    # Payload per Kimi
    payload = {
        "model": "kimi-k2.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 6000,
        "temperature": 0.7
    }
    
    print("\n📋 Configurazione:")
    print("  Modello: kimi-k2.5")
    print("  Business: Ristorante Da Mario")
    print("  Endpoint: api.moonshot.cn/v1")
    
    print("\n⏳ Generazione in corso... (può richiedere 30-90 secondi)")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Estrai dati
            content = data["choices"][0]["message"]["content"]
            tokens_in = data.get("usage", {}).get("prompt_tokens", 0)
            tokens_out = data.get("usage", {}).get("completion_tokens", 0)
            
            # Estrai HTML
            import re
            html_match = re.search(r'```html\n(.*?)\n```', content, re.DOTALL)
            if html_match:
                html = html_match.group(1).strip()
            else:
                html = content.strip()
            
            # Calcola costo (prezzi Kimi: $0.60/M input, $2.50/M output)
            cost_usd = (tokens_in * 0.60 + tokens_out * 2.50) / 1_000_000
            
            print("✅ GENERAZIONE COMPLETATA!")
            print(f"\n📊 Statistiche:")
            print(f"  Token input: {tokens_in}")
            print(f"  Token output: {tokens_out}")
            print(f"  Costo stimato: ${cost_usd:.6f} USD")
            print(f"  ~€{cost_usd*0.92:.4f} EUR")
            
            # Salva file
            output_file = "sito_ristorante.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"\n💾 HTML salvato: {output_file}")
            print(f"📄 Dimensione: {len(html):,} caratteri")
            
            print(f"\n🌎 Per vedere il sito:")
            print(f"   1. Apri {output_file} nel browser")
            print(f"   2. O esegui: python -m http.server 8000")
            
            # Preview
            print("\n🔍 Preview (prime 800 caratteri):")
            print("-" * 50)
            print(html[:800])
            print("\n...")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ Errore HTTP {e.response.status_code}")
        print(f"Risposta: {e.response.text}")
        
        if e.response.status_code == 401:
            print("\n💡 API Key non valida o scaduta")
        elif e.response.status_code == 429:
            print("\n💡 Rate limit raggiunto - aspetta un momento")
            
    except Exception as e:
        print(f"❌ Errore: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_kimi_direct())

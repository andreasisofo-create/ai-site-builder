"""
Test semplificato OpenRouter - Genera un sito di esempio
Usa solo httpx, senza dipendenze dal progetto
"""
import asyncio
import os
from dotenv import load_dotenv

# Carica env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

import httpx


async def test_generation():
    """Test generazione sito con OpenRouter."""
    
    print("🚀 Test OpenRouter con Kimi K2.5")
    print("=" * 50)
    
    # Verifica API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("❌ ERRORE: API Key non configurata!")
        return
    
    print(f"✅ API Key: {api_key[:20]}...")
    
    # Header per OpenRouter
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sitebuilder.com",
        "X-Title": "AI Site Builder"
    }
    
    # Prompt di sistema
    system_prompt = """You are an expert frontend developer. Generate complete, production-ready HTML5 websites with Tailwind CSS.

RULES:
1. Use semantic HTML5 with inline Tailwind classes
2. Include Tailwind CDN: https://cdn.tailwindcss.com
3. Mobile-first responsive design
4. Include meta tags for SEO
5. Use placeholder images from placehold.co
6. Professional, modern design
7. Return ONLY HTML code between ```html and ``` tags"""

    # Prompt utente
    user_prompt = """Create a website for:

BUSINESS: Caffè Roma
DESCRIPTION: Caffè storico nel cuore di Roma dal 1950. Specialità caffè artigianale tostato sul momento e cornetti freschi fatti in casa.

SECTIONS TO INCLUDE:
- Hero with headline and CTA button
- About section with business story
- Menu section with coffee and pastries
- Contact section with form
- Footer with social links

STYLE: Vintage, warm, welcoming, traditional Italian café
PRIMARY COLOR: #8B4513 (brown)

Generate the complete HTML file now."""

    # Payload
    payload = {
        "model": "moonshot-ai/kimi-k2.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }
    
    print("\n📋 Configurazione:")
    print("  Modello: moonshot-ai/kimi-k2.5")
    print("  Business: Caffè Roma")
    print("  Sezioni: Hero, About, Menu, Contact, Footer")
    
    print("\n⏳ Generazione in corso... (30-60 secondi)")
    print("-" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Estrai dati
            content = data["choices"][0]["message"]["content"]
            tokens_in = data.get("usage", {}).get("prompt_tokens", 0)
            tokens_out = data.get("usage", {}).get("completion_tokens", 0)
            model_used = data.get("model", "unknown")
            
            # Estrai HTML
            import re
            html_match = re.search(r'```html\n(.*?)\n```', content, re.DOTALL)
            if html_match:
                html = html_match.group(1).strip()
            else:
                html = content.strip()
            
            # Calcola costo
            cost = (tokens_in * 0.60 + tokens_out * 2.40) / 1_000_000
            
            print("✅ GENERAZIONE COMPLETATA!")
            print(f"\n📊 Statistiche:")
            print(f"  Modello: {model_used}")
            print(f"  Token input: {tokens_in}")
            print(f"  Token output: {tokens_out}")
            print(f"  Costo: ${cost:.6f} USD (~€{cost*0.92:.4f})")
            
            # Salva file
            output_file = "sito_generato.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"\n💾 HTML salvato in: {output_file}")
            print(f"📄 Dimensione: {len(html)} caratteri")
            
            print(f"\n🌎 Per vedere il sito:")
            print(f"   1. Apri il file {output_file} nel browser")
            print(f"   2. Oppure esegui: python -m http.server 8000")
            print(f"   3. Vai su http://localhost:8000")
            
            # Preview prime righe
            print("\n🔍 Preview HTML (prime 500 caratteri):")
            print("-" * 50)
            print(html[:500])
            print("...")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ Errore HTTP {e.response.status_code}")
        print(f"Dettagli: {e.response.text}")
    except Exception as e:
        print(f"❌ Errore: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_generation())

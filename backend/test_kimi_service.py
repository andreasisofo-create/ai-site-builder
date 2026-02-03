"""
Test completo del servizio AI con Kimi API diretta.
Usa il servizio AI completo del backend.
"""
import asyncio
import os
import sys

# Setup path per importare dal backend
sys.path.insert(0, os.path.dirname(__file__))

# Carica env
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

from app.services.ai_service import AIService


async def test_generate_restaurant():
    """Test: Genera sito ristorante completo."""
    
    print("🍝 Test Generazione Sito Ristorante")
    print("=" * 60)
    
    # Verifica API key
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ ERRORE: KIMI_API_KEY non trovata in .env!")
        print("   Aggiungi: KIMI_API_KEY=sk-tua-chiave")
        return
    
    print(f"✅ API Key configurata: {api_key[:15]}...")
    
    # Dati del ristorante
    business = {
        "name": "Trattoria Da Mario",
        "description": """Ristorante italiano autentico nel centro storico di Roma. 
Dal 1985 serviamo piatti della tradizione romana con ingredienti freschi e locali. 
Specialità: carbonara, cacio e pepe, saltimbocca alla romana. 
Atmosfera familiare e accogliente, perfetto per cene in famiglia e romantiche.""",
        "sections": ["hero", "about", "menu", "gallery", "contact", "footer"],
        "style": {
            "primary_color": "#8B1a1a",
            "secondary_color": "#d4af37",
            "mood": "elegant, traditional, warm, Italian"
        },
        "contact": {
            "address": "Via del Corso 123, 00186 Roma",
            "phone": "+39 06 1234 5678",
            "email": "info@trattoriamario.it",
            "hours": "Lun-Sab: 12:00-15:00, 19:00-23:00"
        }
    }
    
    print(f"\n📋 Dati business:")
    print(f"   Nome: {business['name']}")
    print(f"   Sezioni: {', '.join(business['sections'])}")
    print(f"   Stile: {business['style']['mood']}")
    
    print(f"\n⏳ Generazione in corso con Kimi K2.5...")
    print("   (Questo può richiedere 30-90 secondi)")
    print("-" * 60)
    
    # Crea servizio e genera
    ai = AIService()
    
    result = await ai.generate_website(
        business_name=business["name"],
        business_description=business["description"],
        sections=business["sections"],
        style_preferences=business["style"],
        contact_info=business["contact"]
    )
    
    if result.get("success"):
        print("✅ GENERAZIONE COMPLETATA!")
        print(f"\n📊 Statistiche:")
        print(f"   Modello: {result['model_used']}")
        print(f"   Token: {result['tokens_input']:,} in / {result['tokens_output']:,} out")
        print(f"   Costo: ${result['cost_usd']:.6f} USD (~€{result['cost_usd']*0.92:.4f})")
        print(f"   Tempo: {result['generation_time_ms']/1000:.1f} secondi")
        
        # Salva file
        filename = "ristorante_da_mario.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result['html_content'])
        
        size_kb = len(result['html_content']) / 1024
        print(f"\n💾 File salvato: {filename}")
        print(f"   Dimensione: {size_kb:.1f} KB")
        
        print(f"\n🌎 Per visualizzare:")
        print(f"   1. Apri {filename} nel browser")
        print(f"   2. O esegui: python -m http.server 8000")
        print(f"   3. Vai su http://localhost:8000/{filename}")
        
        # Preview
        print(f"\n🔍 Preview codice (prime 600 caratteri):")
        print("-" * 60)
        preview = result['html_content'][:600].replace('\n', ' ')
        print(preview + "...")
        
        return result
        
    else:
        print(f"❌ ERRORE: {result.get('error')}")
        if result.get('details'):
            print(f"   Dettagli: {result['details']}")
        return None


async def test_analyze_image():
    """Test: Analisi immagine di riferimento."""
    
    print("\n\n🖼️  Test Analisi Immagine (Vision)")
    print("=" * 60)
    
    # URL immagine di esempio (screenshot sito)
    image_url = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800"
    
    print(f"Immagine: {image_url[:50]}...")
    print("Analisi stile in corso...")
    
    ai = AIService()
    result = await ai.analyze_image_style(image_url)
    
    if result.get("success"):
        print("✅ Analisi completata!")
        print(f"   Token usati: {result['tokens_used']}")
        print(f"   Costo: ${result['cost_usd']:.6f}")
        print(f"\n📊 Risultato analisi:")
        print(result['analysis'])
    else:
        print(f"❌ Errore: {result.get('error')}")


async def test_refinement():
    """Test: Modifica sito esistente."""
    
    print("\n\n✏️  Test Refinement (Modifica)")
    print("=" * 60)
    
    # HTML semplice di esempio
    html_sample = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body class="bg-white">
  <h1 class="text-2xl">Benvenuti</h1>
  <button class="bg-blue-500">Contattaci</button>
</body>
</html>"""
    
    print("HTML originale:")
    print(html_sample[:200] + "...")
    print("\nRichiesta: 'Cambia il bottone in rosso e più grande'")
    
    ai = AIService()
    result = await ai.refine_page(
        current_html=html_sample,
        modification_request="Cambia il bottone in colore rosso (red-600) e più grande (text-lg, py-3, px-6)"
    )
    
    if result.get("success"):
        print("✅ Modifica completata!")
        print(f"   Costo: ${result['cost_usd']:.6f}")
        print("\nPreview risultato:")
        preview = result['html_content'][:300].replace('\n', ' ')
        print(preview + "...")
    else:
        print(f"❌ Errore: {result.get('error')}")


async def main():
    """Esegue tutti i test."""
    
    print("🚀 Test Completo Servizio AI - Kimi API Diretta")
    print("=" * 60)
    print()
    
    # Test 1: Generazione sito completo
    result = await test_generate_restaurant()
    
    if not result:
        print("\n⚠️  Test principale fallito. Arresto.")
        return
    
    # Test 2: Analisi immagine (opzionale)
    try:
        await test_analyze_image()
    except Exception as e:
        print(f"\n⚠️  Test immagine saltato: {e}")
    
    # Test 3: Refinement (opzionale)
    try:
        await test_refinement()
    except Exception as e:
        print(f"\n⚠️  Test refinement saltato: {e}")
    
    print("\n" + "=" * 60)
    print("✨ Test completati!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

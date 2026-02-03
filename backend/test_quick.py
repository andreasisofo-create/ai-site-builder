"""
Test rapido OpenRouter - Genera un sito di esempio
"""
import asyncio
import os
from dotenv import load_dotenv

# Carica env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Setup path
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import AIService


async def main():
    print("🚀 Test OpenRouter con Kimi K2.5")
    print("=" * 50)
    
    # Verifica API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ API Key non trovata in .env")
        return
    
    masked_key = api_key[:20] + "..." + api_key[-10:]
    print(f"✅ API Key: {masked_key}")
    
    # Test dati
    print("\n📋 Dati di test:")
    print("  Business: Caffè Roma")
    print("  Sezioni: Hero, About, Menu, Contact")
    print("  Stile: Vintage, accogliente")
    
    # Genera
    print("\n⏳ Generazione in corso... (30-60 secondi)")
    print("-" * 50)
    
    ai = AIService()
    
    result = await ai.generate_website(
        business_name="Caffè Roma",
        business_description="""Caffè storico nel cuore di Roma dal 1950. 
Specialità caffè artigianale tostato sul momento, cornetti freschi fatti in casa,
e cioccolata calda cremosa. Atmosfera accogliente e tradizionale.""",
        sections=["hero", "about", "menu", "contact", "footer"],
        style_preferences={
            "primary_color": "#8B4513",
            "mood": "vintage, warm, welcoming"
        }
    )
    
    if result.get("success"):
        print("✅ SUCCESSO!")
        print(f"\n📊 Risultati:")
        print(f"  Modello: {result['model_used']}")
        print(f"  Token: {result['tokens_input']} in / {result['tokens_output']} out")
        print(f"  Costo: ${result['cost_usd']:.6f} USD (~€{result['cost_usd']*0.92:.4f})")
        print(f"  Tempo: {result['generation_time_ms']/1000:.1f}s")
        
        # Salva file
        output_file = "test_sito_generato.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result['html_content'])
        
        print(f"\n💾 File salvato: {output_file}")
        print(f"📄 Dimensione: {len(result['html_content'])} caratteri")
        print(f"\n🌎 Per vedere il sito:")
        print(f"   1. Apri {output_file} nel browser")
        print(f"   2. Oppure usa: python -m http.server 8000")
        
    else:
        print(f"❌ ERRORE: {result.get('error')}")
        if result.get('details'):
            print(f"Dettagli: {result['details']}")


if __name__ == "__main__":
    asyncio.run(main())

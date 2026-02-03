"""
Script di test per l'integrazione OpenRouter.
Da eseguire con: python test_ai.py
"""

import asyncio
import os
from dotenv import load_dotenv

# Load env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Import dopo aver caricato env
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import AIService


async def test_generation():
    """Test generazione sito."""
    
    print("🧪 Test Generazione AI con OpenRouter")
    print("=" * 50)
    
    # Verifica API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("❌ ERRORE: OPENROUTER_API_KEY non configurata!")
        print("\nPer ottenere una API key:")
        print("1. Vai su https://openrouter.ai/keys")
        print("2. Crea un account")
        print("3. Genera una API key")
        print("4. Aggiungila al file .env")
        return
    
    print(f"✅ API Key configurata: {api_key[:20]}...")
    
    # Crea servizio
    ai = AIService()
    
    # Test dati
    business_name = "Caffè Roma"
    business_description = """Caffè storico nel cuore di Roma, dal 1950. 
Specialità caffè artigianale tostato sul momento e cornetti freschi 
fatti in casa ogni mattina. Atmosfera accogliente e tradizionale."""
    
    sections = ["hero", "about", "menu", "gallery", "contact", "footer"]
    
    style_preferences = {
        "primary_color": "#8B4513",
        "mood": "vintage, warm, welcoming, traditional"
    }
    
    print(f"\n📋 Business: {business_name}")
    print(f"📄 Sezioni: {', '.join(sections)}")
    print(f"🎨 Stile: {style_preferences['mood']}")
    print("\n⏳ Generazione in corso... (può richiedere 30-60 secondi)")
    print("-" * 50)
    
    try:
        result = await ai.generate_website(
            business_name=business_name,
            business_description=business_description,
            sections=sections,
            style_preferences=style_preferences
        )
        
        if result.get("success"):
            print("✅ Generazione completata!")
            print(f"\n📊 Statistiche:")
            print(f"   Modello: {result['model_used']}")
            print(f"   Token input: {result['tokens_input']}")
            print(f"   Token output: {result['tokens_output']}")
            print(f"   Costo: ${result['cost_usd']:.6f} USD")
            print(f"   Tempo: {result['generation_time_ms']}ms")
            
            # Salva HTML in file
            output_file = "test_output.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result['html_content'])
            
            print(f"\n💾 HTML salvato in: {output_file}")
            print(f"📄 Dimensione: {len(result['html_content'])} caratteri")
            
            # Preview prime righe
            print("\n🔍 Preview HTML (prime 500 char):")
            print(result['html_content'][:500] + "...")
            
        else:
            print(f"❌ Errore: {result.get('error')}")
            if result.get('details'):
                print(f"Dettagli: {result['details']}")
                
    except Exception as e:
        print(f"❌ Eccezione: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_with_fallback():
    """Test con modello fallback."""
    
    print("\n\n🧪 Test con Modello Fallback (Claude)")
    print("=" * 50)
    
    ai = AIService()
    
    result = await ai.generate_website(
        business_name="Tech Startup",
        business_description="Innovative AI solutions for businesses",
        sections=["hero", "about", "services", "contact"],
        use_fallback=True
    )
    
    if result.get("success"):
        print(f"✅ Generazione con fallback riuscita!")
        print(f"   Modello: {result['model_used']}")
        print(f"   Costo: ${result['cost_usd']:.6f} USD")
    else:
        print(f"❌ Errore: {result.get('error')}")


async def test_cost_comparison():
    """Confronta costi tra modelli."""
    
    print("\n\n💰 Confronto Costi Modelli")
    print("=" * 50)
    
    # Stima per un sito tipico
    tokens_input = 3000
    tokens_output = 4000
    
    models = {
        "Kimi K2.5": {"input": 0.60, "output": 2.40},
        "Claude 3.5 Sonnet": {"input": 3.00, "output": 15.00},
        "GPT-4o": {"input": 5.00, "output": 15.00}
    }
    
    print(f"Stima per sito ({tokens_input} input + {tokens_output} output tokens):\n")
    
    for model, prices in models.items():
        input_cost = (tokens_input / 1_000_000) * prices["input"]
        output_cost = (tokens_output / 1_000_000) * prices["output"]
        total = input_cost + output_cost
        
        print(f"{model:20} ${total:.4f} USD (${input_cost:.4f} in + ${output_cost:.4f} out)")


if __name__ == "__main__":
    print("🚀 OpenRouter AI Test Suite")
    print("=" * 50)
    
    # Esegui test
    asyncio.run(test_generation())
    
    # Opzionale: test fallback
    # asyncio.run(test_with_fallback())
    
    # Mostra confronto costi
    asyncio.run(test_cost_comparison())
    
    print("\n✨ Test completati!")

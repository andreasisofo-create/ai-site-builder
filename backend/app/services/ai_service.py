"""
Servizio AI per generazione siti web usando Kimi API diretta.
Endpoint: https://api.moonshot.cn/v1
Modello: kimi-k2.5
"""

import httpx
import json
import time
from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Servizio per generazione AI tramite Kimi API diretta."""
    
    def __init__(self):
        self.api_key = settings.KIMI_API_KEY
        self.api_url = "https://api.moonshot.cn/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_website(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Genera un sito web completo usando Kimi K2.5.
        
        Args:
            business_name: Nome del business
            business_description: Descrizione dettagliata
            sections: Lista sezioni da includere
            style_preferences: Preferenze stile (colori, font, mood)
            reference_analysis: Analisi stile da immagine di riferimento
            logo_url: URL del logo da includere
            contact_info: Info contatto (indirizzo, telefono, email)
            
        Returns:
            Dict con html_content, tokens_usati, costo_stimato
        """
        
        # Costruisci il prompt di sistema
        system_prompt = self._build_system_prompt()
        
        # Costruisci il prompt utente
        user_prompt = self._build_user_prompt(
            business_name=business_name,
            business_description=business_description,
            sections=sections,
            style_preferences=style_preferences,
            reference_analysis=reference_analysis,
            logo_url=logo_url,
            contact_info=contact_info
        )
        
        # Payload per Kimi API
        payload = {
            "model": "kimi-k2.5",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 6000,
            "temperature": 0.7
        }
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Estrai risultati
                html_content = data["choices"][0]["message"]["content"]
                tokens_input = data.get("usage", {}).get("prompt_tokens", 0)
                tokens_output = data.get("usage", {}).get("completion_tokens", 0)
                generation_time = int((time.time() - start_time) * 1000)
                
                # Estrai HTML dal markdown se presente
                html_content = self._extract_html_from_markdown(html_content)
                
                # Calcola costo (prezzi Kimi: $0.60/M input, $2.50/M output)
                cost = self._calculate_cost(tokens_input, tokens_output)
                
                return {
                    "success": True,
                    "html_content": html_content,
                    "model_used": "kimi-k2.5",
                    "tokens_input": tokens_input,
                    "tokens_output": tokens_output,
                    "cost_usd": cost,
                    "generation_time_ms": generation_time
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Kimi API: {e.response.status_code} - {e.response.text}")
            
            # Gestione errori specifici
            error_msg = f"API error: {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg = "API Key non valida o scaduta"
            elif e.response.status_code == 429:
                error_msg = "Rate limit raggiunto. Riprova tra qualche secondo."
            elif e.response.status_code >= 500:
                error_msg = "Errore server Kimi. Riprova più tardi."
            
            return {
                "success": False,
                "error": error_msg,
                "details": e.response.text
            }
            
        except Exception as e:
            logger.exception("Errore durante generazione AI")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_system_prompt(self) -> str:
        """Costruisce il prompt di sistema per Kimi."""
        return """You are an expert frontend developer and web designer specializing in Tailwind CSS.
Your task is to generate complete, production-ready HTML5 websites.

RULES:
1. Generate semantic HTML5 with inline Tailwind CSS classes
2. Use Tailwind CDN: https://cdn.tailwindcss.com
3. Mobile-first responsive design
4. Include all sections requested by the user
5. Use placeholder images from https://placehold.co with descriptive text
6. Include a working contact form with proper form structure
7. Add smooth scroll navigation and mobile hamburger menu
8. Include meta tags for SEO (charset, viewport, description, OG tags)
9. Add favicon placeholder
10. NO external CSS files - all styles inline with Tailwind
11. NO JavaScript frameworks - vanilla JS only for menu
12. Professional, modern design aesthetic
13. Use Italian language for content if business is Italian

OUTPUT FORMAT:
Return ONLY the complete HTML code between ```html and ``` tags. No explanations before or after."""
    
    def _build_user_prompt(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None
    ) -> str:
        """Costruisce il prompt utente specifico."""
        
        prompt = f"""Create a professional website for:

BUSINESS NAME: {business_name}

DESCRIPTION: {business_description}

SECTIONS TO INCLUDE:
"""
        
        for section in sections:
            prompt += f"- {section}\n"
        
        # Aggiungi stile
        if style_preferences:
            prompt += f"\nSTYLE PREFERENCES:\n"
            if "primary_color" in style_preferences:
                prompt += f"- Primary color: {style_preferences['primary_color']}\n"
            if "secondary_color" in style_preferences:
                prompt += f"- Secondary color: {style_preferences['secondary_color']}\n"
            if "font_family" in style_preferences:
                prompt += f"- Font: {style_preferences['font_family']}\n"
            if "mood" in style_preferences:
                prompt += f"- Mood/Style: {style_preferences['mood']}\n"
        
        if reference_analysis:
            prompt += f"\nSTYLE ANALYSIS FROM REFERENCE IMAGE:\n{reference_analysis}\n"
        
        if logo_url:
            prompt += f"\nLOGO URL: {logo_url}\n"
        
        if contact_info:
            prompt += f"\nCONTACT INFORMATION:\n"
            for key, value in contact_info.items():
                prompt += f"- {key}: {value}\n"
        
        prompt += """

REQUIREMENTS:
- One-page website with smooth scroll navigation
- Hero section with compelling headline and CTA button
- Professional color scheme matching the business
- Contact form in the contact section (use proper HTML form)
- Mobile responsive (hamburger menu on mobile)
- Footer with social links placeholder
- Content in Italian if business is Italian

Generate the complete HTML file now."""
        
        return prompt
    
    def _extract_html_from_markdown(self, content: str) -> str:
        """Estrae HTML dal markdown se presente."""
        import re
        
        # Cerca blocchi ```html ... ```
        html_match = re.search(r'```html\n(.*?)\n```', content, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()
        
        # Cerca blocchi ``` ... ```
        code_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Se non trova blocchi, ritorna tutto
        return content.strip()
    
    def _calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """Calcola il costo stimato in USD."""
        # Prezzi Kimi: $0.60 per 1M input, $2.50 per 1M output
        input_cost = (tokens_input / 1_000_000) * 0.60
        output_cost = (tokens_output / 1_000_000) * 2.50
        
        return round(input_cost + output_cost, 6)
    
    async def analyze_image_style(self, image_url: str) -> Dict[str, Any]:
        """
        Analizza un'immagine di riferimento per estrarre stile e colori.
        Usa la vision capability di Kimi.
        """
        
        prompt = """Analyze this website screenshot and describe:
1. Color palette (primary, secondary, accent colors in hex format)
2. Typography style (modern, classic, bold, minimal, elegant)
3. Layout structure (clean, busy, grid-based, fluid, centered)
4. Overall mood/atmosphere (professional, playful, elegant, corporate, cozy)
5. Key design elements that stand out

Be specific and concise."""
        
        payload = {
            "model": "kimi-k2.5",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                analysis = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                cost = (tokens / 1_000_000) * 0.60  # Vision usa stesso prezzo
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "tokens_used": tokens,
                    "cost_usd": round(cost, 6)
                }
                
        except Exception as e:
            logger.exception("Errore analisi immagine")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def refine_page(
        self,
        current_html: str,
        modification_request: str,
        section_to_modify: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modifica una pagina esistente in base alla richiesta dell'utente.
        
        Args:
            current_html: HTML attuale della pagina
            modification_request: Cosa modificare (es. "Cambia il colore in blu")
            section_to_modify: Sezione specifica da modificare (opzionale)
        """
        
        if section_to_modify:
            prompt = f"""Modify the {section_to_modify} section of this HTML website.

CURRENT HTML:
{current_html}

MODIFICATION REQUEST:
{modification_request}

Instructions:
1. Modify ONLY the {section_to_modify} section
2. Keep all other sections exactly as they are
3. Return the COMPLETE HTML file with the modification
4. Use the same styling approach (Tailwind CSS)
5. Return ONLY the HTML code between ```html and ``` tags"""
        else:
            prompt = f"""Modify this HTML website according to the request.

CURRENT HTML:
{current_html}

MODIFICATION REQUEST:
{modification_request}

Instructions:
1. Apply the requested changes
2. Keep the overall structure and style consistent
3. Return the COMPLETE modified HTML file
4. Return ONLY the HTML code between ```html and ``` tags"""
        
        payload = {
            "model": "kimi-k2.5",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 6000,
            "temperature": 0.7
        }
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                html_content = data["choices"][0]["message"]["content"]
                tokens_input = data.get("usage", {}).get("prompt_tokens", 0)
                tokens_output = data.get("usage", {}).get("completion_tokens", 0)
                generation_time = int((time.time() - start_time) * 1000)
                
                html_content = self._extract_html_from_markdown(html_content)
                cost = self._calculate_cost(tokens_input, tokens_output)
                
                return {
                    "success": True,
                    "html_content": html_content,
                    "model_used": "kimi-k2.5",
                    "tokens_input": tokens_input,
                    "tokens_output": tokens_output,
                    "cost_usd": cost,
                    "generation_time_ms": generation_time
                }
                
        except Exception as e:
            logger.exception("Errore durante refinement")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
ai_service = AIService()

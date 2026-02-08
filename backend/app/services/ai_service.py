"""
Servizio AI per generazione siti web usando Kimi API diretta.
Endpoint: https://api.moonshot.cn/v1
Modello: kimi-k2.5

Pipeline a 3 step:
  Step 1: Analizza immagine di riferimento (se presente)
  Step 2: Genera HTML completo
  Step 3: Revisiona e correggi HTML
"""

import httpx
import re
import time
from typing import Optional, Dict, Any, List, Callable
from app.core.config import settings
from app.services.sanitizer import sanitize_input, sanitize_output, sanitize_refine_input
import logging

logger = logging.getLogger(__name__)

# Callback type per progress updates
ProgressCallback = Optional[Callable[[int, str], None]]


class AIService:
    """Servizio per generazione AI tramite Kimi API diretta."""

    def __init__(self):
        self.api_url = settings.KIMI_API_URL or "https://api.moonshot.ai/v1"

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.active_api_key}",
            "Content-Type": "application/json",
        }

    async def _call_kimi(
        self,
        messages: list,
        max_tokens: int = 8000,
        temperature: float = 0.6,
        timeout: float = 180.0,
    ) -> Dict[str, Any]:
        """Chiamata base a Kimi API. Ritorna response dict o errore."""
        payload = {
            "model": "kimi-k2.5",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}

        except httpx.HTTPStatusError as e:
            error_msg = f"API error: {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg = "API Key non valida o scaduta"
            elif e.response.status_code == 429:
                error_msg = "Rate limit raggiunto. Riprova tra qualche secondo."
            elif e.response.status_code >= 500:
                error_msg = "Errore server Kimi. Riprova più tardi."

            logger.error(f"HTTP error from Kimi API: {e.response.status_code} - {e.response.text}")
            return {"success": False, "error": error_msg}

        except Exception as e:
            logger.exception("Errore chiamata Kimi API")
            return {"success": False, "error": str(e)}

    # =========================================================
    # PIPELINE 3-STEP: generate_website_pipeline
    # =========================================================

    async def generate_website_pipeline(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_image_url: Optional[str] = None,
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None,
        on_progress: ProgressCallback = None,
    ) -> Dict[str, Any]:
        """
        Pipeline completa a 3 step per generazione sito.

        Step 1: Analizza riferimento (se immagine presente)
        Step 2: Genera HTML
        Step 3: Revisiona e correggi

        Args:
            on_progress: callback(step_number, message) per aggiornare progresso
        """
        start_time = time.time()
        total_tokens_in = 0
        total_tokens_out = 0

        # Sanitizza input
        try:
            business_name, business_description, sections = sanitize_input(
                business_name, business_description, sections
            )
        except ValueError as e:
            return {"success": False, "error": str(e)}

        # ---- STEP 1: Analizza Riferimento ----
        if reference_image_url and not reference_analysis:
            if on_progress:
                on_progress(1, "Analisi immagine di riferimento...")

            logger.info("Pipeline Step 1: Analyzing reference image")
            analysis_result = await self.analyze_image_style(reference_image_url)

            if analysis_result.get("success"):
                reference_analysis = analysis_result["analysis"]
                total_tokens_in += analysis_result.get("tokens_used", 0)
                logger.info(f"Step 1 complete: got style analysis ({len(reference_analysis)} chars)")
            else:
                logger.warning(f"Step 1 failed: {analysis_result.get('error')}. Continuing without reference.")
        elif not reference_image_url:
            if on_progress:
                on_progress(1, "Nessuna immagine di riferimento, salto analisi...")
            logger.info("Pipeline Step 1: Skipped (no reference image)")

        # ---- STEP 2: Genera HTML ----
        if on_progress:
            on_progress(2, "Generazione HTML del sito...")

        logger.info("Pipeline Step 2: Generating HTML")
        gen_result = await self.generate_website(
            business_name=business_name,
            business_description=business_description,
            sections=sections,
            style_preferences=style_preferences,
            reference_analysis=reference_analysis,
            logo_url=logo_url,
            contact_info=contact_info,
        )

        if not gen_result.get("success"):
            return gen_result

        html_content = gen_result["html_content"]
        total_tokens_in += gen_result.get("tokens_input", 0)
        total_tokens_out += gen_result.get("tokens_output", 0)
        logger.info(f"Step 2 complete: HTML generated ({len(html_content)} chars)")

        # ---- STEP 3: Revisiona e Correggi ----
        if on_progress:
            on_progress(3, "Revisione e ottimizzazione...")

        logger.info("Pipeline Step 3: Reviewing and fixing HTML")
        review_result = await self._review_html(html_content, business_name)

        if review_result.get("success"):
            html_content = review_result["html_content"]
            total_tokens_in += review_result.get("tokens_input", 0)
            total_tokens_out += review_result.get("tokens_output", 0)
            logger.info(f"Step 3 complete: HTML reviewed ({len(html_content)} chars)")
        else:
            logger.warning(f"Step 3 failed: {review_result.get('error')}. Using Step 2 output.")

        # Sanitizza output finale
        html_content = sanitize_output(html_content)

        generation_time = int((time.time() - start_time) * 1000)
        cost = self._calculate_cost(total_tokens_in, total_tokens_out)

        return {
            "success": True,
            "html_content": html_content,
            "model_used": "kimi-k2.5",
            "tokens_input": total_tokens_in,
            "tokens_output": total_tokens_out,
            "cost_usd": cost,
            "generation_time_ms": generation_time,
            "pipeline_steps": 3,
        }

    # =========================================================
    # STEP 2: Genera HTML (metodo originale, preservato)
    # =========================================================

    async def generate_website(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Genera un sito web completo usando Kimi K2.5 (singola chiamata)."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            business_name=business_name,
            business_description=business_description,
            sections=sections,
            style_preferences=style_preferences,
            reference_analysis=reference_analysis,
            logo_url=logo_url,
            contact_info=contact_info,
        )

        start_time = time.time()
        result = await self._call_kimi(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=8000,
            temperature=0.6,
        )

        if not result["success"]:
            return result

        data = result["data"]
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
            "generation_time_ms": generation_time,
        }

    # =========================================================
    # STEP 3: Revisiona HTML
    # =========================================================

    async def _review_html(self, html: str, business_name: str) -> Dict[str, Any]:
        """
        Step 3: Revisiona l'HTML generato e correggi errori.
        Controlla responsive, accessibilità, struttura, performance.
        """
        prompt = f"""Review and fix this HTML website for "{business_name}".

CURRENT HTML:
{html}

CHECK AND FIX:
1. Responsive design: ensure all sections work on mobile (375px) and desktop (1440px)
2. Navigation: hamburger menu must work with vanilla JS toggle
3. All images must have alt text
4. Color contrast: ensure text is readable on its background
5. All links must have href attributes (use # for placeholder links)
6. Contact form must have proper input names, labels, and a submit button
7. Footer must include copyright text
8. Smooth scroll must work for navigation links
9. Remove any broken or incomplete HTML tags
10. Ensure the Tailwind CDN script tag is present in <head>

IMPORTANT:
- Return the COMPLETE fixed HTML file
- If no issues found, return the HTML as-is
- Return ONLY the HTML code between ```html and ``` tags
- Do NOT add explanations"""

        result = await self._call_kimi(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            temperature=0.3,  # Bassa temperatura per review deterministico
            timeout=180.0,
        )

        if not result["success"]:
            return result

        data = result["data"]
        html_content = data["choices"][0]["message"]["content"]
        tokens_input = data.get("usage", {}).get("prompt_tokens", 0)
        tokens_output = data.get("usage", {}).get("completion_tokens", 0)

        html_content = self._extract_html_from_markdown(html_content)

        return {
            "success": True,
            "html_content": html_content,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
        }

    # =========================================================
    # STEP 1: Analizza Immagine Riferimento
    # =========================================================

    async def analyze_image_style(self, image_url: str) -> Dict[str, Any]:
        """Analizza un'immagine di riferimento per estrarre stile e colori."""
        prompt = """Analyze this website screenshot and describe:
1. Color palette (primary, secondary, accent colors in hex format)
2. Typography style (modern, classic, bold, minimal, elegant)
3. Layout structure (clean, busy, grid-based, fluid, centered)
4. Overall mood/atmosphere (professional, playful, elegant, corporate, cozy)
5. Key design elements that stand out

Be specific and concise. Format as a structured list."""

        payload = {
            "model": "kimi-k2.5",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "max_tokens": 1000,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                analysis = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                cost = (tokens / 1_000_000) * 0.60

                return {
                    "success": True,
                    "analysis": analysis,
                    "tokens_used": tokens,
                    "cost_usd": round(cost, 6),
                }

        except Exception as e:
            logger.exception("Errore analisi immagine")
            return {"success": False, "error": str(e)}

    # =========================================================
    # REFINE: Modifica pagina via chat
    # =========================================================

    async def refine_page(
        self,
        current_html: str,
        modification_request: str,
        section_to_modify: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modifica una pagina esistente in base alla richiesta dell'utente."""
        # Sanitizza input
        modification_request = sanitize_refine_input(modification_request)

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

        start_time = time.time()
        result = await self._call_kimi(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            temperature=0.6,
            timeout=180.0,
        )

        if not result["success"]:
            return result

        data = result["data"]
        html_content = data["choices"][0]["message"]["content"]
        tokens_input = data.get("usage", {}).get("prompt_tokens", 0)
        tokens_output = data.get("usage", {}).get("completion_tokens", 0)
        generation_time = int((time.time() - start_time) * 1000)

        html_content = self._extract_html_from_markdown(html_content)
        html_content = sanitize_output(html_content)
        cost = self._calculate_cost(tokens_input, tokens_output)

        return {
            "success": True,
            "html_content": html_content,
            "model_used": "kimi-k2.5",
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost_usd": cost,
            "generation_time_ms": generation_time,
        }

    # =========================================================
    # UTILITY
    # =========================================================

    def _build_system_prompt(self) -> str:
        """Prompt di sistema migliorato per generazione HTML."""
        return """You are an expert frontend developer and web designer specializing in Tailwind CSS.
Your task is to generate complete, production-ready HTML5 websites.

RULES:
1. Generate semantic HTML5 with Tailwind CSS utility classes
2. Use Tailwind CDN: <script src="https://cdn.tailwindcss.com"></script>
3. Mobile-first responsive design (test at 375px, 768px, 1440px breakpoints)
4. Include ALL sections requested by the user
5. Use placeholder images from https://placehold.co with descriptive alt text
6. Include a working contact form with proper labels, names, and submit button
7. Add smooth scroll navigation with working mobile hamburger menu (vanilla JS)
8. Include meta tags: charset UTF-8, viewport, description, og:title, og:description
9. Add favicon placeholder link
10. NO external CSS files - all styles via Tailwind utility classes
11. NO JavaScript frameworks - vanilla JS only for menu toggle and smooth scroll
12. Professional, modern design with consistent spacing
13. Use Italian language for all content text
14. Ensure proper color contrast for accessibility (WCAG AA)
15. Use Google Fonts via CDN link if a specific font is requested
16. All interactive elements must have hover/focus states
17. Images should use lazy loading (loading="lazy")

OUTPUT FORMAT:
Return ONLY the complete HTML code between ```html and ``` tags. No explanations."""

    def _build_user_prompt(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None,
    ) -> str:
        """Costruisce il prompt utente specifico."""
        prompt = f"""Create a professional one-page website for:

BUSINESS NAME: {business_name}

DESCRIPTION: {business_description}

SECTIONS TO INCLUDE:
"""
        for section in sections:
            prompt += f"- {section}\n"

        if style_preferences:
            prompt += "\nSTYLE PREFERENCES:\n"
            if "primary_color" in style_preferences:
                prompt += f"- Primary color: {style_preferences['primary_color']}\n"
            if "secondary_color" in style_preferences:
                prompt += f"- Secondary color: {style_preferences['secondary_color']}\n"
            if "font_family" in style_preferences:
                prompt += f"- Font: {style_preferences['font_family']}\n"
            if "mood" in style_preferences:
                prompt += f"- Mood/Style: {style_preferences['mood']}\n"

        if reference_analysis:
            prompt += f"\nSTYLE REFERENCE (from analyzed screenshot):\n{reference_analysis}\n"
            prompt += "Use this analysis to match the visual style of the reference image.\n"

        if logo_url:
            prompt += f"\nLOGO: Use this image URL for the logo: {logo_url}\n"

        if contact_info:
            prompt += "\nCONTACT INFORMATION:\n"
            for key, value in contact_info.items():
                prompt += f"- {key}: {value}\n"

        prompt += """
REQUIREMENTS:
- One-page website with smooth scroll navigation between sections
- Hero section with compelling headline, subtitle, and CTA button
- Professional color scheme matching the business type
- Contact section with a proper HTML form (name, email, message fields)
- Fully responsive: mobile hamburger menu, stacked layout on small screens
- Footer with business name, copyright, and social links placeholders
- All content in Italian
- Minimum 5 sections for a complete, professional feel

Generate the complete HTML file now."""

        return prompt

    def _extract_html_from_markdown(self, content: str) -> str:
        """Estrae HTML dal markdown se presente."""
        # Cerca blocchi ```html ... ```
        html_match = re.search(r'```html\n(.*?)\n```', content, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()

        # Cerca blocchi ``` ... ```
        code_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        return content.strip()

    def _calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """Calcola il costo stimato in USD (prezzi Kimi K2.5)."""
        input_cost = (tokens_input / 1_000_000) * 0.60
        output_cost = (tokens_output / 1_000_000) * 2.50
        return round(input_cost + output_cost, 6)


# Singleton instance
ai_service = AIService()

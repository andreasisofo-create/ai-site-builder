"""
DIY Swarm Generator - Generazione parallela siti web.

Simula Agent Swarm di Kimi K2.5 usando asyncio.gather() per
eseguire 3 analisi iniziali IN PARALLELO, poi genera HTML e review.

Fasi:
  Fase 1 (PARALLELA via asyncio.gather):
    - _analyze_layout()    : struttura/griglia      (Thinking mode)
    - _analyze_colors()    : colori/font             (Thinking mode)
    - _generate_seo_texts(): testi SEO per sezioni   (Instant mode)
  Fase 2 (SEQUENZIALE): _generate_html() con risultati merged
  Fase 3 (SEQUENZIALE): _review_html() confronto con reference
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable

from app.services.kimi_client import kimi, KimiClient
from app.services.sanitizer import sanitize_input, sanitize_output, sanitize_refine_input

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[int, str], None]]


class SwarmGenerator:
    """Generatore siti web con esecuzione parallela a 3 fasi."""

    def __init__(self, client: Optional[KimiClient] = None):
        self.kimi = client or kimi

    # =================================================================
    # FASE 1 - Sub-agenti PARALLELI
    # =================================================================

    async def _analyze_layout(
        self,
        business_description: str,
        sections: List[str],
        reference_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sub-agente 1: Analisi layout e struttura.
        Instant mode per velocita' (analisi semplice, non serve deep reasoning).
        """
        prompt = f"""Analyze the ideal layout for a one-page website. Be concise.

BUSINESS: {business_description}
SECTIONS: {', '.join(sections)}

Provide briefly:
1. Grid system (single/two column)
2. Section ordering
3. Key visual elements per section
4. Navigation style (sticky/transparent)

Focus on Tailwind CSS patterns. Keep response under 300 words."""

        if reference_image_url:
            result = await self.kimi.call_with_image(
                prompt=prompt,
                image_url=reference_image_url,
                max_tokens=800,
                thinking=False,
                timeout=60.0,
            )
        else:
            result = await self.kimi.call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                thinking=False,
                timeout=60.0,
            )

        if result["success"]:
            logger.info(f"[Swarm] Layout analysis done ({result.get('tokens_output', 0)} tokens)")
        else:
            logger.warning(f"[Swarm] Layout analysis failed: {result.get('error')}")

        return result

    async def _analyze_colors(
        self,
        business_name: str,
        business_description: str,
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sub-agente 2: Analisi colori e tipografia.
        Instant mode per velocita'.
        """
        style_str = ""
        if style_preferences:
            for k, v in style_preferences.items():
                style_str += f"- {k}: {v}\n"

        style_section = f"STYLE PREFERENCES:\n{style_str}" if style_str else ""

        prompt = f"""Define color palette and typography for a website. Be concise.

BUSINESS: {business_name} - {business_description}
{style_section}

Provide:
1. Primary color (hex)
2. Secondary color (hex)
3. Accent color (hex)
4. Background colors (light/dark)
5. Text colors
6. Font pair from Google Fonts

Use Tailwind CSS naming. Keep under 200 words."""

        if reference_image_url:
            result = await self.kimi.call_with_image(
                prompt=prompt,
                image_url=reference_image_url,
                max_tokens=800,
                thinking=False,
                timeout=60.0,
            )
        else:
            result = await self.kimi.call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                thinking=False,
                timeout=60.0,
            )

        if result["success"]:
            logger.info(f"[Swarm] Color analysis done ({result.get('tokens_output', 0)} tokens)")
        else:
            logger.warning(f"[Swarm] Color analysis failed: {result.get('error')}")

        return result

    async def _generate_seo_texts(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        contact_info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Sub-agente 3: Generazione testi SEO.
        Instant mode (piu' veloce, non serve deep reasoning).
        """
        contact_str = ""
        if contact_info:
            for k, v in contact_info.items():
                contact_str += f"- {k}: {v}\n"

        contact_section = f"CONTACT INFO:\n{contact_str}" if contact_str else ""

        prompt = f"""Generate SEO-optimized Italian text content for each section of a website.

BUSINESS: {business_name}
DESCRIPTION: {business_description}
SECTIONS: {', '.join(sections)}
{contact_section}

For each section provide:
- Heading (compelling, keyword-rich)
- Subheading or tagline
- Body text (2-4 sentences, persuasive, natural Italian)
- CTA button text (where applicable)

Also provide:
- Meta title (max 60 chars)
- Meta description (max 155 chars)
- OG title and description

All text must be in Italian. Use a professional but warm tone.
Make the hero section particularly impactful."""

        result = await self.kimi.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            thinking=False,  # Instant mode - veloce
            timeout=60.0,
        )

        if result["success"]:
            logger.info(f"[Swarm] SEO texts done ({result.get('tokens_output', 0)} tokens)")
        else:
            logger.warning(f"[Swarm] SEO texts failed: {result.get('error')}")

        return result

    # =================================================================
    # FASE 2 - Genera HTML con risultati merged
    # =================================================================

    async def _generate_html(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        layout_analysis: str,
        color_analysis: str,
        seo_texts: str,
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Fase 2: Genera HTML completo usando i risultati delle 3 analisi parallele.
        Thinking mode per generazione di codice complesso.
        """
        style_str = ""
        if style_preferences:
            for k, v in style_preferences.items():
                style_str += f"- {k}: {v}\n"

        contact_str = ""
        if contact_info:
            for k, v in contact_info.items():
                contact_str += f"- {k}: {v}\n"

        system_prompt = """You are an expert frontend developer specializing in Tailwind CSS.
Generate a complete, production-ready HTML5 one-page website.

STRICT RULES:
1. Semantic HTML5 with Tailwind CSS utility classes
2. Use Tailwind CDN: <script src="https://cdn.tailwindcss.com"></script>
3. Mobile-first responsive design (375px, 768px, 1440px)
4. Use placeholder images from https://placehold.co with descriptive alt text
5. Working contact form with labels, names, submit button
6. Smooth scroll navigation + mobile hamburger menu (vanilla JS)
7. Meta tags: charset UTF-8, viewport, description, og:title, og:description
8. NO external CSS files - Tailwind utilities only
9. NO JavaScript frameworks - vanilla JS only
10. Google Fonts via CDN link if recommended
11. All interactive elements have hover/focus states
12. Images use lazy loading (loading="lazy")
13. All content in Italian

OUTPUT: Return ONLY the complete HTML between ```html and ``` tags. No explanations."""

        user_prompt = f"""Generate a complete one-page website using these pre-analyzed specifications:

=== BUSINESS ===
Name: {business_name}
Description: {business_description}

=== LAYOUT ANALYSIS (from layout agent) ===
{layout_analysis}

=== COLOR & TYPOGRAPHY (from color agent) ===
{color_analysis}

=== SEO TEXTS (from SEO agent) ===
{seo_texts}

=== SECTIONS ===
{', '.join(sections)}
{f'''
=== STYLE PREFERENCES ===
{style_str}''' if style_str else ''}
{f'''
=== REFERENCE STYLE ===
{reference_analysis}
Match this visual style closely.''' if reference_analysis else ''}
{f'''
=== LOGO ===
Use this URL for the logo: {logo_url}''' if logo_url else ''}
{f'''
=== CONTACT INFO ===
{contact_str}''' if contact_str else ''}

IMPORTANT:
- Use the exact colors, fonts, and layout from the analyses above
- Use the exact Italian texts from the SEO analysis
- Ensure smooth scroll, hamburger menu, and responsive design work
- Minimum 5 complete sections
- Professional, polished result

Generate the complete HTML now."""

        # Streaming per evitare timeout su generazioni lunghe
        result = await self.kimi.call_stream(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=6000,
            thinking=False,  # Instant mode: Phase 1 gia' fornisce analisi dettagliate
            timeout=300.0,
        )

        if result["success"]:
            result["content"] = self.kimi.extract_html(result["content"])
            logger.info(f"[Swarm] HTML generated ({len(result['content'])} chars)")

        return result

    # =================================================================
    # FASE 3 - Review HTML
    # =================================================================

    async def _review_html(
        self,
        html: str,
        business_name: str,
        reference_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fase 3: Revisiona HTML generato.
        Confronta con reference se disponibile.
        Instant mode (review veloce, non serve deep reasoning).
        """
        prompt = f"""Review and fix this HTML website for "{business_name}".

CURRENT HTML:
{html}

CHECK AND FIX:
1. Responsive: works on mobile (375px) and desktop (1440px)
2. Navigation: hamburger menu works with vanilla JS toggle
3. All images have alt text
4. Color contrast: text readable on background
5. All links have href (use # for placeholders)
6. Contact form has proper inputs, labels, submit button
7. Footer has copyright text
8. Smooth scroll works for nav links
9. No broken/incomplete HTML tags
10. Tailwind CDN script tag present in <head>
11. All sections are complete and visually consistent

IMPORTANT:
- Return the COMPLETE fixed HTML file
- If no issues, return HTML as-is
- Return ONLY HTML between ```html and ``` tags
- NO explanations"""

        if reference_image_url:
            # Se abbiamo l'immagine reference, confronta visivamente
            prompt += f"\n\nAlso compare with the reference image and ensure the generated site matches the visual style as closely as possible."
            result = await self.kimi.call_with_image(
                prompt=prompt,
                image_url=reference_image_url,
                max_tokens=12000,
                thinking=False,  # Instant per review veloce
                timeout=180.0,
            )
        else:
            result = await self.kimi.call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=12000,
                thinking=False,
                timeout=180.0,
            )

        if result["success"]:
            result["content"] = self.kimi.extract_html(result["content"])
            logger.info(f"[Swarm] Review done ({len(result['content'])} chars)")

        return result

    # =================================================================
    # METODO PRINCIPALE: generate()
    # =================================================================

    async def generate(
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
        Genera un sito web completo con DIY Swarm.

        Fase 1: 3 analisi PARALLELE via asyncio.gather()
        Fase 2: Genera HTML con risultati merged
        Fase 3: Review (solo con reference image)

        Returns:
            {"success": True, "html_content": str, "model_used": str,
             "tokens_input": int, "tokens_output": int, "cost_usd": float,
             "generation_time_ms": int, "pipeline_steps": int}
        """
        try:
            return await asyncio.wait_for(
                self._generate_pipeline(
                    business_name=business_name,
                    business_description=business_description,
                    sections=sections,
                    style_preferences=style_preferences,
                    reference_image_url=reference_image_url,
                    reference_analysis=reference_analysis,
                    logo_url=logo_url,
                    contact_info=contact_info,
                    on_progress=on_progress,
                ),
                timeout=180.0,  # Hard timeout: 3 minuti
            )
        except asyncio.TimeoutError:
            logger.error("[Swarm] TIMEOUT: generazione superato 180s")
            return {"success": False, "error": "Timeout: la generazione ha impiegato troppo tempo. Riprova."}

    async def _generate_pipeline(
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
        """Pipeline interna di generazione."""
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

        # ===== FASE 1: 3 sub-agenti PARALLELI =====
        if on_progress:
            on_progress(1, "Analisi parallela: layout, colori, testi SEO...")

        logger.info("[Swarm] === FASE 1: Lancio 3 sub-agenti in parallelo ===")
        phase1_start = time.time()

        layout_task = self._analyze_layout(
            business_description=business_description,
            sections=sections,
            reference_image_url=reference_image_url,
        )
        color_task = self._analyze_colors(
            business_name=business_name,
            business_description=business_description,
            style_preferences=style_preferences,
            reference_image_url=reference_image_url,
        )
        seo_task = self._generate_seo_texts(
            business_name=business_name,
            business_description=business_description,
            sections=sections,
            contact_info=contact_info,
        )

        # PARALLELO! Tutte e 3 partono contemporaneamente
        layout_result, color_result, seo_result = await asyncio.gather(
            layout_task, color_task, seo_task
        )

        phase1_time = time.time() - phase1_start
        logger.info(f"[Swarm] Fase 1 completata in {phase1_time:.1f}s (parallelo)")

        # Raccogli risultati (usa fallback se qualche analisi fallisce)
        layout_analysis = layout_result.get("content", "") if layout_result["success"] else "Use a clean, modern single-column layout with spacious sections."
        color_analysis = color_result.get("content", "") if color_result["success"] else "Use a professional blue (#2563EB) and gray (#1F2937) palette with Inter font."
        seo_texts = seo_result.get("content", "") if seo_result["success"] else ""

        # Somma token fase 1
        for r in [layout_result, color_result, seo_result]:
            if r["success"]:
                total_tokens_in += r.get("tokens_input", 0)
                total_tokens_out += r.get("tokens_output", 0)

        # Usa reference_analysis pre-esistente se fornita
        if reference_analysis and not reference_image_url:
            # L'utente ha fornito un'analisi testuale senza immagine
            pass

        # ===== FASE 2: Genera HTML con risultati merged =====
        if on_progress:
            on_progress(2, "Generazione HTML completo...")

        logger.info("[Swarm] === FASE 2: Generazione HTML ===")
        phase2_start = time.time()

        html_result = await self._generate_html(
            business_name=business_name,
            business_description=business_description,
            sections=sections,
            layout_analysis=layout_analysis,
            color_analysis=color_analysis,
            seo_texts=seo_texts,
            style_preferences=style_preferences,
            reference_analysis=reference_analysis,
            logo_url=logo_url,
            contact_info=contact_info,
        )

        phase2_time = time.time() - phase2_start
        logger.info(f"[Swarm] Fase 2 completata in {phase2_time:.1f}s")

        if not html_result["success"]:
            return html_result

        html_content = html_result["content"]
        total_tokens_in += html_result.get("tokens_input", 0)
        total_tokens_out += html_result.get("tokens_output", 0)

        if on_progress and not reference_image_url:
            on_progress(3, "Finalizzazione...")

        # ===== FASE 3: Review (solo con reference image) =====
        phase3_time = 0.0
        if reference_image_url:
            if on_progress:
                on_progress(3, "Revisione con immagine di riferimento...")

            logger.info("[Swarm] === FASE 3: Review con reference image ===")
            phase3_start = time.time()

            review_result = await self._review_html(
                html=html_content,
                business_name=business_name,
                reference_image_url=reference_image_url,
            )

            phase3_time = time.time() - phase3_start
            logger.info(f"[Swarm] Fase 3 completata in {phase3_time:.1f}s")

            if review_result["success"]:
                html_content = review_result["content"]
                total_tokens_in += review_result.get("tokens_input", 0)
                total_tokens_out += review_result.get("tokens_output", 0)
            else:
                logger.warning(f"[Swarm] Review fallita, uso output Fase 2: {review_result.get('error')}")
        else:
            logger.info("[Swarm] Fase 3 skippata (nessuna reference image)")

        # Sanitizza output finale
        html_content = sanitize_output(html_content)

        generation_time = int((time.time() - start_time) * 1000)
        cost = self.kimi.calculate_cost(total_tokens_in, total_tokens_out)

        logger.info(
            f"[Swarm] COMPLETATO in {generation_time}ms "
            f"(Fase1: {phase1_time:.1f}s, Fase2: {phase2_time:.1f}s, Fase3: {phase3_time:.1f}s) "
            f"Tokens: {total_tokens_in}+{total_tokens_out} = ${cost}"
        )

        return {
            "success": True,
            "html_content": html_content,
            "model_used": "kimi-k2.5-swarm",
            "tokens_input": total_tokens_in,
            "tokens_output": total_tokens_out,
            "cost_usd": cost,
            "generation_time_ms": generation_time,
            "pipeline_steps": 5,  # 3 paralleli + generate + review
        }

    # =================================================================
    # REFINE: Modifica via chat (Instant mode, veloce)
    # =================================================================

    async def refine(
        self,
        current_html: str,
        modification_request: str,
        section_to_modify: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Modifica un sito esistente via chat.
        Usa Instant mode per risposta rapida (~3-8s).
        """
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
5. Return ONLY HTML between ```html and ``` tags"""
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
4. Return ONLY HTML between ```html and ``` tags"""

        start_time = time.time()
        # Streaming per evitare timeout su refine lunghi
        result = await self.kimi.call_stream(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            thinking=False,  # Instant mode per velocita'
            timeout=300.0,
        )

        if not result["success"]:
            return result

        html_content = self.kimi.extract_html(result["content"])
        html_content = sanitize_output(html_content)
        generation_time = int((time.time() - start_time) * 1000)
        cost = self.kimi.calculate_cost(
            result.get("tokens_input", 0),
            result.get("tokens_output", 0),
        )

        logger.info(f"[Swarm] Refine completato in {generation_time}ms (${cost})")

        return {
            "success": True,
            "html_content": html_content,
            "model_used": "kimi-k2.5-instant",
            "tokens_input": result.get("tokens_input", 0),
            "tokens_output": result.get("tokens_output", 0),
            "cost_usd": cost,
            "generation_time_ms": generation_time,
        }


# Singleton
swarm = SwarmGenerator()

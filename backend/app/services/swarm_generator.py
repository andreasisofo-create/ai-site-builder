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
import json
import logging
import time
import re
from typing import Dict, Any, Optional, List, Callable, Tuple

from app.services.kimi_client import kimi, kimi_refine, KimiClient
from app.services.sanitizer import sanitize_input, sanitize_output, sanitize_refine_input

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[int, str], None]]


class SwarmGenerator:
    """Generatore siti web con esecuzione parallela a 3 fasi."""

    def __init__(self, client: Optional[KimiClient] = None):
        self.kimi = client or kimi
        # Hybrid strategy: use a separate (higher quality) client for chat refine
        self.kimi_refine = kimi_refine

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
        Fase 2: Genera HTML completo.
        Prompt semplificato per ridurre tempo di generazione.
        """
        color_hint = ""
        if style_preferences and style_preferences.get("primary_color"):
            color_hint = f"Primary color: {style_preferences['primary_color']}. "

        logo_hint = f'<img src="{logo_url}" alt="{business_name}" class="h-10">' if logo_url else ""

        contact_str = ""
        if contact_info:
            for k, v in contact_info.items():
                contact_str += f"{k}: {v}, "

        prompt = f"""Generate a simple, professional one-page HTML website.

BUSINESS: {business_name} - {business_description}
SECTIONS: {', '.join(sections)}
{color_hint}
{f'CONTACT: {contact_str}' if contact_str else ''}

DESIGN BRIEF:
{color_analysis}

TEXTS (use these Italian texts):
{seo_texts}

RULES:
- Complete HTML5 document with <!DOCTYPE html>
- Tailwind CSS via CDN (add BOTH scripts): <script>const _w=console.warn;console.warn=(...a)=>{{if(a[0]&&typeof a[0]==='string'&&a[0].includes('cdn.tailwindcss.com'))return;_w.apply(console,a)}};</script><script src="https://cdn.tailwindcss.com"></script>
- Add GSAP: <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
- Use data-animate attributes on elements: fade-up, fade-left, fade-right, scale-in, text-split (on headings), magnetic (on buttons), stagger (on grids with stagger-item children), image-zoom (on images), tilt (on cards)
- Section headings: data-animate="text-split" data-split-type="words"
- CTA buttons: data-animate="magnetic"
- Cards/grid items: parent data-animate="stagger", children class="stagger-item"
- Responsive (mobile + desktop)
- Hamburger menu with vanilla JS
- Contact form with name, email, message fields
- Footer with copyright
- All text in Italian - RICH, CREATIVE content specific to the business (NEVER leave empty sections)
- NO explanations, ONLY HTML code between ```html and ``` tags
{f'- Logo: {logo_hint}' if logo_hint else ''}

Generate the HTML now."""

        result = await self.kimi.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            thinking=False,
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
                timeout=360.0,  # Hard timeout: 6 minuti
            )
        except asyncio.TimeoutError:
            logger.error("[Swarm] TIMEOUT: generazione superato 360s")
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
    # HELPERS: Aggressive strip/re-inject for refine to stay under token limit
    # =================================================================

    # Kimi K2.5 hard limit is 262144 tokens total (input + output).
    # We reserve 16K for output (max_tokens) + 10K safety margin.
    # Target input: 262144 - 16000 - 10000 = ~236K tokens max input.
    # At ~3.3 chars/token for HTML, that's ~780K chars.
    # But to be safe, we use a hard limit of 200K input tokens (~660K chars).
    _MAX_INPUT_TOKENS = 200000
    _MAX_INPUT_CHARS = 660000  # ~200K tokens at ~3.3 chars/token
    _TRUNCATION_THRESHOLD_TOKENS = 180000  # Start truncating at 180K tokens

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Token estimate: ~3.3 chars per token for HTML (tags, attributes, short values).
        HTML is denser than natural text, so we use a lower ratio than the typical 4."""
        return int(len(text) / 3.3)

    @staticmethod
    def _strip_for_refine(html: str) -> Tuple[str, Dict[str, Any]]:
        """Aggressively strip heavy content from HTML before sending to Kimi.

        Strips (in order):
        1. GSAP Universal Animation Engine inline script (~20KB)
        2. All <style> blocks (CSS can be large in Awwwards-quality templates)
        3. SVG content (replace with small placeholder keeping attributes)
        4. Excessive whitespace / empty lines
        5. HTML comments (except our placeholders)

        Returns (stripped_html, stash) where stash contains all removed content
        for reinject later.
        """
        stash: Dict[str, Any] = {"gsap": "", "styles": [], "svgs": []}

        # 1. Strip GSAP Universal Animation Engine script
        gsap_pattern = r'<script>\s*/\*[\s\S]*?GSAP Universal Animation Engine[\s\S]*?</script>'
        gsap_match = re.search(gsap_pattern, html)
        if gsap_match:
            stash["gsap"] = gsap_match.group(0)
            html = html[:gsap_match.start()] + '<!-- __GSAP_PLACEHOLDER__ -->' + html[gsap_match.end():]
            logger.info(f"[Swarm] Stripped GSAP script ({len(stash['gsap'])} chars)")

        # 2. Strip all <style> blocks (numbered placeholders)
        style_pattern = r'<style[^>]*>[\s\S]*?</style>'
        style_matches = list(re.finditer(style_pattern, html))
        # Process in reverse so indices stay valid
        for i, m in enumerate(reversed(style_matches)):
            idx = len(style_matches) - 1 - i
            stash["styles"].insert(0, m.group(0))
            html = html[:m.start()] + f'<!-- __STYLE_{idx}__ -->' + html[m.end():]
        if style_matches:
            logger.info(f"[Swarm] Stripped {len(style_matches)} <style> blocks ({sum(len(s) for s in stash['styles'])} chars)")

        # 3. Strip SVG content (keep the <svg> tag with attributes but remove inner paths/shapes)
        svg_pattern = r'(<svg[^>]*>)([\s\S]*?)(</svg>)'
        svg_matches = list(re.finditer(svg_pattern, html))
        for i, m in enumerate(reversed(svg_matches)):
            idx = len(svg_matches) - 1 - i
            inner = m.group(2)
            # Only strip if SVG inner content is substantial (>200 chars)
            if len(inner) > 200:
                stash["svgs"].insert(0, {"index": idx, "inner": inner, "open_tag": m.group(1), "close_tag": m.group(3)})
                html = html[:m.start()] + f'{m.group(1)}<!-- __SVG_INNER_{idx}__ -->{m.group(3)}' + html[m.end():]
        if stash["svgs"]:
            logger.info(f"[Swarm] Stripped {len(stash['svgs'])} large SVG inners ({sum(len(s['inner']) for s in stash['svgs'])} chars)")

        # 4. Strip HTML comments (except our placeholders)
        html = re.sub(r'<!--(?!\s*__)[^>]*?-->', '', html)

        # 5. Collapse excessive whitespace: multiple blank lines -> single, trim line whitespace
        html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)  # 3+ blank lines -> 1
        html = re.sub(r'[ \t]+\n', '\n', html)  # trailing whitespace
        html = re.sub(r'\n[ \t]+', '\n', html)  # leading whitespace (careful with pre tags, but HTML templates don't use them)
        html = re.sub(r'  +', ' ', html)  # multiple spaces -> single

        return html, stash

    @staticmethod
    def _reinject_after_refine(html: str, stash: Dict[str, Any]) -> str:
        """Re-inject all stripped content back into the HTML after AI refinement."""

        # 1. Re-inject SVG inners
        for svg_info in stash.get("svgs", []):
            placeholder = f'<!-- __SVG_INNER_{svg_info["index"]}__ -->'
            if placeholder in html:
                html = html.replace(placeholder, svg_info["inner"])

        # 2. Re-inject <style> blocks
        for i, style_block in enumerate(stash.get("styles", [])):
            placeholder = f'<!-- __STYLE_{i}__ -->'
            if placeholder in html:
                html = html.replace(placeholder, style_block)

        # 3. Re-inject GSAP script
        gsap_block = stash.get("gsap", "")
        if gsap_block:
            if '<!-- __GSAP_PLACEHOLDER__ -->' in html:
                html = html.replace('<!-- __GSAP_PLACEHOLDER__ -->', gsap_block)
            elif '</body>' in html.lower():
                idx = html.lower().rfind('</body>')
                html = html[:idx] + '\n' + gsap_block + '\n' + html[idx:]
            else:
                html = html + '\n' + gsap_block

        return html

    # Keep legacy methods for backward compatibility with any other callers
    @staticmethod
    def _strip_gsap_script(html: str) -> Tuple[str, str]:
        """Legacy: Strip only GSAP script. Use _strip_for_refine for full stripping."""
        pattern = r'<script>\s*/\*[\s\S]*?GSAP Universal Animation Engine[\s\S]*?</script>'
        match = re.search(pattern, html)
        if match:
            gsap_block = match.group(0)
            stripped = html[:match.start()] + '<!-- __GSAP_PLACEHOLDER__ -->' + html[match.end():]
            return stripped, gsap_block
        return html, ""

    @staticmethod
    def _reinject_gsap_script(html: str, gsap_block: str) -> str:
        """Legacy: Re-inject GSAP script. Use _reinject_after_refine for full reinjection."""
        if not gsap_block:
            return html
        if '<!-- __GSAP_PLACEHOLDER__ -->' in html:
            return html.replace('<!-- __GSAP_PLACEHOLDER__ -->', gsap_block)
        if '</body>' in html.lower():
            idx = html.lower().rfind('</body>')
            return html[:idx] + '\n' + gsap_block + '\n' + html[idx:]
        return html + '\n' + gsap_block

    # =================================================================
    # SMART REFINE: Classifica richiesta e usa strategia ottimale
    # =================================================================

    # Request classification categories
    _CSS_KEYWORDS = [
        # Colors (all Italian gender/plural variants)
        "colore", "colori", "sfondo", "background", "primario", "secondario",
        "scuro", "scura", "scuri", "scure", "chiaro", "chiara", "chiari", "chiare",
        "dark", "light", "tema",
        "bianco", "bianca", "bianchi", "bianche",
        "nero", "nera", "neri", "nere",
        "grigio", "grigia", "grigi", "grigie",
        "blu",
        "rosso", "rossa", "rossi", "rosse",
        "verde", "verdi",
        "giallo", "gialla", "gialli", "gialle",
        "arancione", "arancioni",
        "viola", "rosa", "azzurro", "azzurra", "azzurri", "azzurre",
        "marrone", "marroni", "beige",
        "color", "colour", "palette", "tinta", "tonalità", "tonalita",
        "sfumatura", "sfumature",
        # Fonts
        "font", "carattere", "tipografia", "grassetto", "bold",
        "dimensione", "size", "serif", "sans",
        # Spacing / radius / shadow (CSS vars)
        "bordi arrotondati", "border-radius", "ombra", "shadow",
        "spaziatura", "spacing", "padding", "margine",
    ]

    _TEXT_KEYWORDS = [
        "testo", "testi", "titolo", "titoli", "scrivi", "riscrivi",
        "modifica il testo", "cambia il nome", "sostituisci", "rinomina",
        "descrizione", "sottotitolo", "paragrafo", "paragrafi",
        "slogan", "frase", "headline",
        "scritta", "scritte", "lettere", "lettera",
        "cambia la scritta", "modifica la scritta", "testo del",
        "title", "text", "heading", "label", "copy",
        "parola", "parole", "contenuto testuale",
        # Italian imperative verbs for "make them/it" (color target)
        "falle", "falli", "fallo", "falla",
        "rendile", "rendili", "rendilo", "rendila",
        "mettile", "mettili", "mettilo", "mettila",
    ]

    # Major theme change patterns — these need structural strategy, not just CSS vars,
    # because switching light↔dark requires changing Tailwind classes, overlays, etc.
    _MAJOR_THEME_PATTERNS = [
        r'(?:colori?|palette|tema)\s+(?:sono|è|e\'|sbagliat|non\s+(?:va|corrett|corrispon))',
        r'(?:non\s+corrisponde?|non\s+(?:è|e\')\s+come)\s+(?:la\s+)?(?:reference|riferimento|immagine)',
        r'(?:cambia|modifica)\s+tutt[oi]\s+(?:il\s+)?(?:tema|colori?|palette|scheme)',
        r'(?:fai|rendi|metti)\s+(?:tutto\s+)?(?:scuro|dark|nero|chiaro|light|bianco)',
        r'(?:da\s+(?:chiaro|light)\s+a\s+(?:scuro|dark))|(?:da\s+(?:scuro|dark)\s+a\s+(?:chiaro|light))',
        r'(?:inverti|ribalta|scambia)\s+(?:i\s+)?(?:colori|tema|palette)',
        r'(?:rifai|rigenera)\s+(?:i\s+)?(?:colori|tema|palette)',
        r'sbagliati?\s+(?:i\s+)?colori',
        r'(?:tutto|completamente)\s+(?:diverso|sbagliato|errato)',
    ]

    @staticmethod
    def _classify_refine_request(message: str) -> str:
        """Classify a refine request into a strategy category.

        Returns one of: 'css_vars', 'text', 'section', 'structural'
        """
        msg_lower = message.lower().strip()

        # === EARLY EXIT: Major theme changes need structural, not css_vars ===
        for pat in SwarmGenerator._MAJOR_THEME_PATTERNS:
            if re.search(pat, msg_lower):
                logger.info(f"[SmartRefine] Classified as STRUCTURAL (major theme change: {pat})")
                return "structural"

        # === SPECIAL RULE: "da [color] a [color]" pattern is ALWAYS css_vars ===
        # e.g., "da nere a rosse", "da bianco a nero"
        _ALL_COLOR_WORDS = {
            "nero", "nera", "neri", "nere", "rosso", "rossa", "rossi", "rosse",
            "verde", "verdi", "giallo", "gialla", "gialli", "gialle",
            "bianco", "bianca", "bianchi", "bianche", "grigio", "grigia", "grigi", "grigie",
            "viola", "arancione", "arancioni", "rosa", "azzurro", "azzurra", "azzurri", "azzurre",
            "blu", "marrone", "marroni", "beige",
            "scuro", "scura", "scuri", "scure", "chiaro", "chiara", "chiari", "chiare",
        }
        da_a_match = re.search(r'\bda\s+(\w+)\s+a\s+(\w+)', msg_lower)
        if da_a_match:
            word1, word2 = da_a_match.group(1), da_a_match.group(2)
            if word1 in _ALL_COLOR_WORDS or word2 in _ALL_COLOR_WORDS:
                logger.info(f"[SmartRefine] Classified as CSS_VARS ('da {word1} a {word2}' color pattern)")
                return "css_vars"

        # Score-based classification
        css_score = 0
        text_score = 0

        for kw in SwarmGenerator._CSS_KEYWORDS:
            if kw in msg_lower:
                css_score += 1

        for kw in SwarmGenerator._TEXT_KEYWORDS:
            if kw in msg_lower:
                text_score += 1

        # Boost: ANY color word found is a strong signal for CSS change
        if any(cw in msg_lower for cw in _ALL_COLOR_WORDS):
            css_score += 3

        # Strong CSS signals (color change requests)
        if re.search(r'cambia.*(?:colore|sfondo|background|font|carattere)', msg_lower):
            css_score += 3
        if re.search(r'(?:più|piu)\s+(?:scuro|chiaro)', msg_lower):
            css_score += 3
        if re.search(r'(?:dark|light)\s*mode', msg_lower):
            css_score += 5
        if re.search(r'(?:usa|metti|applica)\s+(?:il\s+)?(?:font|colore)', msg_lower):
            css_score += 3

        # Strong text signals
        if re.search(r'(?:cambia|modifica|riscrivi|scrivi)\s+(?:il\s+)?(?:testo|titolo|nome|descrizione)', msg_lower):
            text_score += 3
        if re.search(r'sostituisci\s+.+\s+con\s+', msg_lower):
            text_score += 3

        # Structural signals (override everything)
        structural_patterns = [
            r'(?:aggiungi|rimuovi|elimina|sposta|riordina)\s+(?:una?\s+)?(?:sezione|mappa|form|modulo|immagine|video|slider|carousel)',
            r'(?:add|remove|delete|move)\s+(?:a\s+)?(?:section|map|form|image|video)',
            r'layout|struttura|griglia|grid|colonne|columns',
        ]
        for pat in structural_patterns:
            if re.search(pat, msg_lower):
                logger.info(f"[SmartRefine] Classified as STRUCTURAL (pattern: {pat})")
                return "structural"

        logger.info(f"[SmartRefine] Scores - CSS: {css_score}, Text: {text_score}")

        if css_score >= 2 and css_score > text_score:
            return "css_vars"
        if text_score >= 2 and text_score > css_score:
            return "text"
        if css_score == 1 and text_score == 0:
            return "css_vars"
        if text_score == 1 and css_score == 0:
            return "text"

        # Default: section if a section is specified, otherwise structural
        return "structural"

    # Common section names in Italian and English, mapped to typical HTML IDs
    _SECTION_NAMES = {
        "hero": "hero", "header": "hero", "intestazione": "hero",
        "about": "about", "chi siamo": "about", "chi-siamo": "about",
        "servizi": "services", "services": "services",
        "contatti": "contact", "contatto": "contact", "contact": "contact",
        "footer": "footer", "piè di pagina": "footer",
        "testimonial": "testimonials", "testimonianze": "testimonials",
        "gallery": "gallery", "galleria": "gallery",
        "portfolio": "portfolio", "lavori": "portfolio", "progetti": "portfolio",
        "pricing": "pricing", "prezzi": "pricing",
        "team": "team", "squadra": "team",
        "faq": "faq", "domande": "faq",
        "stats": "stats", "numeri": "stats", "statistiche": "stats",
        "cta": "cta", "call to action": "cta",
        "blog": "blog", "news": "news", "notizie": "news",
        "features": "features", "caratteristiche": "features", "funzionalità": "features",
    }

    @staticmethod
    def _detect_section_from_request(message: str, html: str) -> Optional[str]:
        """Auto-detect which section the user is referring to from their message.
        Cross-references with actual section IDs in the HTML."""
        msg_lower = message.lower()

        # Find all section IDs actually present in the HTML
        html_section_ids = set()
        for m in re.finditer(r'<(?:section|div|header|footer)[^>]*\bid\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE):
            html_section_ids.add(m.group(1).lower())

        # Check each known section name against the message
        for keyword, section_id in SwarmGenerator._SECTION_NAMES.items():
            if keyword in msg_lower:
                # Verify the section actually exists in the HTML
                # Try exact match first, then partial match
                if section_id in html_section_ids:
                    return section_id
                # Try partial match (e.g., "hero-section" contains "hero")
                for html_id in html_section_ids:
                    if section_id in html_id or html_id in section_id:
                        return html_id

        # Also try matching raw section IDs mentioned in the message
        for html_id in html_section_ids:
            if html_id in msg_lower:
                return html_id

        return None

    @staticmethod
    def _extract_css_root(html: str) -> Optional[str]:
        """Extract the :root { ... } CSS block from HTML.
        Uses balanced brace matching to handle any nested content."""
        start = html.find(':root')
        if start == -1:
            return None
        brace_start = html.find('{', start)
        if brace_start == -1:
            return None
        depth = 0
        for i in range(brace_start, len(html)):
            if html[i] == '{':
                depth += 1
            elif html[i] == '}':
                depth -= 1
                if depth == 0:
                    return html[start:i + 1]
        return None

    @staticmethod
    def _replace_css_root(html: str, new_root: str) -> str:
        """Replace the :root { ... } CSS block in HTML."""
        old_root = SwarmGenerator._extract_css_root(html)
        if old_root:
            return html.replace(old_root, new_root, 1)
        return html

    @staticmethod
    def _parse_css_vars(root_block: str) -> Dict[str, str]:
        """Parse CSS :root block into a dict of variable name -> value."""
        result = {}
        for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;]+);', root_block):
            result[m.group(1).strip()] = m.group(2).strip()
        return result

    async def _refine_css_vars(
        self,
        current_html: str,
        modification_request: str,
        reference_analysis: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Strategy 1: Modify only CSS variables. Ultra-fast, zero risk to HTML."""
        start_time = time.time()

        root_block = self._extract_css_root(current_html)
        if not root_block:
            logger.warning("[SmartRefine/CSS] No :root block found, falling back to structural")
            return {"success": False, "fallback": True}

        logger.info(f"[SmartRefine/CSS] Extracted :root block ({len(root_block)} chars)")

        # Also extract Google Fonts link to know current fonts
        font_links = re.findall(r'<link[^>]*fonts\.googleapis\.com[^>]*>', current_html)
        font_context = "\n".join(font_links) if font_links else ""

        ref_hint = ""
        if reference_analysis:
            ref_hint = f"\nREFERENCE ANALYSIS (user's desired look):\n{reference_analysis}\nUse the colors from the reference analysis when correcting the palette.\n"

        prompt = f"""Modify ONLY the CSS :root variables based on the user request.
Return ONLY the modified :root {{ ... }} block, nothing else.

IMPORTANT RULES:
- Return valid CSS :root block
- Keep ALL existing variables, modify only the ones needed
- For color changes, use proper hex values
- For font changes, use Google Fonts names (e.g., 'Inter', 'Playfair Display')
- If user asks for "dark mode", invert bg/text colors and adjust ALL colors atomically
- When switching theme (light↔dark), update --bg-color AND --bg-alt-color AND --text-color AND --text-muted together
- RGB variants (--color-primary-rgb etc.) must match their hex counterparts
- Do NOT add any explanation, just the CSS

CRITICAL SCOPE RULES — ONLY change what the user asked:
- If user asks about SCRITTE/TESTO/LETTERE/TEXT → ONLY change --color-text and --color-text-muted. NEVER touch --color-bg or --color-bg-alt.
- If user asks about SFONDO/BACKGROUND → ONLY change --color-bg and --color-bg-alt. NEVER touch --color-text or --color-text-muted.
- If user asks about COLORE PRIMARIO/BRAND → ONLY change --color-primary (and its -rgb variant).
- If user asks about BOTTONE/CTA/ACCENTO → ONLY change --color-accent (and its -rgb variant).
- NEVER change --color-bg when the user only asked about text color.
- NEVER change --color-text when the user only asked about background color.
- When in doubt, change FEWER variables rather than more.

USER REQUEST: {modification_request}
{ref_hint}
{f"CURRENT FONTS: {font_context}" if font_context else ""}

CURRENT :root BLOCK:
{root_block}"""

        result = await self.kimi_refine.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            thinking=False,
            timeout=30.0,
            temperature=0.3,
        )

        if not result["success"]:
            logger.error(f"[SmartRefine/CSS] AI call failed: {result.get('error')}")
            return {"success": False, "fallback": True}

        new_root = result["content"].strip()

        # Clean up: extract just the :root block if AI wrapped it
        root_match = re.search(r':root\s*\{[^}]+\}', new_root, re.DOTALL)
        if root_match:
            new_root = root_match.group(0)
        elif new_root.startswith('{') and new_root.endswith('}'):
            new_root = ':root ' + new_root
        else:
            # Try to extract from code block
            code_match = re.search(r'```(?:css)?\s*\n?(.*?)\n?```', new_root, re.DOTALL)
            if code_match:
                inner = code_match.group(1).strip()
                root_match2 = re.search(r':root\s*\{[^}]+\}', inner, re.DOTALL)
                if root_match2:
                    new_root = root_match2.group(0)
                else:
                    logger.warning("[SmartRefine/CSS] Could not extract :root from AI response")
                    return {"success": False, "fallback": True}

        # Validate: must contain at least --color-primary
        if "--color-" not in new_root:
            logger.warning("[SmartRefine/CSS] AI response missing CSS vars, falling back")
            return {"success": False, "fallback": True}

        # === POST-VALIDATION: Revert unrelated variable changes ===
        # Parse the user request to determine scope, then revert out-of-scope changes
        req_lower = modification_request.lower()
        _text_signal_words = {"scritte", "scritta", "testo", "testi", "lettere", "lettera", "titolo", "titoli", "paragrafo", "paragrafi", "testo", "text"}
        _bg_signal_words = {"sfondo", "background", "bg"}
        is_text_request = any(w in req_lower for w in _text_signal_words)
        is_bg_request = any(w in req_lower for w in _bg_signal_words)

        # Only apply revert guard when request is clearly scoped (not both, not neither)
        if is_text_request and not is_bg_request:
            # User asked about text only — revert any bg changes
            old_vars = self._parse_css_vars(root_block)
            new_vars = self._parse_css_vars(new_root)
            bg_var_names = [k for k in old_vars if "bg" in k or "background" in k]
            reverted = []
            for var_name in bg_var_names:
                if var_name in old_vars and var_name in new_vars and old_vars[var_name] != new_vars[var_name]:
                    new_root = new_root.replace(
                        f"{var_name}: {new_vars[var_name]}",
                        f"{var_name}: {old_vars[var_name]}"
                    )
                    reverted.append(var_name)
            if reverted:
                logger.info(f"[SmartRefine/CSS] Reverted out-of-scope bg changes: {reverted}")
        elif is_bg_request and not is_text_request:
            # User asked about bg only — revert any text changes
            old_vars = self._parse_css_vars(root_block)
            new_vars = self._parse_css_vars(new_root)
            text_var_names = [k for k in old_vars if "text" in k and "bg" not in k]
            reverted = []
            for var_name in text_var_names:
                if var_name in old_vars and var_name in new_vars and old_vars[var_name] != new_vars[var_name]:
                    new_root = new_root.replace(
                        f"{var_name}: {new_vars[var_name]}",
                        f"{var_name}: {old_vars[var_name]}"
                    )
                    reverted.append(var_name)
            if reverted:
                logger.info(f"[SmartRefine/CSS] Reverted out-of-scope text changes: {reverted}")

        # Apply the new :root block
        new_html = self._replace_css_root(current_html, new_root)

        # If fonts changed, update Google Fonts link
        new_heading = re.search(r"--font-heading:\s*'([^']+)'", new_root)
        new_body = re.search(r"--font-body:\s*'([^']+)'", new_root)
        if new_heading or new_body:
            fonts = []
            if new_heading:
                fonts.append(new_heading.group(1).replace(' ', '+'))
            if new_body:
                fonts.append(new_body.group(1).replace(' ', '+'))
            if fonts:
                new_font_link = f'<link href="https://fonts.googleapis.com/css2?{"&".join("family=" + f + ":wght@300;400;500;600;700;800;900" for f in fonts)}&display=swap" rel="stylesheet">'
                # Replace existing Google Fonts link
                old_font_pattern = r'<link[^>]*fonts\.googleapis\.com[^>]*>'
                if re.search(old_font_pattern, new_html):
                    new_html = re.sub(old_font_pattern, new_font_link, new_html, count=1)
                    # Remove additional font links (there might be multiple)
                    new_html = re.sub(old_font_pattern, '', new_html)
                    # Re-insert the new one before </head>
                    if new_font_link not in new_html:
                        new_html = new_html.replace('</head>', f'{new_font_link}\n</head>')

        generation_time = int((time.time() - start_time) * 1000)
        cost = self.kimi_refine.calculate_cost(
            result.get("tokens_input", 0),
            result.get("tokens_output", 0),
        )

        logger.info(f"[SmartRefine/CSS] Done in {generation_time}ms (${cost}) - CSS vars only, HTML untouched")

        return {
            "success": True,
            "html_content": new_html,
            "model_used": self.kimi_refine.model,
            "tokens_input": result.get("tokens_input", 0),
            "tokens_output": result.get("tokens_output", 0),
            "cost_usd": cost,
            "generation_time_ms": generation_time,
            "strategy": "css_vars",
        }

    async def _refine_text_only(
        self,
        current_html: str,
        modification_request: str,
        section_to_modify: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Strategy 2: Modify only text content. Fast, safe — HTML structure untouched."""
        start_time = time.time()

        # Extract visible text elements with their context
        # Target: headings, paragraphs, buttons, list items, spans with text
        text_elements = []
        # Match tags that typically contain visible text
        pattern = r'<(h[1-6]|p|button|a|span|li|figcaption|blockquote|label|td|th)([^>]*)>(.*?)</\1>'
        matches = list(re.finditer(pattern, current_html, re.DOTALL | re.IGNORECASE))

        for i, m in enumerate(matches):
            tag = m.group(1)
            attrs = m.group(2)
            inner = m.group(3).strip()
            # Skip empty, icon-only, or very short content
            clean_text = re.sub(r'<[^>]+>', '', inner).strip()
            if len(clean_text) < 2:
                continue
            # Skip elements that are likely icons or SVGs
            if '<svg' in inner.lower() or '<i ' in inner.lower():
                if len(clean_text) < 5:
                    continue
            text_elements.append({
                "index": i,
                "tag": tag,
                "text": clean_text,
                "full_match": m.group(0),
            })

        if not text_elements:
            logger.warning("[SmartRefine/Text] No text elements found, falling back")
            return {"success": False, "fallback": True}

        # Build a compact text map for the AI
        text_map = "\n".join(
            f"[{el['index']}] <{el['tag']}> {el['text']}"
            for el in text_elements[:80]  # Limit to 80 elements
        )

        section_hint = f" in the {section_to_modify} section" if section_to_modify else ""

        prompt = f"""Modify the website text{section_hint} based on the user request.

Return a JSON array of replacements. Each replacement: {{"index": <number>, "new_text": "<new text>"}}
Only include elements that need to change. Keep the same language (Italian).

USER REQUEST: {modification_request}

CURRENT TEXT ELEMENTS:
{text_map}

Return ONLY valid JSON array, no explanation."""

        result = await self.kimi_refine.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            thinking=False,
            timeout=45.0,
            temperature=0.4,
            json_mode=True,
        )

        if not result["success"]:
            logger.error(f"[SmartRefine/Text] AI call failed: {result.get('error')}")
            return {"success": False, "fallback": True}

        # Parse replacements
        try:
            content = result["content"].strip()
            # Extract JSON from potential code block
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1).strip()
            replacements = json.loads(content)
            if not isinstance(replacements, list):
                # Maybe it's wrapped in an object
                if isinstance(replacements, dict) and "replacements" in replacements:
                    replacements = replacements["replacements"]
                else:
                    raise ValueError("Expected JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"[SmartRefine/Text] Failed to parse AI response: {e}")
            return {"success": False, "fallback": True}

        if not replacements:
            logger.info("[SmartRefine/Text] AI returned no replacements needed")
            return {"success": False, "fallback": True}

        # Apply replacements
        new_html = current_html
        applied = 0
        for rep in replacements:
            idx = rep.get("index")
            new_text = rep.get("new_text", "")
            if idx is None or not new_text:
                continue
            # Find the matching element
            el = next((e for e in text_elements if e["index"] == idx), None)
            if not el:
                continue
            old_match = el["full_match"]
            if old_match not in new_html:
                continue
            # Replace the text content, preserving HTML structure inside
            tag = el["tag"]
            attrs_match = re.match(rf'<{re.escape(tag)}([^>]*)>', old_match, re.IGNORECASE)
            attrs = attrs_match.group(1) if attrs_match else ""
            # If the original had inner HTML (like <span>, <strong>), just replace the text
            inner_html = re.search(rf'<{re.escape(tag)}[^>]*>(.*?)</{re.escape(tag)}>', old_match, re.DOTALL | re.IGNORECASE)
            if inner_html:
                old_inner = inner_html.group(1)
                # Check if inner has child tags — if so, replace just the text parts
                if '<' in old_inner:
                    # Has nested tags — replace just the text portion (first text node)
                    new_inner = re.sub(r'^([^<]*)', new_text, old_inner, count=1)
                else:
                    new_inner = new_text
                new_element = f"<{tag}{attrs}>{new_inner}</{tag}>"
                new_html = new_html.replace(old_match, new_element, 1)
                applied += 1

        if applied == 0:
            logger.warning("[SmartRefine/Text] No replacements applied, falling back")
            return {"success": False, "fallback": True}

        generation_time = int((time.time() - start_time) * 1000)
        cost = self.kimi_refine.calculate_cost(
            result.get("tokens_input", 0),
            result.get("tokens_output", 0),
        )

        logger.info(f"[SmartRefine/Text] Done in {generation_time}ms (${cost}) - {applied} text replacements, HTML structure untouched")

        return {
            "success": True,
            "html_content": new_html,
            "model_used": self.kimi_refine.model,
            "tokens_input": result.get("tokens_input", 0),
            "tokens_output": result.get("tokens_output", 0),
            "cost_usd": cost,
            "generation_time_ms": generation_time,
            "strategy": "text",
        }

    # =================================================================
    # REFINE: Section extraction helpers
    # =================================================================

    @staticmethod
    def _extract_section_html(html: str, section_name: str) -> Optional[str]:
        """Extract a specific section from HTML by looking for id/class/comment markers.
        Returns the section HTML or None if not found."""
        section_name_lower = section_name.lower().strip()

        # Try multiple patterns to find the section
        patterns = [
            # id="hero", id="about", etc.
            rf'(<(?:section|div|header|footer)[^>]*\bid\s*=\s*["\'](?:[^"\']*\b)?{re.escape(section_name_lower)}(?:\b[^"\']*)?["\'][^>]*>)',
            # <!-- HERO SECTION --> or <!-- hero -->
            rf'(<!--\s*{re.escape(section_name_lower)}[\s\w]*-->)',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                start_pos = match.start()
                # Find the end of this section (next section or end of body)
                # Look for next <section, <footer, <!-- next section -->, or </body>
                end_patterns = [
                    r'<(?:section|footer)[^>]*\bid\s*=\s*["\']',
                    r'<!--\s*(?:end|/)\s',
                    r'</body>',
                ]
                end_pos = len(html)
                remaining = html[match.end():]
                for ep in end_patterns:
                    end_match = re.search(ep, remaining, re.IGNORECASE)
                    if end_match:
                        candidate = match.end() + end_match.start()
                        if candidate < end_pos:
                            end_pos = candidate

                return html[start_pos:end_pos]
        return None

    async def refine(
        self,
        current_html: str,
        modification_request: str,
        section_to_modify: Optional[str] = None,
        reference_analysis: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Smart Refine: classifica la richiesta e usa la strategia ottimale.

        Strategies (from fastest/safest to slowest/riskiest):
        1. css_vars  — Only modify :root CSS variables (colors, fonts, spacing)
        2. text      — Only modify text content (headings, paragraphs, buttons)
        3. section   — Extract and modify a single section
        4. structural — Full HTML modification (original approach, last resort)
        """
        modification_request = sanitize_refine_input(modification_request)

        # === SMART ROUTING ===
        strategy = self._classify_refine_request(modification_request)
        logger.info(f"[SmartRefine] Request: '{modification_request[:80]}...' → Strategy: {strategy}")

        # Strategy 1: CSS Variables (colors, fonts, backgrounds)
        if strategy == "css_vars":
            result = await self._refine_css_vars(current_html, modification_request, reference_analysis)
            if result.get("success"):
                return result
            if result.get("fallback"):
                logger.info("[SmartRefine] CSS strategy failed, falling back to structural")
            # Fall through to structural

        # Strategy 2: Text-only modifications
        if strategy == "text":
            result = await self._refine_text_only(current_html, modification_request, section_to_modify)
            if result.get("success"):
                return result
            if result.get("fallback"):
                logger.info("[SmartRefine] Text strategy failed, falling back to structural")
            # Fall through to structural

        # === AUTO-DETECT SECTION from user message (frontend never sends it) ===
        if not section_to_modify:
            section_to_modify = self._detect_section_from_request(modification_request, current_html)
            if section_to_modify:
                logger.info(f"[SmartRefine] Auto-detected section: '{section_to_modify}'")

        # Strategy 3+4: Section or full structural (original approach)
        logger.info(f"[SmartRefine] Using structural strategy (section={section_to_modify})")

        # Aggressive strip: GSAP script + <style> blocks + SVGs + whitespace
        stripped_html, stash = self._strip_for_refine(current_html)

        original_tokens = self._estimate_tokens(current_html)
        stripped_tokens = self._estimate_tokens(stripped_html)
        logger.info(
            f"[Swarm] Refine HTML reduction: {len(current_html)} -> {len(stripped_html)} chars "
            f"(~{original_tokens} -> ~{stripped_tokens} tokens, saved ~{original_tokens - stripped_tokens} tokens)"
        )

        # Compact design system prompt (trimmed from ~1200 chars to ~600)
        design_system = """RULES:
- Preserve CSS vars: var(--color-primary/secondary/accent/bg/bg-alt/text/text-muted)
- Use Tailwind CSS + font-heading/font-body classes
- Preserve all data-animate attributes. Headings: data-animate="text-split" data-split-type="words". Buttons: data-animate="magnetic". Grids: data-animate="stagger" with .stagger-item children.
- Add data-animate to new elements (fade-up, scale-in, etc.)
- Keep all <!-- __*_PLACEHOLDER__ --> and <!-- __STYLE_*__ --> and <!-- __SVG_INNER_*__ --> comments intact - they are auto-restored after your edit.
- Return ONLY complete HTML between ```html and ``` tags. Do NOT truncate."""

        # Add reference analysis context for color/theme correction
        reference_context = ""
        if reference_analysis:
            reference_context = f"""
ORIGINAL REFERENCE ANALYSIS (the user's desired look):
{reference_analysis}

When the user complains about colors or theme, use the reference analysis above to determine the CORRECT colors, fonts, and mood. Update :root CSS variables, Tailwind classes, and background colors to match the reference."""

        # Strategy: ALWAYS use section-only mode when a section is specified
        # This dramatically reduces token usage and improves quality
        section_only_mode = False
        section_html = None
        if section_to_modify:
            section_html = self._extract_section_html(stripped_html, section_to_modify)
            if section_html:
                section_tokens = self._estimate_tokens(section_html)
                logger.info(
                    f"[Swarm] Section-only mode: extracted '{section_to_modify}' "
                    f"({len(section_html)} chars, ~{section_tokens} tokens)"
                )
                section_only_mode = True

        if section_only_mode and section_html:
            prompt = f"""Modify ONLY this {section_to_modify} section HTML. Return ONLY the modified section.

REQUEST: {modification_request}
{reference_context}

{design_system}

SECTION HTML:
{section_html}"""
        elif section_to_modify:
            prompt = f"""Modify ONLY the {section_to_modify} section. Keep all other sections unchanged.

REQUEST: {modification_request}
{reference_context}

{design_system}

HTML:
{stripped_html}"""
        else:
            prompt = f"""Modify this HTML website.

REQUEST: {modification_request}
{reference_context}

{design_system}

HTML:
{stripped_html}"""

        prompt_tokens = self._estimate_tokens(prompt)
        logger.info(f"[Swarm] Refine prompt: ~{prompt_tokens} tokens (limit: 262144)")

        # Safety check: if still over limit, apply further truncation
        if prompt_tokens > self._TRUNCATION_THRESHOLD_TOKENS:
            logger.warning(f"[Swarm] Prompt too large (~{prompt_tokens} tokens), truncating HTML")
            # Calculate how many chars of HTML we can keep
            # prompt_overhead = prompt length minus the HTML part
            prompt_overhead = len(prompt) - len(stripped_html if not section_only_mode else section_html)
            overhead_tokens = self._estimate_tokens("x" * prompt_overhead)
            max_html_tokens = self._MAX_INPUT_TOKENS - overhead_tokens
            max_html_chars = int(max_html_tokens * 3.3)  # Convert back to chars

            html_to_truncate = stripped_html if not section_only_mode else section_html
            if max_html_chars < len(html_to_truncate) and max_html_chars > 0:
                # Truncate from the middle, keeping head and tail for structure
                keep_head = max_html_chars * 2 // 3
                keep_tail = max_html_chars // 3
                truncated_html = (
                    html_to_truncate[:keep_head]
                    + '\n<!-- ... MIDDLE SECTIONS TRUNCATED FOR SIZE ... -->\n'
                    + html_to_truncate[-keep_tail:]
                )
                # Rebuild prompt with truncated HTML
                if section_only_mode:
                    prompt = f"""Modify ONLY this {section_to_modify} section HTML. Return ONLY the modified section.

REQUEST: {modification_request}
{reference_context}

{design_system}

SECTION HTML:
{truncated_html}"""
                elif section_to_modify:
                    prompt = f"""Modify ONLY the {section_to_modify} section. Keep all other sections unchanged.

REQUEST: {modification_request}
{reference_context}

{design_system}

HTML:
{truncated_html}"""
                else:
                    prompt = f"""Modify this HTML website.

REQUEST: {modification_request}
{reference_context}

{design_system}

HTML:
{truncated_html}"""
                prompt_tokens = self._estimate_tokens(prompt)
                logger.info(f"[Swarm] After truncation: ~{prompt_tokens} tokens")

        start_time = time.time()
        # Hybrid strategy: use the refine client for chat modifications
        # Use higher max_tokens for section mode (section is small), lower for full HTML
        output_tokens = 8000 if section_only_mode else 32000
        logger.info(f"[Swarm] Refine using model: {self.kimi_refine.model}, max_tokens={output_tokens}")
        result = await self.kimi_refine.call_stream(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=output_tokens,
            thinking=False,
            timeout=300.0,
        )

        if not result["success"]:
            # Check for token limit error and return user-friendly message
            error_msg = result.get("error", "")
            if "token limit" in error_msg.lower():
                return {
                    "success": False,
                    "error": "Il sito è troppo grande per essere modificato via chat. Prova a specificare la sezione da modificare (es. 'hero', 'about', 'contact').",
                    "error_code": "token_limit",
                }
            return result

        html_content = self.kimi_refine.extract_html(result["content"])

        # === VALIDATION GUARD: Reject if AI destroyed the site ===
        if html_content:
            original_len = len(stripped_html)
            result_len = len(html_content)
            ratio = result_len / max(original_len, 1)
            logger.info(f"[Swarm] Structural refine size ratio: {ratio:.2f} (result {result_len} / original {original_len})")

            if ratio < 0.5:
                logger.error(f"[Swarm] AI returned truncated/destroyed HTML ({ratio:.0%} of original). Rejecting.")
                return {
                    "success": False,
                    "error": "La modifica ha generato un risultato incompleto. Prova con una richiesta più specifica (es. 'cambia il colore di sfondo della hero section in blu').",
                    "error_code": "truncated_output",
                }

        # If we used section-only mode, re-integrate the modified section into the full HTML
        if section_only_mode and section_to_modify:
            original_section = self._extract_section_html(stripped_html, section_to_modify)
            if original_section and original_section in stripped_html:
                # Replace the old section with the new one in the stripped HTML
                html_content = stripped_html.replace(original_section, html_content, 1)
                logger.info(f"[Swarm] Re-integrated modified '{section_to_modify}' section into full HTML")

        # Re-inject everything that was stripped: SVGs, <style> blocks, GSAP script
        html_content = self._reinject_after_refine(html_content, stash)

        html_content = sanitize_output(html_content)

        # Validate HTML completeness - check for closing tags
        if html_content and "</html>" not in html_content.lower():
            logger.warning("[Swarm] Refine returned truncated HTML (missing </html>)")
            # Try auto-repair: close open tags
            if "</body>" not in html_content.lower():
                html_content += "\n</body>\n</html>"
                logger.info("[Swarm] Auto-repaired truncated HTML (added </body></html>)")
            else:
                html_content += "\n</html>"
                logger.info("[Swarm] Auto-repaired truncated HTML (added </html>)")

        # Validate CSS variables are preserved (critical for theme consistency)
        if html_content and "--color-primary" not in html_content:
            logger.warning("[Swarm] Refine stripped CSS variables - this may break theme styling")

        generation_time = int((time.time() - start_time) * 1000)
        cost = self.kimi_refine.calculate_cost(
            result.get("tokens_input", 0),
            result.get("tokens_output", 0),
        )

        logger.info(f"[Swarm] Refine completato in {generation_time}ms (${cost})")

        return {
            "success": True,
            "html_content": html_content,
            "model_used": self.kimi_refine.model,
            "tokens_input": result.get("tokens_input", 0),
            "tokens_output": result.get("tokens_output", 0),
            "cost_usd": cost,
            "generation_time_ms": generation_time,
            "strategy": "section" if section_only_mode else "structural",
        }


# Singleton
swarm = SwarmGenerator()

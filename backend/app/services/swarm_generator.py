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
import re
from typing import Dict, Any, Optional, List, Callable, Tuple

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

    # Kimi K2.5 hard limit is 262144 tokens. We target <180K input tokens
    # to leave room for max_tokens output and safety margin.
    _MAX_INPUT_CHARS = 600000  # ~150K tokens at ~4 chars/token

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 chars per token for mixed HTML/text."""
        return len(text) // 4

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
        Usa streaming per evitare timeout con HTML grandi.
        Aggressively strips GSAP, <style>, SVGs, whitespace to stay under 262144 token limit.
        """
        modification_request = sanitize_refine_input(modification_request)

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

        if section_to_modify:
            prompt = f"""Modify ONLY the {section_to_modify} section. Keep all other sections unchanged.

REQUEST: {modification_request}

{design_system}

HTML:
{stripped_html}"""
        else:
            prompt = f"""Modify this HTML website.

REQUEST: {modification_request}

{design_system}

HTML:
{stripped_html}"""

        prompt_tokens = self._estimate_tokens(prompt)
        logger.info(f"[Swarm] Refine prompt: ~{prompt_tokens} tokens (limit: 262144)")

        # Safety check: if still over limit, apply further truncation
        if prompt_tokens > 200000:
            logger.warning(f"[Swarm] Prompt still too large (~{prompt_tokens} tokens), truncating HTML")
            # Keep first 400K chars of HTML (~100K tokens) - enough for structure
            max_html_chars = self._MAX_INPUT_CHARS - len(prompt) + len(stripped_html)
            if max_html_chars < len(stripped_html):
                # Truncate from the middle, keeping head and tail for structure
                keep_head = max_html_chars * 2 // 3
                keep_tail = max_html_chars // 3
                stripped_html = (
                    stripped_html[:keep_head]
                    + '\n<!-- ... MIDDLE SECTIONS TRUNCATED FOR SIZE ... -->\n'
                    + stripped_html[-keep_tail:]
                )
                # Rebuild prompt with truncated HTML
                if section_to_modify:
                    prompt = f"""Modify ONLY the {section_to_modify} section. Keep all other sections unchanged.

REQUEST: {modification_request}

{design_system}

HTML:
{stripped_html}"""
                else:
                    prompt = f"""Modify this HTML website.

REQUEST: {modification_request}

{design_system}

HTML:
{stripped_html}"""
                prompt_tokens = self._estimate_tokens(prompt)
                logger.info(f"[Swarm] After truncation: ~{prompt_tokens} tokens")

        start_time = time.time()
        # Use streaming with higher max_tokens to handle large HTML sites
        result = await self.kimi.call_stream(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=16000,
            thinking=False,
            timeout=300.0,
        )

        if not result["success"]:
            return result

        html_content = self.kimi.extract_html(result["content"])

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

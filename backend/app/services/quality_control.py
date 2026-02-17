"""
Quality Control Pipeline - Autocritica e auto-fix per siti generati.

Pipeline:
  Phase 1: Fast automated validation (HTML structure, GSAP, colors, accessibility)
  Phase 2: AI self-critique via Kimi (design evaluation by a "senior web designer")
  Phase 3: Auto-fix agents apply targeted repairs
  Phase 4: Re-validate to confirm fixes

Max 2 iterations. If score doesn't improve, mark as needs_manual_review.
"""

import logging
import re
import time
import json
from typing import Dict, Any, List, Optional, Callable

from app.services.kimi_client import kimi
from app.services.qc_agents import (
    AnimationFixAgent,
    ColorCoherenceAgent,
    TextQualityAgent,
    AccessibilityAgent,
    LayoutFixAgent,
    SectionFixAgent,
)
from app.models.qc_report import QCIssue, QCReport, QCFixResult

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[int, str, Optional[Dict[str, Any]]], None]]

PASS_THRESHOLD = 7.0
MAX_ITERATIONS = 2

BANNED_PHRASES = [
    "benvenuti",
    "benvenuto",
    "siamo un'azienda",
    "siamo un azienda",
    "leader nel settore",
    "a 360 gradi",
    "offriamo servizi",
    "il nostro team",
    "qualita e professionalita",
    "qualit\u00e0 e professionalit\u00e0",
    "la nostra azienda",
    "benvenuti nel nostro sito",
    "benvenuti sul nostro sito",
]


class QualityControlPipeline:
    """Pipeline di autocritica e auto-fix per siti generati."""

    def __init__(self):
        self.kimi = kimi
        self.animation_agent = AnimationFixAgent()
        self.color_agent = ColorCoherenceAgent()
        self.text_agent = TextQualityAgent()
        self.accessibility_agent = AccessibilityAgent()
        self.layout_agent = LayoutFixAgent()
        self.section_agent = SectionFixAgent()

    async def run_full_qc(
        self,
        html: str,
        theme_config: Dict[str, Any],
        requested_sections: List[str],
        style_id: str,
        site_id: str = "",
        on_progress: ProgressCallback = None,
        variant_selections: Optional[Dict[str, str]] = None,
    ) -> QCReport:
        """
        Run complete QC pipeline: validate -> critique -> fix -> re-validate.
        Returns a QCReport with scores, issues found, and fixes applied.
        """
        start_time = time.time()
        html_before = html
        all_fixes: List[QCFixResult] = []
        iteration = 0

        report = QCReport(
            site_id=site_id,
            overall_score=0.0,
            html_before=html_before,
        )

        if on_progress:
            on_progress(0, "Avvio controllo qualit\u00e0...", {"phase": "qc_start"})

        # ===============================
        # PHASE 1: Automated Checks
        # ===============================
        logger.info("[QC] Phase 1: Automated validation")
        automated_issues = self.run_automated_checks(
            html, theme_config, requested_sections,
            variant_selections=variant_selections,
        )
        report.automated_issues = automated_issues

        critical_count = sum(1 for i in automated_issues if i.severity == "critical")
        warning_count = sum(1 for i in automated_issues if i.severity == "warning")
        logger.info(
            f"[QC] Phase 1 complete: {len(automated_issues)} issues "
            f"({critical_count} critical, {warning_count} warning)"
        )

        if on_progress:
            on_progress(1, f"Trovati {len(automated_issues)} problemi", {
                "phase": "qc_validated",
                "issues": len(automated_issues),
                "critical": critical_count,
            })

        # ===============================
        # PHASE 2: AI Critique
        # ===============================
        logger.info("[QC] Phase 2: AI critique")
        ai_critique = await self.run_ai_critique(
            html, style_id, variant_selections=variant_selections,
        )
        report.ai_critique = ai_critique
        report.overall_score = ai_critique.get("overall_score", 5.0)

        logger.info(f"[QC] Phase 2 complete: AI score = {report.overall_score}/10")

        if on_progress:
            on_progress(2, f"Valutazione AI: {report.overall_score}/10", {
                "phase": "qc_critique",
                "score": report.overall_score,
            })

        # ===============================
        # PHASE 3: Fix Loop (max 2 iterations)
        # ===============================
        fixable_issues = [i for i in automated_issues if i.auto_fixable]

        # Also convert AI-identified issues
        ai_issues_list = ai_critique.get("issues", [])
        for ai_issue in ai_issues_list:
            if isinstance(ai_issue, dict) and ai_issue.get("auto_fixable"):
                fixable_issues.append(QCIssue(
                    type=ai_issue.get("type", "layout"),
                    severity=ai_issue.get("severity", "warning"),
                    element=ai_issue.get("element", "unknown"),
                    description=ai_issue.get("description", ""),
                    auto_fixable=True,
                ))

        while iteration < MAX_ITERATIONS and fixable_issues:
            iteration += 1
            logger.info(f"[QC] Phase 3: Fix iteration {iteration}/{MAX_ITERATIONS}")

            if on_progress:
                on_progress(3, f"Correzione automatica (round {iteration})...", {
                    "phase": "qc_fixing",
                    "iteration": iteration,
                })

            html, fixes = await self._apply_fix_agents(html, fixable_issues, theme_config, style_id)
            all_fixes.extend(fixes)

            actual_fixes = sum(f.issues_fixed for f in fixes)
            if actual_fixes == 0:
                logger.info("[QC] No fixes applied, stopping iteration loop")
                break

            # Re-validate
            new_issues = self.run_automated_checks(html, theme_config, requested_sections)
            new_fixable = [i for i in new_issues if i.auto_fixable]

            if len(new_issues) >= len(automated_issues):
                logger.info("[QC] Issues not improving, stopping iteration loop")
                break

            fixable_issues = new_fixable
            automated_issues = new_issues

        report.automated_issues = automated_issues
        report.fixes_applied = all_fixes
        report.iterations = iteration

        # ===============================
        # PHASE 4: Final Score
        # ===============================
        fixes_applied_count = sum(f.issues_fixed for f in all_fixes)
        fix_bonus = min(fixes_applied_count * 0.2, 1.5)
        report.final_score = min(10.0, report.overall_score + fix_bonus)
        report.passed = report.final_score >= PASS_THRESHOLD
        report.html_after = html
        report.needs_manual_review = not report.passed and iteration >= MAX_ITERATIONS

        elapsed = int((time.time() - start_time) * 1000)
        logger.info(
            f"[QC] Pipeline complete in {elapsed}ms: "
            f"score {report.overall_score} -> {report.final_score}, "
            f"passed={report.passed}, fixes={fixes_applied_count}, "
            f"iterations={iteration}"
        )

        if on_progress:
            status = "superato" if report.passed else "revisione necessaria"
            on_progress(4, f"QC {status}: {report.final_score:.1f}/10", {
                "phase": "qc_complete",
                "final_score": report.final_score,
                "passed": report.passed,
            })

        return report

    # =========================================================
    # Phase 1: Automated Validation
    # =========================================================
    def run_automated_checks(
        self,
        html: str,
        theme_config: Dict[str, Any],
        requested_sections: List[str],
        variant_selections: Optional[Dict[str, str]] = None,
    ) -> List[QCIssue]:
        """Phase 1: Fast automated validation (no AI). Should complete <1 second."""
        issues: List[QCIssue] = []

        issues.extend(self._check_html_structure(html))
        issues.extend(self._check_placeholders(html))
        issues.extend(self._check_required_sections(html, requested_sections))
        issues.extend(self._check_gsap_animations(html))
        issues.extend(self._check_color_coherence(html, theme_config))
        issues.extend(self._check_required_resources(html))
        issues.extend(self._check_duplicate_ids(html))
        issues.extend(self._check_accessibility(html))
        issues.extend(self._check_heading_hierarchy(html))
        issues.extend(self._check_banned_phrases(html))

        # Art Director checks (always active, instant, no AI)
        issues.extend(self._check_animation_density(html))
        issues.extend(self._check_section_flow(html))
        if variant_selections:
            issues.extend(self._check_visual_harmony(variant_selections))

        return issues

    def _check_html_structure(self, html: str) -> List[QCIssue]:
        issues = []
        if "<!DOCTYPE html>" not in html and "<!doctype html>" not in html.lower():
            issues.append(QCIssue(
                type="structure", severity="warning",
                element="document", description="Missing <!DOCTYPE html> declaration",
                auto_fixable=False,
            ))
        if "<html" not in html.lower():
            issues.append(QCIssue(
                type="structure", severity="critical",
                element="document", description="Missing <html> tag",
                auto_fixable=False,
            ))
        if "</body>" not in html.lower():
            issues.append(QCIssue(
                type="structure", severity="critical",
                element="document", description="Missing </body> closing tag",
                auto_fixable=False,
            ))
        if "</html>" not in html.lower():
            issues.append(QCIssue(
                type="structure", severity="critical",
                element="document", description="Missing </html> closing tag",
                auto_fixable=False,
            ))
        return issues

    def _check_placeholders(self, html: str) -> List[QCIssue]:
        issues = []
        # Check for unreplaced {{PLACEHOLDER}} tokens
        placeholders = re.findall(r'\{\{(\w+)\}\}', html)
        for ph in placeholders:
            if ph in ("LOGO_URL",):
                continue
            issues.append(QCIssue(
                type="structure", severity="critical",
                element=f"{{{{{ph}}}}}",
                description=f"Unreplaced placeholder: {{{{{ph}}}}}",
                auto_fixable=True,
            ))

        # Check for unexpanded REPEAT blocks (template engine failed to process them)
        unexpanded = re.findall(r'<!-- REPEAT:(\w+) -->', html)
        for repeat_key in unexpanded:
            issues.append(QCIssue(
                type="structure", severity="warning",
                element=f"REPEAT:{repeat_key}",
                description=f"Unexpanded REPEAT block: {repeat_key} (missing data array)",
                auto_fixable=False,
            ))
        return issues

    def _check_required_sections(self, html: str, requested_sections: List[str]) -> List[QCIssue]:
        issues = []
        html_lower = html.lower()
        for section in requested_sections:
            section_found = (
                f'id="{section}"' in html_lower
                or f"id='{section}'" in html_lower
                or f'id="{section}-section"' in html_lower
                or f'<!-- {section}' in html_lower
            )
            if not section_found:
                issues.append(QCIssue(
                    type="section", severity="warning",
                    element=f"section#{section}",
                    description=f"Requested section '{section}' not found in HTML",
                    auto_fixable=False,
                ))
        return issues

    def _check_gsap_animations(self, html: str) -> List[QCIssue]:
        issues = []

        # h1 tags should have text-split
        h1_tags = re.findall(r'<h1\b[^>]*>', html, re.IGNORECASE)
        for tag in h1_tags:
            if 'data-animate' not in tag:
                issues.append(QCIssue(
                    type="animation", severity="warning",
                    element="h1",
                    description="h1 missing data-animate=\"text-split\"",
                    auto_fixable=True,
                ))
                break

        # h2 tags should have text-split
        h2_tags = re.findall(r'<h2\b[^>]*>', html, re.IGNORECASE)
        h2_without = [t for t in h2_tags if 'data-animate' not in t]
        if h2_without and len(h2_without) > len(h2_tags) // 2:
            issues.append(QCIssue(
                type="animation", severity="warning",
                element="h2",
                description=f"{len(h2_without)}/{len(h2_tags)} h2 tags missing data-animate=\"text-split\"",
                auto_fixable=True,
            ))

        # CTA buttons should have magnetic
        cta_pattern = re.compile(
            r'<a\b[^>]*(?:bg-\[var\(--color-primary\)\]|btn|cta|bg-primary)[^>]*>',
            re.IGNORECASE
        )
        cta_tags = cta_pattern.findall(html)
        cta_without = [t for t in cta_tags if 'data-animate="magnetic"' not in t]
        if cta_without:
            issues.append(QCIssue(
                type="animation", severity="warning",
                element="a.cta-button",
                description=f"{len(cta_without)} CTA buttons missing data-animate=\"magnetic\"",
                auto_fixable=True,
            ))

        # Cards should have animation
        card_pattern = re.compile(
            r'<div\b[^>]*(?:rounded-(?:xl|2xl|3xl))[^>]*(?:shadow-(?:lg|xl|2xl))[^>]*>',
            re.IGNORECASE
        )
        card_tags = card_pattern.findall(html)
        cards_without = [t for t in card_tags if 'data-animate' not in t]
        if cards_without and len(cards_without) > 2:
            issues.append(QCIssue(
                type="animation", severity="info",
                element="div.card",
                description=f"{len(cards_without)} card elements missing data-animate=\"fade-up\"",
                auto_fixable=True,
            ))

        # Validate data-animate values
        valid_animations = {
            'fade-up', 'fade-down', 'fade-left', 'fade-right',
            'scale-in', 'scale-up', 'rotate-in', 'flip-up', 'blur-in',
            'slide-up', 'reveal-left', 'reveal-right', 'reveal-up', 'reveal-down',
            'bounce-in', 'zoom-out', 'text-split', 'text-reveal', 'typewriter',
            'clip-reveal', 'blur-slide', 'rotate-3d', 'stagger', 'stagger-scale',
            'tilt', 'magnetic', 'card-hover-3d', 'float', 'gradient-flow',
            'morph-bg', 'image-zoom', 'draw-svg', 'split-screen', 'parallax',
            'marquee', 'count-up',
        }
        used_animations = re.findall(r'data-animate="([^"]*)"', html)
        for anim in used_animations:
            if anim not in valid_animations:
                issues.append(QCIssue(
                    type="animation", severity="warning",
                    element=f'[data-animate="{anim}"]',
                    description=f"Invalid data-animate value: '{anim}'",
                    auto_fixable=False,
                ))

        return issues

    def _check_color_coherence(self, html: str, theme_config: Dict[str, Any]) -> List[QCIssue]:
        issues = []
        if not theme_config:
            return issues

        palette = set()
        for key in ["primary_color", "secondary_color", "accent_color", "bg_color",
                     "bg_alt_color", "text_color", "text_muted_color"]:
            color = theme_config.get(key, "")
            if color:
                palette.add(color.lower().strip())

        # Common neutrals always acceptable
        acceptable = {'#fff', '#ffffff', '#000', '#000000', '#333', '#333333',
                      '#666', '#666666', '#999', '#999999', '#ccc', '#cccccc',
                      '#eee', '#eeeeee', '#f8f8f8', '#f0f0f0', 'transparent',
                      '#111', '#111111', '#222', '#222222'}
        palette.update(acceptable)

        inline_colors = re.findall(
            r'(?:color|background-color|background|border-color)\s*:\s*(#[0-9a-fA-F]{3,8})',
            html
        )

        off_palette = set()
        for color in inline_colors:
            normalized = color.lower().strip()
            if len(normalized) == 4:
                normalized = '#' + ''.join(c * 2 for c in normalized[1:])
            if normalized not in palette:
                off_palette.add(color)

        for color in list(off_palette)[:5]:
            issues.append(QCIssue(
                type="color", severity="info",
                element="inline-style",
                description=f"Off-palette color found: {color}",
                auto_fixable=True,
            ))

        return issues

    def _check_required_resources(self, html: str) -> List[QCIssue]:
        issues = []
        if 'name="viewport"' not in html:
            issues.append(QCIssue(
                type="structure", severity="critical",
                element="meta[viewport]",
                description="Missing responsive viewport meta tag",
                auto_fixable=False,
            ))
        if 'tailwindcss' not in html.lower() and 'tailwind' not in html.lower():
            issues.append(QCIssue(
                type="structure", severity="critical",
                element="script[tailwind]",
                description="Tailwind CSS CDN not found",
                auto_fixable=False,
            ))
        if 'gsap' not in html.lower():
            issues.append(QCIssue(
                type="structure", severity="critical",
                element="script[gsap]",
                description="GSAP library not loaded",
                auto_fixable=False,
            ))
        if 'fonts.googleapis.com' not in html and 'fonts.google' not in html:
            issues.append(QCIssue(
                type="structure", severity="warning",
                element="link[google-fonts]",
                description="Google Fonts not loaded",
                auto_fixable=False,
            ))
        return issues

    def _check_duplicate_ids(self, html: str) -> List[QCIssue]:
        issues = []
        ids = re.findall(r'\bid="([^"]*)"', html)
        seen = set()
        for id_val in ids:
            if not id_val:
                continue
            if id_val in seen:
                issues.append(QCIssue(
                    type="structure", severity="warning",
                    element=f'#{id_val}',
                    description=f"Duplicate id=\"{id_val}\" found in document",
                    auto_fixable=True,
                ))
            seen.add(id_val)
        return issues

    def _check_accessibility(self, html: str) -> List[QCIssue]:
        issues = []
        img_tags = re.findall(r'<img\b[^>]*>', html, re.IGNORECASE)
        imgs_without_alt = [t for t in img_tags if 'alt' not in t.lower()]
        if imgs_without_alt:
            issues.append(QCIssue(
                type="accessibility", severity="warning",
                element="img",
                description=f"{len(imgs_without_alt)} images missing alt attribute",
                auto_fixable=True,
            ))

        imgs_empty_src = [t for t in img_tags if 'src=""' in t or "src=''" in t]
        if imgs_empty_src:
            issues.append(QCIssue(
                type="accessibility", severity="warning",
                element="img[src='']",
                description=f"{len(imgs_empty_src)} images have empty src attribute",
                auto_fixable=False,
            ))
        return issues

    def _check_heading_hierarchy(self, html: str) -> List[QCIssue]:
        issues = []
        headings = re.findall(r'<(h[1-6])\b', html, re.IGNORECASE)
        if not headings:
            return issues

        levels = [int(h[1]) for h in headings]

        if levels and levels[0] != 1:
            issues.append(QCIssue(
                type="accessibility", severity="info",
                element=f"h{levels[0]}",
                description=f"First heading is h{levels[0]}, expected h1",
                auto_fixable=False,
            ))

        for i in range(1, len(levels)):
            if levels[i] > levels[i - 1] + 1:
                issues.append(QCIssue(
                    type="accessibility", severity="info",
                    element=f"h{levels[i]}",
                    description=f"Heading hierarchy skip: h{levels[i-1]} -> h{levels[i]}",
                    auto_fixable=False,
                ))
                break
        return issues

    def _check_banned_phrases(self, html: str) -> List[QCIssue]:
        issues = []
        text_content = re.sub(r'<[^>]+>', ' ', html).lower()
        for phrase in BANNED_PHRASES:
            if phrase.lower() in text_content:
                issues.append(QCIssue(
                    type="text", severity="warning",
                    element="text-content",
                    description=f"Banned generic phrase found: \"{phrase}\"",
                    auto_fixable=True,
                ))
        return issues

    # =========================================================
    # Art Director Checks (instant, no AI)
    # =========================================================

    # Expected narrative flow — sections that should appear before others
    _FLOW_RULES = [
        ("about", "testimonials"),
        ("services", "pricing"),
        ("about", "team"),
        ("hero", "about"),
        ("features", "pricing"),
        ("services", "cta"),
    ]

    # Visual families — variants from different families clash
    _VISUAL_FAMILIES: Dict[str, List[str]] = {
        "bento": ["bento", "masonry"],
        "minimal": ["minimal", "zen", "clean"],
        "editorial": ["magazine", "editorial", "spotlight", "split-scroll"],
        "bold": ["brutalist", "neon", "dark-bold", "animated-shapes"],
    }

    def _check_animation_density(self, html: str) -> List[QCIssue]:
        """Warn if too many different scroll-entrance animation types are used.
        More than 6 distinct types creates visual chaos."""
        issues = []
        used_types = set(re.findall(r'data-animate="([^"]*)"', html))
        # Only count scroll-entrance animations, not interactive ones
        entrance_types = {
            "fade-up", "fade-down", "fade-left", "fade-right",
            "scale-in", "scale-up", "rotate-in", "flip-up", "blur-in",
            "slide-up", "reveal-left", "reveal-right", "reveal-up", "reveal-down",
            "bounce-in", "zoom-out", "clip-reveal", "blur-slide", "rotate-3d",
        }
        entrance_used = used_types & entrance_types
        if len(entrance_used) > 6:
            issues.append(QCIssue(
                type="animation", severity="warning",
                element="data-animate",
                description=(
                    f"Animation overload: {len(entrance_used)} distinct entrance types "
                    f"({', '.join(sorted(entrance_used))}). "
                    f"Consider limiting to 4-5 for visual cohesion."
                ),
                auto_fixable=False,
            ))
        return issues

    def _check_section_flow(self, html: str) -> List[QCIssue]:
        """Verify logical section ordering (about before testimonials, etc.)."""
        issues = []
        # Extract section IDs from HTML in order
        section_ids = re.findall(r'id="([a-z]+)(?:-section)?"', html.lower())
        if not section_ids:
            return issues

        # Build position map
        positions: Dict[str, int] = {}
        for i, sid in enumerate(section_ids):
            if sid not in positions:
                positions[sid] = i

        for before, after in self._FLOW_RULES:
            if before in positions and after in positions:
                if positions[before] > positions[after]:
                    issues.append(QCIssue(
                        type="layout", severity="info",
                        element=f"section#{after}",
                        description=(
                            f"Section flow: '{after}' appears before '{before}'. "
                            f"Consider placing '{before}' first for better narrative."
                        ),
                        auto_fixable=False,
                    ))
        return issues

    def _check_visual_harmony(self, variant_selections: Dict[str, str]) -> List[QCIssue]:
        """Detect clashing visual families across selected component variants."""
        issues = []
        # Map each selected variant to its visual family
        families_used: Dict[str, List[str]] = {}
        for section, variant_id in variant_selections.items():
            if section in ("nav", "footer"):
                continue
            variant_lower = variant_id.lower()
            for family_name, keywords in self._VISUAL_FAMILIES.items():
                if any(kw in variant_lower for kw in keywords):
                    families_used.setdefault(family_name, []).append(section)
                    break

        # If 3+ different families are represented, flag it
        if len(families_used) >= 3:
            family_summary = ", ".join(
                f"{name}({'+'.join(secs)})"
                for name, secs in families_used.items()
            )
            issues.append(QCIssue(
                type="layout", severity="info",
                element="variant-selection",
                description=(
                    f"Visual harmony: {len(families_used)} different style families "
                    f"detected ({family_summary}). Consider using fewer families "
                    f"for a more cohesive look."
                ),
                auto_fixable=False,
            ))
        return issues

    # =========================================================
    # Phase 2: AI Critique
    # =========================================================
    async def run_ai_critique(
        self, html: str, style_id: str,
        variant_selections: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Phase 2: AI self-critique using Kimi. Returns structured evaluation.
        When ART_DIRECTOR_QC is enabled, adds section_flow and visual_coherence dimensions."""

        from app.core.config import settings as _settings

        # Truncate HTML to save tokens (keep first ~8000 chars)
        html_excerpt = html[:8000]
        if len(html) > 8000:
            html_excerpt += "\n... [HTML truncated for review] ..."

        # Enhanced dimensions when Art Director QC is on
        art_director_block = ""
        art_director_scores = ""
        if _settings.ART_DIRECTOR_QC:
            variant_context = ""
            if variant_selections:
                variant_context = f"\nVarianti selezionate: {json.dumps(variant_selections)}\n"
            art_director_block = f"""
9. section_flow - Le sezioni seguono un ordine narrativo logico? (identita' → offerta → prova sociale → azione)
10. visual_coherence - I componenti selezionati appartengono alla stessa famiglia visiva? Coesione cross-sezione?
{variant_context}"""
            art_director_scores = ',\n    "section_flow": 7,\n    "visual_coherence": 7'

        prompt = f"""Sei un Senior Web Designer con 15 anni di esperienza. Valuta questo sito generato automaticamente.
Il template style e' "{style_id}".

Rispondi SOLO con un JSON valido, nessun markdown, nessuna spiegazione.

HTML DA VALUTARE:
{html_excerpt}

Valuta queste categorie (1-10 ciascuna):
1. visual_hierarchy - Gerarchia visiva chiara? L'occhio sa dove guardare?
2. color_harmony - I colori sono armonici? Palette coerente?
3. typography - Font leggibili? Contrasto testo/sfondo? Heading vs body differenziati?
4. animation_quality - Animazioni GSAP presenti e sensate? data-animate usati bene?
5. content_quality - Testi specifici e coinvolgenti? (NO frasi generiche)
6. cta_effectiveness - CTA visibili, persuasivi, ben posizionati?
7. whitespace_balance - Spaziatura equilibrata? Non troppo denso ne' troppo vuoto?
8. mobile_readiness - Grid responsive? Classi Tailwind mobile-first?
{art_director_block}
Rispondi con questo JSON:
{{
  "overall_score": 7.5,
  "scores": {{
    "visual_hierarchy": 8,
    "color_harmony": 7,
    "typography": 8,
    "animation_quality": 7,
    "content_quality": 6,
    "cta_effectiveness": 8,
    "whitespace_balance": 7,
    "mobile_readiness": 8{art_director_scores}
  }},
  "strengths": [
    "Punto di forza 1",
    "Punto di forza 2"
  ],
  "issues": [
    {{
      "type": "animation",
      "severity": "warning",
      "element": "h2",
      "description": "Descrizione problema",
      "auto_fixable": true
    }}
  ],
  "suggestions": [
    "Suggerimento miglioramento 1",
    "Suggerimento miglioramento 2"
  ]
}}

IMPORTANT: overall_score deve essere la media pesata (content_quality e cta_effectiveness pesano doppio).
Rispondi SOLO con il JSON."""

        result = await self.kimi.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500, thinking=False, timeout=45.0,
        )

        if result.get("success"):
            try:
                content = result["content"]
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    critique = json.loads(json_match.group(0))
                    score = critique.get("overall_score", 5.0)
                    if not isinstance(score, (int, float)) or score < 1 or score > 10:
                        critique["overall_score"] = 5.0
                    return critique
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[QC] AI critique JSON parse failed: {e}")

        logger.warning("[QC] AI critique failed, using fallback scores")
        return {
            "overall_score": 6.0,
            "scores": {
                "visual_hierarchy": 6, "color_harmony": 6,
                "typography": 6, "animation_quality": 6,
                "content_quality": 6, "cta_effectiveness": 6,
                "whitespace_balance": 6, "mobile_readiness": 6,
            },
            "strengths": [],
            "issues": [],
            "suggestions": ["AI critique unavailable - manual review recommended"],
        }

    # =========================================================
    # Phase 3: Fix Agents
    # =========================================================
    async def _apply_fix_agents(
        self,
        html: str,
        issues: List[QCIssue],
        theme_config: Dict[str, Any],
        style_id: str,
    ) -> tuple:
        """
        Apply targeted fixes using specialized agents.
        Returns (modified_html, list_of_fix_results).

        Each agent receives the current HTML and returns (modified_html, QCFixResult).
        Agents are chained so each one operates on the output of the previous.
        Order: layout -> animation -> color -> text -> accessibility -> section
        """
        results: List[QCFixResult] = []
        fixable = [i for i in issues if i.auto_fixable]

        if not fixable:
            return html, results

        # Group issues by type
        by_type: Dict[str, List[QCIssue]] = {}
        for issue in fixable:
            by_type.setdefault(issue.type, []).append(issue)

        # Apply fixes in order, chaining HTML through each agent
        if "structure" in by_type:
            html, fix_result = self.layout_agent.fix(html, by_type["structure"])
            results.append(fix_result)

        if "animation" in by_type:
            html, fix_result = self.animation_agent.fix(html, by_type["animation"])
            results.append(fix_result)

        if "color" in by_type:
            html, fix_result = self.color_agent.fix(html, theme_config, by_type["color"])
            results.append(fix_result)

        if "text" in by_type:
            html, fix_result = await self.text_agent.fix(html, by_type["text"], kimi_client=self.kimi)
            results.append(fix_result)

        if "accessibility" in by_type:
            html, fix_result = self.accessibility_agent.fix(html, by_type["accessibility"])
            results.append(fix_result)

        if "section" in by_type:
            missing = [i.element.replace("section#", "") for i in by_type["section"]]
            html, fix_result = await self.section_agent.fix(
                html, missing, theme_config, style_id, kimi_client=self.kimi,
            )
            results.append(fix_result)

        return html, results


# =========================================================
# Quick QC (lightweight, for chat refinements)
# =========================================================
async def quick_qc(html: str, theme_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Lightweight QC check for chat refinement outputs.
    Only runs automated checks, no AI critique.
    """
    pipeline = QualityControlPipeline()
    issues = pipeline.run_automated_checks(html, theme_config or {}, [])

    critical = [i for i in issues if i.severity == "critical"]
    warnings = [i for i in issues if i.severity == "warning"]

    return {
        "total_issues": len(issues),
        "critical": len(critical),
        "warnings": len(warnings),
        "issues": [i.to_dict() for i in issues[:10]],
        "passed": len(critical) == 0,
    }


# Singleton
qc_pipeline = QualityControlPipeline()

"""
Pre-Delivery Quality Check - Fast deterministic validation for generated HTML.

Runs AFTER template assembly and BEFORE the AI-powered QC pipeline.
Catches common issues: leftover placeholders, missing images, empty sections,
banned generic text, missing alt text, broken links, missing GSAP animations.

Auto-fixes what it can (placeholders, alt text, broken images, empty sections).
Returns a scored report with issues and the fixed HTML.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PreDeliveryIssue:
    severity: str  # "critical", "high", "medium", "low"
    check_type: str  # "placeholder", "missing_image", "empty_section", etc.
    message: str
    location: str = ""  # e.g. "hero section", "line 42"


@dataclass
class PreDeliveryReport:
    score: float = 100.0
    issues: List[PreDeliveryIssue] = field(default_factory=list)
    fixes_applied: List[Dict[str, str]] = field(default_factory=list)
    html_fixed: str = ""
    passed: bool = True

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "issues": [
                {
                    "severity": i.severity,
                    "type": i.check_type,
                    "message": i.message,
                    "location": i.location,
                }
                for i in self.issues
            ],
            "fixes_applied": self.fixes_applied,
            "passed": self.passed,
        }


# ---------------------------------------------------------------------------
# Severity weights for scoring
# ---------------------------------------------------------------------------

_SEVERITY_PENALTY = {
    "critical": 15,
    "high": 8,
    "medium": 3,
    "low": 1,
}

# ---------------------------------------------------------------------------
# Known section IDs (matching backend/app/components/ directory layout)
# ---------------------------------------------------------------------------

KNOWN_SECTION_IDS = {
    "hero", "about", "services", "contact", "footer", "gallery",
    "testimonials", "pricing", "features", "team", "faq", "blog",
    "cta", "stats", "process", "menu", "nav", "booking",
    "reservation", "schedule", "logos", "social-proof", "awards",
    "comparison", "donations", "listings", "newsletter", "app-download",
}

# Map of common aliases / alternative names to canonical section IDs
_SECTION_ALIASES = {
    "contatti": "contact",
    "contatto": "contact",
    "chi-siamo": "about",
    "chi_siamo": "about",
    "servizi": "services",
    "galleria": "gallery",
    "portfolio": "gallery",
    "prezzi": "pricing",
    "domande": "faq",
    "recensioni": "testimonials",
    "squadra": "team",
    "processo": "process",
    "caratteristiche": "features",
    "statistiche": "stats",
    "prenotazione": "booking",
    "calendario": "schedule",
    "donazioni": "donations",
}


# ---------------------------------------------------------------------------
# Main checker class
# ---------------------------------------------------------------------------

class PreDeliveryCheck:
    """Fast, deterministic quality check for generated HTML."""

    # Banned generic phrases (Italian) - case-insensitive matching
    BANNED_PHRASES = [
        "lorem ipsum",
        "dolor sit amet",
        "benvenuti nel nostro sito",
        "benvenuti sul nostro sito",
        "siamo un'azienda leader",
        "siamo un azienda leader",
        "la nostra mission",
        "azienda leader nel settore",
        "siamo un team di professionisti",
        "il nostro obiettivo",
        "leader nel settore",
        "a 360 gradi",
        "offriamo servizi",
        "qualita e professionalita",
        "qualità e professionalità",
        "la nostra azienda",
    ]

    # Patterns for placeholder detection
    _PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_][A-Z0-9_]*\}\}")

    # Patterns for broken image detection
    _IMG_TAG_RE = re.compile(r"<img\b[^>]*?>", re.IGNORECASE | re.DOTALL)
    _SRC_ATTR_RE = re.compile(r"""\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
    _ALT_ATTR_RE = re.compile(r"""\balt\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)

    # Section detection: <section id="...">, <footer id="...">, or data-section="..."
    _SECTION_ID_RE = re.compile(
        r"""<(?:section|footer|div|header)\b[^>]*?\bid\s*=\s*["']([^"']+)["'][^>]*?>""",
        re.IGNORECASE | re.DOTALL,
    )
    _DATA_SECTION_RE = re.compile(
        r"""data-section\s*=\s*["']([^"']+)["']""",
        re.IGNORECASE,
    )

    # Entire section block (greedy enough to capture content, non-greedy overall)
    _SECTION_BLOCK_RE = re.compile(
        r"(<(?:section|footer)\b[^>]*?>)(.*?)(</(?:section|footer)>)",
        re.IGNORECASE | re.DOTALL,
    )

    # GSAP data-animate attributes
    _DATA_ANIMATE_RE = re.compile(r'data-animate\s*=\s*["\'][^"\']+["\']', re.IGNORECASE)

    # Link detection
    _LINK_RE = re.compile(r"<a\b[^>]*?>", re.IGNORECASE | re.DOTALL)
    _HREF_RE = re.compile(r"""\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)

    # Strip HTML tags for text content check
    _STRIP_TAGS_RE = re.compile(r"<[^>]+>")

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def check(
        self,
        html: str,
        requested_sections: Optional[List[str]] = None,
        site_plan: Optional[Dict[str, Any]] = None,
    ) -> PreDeliveryReport:
        """
        Run all checks and auto-fixes on the generated HTML.

        Args:
            html: The assembled HTML string.
            requested_sections: List of section types that should be present
                                (e.g. ["hero", "about", "services", "contact", "footer"]).
            site_plan: Optional dict with generation metadata (unused for now,
                       reserved for future checks).

        Returns:
            PreDeliveryReport with score, issues, fixes, and corrected HTML.
        """
        all_issues: List[PreDeliveryIssue] = []
        all_fixes: List[Dict[str, str]] = []
        working_html = html

        # --- Auto-fixable checks (modify HTML) ---

        issues, working_html, fixes = self._check_placeholders(working_html)
        all_issues.extend(issues)
        all_fixes.extend(fixes)

        issues, working_html, fixes = self._check_images(working_html)
        all_issues.extend(issues)
        all_fixes.extend(fixes)

        issues, working_html, fixes = self._check_alt_text(working_html)
        all_issues.extend(issues)
        all_fixes.extend(fixes)

        issues, working_html, fixes = self._check_empty_sections(working_html)
        all_issues.extend(issues)
        all_fixes.extend(fixes)

        # --- Read-only checks ---

        if requested_sections:
            issues = self._check_sections(working_html, requested_sections)
            all_issues.extend(issues)

        issues = self._check_gsap(working_html)
        all_issues.extend(issues)

        issues = self._check_generic_text(working_html)
        all_issues.extend(issues)

        issues = self._check_empty_links(working_html)
        all_issues.extend(issues)

        # --- Calculate score and build report ---

        score = self._calculate_score(all_issues)
        has_critical = any(i.severity == "critical" for i in all_issues)
        passed = score >= 70 and not has_critical

        report = PreDeliveryReport(
            score=score,
            issues=all_issues,
            fixes_applied=all_fixes,
            html_fixed=working_html,
            passed=passed,
        )

        # --- Logging ---

        n_issues = len(all_issues)
        n_fixes = len(all_fixes)
        if n_issues > 0:
            severity_counts = {}
            for iss in all_issues:
                severity_counts[iss.severity] = severity_counts.get(iss.severity, 0) + 1
            logger.warning(
                "[PreDeliveryCheck] score=%.1f passed=%s issues=%d fixes=%d breakdown=%s",
                score, passed, n_issues, n_fixes, severity_counts,
            )
            for iss in all_issues:
                if iss.severity in ("critical", "high"):
                    logger.warning(
                        "[PreDeliveryCheck] %s [%s] %s | %s",
                        iss.severity.upper(), iss.check_type, iss.message, iss.location,
                    )
        else:
            logger.info("[PreDeliveryCheck] score=%.1f passed=%s - no issues found", score, passed)

        return report

    # ---------------------------------------------------------------------------
    # Individual checks
    # ---------------------------------------------------------------------------

    def _check_placeholders(
        self, html: str
    ) -> Tuple[List[PreDeliveryIssue], str, List[Dict[str, str]]]:
        """Find and remove leftover {{PLACEHOLDER_NAME}} patterns."""
        issues: List[PreDeliveryIssue] = []
        fixes: List[Dict[str, str]] = []

        matches = list(self._PLACEHOLDER_RE.finditer(html))
        if not matches:
            return issues, html, fixes

        seen = set()
        for m in matches:
            placeholder = m.group(0)
            if placeholder not in seen:
                seen.add(placeholder)
                issues.append(PreDeliveryIssue(
                    severity="critical",
                    check_type="placeholder",
                    message=f"Leftover placeholder found: {placeholder}",
                    location=self._approx_location(html, m.start()),
                ))

        # Auto-fix: remove all placeholders
        fixed_html = self._PLACEHOLDER_RE.sub("", html)
        fixes.append({
            "type": "remove_placeholders",
            "description": f"Removed {len(matches)} leftover placeholder(s): {', '.join(sorted(seen))}",
        })

        return issues, fixed_html, fixes

    def _check_images(
        self, html: str
    ) -> Tuple[List[PreDeliveryIssue], str, List[Dict[str, str]]]:
        """Check for broken/missing images and remove them."""
        issues: List[PreDeliveryIssue] = []
        fixes: List[Dict[str, str]] = []
        tags_to_remove: List[str] = []

        for img_match in self._IMG_TAG_RE.finditer(html):
            img_tag = img_match.group(0)
            src_match = self._SRC_ATTR_RE.search(img_tag)

            if not src_match:
                # No src attribute at all
                issues.append(PreDeliveryIssue(
                    severity="high",
                    check_type="missing_image",
                    message="<img> tag has no src attribute",
                    location=self._approx_location(html, img_match.start()),
                ))
                tags_to_remove.append(img_tag)
                continue

            src_value = (src_match.group(1) or src_match.group(2) or "").strip()

            # Empty src
            if not src_value:
                issues.append(PreDeliveryIssue(
                    severity="high",
                    check_type="missing_image",
                    message='<img> tag has empty src=""',
                    location=self._approx_location(html, img_match.start()),
                ))
                tags_to_remove.append(img_tag)
                continue

            # Placeholder image services
            if self._is_placeholder_src(src_value):
                issues.append(PreDeliveryIssue(
                    severity="medium",
                    check_type="placeholder_image",
                    message=f"Image uses placeholder service: {src_value[:80]}",
                    location=self._approx_location(html, img_match.start()),
                ))
                # Don't remove placeholder images - they're better than nothing
                continue

            # Invalid data: URIs (empty or clearly broken)
            if src_value.startswith("data:") and len(src_value) < 30:
                issues.append(PreDeliveryIssue(
                    severity="high",
                    check_type="missing_image",
                    message=f"<img> has invalid/truncated data URI: {src_value[:50]}",
                    location=self._approx_location(html, img_match.start()),
                ))
                tags_to_remove.append(img_tag)
                continue

        # Auto-fix: remove broken image tags
        fixed_html = html
        if tags_to_remove:
            for tag in tags_to_remove:
                fixed_html = fixed_html.replace(tag, "", 1)
            fixes.append({
                "type": "remove_broken_images",
                "description": f"Removed {len(tags_to_remove)} broken <img> tag(s) with empty/missing src",
            })

        return issues, fixed_html, fixes

    def _check_sections(
        self, html: str, requested: List[str]
    ) -> List[PreDeliveryIssue]:
        """Check that requested sections exist in the HTML."""
        issues: List[PreDeliveryIssue] = []

        # Collect all section IDs present in the HTML
        present_ids: set = set()
        for m in self._SECTION_ID_RE.finditer(html):
            present_ids.add(m.group(1).lower().strip())
        for m in self._DATA_SECTION_RE.finditer(html):
            present_ids.add(m.group(1).lower().strip())

        for section_name in requested:
            canonical = section_name.lower().strip()
            # Check direct match
            if canonical in present_ids:
                continue
            # Check alias mapping
            alias_target = _SECTION_ALIASES.get(canonical, canonical)
            if alias_target in present_ids:
                continue
            # Check if any present ID starts with the section name
            # (e.g. "services" matches id="services-grid")
            if any(pid.startswith(canonical) or pid.startswith(alias_target) for pid in present_ids):
                continue

            # Section is missing
            # "nav" and "footer" are sometimes optional or structured differently
            if canonical in ("nav", "footer"):
                severity = "medium"
            else:
                severity = "high"

            issues.append(PreDeliveryIssue(
                severity=severity,
                check_type="missing_section",
                message=f"Requested section '{section_name}' not found in HTML",
                location="whole document",
            ))

        return issues

    def _check_empty_sections(
        self, html: str
    ) -> Tuple[List[PreDeliveryIssue], str, List[Dict[str, str]]]:
        """Find sections with no meaningful text content and remove them."""
        issues: List[PreDeliveryIssue] = []
        fixes: List[Dict[str, str]] = []
        blocks_to_remove: List[str] = []

        for m in self._SECTION_BLOCK_RE.finditer(html):
            open_tag = m.group(1)
            inner_content = m.group(2)
            full_block = m.group(0)

            # Extract section ID for location reporting
            id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', open_tag, re.IGNORECASE)
            section_id = id_match.group(1) if id_match else "unknown"

            # Strip all HTML tags and check remaining text
            text_content = self._STRIP_TAGS_RE.sub("", inner_content).strip()
            # Also remove common whitespace-like entities
            text_content = re.sub(r"&(?:nbsp|#160|#xa0);", "", text_content).strip()

            if not text_content:
                issues.append(PreDeliveryIssue(
                    severity="high",
                    check_type="empty_section",
                    message=f"Section '{section_id}' has no text content",
                    location=f"section#{section_id}",
                ))
                blocks_to_remove.append(full_block)

        # Auto-fix: remove empty sections
        fixed_html = html
        if blocks_to_remove:
            for block in blocks_to_remove:
                fixed_html = fixed_html.replace(block, "", 1)
            removed_ids = []
            for block in blocks_to_remove:
                id_m = re.search(r'id\s*=\s*["\']([^"\']+)["\']', block, re.IGNORECASE)
                removed_ids.append(id_m.group(1) if id_m else "unknown")
            fixes.append({
                "type": "remove_empty_sections",
                "description": f"Removed {len(blocks_to_remove)} empty section(s): {', '.join(removed_ids)}",
            })

        return issues, fixed_html, fixes

    def _check_gsap(self, html: str) -> List[PreDeliveryIssue]:
        """Verify GSAP data-animate attributes are present."""
        issues: List[PreDeliveryIssue] = []

        animate_count = len(self._DATA_ANIMATE_RE.findall(html))

        if animate_count == 0:
            issues.append(PreDeliveryIssue(
                severity="critical",
                check_type="missing_gsap",
                message="No data-animate attributes found - GSAP animations are missing entirely",
                location="whole document",
            ))
        elif animate_count < 3:
            issues.append(PreDeliveryIssue(
                severity="high",
                check_type="few_gsap",
                message=f"Only {animate_count} data-animate attribute(s) found - expected at least 5+",
                location="whole document",
            ))
        elif animate_count < 5:
            issues.append(PreDeliveryIssue(
                severity="medium",
                check_type="few_gsap",
                message=f"Only {animate_count} data-animate attribute(s) found - a rich site should have 5+",
                location="whole document",
            ))

        return issues

    def _check_generic_text(self, html: str) -> List[PreDeliveryIssue]:
        """Detect banned generic phrases in the HTML."""
        issues: List[PreDeliveryIssue] = []

        # Extract visible text (strip tags) for searching
        # We also search the raw HTML to catch text inside attributes, but
        # primarily we care about visible content.
        html_lower = html.lower()

        for phrase in self.BANNED_PHRASES:
            phrase_lower = phrase.lower()
            # Find all occurrences
            start = 0
            count = 0
            while True:
                idx = html_lower.find(phrase_lower, start)
                if idx == -1:
                    break
                count += 1
                start = idx + len(phrase_lower)

            if count > 0:
                # "lorem ipsum" is critical; other banned phrases are high
                if "lorem" in phrase_lower:
                    severity = "critical"
                else:
                    severity = "high"

                issues.append(PreDeliveryIssue(
                    severity=severity,
                    check_type="generic_text",
                    message=f"Banned generic phrase found ({count}x): \"{phrase}\"",
                    location=self._approx_location(html, html_lower.find(phrase_lower)),
                ))

        return issues

    def _check_alt_text(
        self, html: str
    ) -> Tuple[List[PreDeliveryIssue], str, List[Dict[str, str]]]:
        """Check and fix missing alt attributes on images."""
        issues: List[PreDeliveryIssue] = []
        fixes: List[Dict[str, str]] = []
        fix_count = 0

        fixed_html = html

        for img_match in self._IMG_TAG_RE.finditer(html):
            img_tag = img_match.group(0)
            alt_match = self._ALT_ATTR_RE.search(img_tag)

            if not alt_match:
                # No alt attribute at all
                issues.append(PreDeliveryIssue(
                    severity="medium",
                    check_type="missing_alt",
                    message="<img> tag missing alt attribute",
                    location=self._approx_location(html, img_match.start()),
                ))
                # Auto-fix: add alt="Immagine" before the closing >
                if img_tag.endswith("/>"):
                    fixed_tag = img_tag[:-2].rstrip() + ' alt="Immagine" />'
                else:
                    fixed_tag = img_tag[:-1].rstrip() + ' alt="Immagine">'
                fixed_html = fixed_html.replace(img_tag, fixed_tag, 1)
                fix_count += 1
            else:
                alt_value = (alt_match.group(1) or alt_match.group(2) or "").strip()
                if not alt_value:
                    issues.append(PreDeliveryIssue(
                        severity="low",
                        check_type="empty_alt",
                        message='<img> tag has empty alt=""',
                        location=self._approx_location(html, img_match.start()),
                    ))
                    # Empty alt is acceptable for decorative images (WCAG),
                    # so we don't auto-fix it - just report.

        if fix_count > 0:
            fixes.append({
                "type": "add_missing_alt",
                "description": f'Added alt="Immagine" to {fix_count} image(s) missing alt attribute',
            })

        return issues, fixed_html, fixes

    def _check_empty_links(self, html: str) -> List[PreDeliveryIssue]:
        """Find links with empty or broken href (except legitimate anchors)."""
        issues: List[PreDeliveryIssue] = []

        for link_match in self._LINK_RE.finditer(html):
            link_tag = link_match.group(0)
            href_match = self._HREF_RE.search(link_tag)

            if not href_match:
                # No href attribute
                issues.append(PreDeliveryIssue(
                    severity="low",
                    check_type="empty_link",
                    message="<a> tag has no href attribute",
                    location=self._approx_location(html, link_match.start()),
                ))
                continue

            href_value = (href_match.group(1) or href_match.group(2) or "").strip()

            # Empty href
            if not href_value:
                issues.append(PreDeliveryIssue(
                    severity="low",
                    check_type="empty_link",
                    message='<a> tag has empty href=""',
                    location=self._approx_location(html, link_match.start()),
                ))
                continue

            # href="#" (but NOT anchor links like #about, #services, etc.)
            if href_value == "#":
                issues.append(PreDeliveryIssue(
                    severity="low",
                    check_type="empty_link",
                    message='<a> tag has href="#" (non-functional link)',
                    location=self._approx_location(html, link_match.start()),
                ))
                continue

            # href="javascript:void(0)" or similar
            if href_value.lower().startswith("javascript:"):
                issues.append(PreDeliveryIssue(
                    severity="low",
                    check_type="empty_link",
                    message=f"<a> tag uses javascript: href ({href_value[:40]})",
                    location=self._approx_location(html, link_match.start()),
                ))

        return issues

    # ---------------------------------------------------------------------------
    # Scoring
    # ---------------------------------------------------------------------------

    def _calculate_score(self, issues: List[PreDeliveryIssue]) -> float:
        """Calculate a 0-100 score based on issues found."""
        score = 100.0
        for issue in issues:
            penalty = _SEVERITY_PENALTY.get(issue.severity, 1)
            score -= penalty
        return max(0.0, score)

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    @staticmethod
    def _is_placeholder_src(src: str) -> bool:
        """Check if an image src points to a placeholder service."""
        src_lower = src.lower()
        placeholder_indicators = [
            "placeholder",
            "placehold.co",
            "placehold.it",
            "placekitten",
            "picsum.photos",
            "via.placeholder",
            "dummyimage.com",
            "fakeimg.pl",
            "lorempixel",
        ]
        return any(indicator in src_lower for indicator in placeholder_indicators)

    @staticmethod
    def _approx_location(html: str, char_pos: int) -> str:
        """
        Provide an approximate human-readable location for a character position.
        Returns something like 'near line 42' or 'section#hero'.
        """
        if char_pos < 0:
            return "unknown"

        # Find the nearest section ID above this position
        section_id_re = re.compile(
            r'<(?:section|footer|div|header)\b[^>]*?\bid\s*=\s*["\']([^"\']+)["\']',
            re.IGNORECASE | re.DOTALL,
        )
        last_section = None
        for m in section_id_re.finditer(html):
            if m.start() <= char_pos:
                last_section = m.group(1)
            else:
                break

        # Calculate line number
        line_num = html[:char_pos].count("\n") + 1

        if last_section:
            return f"near line {line_num}, section#{last_section}"
        return f"near line {line_num}"


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------

pre_delivery_check = PreDeliveryCheck()

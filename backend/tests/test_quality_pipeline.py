"""Comprehensive tests for the quality pipeline.

Tests banned_phrases, pre_delivery_check, quality_reviewer, and quality_control
to verify all quality fixes work correctly end-to-end.
"""
import pytest
import sys
import os
import re

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.banned_phrases import BANNED_PHRASES
from app.services.pre_delivery_check import PreDeliveryCheck, PreDeliveryReport
from app.services.agents.quality_reviewer import QualityReviewer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_html(body: str, head: str = "", nav: str = "") -> str:
    """Build a minimal valid HTML page wrapping the given body content."""
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width'>{head}</meta></head>"
        f"<body>{nav}{body}</body></html>"
    )


def _animate_attrs(n: int) -> str:
    """Return n span elements each with a data-animate attribute."""
    return "".join(
        f'<span data-animate="fade-up">x</span>' for _ in range(n)
    )


# ---------------------------------------------------------------------------
# TEST 1: Banned Phrases Module
# ---------------------------------------------------------------------------

class TestBannedPhrases:
    def test_exports_list(self):
        assert isinstance(BANNED_PHRASES, list)

    def test_has_at_least_25_phrases(self):
        assert len(BANNED_PHRASES) >= 25, (
            f"Expected at least 25 phrases, got {len(BANNED_PHRASES)}"
        )

    def test_no_duplicates(self):
        lowered = [p.lower() for p in BANNED_PHRASES]
        assert len(lowered) == len(set(lowered)), "Duplicate phrases detected"

    def test_common_phrases_present(self):
        lowered = {p.lower() for p in BANNED_PHRASES}
        for phrase in [
            "lorem ipsum",
            "benvenuti",
            "leader nel settore",
            "a 360 gradi",
        ]:
            assert phrase in lowered, f"'{phrase}' missing from BANNED_PHRASES"


# ---------------------------------------------------------------------------
# TEST 2: Placeholder Removal + Empty Parents
# ---------------------------------------------------------------------------

class TestPlaceholderRemoval:
    def test_placeholder_removed_and_empty_parent_cleaned(self):
        html = _make_html(
            '<section id="hero"><h1>{{HERO_TITLE}}</h1><p>Some text</p></section>'
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)

        # Placeholder should be gone
        assert "{{HERO_TITLE}}" not in report.html_fixed
        # Empty <h1></h1> should also be removed
        assert "<h1></h1>" not in report.html_fixed
        assert "<h1 ></h1>" not in report.html_fixed
        # The surrounding content should survive
        assert "Some text" in report.html_fixed
        # A fix should be logged
        assert any("placeholder" in f.get("type", "") for f in report.fixes_applied)

    def test_placeholder_issue_is_critical(self):
        html = _make_html('<section id="hero"><h1>{{HERO_TITLE}}</h1></section>')
        checker = PreDeliveryCheck()
        report = checker.check(html)
        placeholder_issues = [
            i for i in report.issues if i.check_type == "placeholder"
        ]
        assert len(placeholder_issues) >= 1
        assert placeholder_issues[0].severity == "critical"


# ---------------------------------------------------------------------------
# TEST 3: Word Count Validation
# ---------------------------------------------------------------------------

class TestWordCount:
    def test_short_hero_heading_flagged(self):
        html = _make_html(
            '<section id="hero">'
            '<h1>Ciao</h1>'
            '<p>Questo è un sottotitolo molto lungo che contiene almeno dieci parole per superare il controllo.</p>'
            '</section>'
            + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        word_issues = [
            i for i in report.issues
            if i.check_type == "word_count" and "hero_heading" in i.message
        ]
        assert len(word_issues) >= 1
        assert word_issues[0].severity == "high"

    def test_short_hero_subtitle_flagged(self):
        html = _make_html(
            '<section id="hero">'
            '<h1>Un titolo con almeno tre parole</h1>'
            '<p>Tre parole qui</p>'
            '</section>'
            + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        word_issues = [
            i for i in report.issues
            if i.check_type == "word_count" and "hero_subtitle" in i.message
        ]
        assert len(word_issues) >= 1
        assert word_issues[0].severity == "high"

    def test_proper_word_counts_pass(self):
        html = _make_html(
            '<section id="hero">'
            '<h1>Un bellissimo titolo con parole sufficienti</h1>'
            '<p>Questo è un sottotitolo lungo e descrittivo che contiene molte parole '
            'per superare la soglia minima richiesta dal sistema.</p>'
            '</section>'
            + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        word_issues = [
            i for i in report.issues if i.check_type == "word_count"
        ]
        assert len(word_issues) == 0, f"Unexpected word count issues: {word_issues}"


# ---------------------------------------------------------------------------
# TEST 4: Nav Anchor Validation
# ---------------------------------------------------------------------------

class TestNavAnchors:
    def test_missing_anchor_detected(self):
        nav = (
            '<nav>'
            '<a href="#about">About</a>'
            '<a href="#services">Services</a>'
            '<a href="#contact">Contact</a>'
            '</nav>'
        )
        body = (
            '<section id="about"><p>About content here with enough words.</p></section>'
            '<section id="contact"><p>Contact content here with enough words.</p></section>'
            + _animate_attrs(10)
        )
        html = _make_html(body, nav=nav)
        checker = PreDeliveryCheck()
        report = checker.check(html)

        anchor_issues = [
            i for i in report.issues if i.check_type == "broken_nav_anchor"
        ]
        missing_ids = [i.message for i in anchor_issues]
        assert any("services" in m for m in missing_ids), (
            f"Expected missing #services anchor, got: {missing_ids}"
        )

    def test_valid_anchors_pass(self):
        nav = (
            '<nav>'
            '<a href="#about">About</a>'
            '<a href="#contact">Contact</a>'
            '</nav>'
        )
        body = (
            '<section id="about"><p>About content here.</p></section>'
            '<section id="contact"><p>Contact content here.</p></section>'
            + _animate_attrs(10)
        )
        html = _make_html(body, nav=nav)
        checker = PreDeliveryCheck()
        report = checker.check(html)
        anchor_issues = [
            i for i in report.issues if i.check_type == "broken_nav_anchor"
        ]
        assert len(anchor_issues) == 0


# ---------------------------------------------------------------------------
# TEST 5: Banned Phrases Detection
# ---------------------------------------------------------------------------

class TestBannedPhrasesDetection:
    def test_banned_phrase_detected(self):
        html = _make_html(
            '<section id="about">'
            "<p>Siamo un'azienda leader nel settore della tecnologia.</p>"
            '</section>'
            + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        generic_issues = [
            i for i in report.issues if i.check_type == "generic_text"
        ]
        assert len(generic_issues) >= 1, "Expected at least one banned phrase issue"

    def test_clean_html_passes(self):
        html = _make_html(
            '<section id="about">'
            '<p>La nostra esperienza trentennale ci rende unici nel panorama digitale.</p>'
            '</section>'
            + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        generic_issues = [
            i for i in report.issues if i.check_type == "generic_text"
        ]
        assert len(generic_issues) == 0, (
            f"False positive banned phrase: {[i.message for i in generic_issues]}"
        )

    def test_lorem_ipsum_is_critical(self):
        html = _make_html(
            '<section id="hero"><p>Lorem ipsum dolor sit amet.</p></section>'
            + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        lorem_issues = [
            i for i in report.issues
            if i.check_type == "generic_text" and "lorem" in i.message.lower()
        ]
        assert len(lorem_issues) >= 1
        assert any(i.severity == "critical" for i in lorem_issues)


# ---------------------------------------------------------------------------
# TEST 6: GSAP Animation Check
# ---------------------------------------------------------------------------

class TestGsapCheck:
    def test_zero_animations_critical(self):
        html = _make_html(
            '<section id="hero"><h1>Titolo senza animazioni</h1></section>'
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        gsap_issues = [
            i for i in report.issues if i.check_type == "missing_gsap"
        ]
        assert len(gsap_issues) == 1
        assert gsap_issues[0].severity == "critical"

    def test_two_animations_high(self):
        html = _make_html(
            '<section id="hero"><h1>Titolo</h1></section>'
            + _animate_attrs(2)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        gsap_issues = [
            i for i in report.issues
            if i.check_type in ("missing_gsap", "few_gsap")
        ]
        assert len(gsap_issues) >= 1
        assert gsap_issues[0].severity == "high"

    def test_ten_animations_no_issues(self):
        html = _make_html(
            '<section id="hero"><h1>Titolo</h1></section>'
            + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        gsap_issues = [
            i for i in report.issues
            if i.check_type in ("missing_gsap", "few_gsap")
        ]
        assert len(gsap_issues) == 0


# ---------------------------------------------------------------------------
# TEST 7: Full Pipeline (Good HTML)
# ---------------------------------------------------------------------------

class TestFullPipelineGood:
    def test_good_html_passes(self):
        hero_heading = "Trasformiamo le tue idee in realtà digitale"
        hero_subtitle = (
            "Progettiamo soluzioni innovative che combinano design moderno "
            "e tecnologia avanzata per far crescere il tuo business online "
            "con risultati misurabili e duraturi nel tempo."
        )
        about_text = (
            "Con oltre dieci anni di esperienza nel settore digitale, "
            "il nostro studio crea esperienze web uniche che catturano "
            "l'attenzione dei visitatori e li trasformano in clienti fedeli. "
            "Ogni progetto nasce da un'analisi approfondita delle esigenze "
            "specifiche del cliente e del suo mercato di riferimento."
        )
        services = "".join(
            f"<div><h3>Servizio {i}</h3>"
            f"<p>Descrizione approfondita del servizio numero {i} con dettagli "
            f"specifici su cosa include e come può aiutare.</p></div>"
            for i in range(1, 4)
        )
        nav = (
            '<nav>'
            '<a href="#hero">Home</a>'
            '<a href="#about">Chi siamo</a>'
            '<a href="#services">Servizi</a>'
            '<a href="#contact">Contatti</a>'
            '</nav>'
        )
        body = (
            f'<section id="hero"><h1>{hero_heading}</h1>'
            f'<p>{hero_subtitle}</p></section>'
            f'<section id="about"><p>{about_text}</p></section>'
            f'<section id="services">{services}</section>'
            f'<section id="contact"><p>Scrivici per una consulenza gratuita.</p></section>'
            f'<footer id="footer"><p>© 2026 Studio Digitale</p></footer>'
            + _animate_attrs(12)
        )
        head = (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Playfair+Display:wght@400;700&family=Inter:wght@400;500&display=swap" '
            'rel="stylesheet">'
        )
        html = _make_html(body, head=head, nav=nav)

        checker = PreDeliveryCheck()
        report = checker.check(html)

        assert report.score > 90, f"Expected score > 90, got {report.score}"
        assert report.passed is True, (
            f"Expected passed=True, issues: "
            f"{[(i.severity, i.check_type, i.message) for i in report.issues]}"
        )


# ---------------------------------------------------------------------------
# TEST 8: Full Pipeline (Bad HTML)
# ---------------------------------------------------------------------------

class TestFullPipelineBad:
    def test_bad_html_fails(self):
        nav = (
            '<nav>'
            '<a href="#pricing">Prezzi</a>'
            '<a href="#about">About</a>'
            '</nav>'
        )
        body = (
            '<section id="hero">'
            '<h1>{{HERO_TITLE}}</h1>'
            '<p>Benvenuti nel nostro sito</p>'
            '</section>'
            '<section id="about"></section>'
            '<section id="services">'
            '<p>Lorem ipsum dolor sit amet</p>'
            '<img src="" alt="">'
            '</section>'
            '<span data-animate="fade-up">x</span>'
        )
        html = _make_html(body, nav=nav)

        checker = PreDeliveryCheck()
        report = checker.check(html)

        # Multiple issues should be caught
        issue_types = {i.check_type for i in report.issues}
        assert "placeholder" in issue_types, "Placeholder not detected"
        assert "generic_text" in issue_types, "Banned phrases not detected"
        assert "broken_nav_anchor" in issue_types, "Missing nav anchor #pricing not detected"
        assert "few_gsap" in issue_types or "missing_gsap" in issue_types, (
            "GSAP deficiency not detected"
        )

        # Score should be low
        assert report.score < 50, f"Expected score < 50, got {report.score}"
        assert report.passed is False


# ---------------------------------------------------------------------------
# TEST 9: QualityReviewer Integration
# ---------------------------------------------------------------------------

class TestQualityReviewer:
    def test_uses_shared_banned_phrases(self):
        html = (
            '<html><body>'
            '<section id="hero"><h1 data-animate="text-split">Titolo</h1></section>'
            '<section id="about">'
            "<p>Siamo un'azienda leader nel settore della consulenza.</p>"
            '</section>'
            + _animate_attrs(10)
            + '</body></html>'
        )
        brief = {
            "typography_direction": {"forbidden_fonts": []},
            "color_direction": {"forbidden_colors": []},
        }
        sections = ["hero", "about"]

        reviewer = QualityReviewer()
        result = reviewer.check(html, brief, sections)

        assert result["stats"]["banned_phrases_found"] >= 1
        assert any(
            "banned phrase" in i["message"].lower()
            for i in result["issues"]
        )

    def test_animation_checks_work(self):
        html = (
            '<html><body>'
            '<section id="hero"><h1>Titolo hero</h1></section>'
            '<section id="about"><p>About text</p></section>'
            '</body></html>'
        )
        brief = {
            "typography_direction": {"forbidden_fonts": []},
            "color_direction": {"forbidden_colors": []},
        }
        sections = ["hero", "about"]

        reviewer = QualityReviewer()
        result = reviewer.check(html, brief, sections)

        assert result["stats"]["animations_found"] == 0
        assert any(
            "animation" in i["message"].lower() or "magnetic" in i["message"].lower()
            for i in result["issues"]
        )

    def test_clean_html_high_score(self):
        html = (
            '<html><body>'
            '<section id="hero">'
            '<h1 data-animate="text-split">Trasformiamo la tua visione</h1>'
            '<a href="#contact" data-animate="magnetic" class="btn">Inizia ora</a>'
            '</section>'
            '<section id="about"><p>Testo personalizzato e unico.</p></section>'
            + _animate_attrs(10)
            + '</body></html>'
        )
        brief = {
            "typography_direction": {"forbidden_fonts": []},
            "color_direction": {"forbidden_colors": []},
        }
        sections = ["hero", "about"]

        reviewer = QualityReviewer()
        result = reviewer.check(html, brief, sections)

        assert result["score"] >= 60
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# TEST 10: Font URL Validation
# ---------------------------------------------------------------------------

class TestFontUrlValidation:
    def test_method_exists(self):
        checker = PreDeliveryCheck()
        assert hasattr(checker, '_check_font_urls'), (
            "_check_font_urls method not found on PreDeliveryCheck"
        )

    def test_missing_font_url_detected(self):
        html = _make_html(
            '<section id="hero"><h1>Titolo</h1></section>' + _animate_attrs(10)
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        font_issues = [
            i for i in report.issues if i.check_type == "missing_font_url"
        ]
        assert len(font_issues) >= 1

    def test_matching_fonts_pass(self):
        head = (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Playfair+Display:wght@400;700&family=Inter:wght@400;500&display=swap" '
            'rel="stylesheet">'
        )
        html = _make_html(
            '<section id="hero"><h1>Titolo</h1></section>' + _animate_attrs(10),
            head=head,
        )
        theme = {
            "font_heading": "Playfair Display",
            "font_body": "Inter",
        }
        checker = PreDeliveryCheck()
        report = checker.check(html, theme_config=theme)
        font_issues = [
            i for i in report.issues if i.check_type == "font_mismatch"
        ]
        assert len(font_issues) == 0

    def test_mismatching_fonts_detected(self):
        head = (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Roboto:wght@400;700&display=swap" rel="stylesheet">'
        )
        html = _make_html(
            '<section id="hero"><h1>Titolo</h1></section>' + _animate_attrs(10),
            head=head,
        )
        theme = {
            "font_heading": "Playfair Display",
            "font_body": "Inter",
        }
        checker = PreDeliveryCheck()
        report = checker.check(html, theme_config=theme)
        font_issues = [
            i for i in report.issues if i.check_type == "font_mismatch"
        ]
        assert len(font_issues) >= 1
        assert font_issues[0].severity == "high"

    def test_font_url_auto_fix(self):
        head = (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Roboto:wght@400;700&display=swap" rel="stylesheet">'
        )
        html = _make_html(
            '<section id="hero"><h1>Titolo</h1></section>' + _animate_attrs(10),
            head=head,
        )
        theme = {
            "font_heading": "Playfair Display",
            "font_body": "Inter",
        }
        checker = PreDeliveryCheck()
        report = checker.check(html, theme_config=theme)
        # Fixed HTML should contain the correct fonts in the URL
        assert "Playfair" in report.html_fixed
        assert "Inter" in report.html_fixed


# ---------------------------------------------------------------------------
# TEST 11: CSS Variable Validation
# ---------------------------------------------------------------------------

class TestCssVariableValidation:
    def test_method_exists(self):
        checker = PreDeliveryCheck()
        assert hasattr(checker, '_check_css_variables'), (
            "_check_css_variables method not found on PreDeliveryCheck"
        )

    def test_undefined_core_var_detected(self):
        head_fonts = (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Inter:wght@400;700&display=swap" rel="stylesheet">'
        )
        html = _make_html(
            '<section id="hero">'
            '<h1 style="color: var(--color-primary)">Titolo</h1>'
            '</section>'
            + _animate_attrs(10),
            head=head_fonts,
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        css_issues = [
            i for i in report.issues if i.check_type == "undefined_css_var"
        ]
        assert len(css_issues) >= 1
        assert any("--color-primary" in i.message for i in css_issues)

    def test_defined_var_passes(self):
        head = (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Inter:wght@400;700&display=swap" rel="stylesheet">'
            '<style>:root { --color-primary: #3b82f6; }</style>'
        )
        html = _make_html(
            '<section id="hero">'
            '<h1 style="color: var(--color-primary)">Titolo</h1>'
            '</section>'
            + _animate_attrs(10),
            head=head,
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        css_issues = [
            i for i in report.issues
            if i.check_type == "undefined_css_var" and "--color-primary" in i.message
        ]
        assert len(css_issues) == 0


# ---------------------------------------------------------------------------
# TEST 12: Report Serialization
# ---------------------------------------------------------------------------

class TestReportSerialization:
    def test_to_dict(self):
        html = _make_html(
            '<section id="hero"><h1>{{HERO_TITLE}}</h1></section>'
        )
        checker = PreDeliveryCheck()
        report = checker.check(html)
        d = report.to_dict()
        assert "score" in d
        assert "issues" in d
        assert "fixes_applied" in d
        assert "passed" in d
        assert isinstance(d["issues"], list)
        if d["issues"]:
            assert "severity" in d["issues"][0]
            assert "type" in d["issues"][0]
            assert "message" in d["issues"][0]


# ---------------------------------------------------------------------------
# TEST: Quality Gate (unified, pre-assembly validation)
# ---------------------------------------------------------------------------

from app.generation.quality_gate import QualityGate, QualityReport, MINIMUM_SCORE


class TestQualityGate:
    def setup_method(self):
        self.gate = QualityGate()

    def test_good_theme_passes(self):
        theme = {
            "primary_color": "#3b82f6",
            "secondary_color": "#1e40af",
            "accent_color": "#f59e0b",
            "bg_color": "#FFFFFF",
            "bg_alt_color": "#F5F5F5",
            "text_color": "#1A1A2E",
            "text_muted_color": "#6B7280",
            "font_heading": "Playfair Display",
            "font_body": "Inter",
        }
        ok, errors = self.gate.validate_theme(theme)
        assert ok is True, f"Good theme should pass, errors: {errors}"
        assert len(errors) == 0

    def test_bad_contrast_fails(self):
        theme = {
            "primary_color": "#3b82f6",
            "secondary_color": "#1e40af",
            "accent_color": "#f59e0b",
            "bg_color": "#FFFFFF",
            "bg_alt_color": "#F5F5F5",
            "text_color": "#CCCCCC",  # Very low contrast on white
            "text_muted_color": "#EEEEEE",
            "font_heading": "Playfair Display",
            "font_body": "Inter",
        }
        ok, errors = self.gate.validate_theme(theme)
        assert ok is False
        assert any("WCAG" in e for e in errors)

    def test_system_font_rejected(self):
        theme = {
            "primary_color": "#3b82f6",
            "secondary_color": "#1e40af",
            "accent_color": "#f59e0b",
            "bg_color": "#FFFFFF",
            "bg_alt_color": "#F5F5F5",
            "text_color": "#1A1A2E",
            "text_muted_color": "#6B7280",
            "font_heading": "Arial",
            "font_body": "Times New Roman",
        }
        ok, errors = self.gate.validate_theme(theme)
        assert ok is False
        assert any("system default" in e.lower() or "Arial" in e for e in errors)

    def test_section_with_banned_phrase(self):
        content = {"HERO_TITLE": "Benvenuti nel nostro sito web"}
        ok, errors = self.gate.validate_section("hero", content)
        assert ok is False
        assert any("banned" in e.lower() for e in errors)

    def test_section_valid_content(self):
        content = {
            "HERO_TITLE": "Trasformiamo le tue idee in realtà",
            "HERO_SUBTITLE": "Un approccio unico al design digitale",
        }
        ok, errors = self.gate.validate_section("hero", content)
        assert ok is True, f"Valid content should pass, errors: {errors}"

    def test_site_validation_with_missing_hero(self):
        site_data = {
            "theme": {
                "primary_color": "#3b82f6",
                "bg_color": "#FFFFFF",
                "text_color": "#1A1A2E",
                "font_heading": "Playfair Display",
                "font_body": "Inter",
            },
            "components": [
                {"variant_id": "about-01", "data": {"ABOUT_TITLE": "Chi siamo test"}},
                {"variant_id": "footer-01", "data": {}},
            ],
        }
        report = self.gate.validate_site(site_data)
        assert any("hero" in e for e in report.errors)

    def test_site_validation_passes_good_data(self):
        site_data = {
            "theme": {
                "primary_color": "#3b82f6",
                "secondary_color": "#1e40af",
                "accent_color": "#f59e0b",
                "bg_color": "#FFFFFF",
                "bg_alt_color": "#F5F5F5",
                "text_color": "#1A1A2E",
                "text_muted_color": "#6B7280",
                "font_heading": "Playfair Display",
                "font_body": "Inter",
            },
            "components": [
                {"variant_id": "hero-01", "data": {"HERO_TITLE": "Trasforma la tua visione digitale"}},
                {"variant_id": "about-01", "data": {"ABOUT_TITLE": "La nostra storia unica"}},
                {"variant_id": "services-01", "data": {"SERVICES_TITLE": "I nostri servizi professionali"}},
                {"variant_id": "footer-01", "data": {}},
            ],
        }
        report = self.gate.validate_site(site_data)
        assert report.passed is True, f"Score: {report.score}, errors: {report.errors}"
        assert report.score >= MINIMUM_SCORE

    def test_retry_prompt_generation(self):
        report = QualityReport(
            passed=False,
            score=30,
            errors=["[hero] WCAG fail: contrast 2.1"],
            warnings=["[about] 'title' has 1 words (minimum 3)"],
            failed_sections=["hero", "about"],
        )
        retry_prompt = self.gate.generate_retry_prompt(report, "Generate hero section")
        assert "CORRECTIONS" in retry_prompt
        assert "hero" in retry_prompt
        assert "about" in retry_prompt

    def test_score_clamped(self):
        # Site with many issues should not go below 0
        site_data = {
            "theme": {"font_heading": "Arial", "font_body": "Verdana"},
            "components": [],
        }
        report = self.gate.validate_site(site_data)
        assert 0 <= report.score <= 100

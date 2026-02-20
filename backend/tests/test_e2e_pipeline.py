"""
End-to-End test for the complete generation pipeline:
  Plan → Questions → Answers → (Simulated) Generation → Quality Check

Runs offline (no server, no database, no AI API calls).
Tests the integration between all 6 new services.

Usage:
    cd backend
    python -m tests.test_e2e_pipeline
"""

import asyncio
import json
import logging
import sys
import os
import io
import uuid
from pathlib import Path
from typing import Any, Dict, List

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(level=logging.WARNING, format="%(name)s: %(message)s")
logger = logging.getLogger("e2e_test")
logger.setLevel(logging.INFO)

# ─── Test helpers ──────────────────────────────────────────────────────────

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

results: List[Dict[str, Any]] = []


def record(name: str, passed: bool, details: str = ""):
    status = PASS if passed else FAIL
    results.append({"name": name, "passed": passed, "details": details})
    logger.info(f"  {status} {name}" + (f" - {details}" if details else ""))


# ─── Sample test data ─────────────────────────────────────────────────────

SCENARIOS = [
    {
        "name": "Ristorante Da Mario",
        "description": "Trattoria tradizionale romana dal 1965, pasta fatta a mano, vini laziali",
        "category": "ristorante",
        "sections": ["hero", "about", "services", "gallery", "testimonials", "contact", "footer"],
        "style_id": "restaurant-elegant",
        "primary_color": "#D4AF37",
        "contact_info": {"phone": "+39 06 1234567", "email": "info@damario.it"},
    },
    {
        "name": "TechFlow SaaS",
        "description": "Piattaforma di project management per team distribuiti con AI integrata",
        "category": "saas",
        "sections": ["hero", "about", "services", "pricing", "testimonials", "faq", "contact", "footer"],
        "style_id": "saas-gradient",
        "primary_color": "#6366F1",
        "contact_info": {"email": "hello@techflow.io"},
    },
    {
        "name": "Studio Legale Bianchi",
        "description": "Avvocati specializzati in diritto commerciale e societario a Milano",
        "category": "business",
        "sections": ["hero", "about", "services", "team", "contact", "footer"],
        "style_id": "business-trust",
        "primary_color": "#1E3A5F",
        "contact_info": {"phone": "+39 02 9876543", "email": "info@studiobianchi.it", "address": "Via Montenapoleone 10, Milano"},
    },
]

# ─── Minimal HTML for quality check testing ─────────────────────────────

SAMPLE_HTML_GOOD = """<!DOCTYPE html>
<html lang="it">
<head><title>Test Site</title></head>
<body>
  <section id="hero">
    <h1 data-animate="text-split">Ristorante Da Mario</h1>
    <p data-animate="blur-slide">Trattoria tradizionale romana dal 1965</p>
    <a href="#contact" class="cta" data-animate="magnetic">Prenota Ora</a>
    <img src="https://example.com/hero.jpg" alt="Ristorante Da Mario" />
  </section>
  <section id="about">
    <h2 data-animate="text-split">Chi Siamo</h2>
    <p data-animate="fade-up">Dal 1965, la nostra famiglia porta avanti la tradizione culinaria romana.</p>
    <img src="https://example.com/about.jpg" alt="La nostra storia" />
  </section>
  <section id="services">
    <h2 data-animate="text-split">I Nostri Piatti</h2>
    <div data-animate="stagger">
      <div><h3>Carbonara</h3><p>La vera ricetta romana con guanciale e pecorino.</p></div>
      <div><h3>Cacio e Pepe</h3><p>Semplicita e tradizione in un piatto.</p></div>
      <div><h3>Amatriciana</h3><p>Il gusto autentico della cucina laziale.</p></div>
    </div>
  </section>
  <section id="contact">
    <h2 data-animate="text-split">Contatti</h2>
    <p>Tel: +39 06 1234567</p>
    <p>Email: info@damario.it</p>
  </section>
  <footer id="footer">
    <p>2026 Ristorante Da Mario. Tutti i diritti riservati.</p>
  </footer>
</body>
</html>"""

SAMPLE_HTML_BAD = """<!DOCTYPE html>
<html lang="it">
<head><title>Test</title></head>
<body>
  <section id="hero">
    <h1>{{HERO_TITLE}}</h1>
    <p>Benvenuti nel nostro sito</p>
    <a href="#">Scopri di piu</a>
    <img src="placeholder.jpg" />
  </section>
  <section id="about">
    <h2>Chi Siamo</h2>
    <p>Siamo un'azienda leader nel settore.</p>
    <p></p>
  </section>
  <section id="services">
    <h2>Lorem ipsum dolor sit amet</h2>
    <p>Lorem ipsum dolor sit amet consectetur.</p>
  </section>
</body>
</html>"""


# ─── Phase 1: Service Imports ─────────────────────────────────────────────

def test_phase1_imports():
    logger.info("\n=== FASE 1: Import Servizi ===")

    services = {}

    for name, import_path in [
        ("ResourceCatalog", "app.services.resource_catalog"),
        ("SiteQualityGuide", "app.services.site_quality_guide"),
        ("UsageTracker", "app.services.usage_tracker"),
        ("SitePlanner", "app.services.site_planner"),
        ("SiteQuestioner", "app.services.site_questioner"),
        ("PreDeliveryCheck", "app.services.pre_delivery_check"),
    ]:
        try:
            mod = __import__(import_path, fromlist=[name.lower()])
            services[name] = mod
            record(f"Import {name}", True)
        except Exception as e:
            record(f"Import {name}", False, str(e))

    return services


# ─── Phase 2: Resource Catalog Scan ────────────────────────────────────────

def test_phase2_catalog(services):
    logger.info("\n=== FASE 2: Resource Catalog ===")

    catalog = services["ResourceCatalog"].catalog
    inv = catalog.get_full_inventory()

    total = inv.get("total_components", 0)
    sections = inv.get("total_section_types", 0)

    record("Catalog: componenti > 100", total > 100, f"{total} componenti")
    record("Catalog: sezioni > 20", sections > 20, f"{sections} sezioni")

    # Test search
    hero_variants = catalog.search_components(section_type="hero")
    record("Catalog: search hero varianti", len(hero_variants) >= 3, f"{len(hero_variants)} hero variants")

    # Test section coverage
    coverage = catalog.get_section_coverage()
    record("Catalog: section coverage", len(coverage) > 15, f"{len(coverage)} sezioni con varianti")

    return catalog


# ─── Phase 3: Site Planner ─────────────────────────────────────────────────

async def test_phase3_planner(services):
    logger.info("\n=== FASE 3: Site Planner (3 scenari) ===")

    planner = services["SitePlanner"].site_planner
    plans = []

    for scenario in SCENARIOS:
        plan = await planner.create_plan(
            business_name=scenario["name"],
            business_description=scenario["description"],
            category=scenario["category"],
            sections=scenario["sections"],
            style_id=scenario["style_id"],
            primary_color=scenario["primary_color"],
            contact_info=scenario["contact_info"],
        )
        plans.append(plan)

        name = scenario["name"]
        has_sections = isinstance(plan.get("sections"), list) and len(plan["sections"]) > 0
        has_components = isinstance(plan.get("components"), dict) and len(plan["components"]) > 0
        has_score = isinstance(plan.get("quality_score"), (int, float)) and plan["quality_score"] > 0
        has_palette = isinstance(plan.get("color_palette"), dict)
        has_fonts = isinstance(plan.get("font_pairing"), dict)

        record(f"Plan '{name}': sezioni", has_sections, f"{len(plan.get('sections', []))} sezioni")
        record(f"Plan '{name}': componenti", has_components, f"{len(plan.get('components', {}))} componenti")
        record(f"Plan '{name}': quality_score", has_score, f"score={plan.get('quality_score')}")
        record(f"Plan '{name}': color_palette", has_palette)
        record(f"Plan '{name}': font_pairing", has_fonts)

    # Anti-repetition: verify different components across same-category plans
    # (only meaningful if we had 2 restaurant plans, but check component diversity anyway)
    all_components = [set(p.get("components", {}).values()) for p in plans]
    if len(all_components) >= 2:
        overlap_01 = all_components[0] & all_components[1]
        total_01 = all_components[0] | all_components[1]
        overlap_pct = len(overlap_01) / max(len(total_01), 1) * 100
        record("Diversita: componenti diversi tra scenari", overlap_pct < 80, f"{overlap_pct:.0f}% overlap")

    return plans


# ─── Phase 4: Questions ──────────────────────────────────────────────────

def test_phase4_questions(services, plans):
    logger.info("\n=== FASE 4: Interactive Questions ===")

    questioner = services["SiteQuestioner"].site_questioner
    all_questions = []

    for i, scenario in enumerate(SCENARIOS):
        plan = plans[i]
        user_data = {
            "business_name": scenario["name"],
            "business_description": scenario["description"],
            "contact_info": scenario.get("contact_info", {}),
        }

        questions = questioner.analyze_completeness(plan, user_data)
        all_questions.append(questions)

        name = scenario["name"]
        record(f"Questions '{name}': generate domande", len(questions) > 0, f"{len(questions)} domande")

        # Check question structure
        if questions:
            q = questions[0]
            has_id = "id" in q
            has_question = "question_it" in q
            has_type = "type" in q and q["type"] in ("text", "image_upload", "choice", "toggle")
            has_section = "section" in q
            record(f"Questions '{name}': struttura corretta", has_id and has_question and has_type and has_section)

            # Check unique IDs
            ids = [q["id"] for q in questions]
            record(f"Questions '{name}': ID univoci", len(ids) == len(set(ids)), f"{len(ids)} IDs")

    return all_questions


# ─── Phase 5: Answer Application ──────────────────────────────────────────

def test_phase5_answers(services, plans, all_questions):
    logger.info("\n=== FASE 5: Apply Answers ===")

    questioner = services["SiteQuestioner"].site_questioner
    updated_plans = []

    for i, scenario in enumerate(SCENARIOS):
        plan = plans[i].copy()
        questions = all_questions[i]

        # Simulate user answering some questions
        answers = {}
        for q in questions[:3]:  # Answer first 3 questions
            if q["type"] == "text":
                answers[q["id"]] = f"Risposta di test per {q['field']}"
            elif q["type"] == "choice" and q.get("options"):
                answers[q["id"]] = q["options"][0]
            elif q["type"] == "toggle":
                answers[q["id"]] = True
            elif q["type"] == "image_upload":
                answers[q["id"]] = "https://example.com/test-photo.jpg"

        updated_plan = questioner.apply_answers(plan, answers)
        updated_plans.append(updated_plan)

        name = scenario["name"]
        has_user_content = "user_content" in updated_plan
        record(f"Answers '{name}': user_content presente", has_user_content)

        if has_user_content:
            content_keys = list(updated_plan["user_content"].keys())
            record(f"Answers '{name}': sezioni con contenuto", len(content_keys) > 0, f"{content_keys}")

    return updated_plans


# ─── Phase 6: Pre-Delivery Quality Check ──────────────────────────────────

def test_phase6_quality_check(services, plans):
    logger.info("\n=== FASE 6: Pre-Delivery Quality Check ===")

    checker = services["PreDeliveryCheck"].pre_delivery_check

    # Test 1: Good HTML
    report_good = checker.check(
        html=SAMPLE_HTML_GOOD,
        requested_sections=["hero", "about", "services", "contact", "footer"],
    )
    record("QC HTML buono: score alto", report_good.score >= 70, f"score={report_good.score}")
    record("QC HTML buono: passed", report_good.passed)
    record("QC HTML buono: pochi issues", len(report_good.issues) <= 3, f"{len(report_good.issues)} issues")

    # Test 2: Bad HTML (placeholders, generic text, lorem ipsum, missing alt)
    report_bad = checker.check(
        html=SAMPLE_HTML_BAD,
        requested_sections=["hero", "about", "services", "contact", "footer"],
    )
    record("QC HTML cattivo: score basso", report_bad.score < 60, f"score={report_bad.score}")
    record("QC HTML cattivo: not passed", not report_bad.passed)
    record("QC HTML cattivo: issues trovati", len(report_bad.issues) >= 3, f"{len(report_bad.issues)} issues")

    # Check that bad HTML has specific issue types
    issue_types = {i.check_type for i in report_bad.issues}
    has_placeholder = "placeholder" in issue_types
    has_generic = "generic_text" in issue_types or "banned_text" in issue_types
    record("QC HTML cattivo: rileva placeholder", has_placeholder, f"types: {issue_types}")

    # Test 3: Auto-fix applied
    if report_bad.fixes_applied:
        record("QC HTML cattivo: auto-fix applicati", True, f"{len(report_bad.fixes_applied)} fix")
        # Verify fixed HTML is different from original
        record("QC HTML cattivo: HTML corretto", report_bad.html_fixed != SAMPLE_HTML_BAD)
    else:
        record("QC HTML cattivo: auto-fix applicati", False, "nessun fix")

    return report_good, report_bad


# ─── Phase 7: Usage Tracker ───────────────────────────────────────────────

def test_phase7_usage_tracker(services, plans):
    logger.info("\n=== FASE 7: Usage Tracker (anti-ripetizione) ===")

    tracker = services["UsageTracker"].usage_tracker

    # Record the 3 plan generations
    gen_ids = []
    for i, (scenario, plan) in enumerate(zip(SCENARIOS, plans)):
        gen_id = f"e2e-test-{uuid.uuid4().hex[:8]}"
        gen_ids.append(gen_id)

        components = plan.get("components", {})
        tracker.record_generation(
            generation_id=gen_id,
            category=scenario["category"],
            style=scenario["style_id"],
            components_dict=components,
        )
        record(f"Tracker: registrazione '{scenario['name']}'", True, f"{len(components)} componenti")

    # Check priority scoring
    if plans[0].get("components"):
        first_component = list(plans[0]["components"].values())[0]
        score = tracker.get_priority_score(first_component, SCENARIOS[0]["category"])
        record("Tracker: priority score funziona", isinstance(score, float), f"score={score:.3f}")

    # Check layout hashing
    hashes = []
    for plan in plans:
        components = plan.get("components", {})
        if components:
            h = tracker.compute_layout_hash(components)
            hashes.append(h)

    unique_hashes = len(set(hashes))
    record("Tracker: layout hash diversi", unique_hashes == len(hashes), f"{unique_hashes}/{len(hashes)} unici")

    # Check usage stats
    stats = tracker.get_usage_stats()
    record("Tracker: usage stats", isinstance(stats, dict) and stats.get("total_generations", 0) >= 3)

    return gen_ids


# ─── Phase 8: Full Pipeline Simulation ─────────────────────────────────────

async def test_phase8_full_pipeline(services):
    logger.info("\n=== FASE 8: Pipeline Completa (simulazione) ===")

    planner = services["SitePlanner"].site_planner
    questioner = services["SiteQuestioner"].site_questioner
    checker = services["PreDeliveryCheck"].pre_delivery_check
    tracker = services["UsageTracker"].usage_tracker

    scenario = {
        "name": "Gelateria Dolce Vita",
        "description": "Gelateria artigianale nel cuore di Firenze, gelato con ingredienti toscani dal 1980",
        "category": "ristorante",
        "sections": ["hero", "about", "services", "gallery", "contact", "footer"],
        "style_id": "restaurant-cozy",
        "primary_color": "#F5A623",
        "contact_info": {"phone": "+39 055 1234567", "email": "ciao@dolcevita.it", "address": "Via dei Calzaiuoli 42, Firenze"},
    }

    # Step 1: Plan
    logger.info("  Step 1: Creazione piano...")
    plan = await planner.create_plan(
        business_name=scenario["name"],
        business_description=scenario["description"],
        category=scenario["category"],
        sections=scenario["sections"],
        style_id=scenario["style_id"],
        primary_color=scenario["primary_color"],
        contact_info=scenario["contact_info"],
    )
    record("Pipeline: piano creato", bool(plan.get("sections")))

    # Step 2: Questions
    logger.info("  Step 2: Generazione domande...")
    questions = questioner.analyze_completeness(plan, {
        "business_name": scenario["name"],
        "business_description": scenario["description"],
        "contact_info": scenario["contact_info"],
    })
    record("Pipeline: domande generate", len(questions) > 0, f"{len(questions)} domande")

    # Step 3: User answers (simulate: answer all text questions, skip uploads)
    logger.info("  Step 3: Risposte utente (simulate)...")
    answers = {}
    for q in questions:
        if q["type"] == "text":
            answers[q["id"]] = f"Contenuto personalizzato per {q['field']}"
        elif q["type"] == "choice" and q.get("options"):
            answers[q["id"]] = q["options"][0]
        elif q["type"] == "toggle":
            answers[q["id"]] = True

    updated_plan = questioner.apply_answers(plan, answers)
    record("Pipeline: risposte applicate", "user_content" in updated_plan)

    # Step 4: Simulate generation (we use the good HTML template)
    logger.info("  Step 4: Generazione simulata...")
    html_content = SAMPLE_HTML_GOOD.replace("Ristorante Da Mario", scenario["name"])
    html_content = html_content.replace(
        "Trattoria tradizionale romana dal 1965",
        scenario["description"],
    )
    record("Pipeline: HTML generato", len(html_content) > 500, f"{len(html_content)} chars")

    # Step 5: Pre-delivery check
    logger.info("  Step 5: Quality check pre-consegna...")
    report = checker.check(
        html=html_content,
        requested_sections=scenario["sections"],
    )
    record("Pipeline: QC score", report.score >= 50, f"score={report.score}")

    if report.fixes_applied:
        html_content = report.html_fixed
        record("Pipeline: auto-fix applicati", True, f"{len(report.fixes_applied)} fix")

    # Step 6: Record usage
    logger.info("  Step 6: Registrazione uso...")
    gen_id = f"e2e-pipeline-{uuid.uuid4().hex[:8]}"
    components = updated_plan.get("components", {})
    tracker.record_generation(
        generation_id=gen_id,
        category=scenario["category"],
        style=scenario["style_id"],
        components_dict=components,
    )
    record("Pipeline: uso registrato", True, f"{len(components)} componenti")

    # Step 7: Verify anti-repetition for next generation
    logger.info("  Step 7: Verifica anti-ripetizione...")
    layout_hash = tracker.compute_layout_hash(components)
    is_dup = tracker.is_duplicate_layout(layout_hash)
    record("Pipeline: layout registrato come usato", is_dup, f"hash={layout_hash[:16]}...")

    logger.info("  Pipeline completa!")


# ─── Main ──────────────────────────────────────────────────────────────────

async def main():
    print("=" * 60)
    print("  TEST E2E - Pipeline Completa")
    print("  Plan -> Questions -> Answers -> Generate -> QC -> Track")
    print("=" * 60)

    # Phase 1: Import all services
    services = test_phase1_imports()
    required = ["ResourceCatalog", "SiteQualityGuide", "UsageTracker",
                 "SitePlanner", "SiteQuestioner", "PreDeliveryCheck"]
    if not all(s in services for s in required):
        print("\nERRORE: Non tutti i servizi sono importabili. Interrompo.")
        return 1

    # Phase 2: Resource Catalog
    catalog = test_phase2_catalog(services)

    # Phase 3: Site Planner (3 scenarios)
    plans = await test_phase3_planner(services)

    # Phase 4: Questions
    all_questions = test_phase4_questions(services, plans)

    # Phase 5: Answer application
    updated_plans = test_phase5_answers(services, plans, all_questions)

    # Phase 6: Pre-Delivery Check
    test_phase6_quality_check(services, plans)

    # Phase 7: Usage Tracker
    test_phase7_usage_tracker(services, plans)

    # Phase 8: Full pipeline simulation
    await test_phase8_full_pipeline(services)

    # ─── Summary ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  RISULTATI")
    print("=" * 60)

    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)

    if failed > 0:
        print(f"\n  Falliti:")
        for r in results:
            if not r["passed"]:
                print(f"    {FAIL} {r['name']}" + (f" - {r['details']}" if r['details'] else ""))

    print(f"\n  Totale: {total} test")
    print(f"  Passati: {passed}")
    print(f"  Falliti: {failed}")
    pct = (passed / total * 100) if total > 0 else 0
    print(f"  Percentuale: {pct:.0f}%")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

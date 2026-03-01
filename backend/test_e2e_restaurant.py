"""
End-to-end test: generate a restaurant site through the full multi-agent pipeline.
Tests the complete flow: Director → Theme+Texts+Choreographer → Assembly → QualityReview → Memory
"""
import asyncio
import json
import logging
import os
import sys
import time

# Setup path
sys.path.insert(0, os.path.dirname(__file__))

# Load .env
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("E2E-TEST")


def progress_callback(step: int, message: str, data=None):
    """Print progress updates."""
    logger.info(f"[PROGRESS {step}] {message}")
    if data and data.get("phase") == "theme_complete":
        colors = data.get("colors", {})
        logger.info(f"  Colors: primary={colors.get('primary')}, accent={colors.get('accent')}, bg={colors.get('bg')}")
        logger.info(f"  Fonts: {data.get('font_heading')} / {data.get('font_body')}")


async def main():
    start = time.time()

    logger.info("=" * 60)
    logger.info("E2E TEST: Generating restaurant-modern site")
    logger.info("=" * 60)

    from app.services.databinding_generator import databinding_generator as gen

    result = await gen.generate(
        business_name="Osteria del Porto",
        business_description=(
            "Ristorante di pesce fresco sul porto di Bari. "
            "Cucina pugliese contemporanea con materie prime locali. "
            "Il chef Marco Ferrara reinterpreta i classici della tradizione: "
            "crudo di mare, orecchiette ai ricci, polpo alla brace. "
            "Terrazza panoramica sul mare, 45 coperti. "
            "Aperto dal martedi alla domenica, prenotazione consigliata."
        ),
        sections=["hero", "about", "services", "testimonials", "gallery", "contact", "footer"],
        style_preferences={"mood": "modern"},
        template_style_id="restaurant-modern",
        contact_info={
            "phone": "+39 080 523 1234",
            "email": "info@osteriadelporto.it",
            "address": "Lungomare Araldo di Crollalanza 12, Bari",
        },
        on_progress=progress_callback,
    )

    elapsed = time.time() - start

    logger.info("=" * 60)
    logger.info(f"RESULT: success={result.get('success')}")
    logger.info(f"TIME: {elapsed:.1f}s")

    if result.get("success"):
        html = result.get("html_content", "") or result.get("html", "")
        logger.info(f"HTML length: {len(html)} chars")

        # === CHECKS ===
        checks = []

        # 1. HTML is substantial
        if len(html) > 5000:
            checks.append(("HTML size > 5KB", True))
        else:
            checks.append(("HTML size > 5KB", False))

        # 2. Has GSAP animations
        anim_count = html.count('data-animate=')
        checks.append((f"Has data-animate ({anim_count}x)", anim_count > 5))

        # 3. Has text-split on headings
        text_split = html.count('data-animate="text-split"')
        checks.append((f"text-split headings ({text_split}x)", text_split >= 1))

        # 4. Has magnetic CTA
        magnetic = html.count('data-animate="magnetic"')
        checks.append((f"magnetic CTAs ({magnetic}x)", magnetic >= 1))

        # 5. No banned phrases
        banned = ["Benvenuti", "Siamo un'azienda", "leader nel settore", "soluzioni su misura"]
        html_lower = html.lower()
        found_banned = [b for b in banned if b.lower() in html_lower]
        checks.append((f"No banned phrases (found: {found_banned})", len(found_banned) == 0))

        # 6. Has Google Fonts (not Inter/Roboto default)
        has_google_fonts = "fonts.googleapis.com" in html
        has_bad_fonts = "family=Inter:" in html or "family=Roboto:" in html
        checks.append(("Custom Google Fonts loaded", has_google_fonts))
        checks.append(("No default Inter/Roboto fonts", not has_bad_fonts))

        # 7. Sections present
        for sec in ["hero", "about", "services", "testimonials", "contact"]:
            checks.append((f"Section '{sec}' present", f'id="{sec}"' in html))

        # 8. Business name present
        checks.append(("Business name in HTML", "Osteria del Porto" in html))

        # 9. Color CSS variables
        checks.append(("CSS variables present", "--color-primary" in html))

        # Print results
        logger.info("")
        logger.info("=" * 60)
        logger.info("QUALITY CHECKS:")
        all_pass = True
        for check_name, passed in checks:
            status = "PASS" if passed else "FAIL"
            logger.info(f"  [{status}] {check_name}")
            if not passed:
                all_pass = False

        logger.info("=" * 60)
        if all_pass:
            logger.info("ALL CHECKS PASSED!")
        else:
            logger.info("SOME CHECKS FAILED - review above")

        # Save HTML for manual inspection
        output_path = os.path.join(os.path.dirname(__file__), "test_output_restaurant.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"HTML saved to: {output_path}")

        # Print cost info
        logger.info(f"Tokens in: {result.get('tokens_input', '?')}")
        logger.info(f"Tokens out: {result.get('tokens_output', '?')}")
        logger.info(f"Cost: ${result.get('estimated_cost_usd', '?')}")
        logger.info(f"Model: {result.get('model_used', '?')}")

    else:
        logger.error(f"GENERATION FAILED: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

"""
Component Ingestion Service
Reads HTML component files, extracts metadata, generates embeddings,
and inserts/upserts into the components_v2 table.

Usage:
  python -m app.services.component_ingestion --dir backend/app/components --dry-run
  python -m app.services.component_ingestion --dir backend/app/components --insert
  python -m app.services.component_ingestion --dir backend/app/components/v2 --insert
"""
import argparse
import asyncio
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Variant cluster detection patterns (filename convention: *-{cluster}-v{N}.html)
VARIANT_PATTERN = re.compile(r"-v(\d)\.html$")
CLUSTER_MAP = {
    "1": "V1", "2": "V2", "3": "V3", "4": "V4", "5": "V5",
}

# Mood detection heuristics from CSS/HTML content
MOOD_KEYWORDS = {
    "luxury": ["luxury", "gold", "elegant", "serif", "playfair", "dm-serif", "cursive"],
    "minimal": ["minimal", "clean", "simple", "whitespace", "zen"],
    "bold": ["bold", "brutalist", "neon", "gradient", "dynamic", "dark-bold"],
    "warm": ["warm", "cozy", "organic", "local", "handwritten"],
    "tech": ["tech", "modern", "saas", "gradient", "glassmorphism", "glass"],
    "creative": ["creative", "gallery", "portfolio", "editorial", "magazine"],
    "professional": ["corporate", "trust", "professional", "business", "pro"],
}

# Section types that accept all categories (shared pool)
SHARED_SECTIONS = {"team", "testimonials", "faq", "cta", "footer", "stats",
                   "pricing", "process", "logos", "timeline", "video", "nav"}

# Category compatibility defaults per variant cluster
CLUSTER_CATEGORIES = {
    "V1": ["ristorante", "fitness", "bellezza"],
    "V2": ["studio_professionale", "salute", "agenzia"],
    "V3": ["saas", "ecommerce"],
    "V4": ["portfolio"],
    "V5": ["artigiani"],
}


def discover_components(base_dir: str) -> List[Dict[str, Any]]:
    """Scan directory tree for .html component files, extracting path metadata."""
    components = []
    base = Path(base_dir)

    for html_file in sorted(base.rglob("*.html")):
        rel = html_file.relative_to(base)
        parts = rel.parts

        # Skip non-component files
        if html_file.name in ("head-template.html",):
            continue

        # Determine section_type from parent directory
        # Patterns: v2/hero/file.html -> hero, or hero/file.html -> hero
        if "v2" in parts:
            idx = parts.index("v2")
            if idx + 1 < len(parts) - 1:
                section_type = parts[idx + 1]
            else:
                continue
        else:
            if len(parts) >= 2:
                section_type = parts[-2]
            else:
                continue

        # Component name = filename without .html
        name = html_file.stem

        components.append({
            "path": str(html_file),
            "name": name,
            "section_type": section_type,
            "is_v2": "v2" in parts,
        })

    return components


def extract_metadata(path: str, name: str, section_type: str, is_v2: bool) -> Dict[str, Any]:
    """Extract rich metadata from an HTML component file."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    meta: Dict[str, Any] = {
        "html_code": content,
        "section_type": section_type,
        "name": name,
    }

    # --- Variant cluster ---
    match = VARIANT_PATTERN.search(name)
    if match:
        meta["variant_cluster"] = CLUSTER_MAP.get(match.group(1), "V2")
    else:
        # Infer from name keywords
        name_lower = name.lower()
        if any(k in name_lower for k in ("elegant", "luxury", "cozy")):
            meta["variant_cluster"] = "V1"
        elif any(k in name_lower for k in ("clean", "corporate", "trust", "pro")):
            meta["variant_cluster"] = "V2"
        elif any(k in name_lower for k in ("gradient", "dark", "modern", "tech", "neon")):
            meta["variant_cluster"] = "V3"
        elif any(k in name_lower for k in ("gallery", "minimal", "creative", "editorial")):
            meta["variant_cluster"] = "V4"
        elif any(k in name_lower for k in ("organic", "warm", "zen", "local")):
            meta["variant_cluster"] = "V5"
        else:
            meta["variant_cluster"] = "V2"  # default

    # --- Compatible categories ---
    if section_type in SHARED_SECTIONS:
        meta["compatible_categories"] = None  # NULL = compatible with all
    else:
        meta["compatible_categories"] = CLUSTER_CATEGORIES.get(
            meta["variant_cluster"], ["ristorante", "studio_professionale", "saas"]
        )

    # --- Placeholders ({{...}}) ---
    meta["placeholders"] = sorted(set(re.findall(r"\{\{(\w+)\}\}", content)))

    # --- GSAP effects (data-animate="...") ---
    meta["gsap_effects"] = sorted(set(re.findall(r'data-animate="([^"]+)"', content)))

    # --- CSS variables (var(--...)) ---
    css_vars = sorted(set(re.findall(r"var\(--([^)]+)\)", content)))
    meta["css_variables"] = {v: None for v in css_vars}  # JSONB map, values filled later

    # --- Density ---
    tag_count = len(re.findall(r"<[a-z]", content))
    if tag_count < 20:
        meta["density"] = "minimal"
    elif tag_count < 50:
        meta["density"] = "balanced"
    else:
        meta["density"] = "dense"

    # --- Mood tags ---
    content_lower = content.lower()
    moods = []
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(kw in content_lower or kw in name.lower() for kw in keywords):
            moods.append(mood)
    meta["mood_tags"] = moods if moods else ["professional"]

    # --- Typography style ---
    if any(f in content_lower for f in ("playfair", "dm-serif", "serif", "georgia", "lora")):
        meta["typography_style"] = "serif"
    elif any(f in content_lower for f in ("space-grotesk", "sora", "display")):
        meta["typography_style"] = "display"
    elif "font-heading" in content_lower and "font-body" in content_lower:
        meta["typography_style"] = "mixed"
    else:
        meta["typography_style"] = "sans"

    # --- Flags ---
    meta["has_video"] = "video" in content_lower or "youtube" in content_lower
    meta["has_slider"] = any(k in content_lower for k in ("swiper", "carousel", "slider", "marquee"))

    # --- Animation level ---
    anim_count = len(meta["gsap_effects"])
    if anim_count <= 2:
        meta["animation_level"] = "subtle"
    elif anim_count <= 5:
        meta["animation_level"] = "moderate"
    else:
        meta["animation_level"] = "dynamic"

    return meta


def format_summary(components: List[Dict[str, Any]]) -> str:
    """Generate a human-readable summary table."""
    lines = [f"\n{'='*80}", f"  Component Scan Summary: {len(components)} components found", f"{'='*80}\n"]

    # Group by section
    from collections import Counter
    section_counts = Counter(c["section_type"] for c in components)
    for sec, cnt in sorted(section_counts.items()):
        lines.append(f"  {sec:20s} : {cnt} components")

    v2_count = sum(1 for c in components if c.get("is_v2"))
    lines.append(f"\n  V2 components: {v2_count}")
    lines.append(f"  Legacy components: {len(components) - v2_count}")
    return "\n".join(lines)


async def ingest_components(
    base_dir: str,
    dry_run: bool = True,
    generate_embeddings: bool = True,
    v2_only: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """Main ingestion pipeline. Scans, extracts, embeds, upserts."""
    discovered = discover_components(base_dir)
    if v2_only:
        discovered = [c for c in discovered if c["is_v2"]]

    logger.info(format_summary(discovered))

    if not discovered:
        logger.warning("No components found. Check the --dir path.")
        return {"total": 0, "inserted": 0, "updated": 0, "errors": 0}

    # Extract metadata for all components
    all_meta = []
    for comp in discovered:
        try:
            meta = extract_metadata(comp["path"], comp["name"], comp["section_type"], comp["is_v2"])
            all_meta.append(meta)
        except Exception as e:
            logger.error(f"Failed to extract metadata for {comp['name']}: {e}")

    if dry_run:
        logger.info("\n--- DRY RUN: showing extracted metadata ---\n")
        for m in all_meta:
            logger.info(
                f"  {m['name']:40s} | {m['section_type']:15s} | {m['variant_cluster']:3s} "
                f"| moods={m['mood_tags']} | density={m['density']} "
                f"| anims={m['gsap_effects'][:3]}{'...' if len(m['gsap_effects']) > 3 else ''} "
                f"| placeholders={len(m['placeholders'])}"
            )
        logger.info(f"\n  Total: {len(all_meta)} components ready for ingestion.")
        logger.info("  Run with --insert to write to database.")
        return {"total": len(all_meta), "inserted": 0, "updated": 0, "errors": 0}

    # Filter out existing components unless --force is set
    if not force:
        from app.core.database import SessionLocal as _SL
        from app.models.component_v2 import ComponentV2 as _CV2
        _db = _SL()
        try:
            existing_names = {row[0] for row in _db.query(_CV2.name).all()}
        finally:
            _db.close()
        new_meta = [m for m in all_meta if m["name"] not in existing_names]
        skipped = len(all_meta) - len(new_meta)
        if skipped:
            logger.info(f"Skipping {skipped} existing components (use --force to re-process)")
        all_meta = new_meta
        if not all_meta:
            logger.info("All components already in DB. Nothing to do.")
            return {"total": 0, "inserted": 0, "updated": 0, "errors": 0, "skipped": skipped}

    # Generate embeddings in batch
    embeddings = [None] * len(all_meta)
    if generate_embeddings:
        from app.services.embedding_service import generate_embeddings_batch, build_component_description
        descriptions = [build_component_description(m) for m in all_meta]
        logger.info(f"Generating embeddings for {len(descriptions)} components...")
        try:
            embeddings = await generate_embeddings_batch(descriptions)
            ok_count = sum(1 for e in embeddings if e is not None)
            logger.info(f"  Embeddings generated: {ok_count}/{len(descriptions)}")
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}. Continuing without embeddings.")

    # Insert/upsert into DB
    from app.core.database import SessionLocal
    from app.models.component_v2 import ComponentV2

    db = SessionLocal()
    inserted = 0
    updated = 0
    errors = 0

    try:
        for i, meta in enumerate(all_meta):
            try:
                existing = db.query(ComponentV2).filter(ComponentV2.name == meta["name"]).first()
                emb = embeddings[i] if i < len(embeddings) else None

                if existing:
                    # Update fields (only reached when --force is set)
                    existing.section_type = meta["section_type"]
                    existing.variant_cluster = meta["variant_cluster"]
                    existing.compatible_categories = meta.get("compatible_categories")
                    existing.mood_tags = meta.get("mood_tags", [])
                    existing.density = meta.get("density")
                    existing.typography_style = meta.get("typography_style")
                    existing.has_video = meta.get("has_video", False)
                    existing.has_slider = meta.get("has_slider", False)
                    existing.animation_level = meta.get("animation_level", "moderate")
                    existing.html_code = meta["html_code"]
                    existing.css_variables = meta.get("css_variables", {})
                    existing.placeholders = meta.get("placeholders", [])
                    existing.gsap_effects = meta.get("gsap_effects", [])
                    if emb is not None:
                        existing.embedding = emb
                    updated += 1
                else:
                    comp = ComponentV2(
                        name=meta["name"],
                        section_type=meta["section_type"],
                        variant_cluster=meta["variant_cluster"],
                        compatible_categories=meta.get("compatible_categories"),
                        mood_tags=meta.get("mood_tags", []),
                        density=meta.get("density"),
                        typography_style=meta.get("typography_style"),
                        has_video=meta.get("has_video", False),
                        has_slider=meta.get("has_slider", False),
                        animation_level=meta.get("animation_level", "moderate"),
                        html_code=meta["html_code"],
                        css_variables=meta.get("css_variables", {}),
                        placeholders=meta.get("placeholders", []),
                        gsap_effects=meta.get("gsap_effects", []),
                        embedding=emb,
                    )
                    db.add(comp)
                    inserted += 1

            except Exception as e:
                logger.error(f"Error processing {meta['name']}: {e}")
                errors += 1

        db.commit()
        logger.info(f"\nIngestion complete: {inserted} inserted, {updated} updated, {errors} errors")
    except Exception as e:
        db.rollback()
        logger.error(f"Database commit failed: {e}")
        errors += 1
    finally:
        db.close()

    return {"total": len(all_meta), "inserted": inserted, "updated": updated, "errors": errors}


async def seed_existing_components(generate_embeddings: bool = True) -> Dict[str, Any]:
    """Convenience function: process ALL components (legacy + v2).

    Scans backend/app/components/ which includes both legacy and v2/ subdirectories.
    Called from main.py lifespan or manually. Idempotent -- skips already-inserted components.
    """
    components_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "app", "components"
    )
    if not os.path.isdir(components_dir):
        # Try alternative path relative to CWD
        components_dir = os.path.join("backend", "app", "components")
    if not os.path.isdir(components_dir):
        logger.warning(f"Components directory not found: {components_dir}")
        return {"total": 0, "inserted": 0, "updated": 0, "errors": 0}

    return await ingest_components(
        base_dir=components_dir,
        dry_run=False,
        generate_embeddings=generate_embeddings,
        v2_only=False,
        force=False,
    )


def main():
    parser = argparse.ArgumentParser(description="Ingest HTML components into components_v2 table")
    parser.add_argument("--dir", required=True, help="Base directory to scan for .html components")
    parser.add_argument("--dry-run", action="store_true", help="Scan and show metadata without writing to DB")
    parser.add_argument("--insert", action="store_true", help="Actually insert/upsert into database")
    parser.add_argument("--no-embeddings", action="store_true", help="Skip embedding generation")
    parser.add_argument("--v2-only", action="store_true", help="Only process v2/ subdirectory components")
    parser.add_argument("--force", action="store_true", help="Re-process and re-embed existing components")
    args = parser.parse_args()

    if not args.dry_run and not args.insert:
        logger.error("Specify either --dry-run or --insert")
        sys.exit(1)

    dry_run = args.dry_run or not args.insert

    result = asyncio.run(ingest_components(
        base_dir=args.dir,
        dry_run=dry_run,
        generate_embeddings=not args.no_embeddings,
        v2_only=args.v2_only,
        force=args.force,
    ))

    logger.info(f"\nResult: {result}")


if __name__ == "__main__":
    main()

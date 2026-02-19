"""
V2 Generation Pipeline Orchestrator
pgvector + diversity engine + Style DNA → unique sites

Pipeline:
  1. extract_style_dna() → Style DNA JSON (colors, fonts, mood, cluster)
  2. Load CategoryBlueprint from DB
  3. For each section: embed query → pgvector search → diversity selection
  4. Compute layout hash, ensure uniqueness
  5. AI generates Italian copywriting for each section's placeholders
  6. Assemble final HTML via v2_assembler
  7. Log generation + update cooldowns
"""

import asyncio
import json
import logging
import random
import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.category_blueprint import CategoryBlueprint
from app.models.component_v2 import ComponentV2
from app.models.generation_log import GenerationLog
from app.models.generation_log_component import GenerationLogComponent
from app.services.diversity_engine import (
    compute_layout_hash,
    ensure_unique_layout,
    select_with_diversity,
    update_cooldown,
)
from app.services.embedding_service import generate_embedding
from app.services.kimi_client import kimi_text
from app.services.style_dna_service import dna_to_query_text, extract_style_dna
from app.services.v2_assembler import assemble, replace_placeholders

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[int, str, Optional[Dict[str, Any]]], None]]

# Section labels for Italian content prompts
_SECTION_CONTENT_HINT = {
    "hero": "sezione principale di apertura (headline impattante, sottotitolo, CTA)",
    "about": "sezione chi siamo (storia, mission, valori, numeri chiave)",
    "services": "sezione servizi offerti (lista servizi con titolo, descrizione, icona)",
    "menu": "sezione menu ristorante (piatti con nome, descrizione, prezzo)",
    "gallery": "sezione galleria immagini (titoli, didascalie)",
    "testimonials": "sezione testimonianze clienti (citazione, nome, ruolo)",
    "team": "sezione team (nome, ruolo, bio breve)",
    "pricing": "sezione prezzi/piani (nome piano, prezzo, features)",
    "faq": "sezione domande frequenti (domanda e risposta)",
    "contact": "sezione contatti (indirizzo, telefono, email, form)",
    "cta": "call to action finale (titolo persuasivo, bottone)",
    "footer": "footer con info aziendali",
    "stats": "sezione statistiche/numeri (cifre con label)",
    "process": "sezione processo/come funziona (passi numerati)",
    "features": "sezione caratteristiche/vantaggi (titolo, descrizione, icona)",
    "programs": "sezione programmi/corsi offerti",
    "products": "sezione prodotti in vetrina",
    "portfolio": "sezione portfolio/lavori recenti",
    "booking": "sezione prenotazione",
    "cases": "sezione casi studio/risultati",
}


class V2Generator:
    """Class-based v2 generation pipeline that accepts an injected DB session."""

    def __init__(self, db: Session):
        self.db = db

    async def generate(
        self,
        category: str,
        color_primary: str,
        description: str,
        business_name: str = "",
        logo_base64: Optional[str] = None,
        logo_mime_type: str = "image/png",
        client_ref: Optional[str] = None,
        progress_callback: ProgressCallback = None,
    ) -> Dict[str, Any]:
        """Full v2 generation pipeline.

        Returns:
            {
                "success": True,
                "html": str,
                "style_dna": dict,
                "components_used": dict,
                "layout_hash": str,
                "sections": list,
                "tokens_input": int,
                "tokens_output": int,
            }
        """
        total_tokens_in = 0
        total_tokens_out = 0

        def _progress(step: int, msg: str, data: Optional[Dict] = None):
            logger.info(f"[v2 gen] Step {step}: {msg}")
            if progress_callback:
                try:
                    progress_callback(step, msg, data)
                except Exception:
                    pass

        # ---- Step 1: Extract Style DNA ----
        _progress(1, "Analisi dello stile visivo...")
        style_dna = await extract_style_dna(
            category=category,
            color_primary=color_primary,
            description=description,
            logo_base64=logo_base64,
            logo_mime_type=logo_mime_type,
        )
        _progress(1, "Style DNA estratto", {
            "mood": style_dna.get("mood"),
            "variant_cluster": style_dna.get("variant_cluster"),
            "colors": style_dna.get("color_palette", [])[:3],
            "fonts": [style_dna.get("typography_heading"), style_dna.get("typography_body")],
        })

        # ---- Step 2: Load Category Blueprint ----
        _progress(2, "Caricamento blueprint di categoria...")
        blueprint = self.db.query(CategoryBlueprint).filter(
            CategoryBlueprint.category_slug == category
        ).first()

        if not blueprint:
            logger.warning(f"No blueprint for category '{category}', using default sections")
            sections_required = ["hero", "about", "services", "contact", "footer"]
            sections_optional = ["testimonials", "faq", "cta"]
        else:
            sections_required = blueprint.sections_required or []
            sections_optional = blueprint.sections_optional or []

        # Determine which optional sections to include
        selected_optional = self._pick_optionals(sections_optional, style_dna)

        all_sections = list(sections_required) + selected_optional
        # Reorder: hero first, footer last
        if "hero" in all_sections:
            all_sections.remove("hero")
            all_sections.insert(0, "hero")
        if "footer" in all_sections:
            all_sections.remove("footer")
            all_sections.append("footer")

        _progress(2, f"Sezioni selezionate: {all_sections}")

        # ---- Step 3: Component Selection via pgvector + diversity ----
        _progress(3, "Selezione componenti con pgvector...")
        query_text = dna_to_query_text(style_dna, category)
        query_embedding = await generate_embedding(query_text)

        components_selected: Dict[str, Dict[str, Any]] = {}
        for section_type in all_sections:
            candidates = _query_pgvector(
                db=self.db,
                section_type=section_type,
                category=category,
                embedding=query_embedding,
                variant_cluster=style_dna.get("variant_cluster"),
                top_k=5,
            )
            if not candidates:
                logger.warning(f"No candidates for section '{section_type}', skipping")
                continue

            winner = select_with_diversity(
                candidates=candidates,
                section_type=section_type,
                category=category,
                db=self.db,
            )
            if winner:
                components_selected[section_type] = winner
                logger.info(f"  {section_type} -> {winner['name']} (score={winner.get('final_score', 0):.3f})")

        # ---- Step 4: Ensure layout uniqueness ----
        _progress(4, "Verifica unicita' layout...")
        name_map = {sec: comp["name"] for sec, comp in components_selected.items()}
        unique_map, layout_hash = ensure_unique_layout(
            category=category,
            components=name_map,
            db=self.db,
        )

        # If force_diversity changed components, reload them
        if unique_map != name_map:
            for sec, new_name in unique_map.items():
                if new_name != name_map.get(sec):
                    new_comp = self.db.query(ComponentV2).filter(ComponentV2.name == new_name).first()
                    if new_comp:
                        components_selected[sec] = {
                            "id": str(new_comp.id),
                            "name": new_comp.name,
                            "html_code": new_comp.html_code,
                            "placeholders": new_comp.placeholders or [],
                        }

        if not components_selected:
            return {"success": False, "error": "Nessun componente trovato per questa categoria"}

        _progress(4, f"Layout hash: {layout_hash} ({len(components_selected)} componenti)")

        # ---- Step 5: Generate Italian copywriting for placeholders ----
        _progress(5, "Generazione contenuti in italiano...")
        section_htmls = {}
        content_tasks = []
        for section_type, comp in components_selected.items():
            placeholders = comp.get("placeholders", [])
            if placeholders:
                content_tasks.append(
                    _generate_section_content(
                        section_type=section_type,
                        placeholders=placeholders,
                        category=category,
                        business_name=business_name,
                        description=description,
                        style_dna=style_dna,
                    )
                )
            else:
                async def _empty():
                    return ({}, 0, 0)
                content_tasks.append(_empty())

        content_results = await asyncio.gather(*content_tasks, return_exceptions=True)

        for i, (section_type, comp) in enumerate(components_selected.items()):
            result = content_results[i]
            if isinstance(result, Exception):
                logger.error(f"Content generation failed for {section_type}: {result}")
                content_data = {}
            else:
                content_data, tok_in, tok_out = result
                total_tokens_in += tok_in
                total_tokens_out += tok_out

            # Inject business info into content
            content_data.setdefault("BUSINESS_NAME", business_name)
            content_data.setdefault("BUSINESS_ADDRESS", "")
            content_data.setdefault("BUSINESS_PHONE", "")
            content_data.setdefault("BUSINESS_EMAIL", "")

            filled_html = replace_placeholders(comp["html_code"], content_data)
            section_htmls[section_type] = filled_html

        _progress(5, "Contenuti generati per tutte le sezioni")

        # ---- Step 6: Assemble final HTML ----
        _progress(6, "Assemblaggio HTML finale...")
        final_order = [s for s in all_sections if s in section_htmls]
        final_html = assemble(
            style_dna=style_dna,
            section_htmls=section_htmls,
            section_order=final_order,
            business_name=business_name,
            meta_title=f"{business_name} - Sito Ufficiale" if business_name else "Sito Web",
            meta_description=description[:160] if description else "",
        )

        _progress(6, f"HTML assemblato ({len(final_html)} chars)")

        # ---- Step 7: Log generation + update cooldowns ----
        _progress(7, "Salvataggio log generazione...")
        self._log_generation(
            category=category,
            style_dna=style_dna,
            color_primary=color_primary,
            client_ref=client_ref or business_name,
            components_selected=components_selected,
            layout_hash=layout_hash,
        )

        _progress(7, "Generazione completata!")

        return {
            "success": True,
            "html": final_html,
            "style_dna": style_dna,
            "components_used": {sec: comp["name"] for sec, comp in components_selected.items()},
            "layout_hash": layout_hash,
            "sections": final_order,
            "tokens_input": total_tokens_in,
            "tokens_output": total_tokens_out,
        }

    def _pick_optionals(
        self,
        sections_optional: List[str],
        style_dna: Dict[str, Any],
    ) -> List[str]:
        """Select 2-3 optional sections based on Style DNA mood matching."""
        if not sections_optional:
            return []

        dna_sections = style_dna.get("sections_order", [])
        selected = [sec for sec in sections_optional if sec in dna_sections]

        if not selected:
            n = random.randint(2, min(3, len(sections_optional)))
            selected = random.sample(sections_optional, n)

        return selected

    def _log_generation(
        self,
        category: str,
        style_dna: Dict[str, Any],
        color_primary: str,
        client_ref: str,
        components_selected: Dict[str, Dict[str, Any]],
        layout_hash: str,
    ):
        """Save generation log + component entries, update cooldowns."""
        try:
            gen_log = GenerationLog(
                category=category,
                style_mood=style_dna.get("mood"),
                color_primary=color_primary,
                client_ref=client_ref,
                style_dna=style_dna,
                components_used={sec: comp["name"] for sec, comp in components_selected.items()},
                layout_hash=layout_hash,
            )
            self.db.add(gen_log)
            self.db.flush()

            for section_type, comp in components_selected.items():
                entry = GenerationLogComponent(
                    generation_id=gen_log.id,
                    component_id=UUID(comp["id"]) if comp.get("id") else None,
                    section_type=section_type,
                    category=category,
                )
                self.db.add(entry)

            self.db.commit()

            for comp in components_selected.values():
                if comp.get("id"):
                    update_cooldown(comp["id"], self.db)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save generation log: {e}")


# Convenience function for backward compat / simple usage without injecting db
async def generate_site_v2(
    category: str,
    color_primary: str,
    description: str,
    business_name: str = "",
    logo_base64: Optional[str] = None,
    logo_mime_type: str = "image/png",
    client_ref: Optional[str] = None,
    progress_callback: ProgressCallback = None,
) -> Dict[str, Any]:
    """Standalone wrapper that creates its own DB session."""
    db = SessionLocal()
    try:
        gen = V2Generator(db)
        return await gen.generate(
            category=category,
            color_primary=color_primary,
            description=description,
            business_name=business_name,
            logo_base64=logo_base64,
            logo_mime_type=logo_mime_type,
            client_ref=client_ref,
            progress_callback=progress_callback,
        )
    finally:
        db.close()


def _query_pgvector(
    db: Session,
    section_type: str,
    category: str,
    embedding: Optional[List[float]],
    variant_cluster: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Query components_v2 via pgvector cosine similarity with filters."""

    if embedding:
        # pgvector cosine distance query
        query = sql_text("""
            SELECT
                id::text, name, html_code, placeholders, gsap_effects,
                1 - (embedding <=> :embedding::vector) AS similarity_score
            FROM components_v2
            WHERE section_type = :section_type
              AND (cooldown_until IS NULL OR cooldown_until < NOW())
              AND (
                  compatible_categories IS NULL
                  OR :category = ANY(compatible_categories)
              )
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """)
        rows = db.execute(query, {
            "embedding": str(embedding),
            "section_type": section_type,
            "category": category,
            "top_k": top_k,
        }).fetchall()
    else:
        # Fallback: no embedding, just filter by section_type + category
        query = sql_text("""
            SELECT
                id::text, name, html_code, placeholders, gsap_effects,
                0.5 AS similarity_score
            FROM components_v2
            WHERE section_type = :section_type
              AND (cooldown_until IS NULL OR cooldown_until < NOW())
              AND (
                  compatible_categories IS NULL
                  OR :category = ANY(compatible_categories)
              )
            ORDER BY usage_count ASC, RANDOM()
            LIMIT :top_k
        """)
        rows = db.execute(query, {
            "section_type": section_type,
            "category": category,
            "top_k": top_k,
        }).fetchall()

    candidates = []
    for row in rows:
        candidates.append({
            "id": row[0],
            "name": row[1],
            "html_code": row[2],
            "placeholders": row[3] or [],
            "gsap_effects": row[4] or [],
            "similarity_score": float(row[5]),
        })

    # Optional: boost candidates matching preferred variant_cluster
    if variant_cluster and candidates:
        for c in candidates:
            if variant_cluster.lower() in c["name"].lower():
                c["similarity_score"] = min(1.0, c["similarity_score"] + 0.1)

    return candidates


async def _generate_section_content(
    section_type: str,
    placeholders: List[str],
    category: str,
    business_name: str,
    description: str,
    style_dna: Dict[str, Any],
) -> Tuple[Dict[str, str], int, int]:
    """Generate Italian copywriting for a section's placeholders.

    Returns: (content_dict, tokens_in, tokens_out)
    """
    section_hint = _SECTION_CONTENT_HINT.get(section_type, f"sezione {section_type}")
    mood = style_dna.get("mood", "professional")

    # Build placeholder list for the prompt
    placeholder_list = "\n".join([f"  - {p}" for p in placeholders])

    # Check for REPEAT blocks (lists of items)
    repeat_keys = [p for p in placeholders if p.endswith("_ITEMS") or p in (
        "SERVICES", "FEATURES", "TESTIMONIALS", "FAQ_ITEMS", "TEAM_MEMBERS",
        "PRICING_PLANS", "GALLERY_ITEMS", "PROCESS_STEPS", "STATS_ITEMS",
        "TIMELINE_ITEMS", "LOGOS_ITEMS", "MENU_ITEMS",
    )]

    prompt = f"""Sei un copywriter italiano esperto in {category}. Scrivi contenuti per la {section_hint}.

REGOLE TASSATIVE:
- SOLO italiano, mai inglese
- VIETATO: "benvenuti", "siamo un'azienda", "la nostra passione", frasi generiche
- Tono: {mood} — scrivi come un brand premium
- Headline: massimo 6-8 parole, impattante e memorabile
- Sottotitoli: massimo 20 parole, specifici e concreti
- Testi: concreti, con dettagli reali credibili per "{business_name}" ({description})
- CTA: verbi d'azione specifici (non "scopri di piu'")

ATTIVITA': {business_name}
DESCRIZIONE: {description}

Genera un JSON con TUTTI questi placeholder:
{placeholder_list}

Per i placeholder che rappresentano LISTE (come SERVICES, FEATURES, TESTIMONIALS, etc.),
genera un array di 3-6 oggetti. Ogni oggetto deve avere i sub-campi appropriati.
Esempio per SERVICES: [{{"ICON": "iconify-icon", "TITLE": "...", "DESCRIPTION": "..."}}]

RISPONDI SOLO con il JSON, senza spiegazioni o markdown."""

    result = await kimi_text.call(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        thinking=False,
        temperature=0.7,
        json_mode=True,
    )

    if not result.get("success"):
        logger.error(f"Content generation failed for {section_type}: {result.get('error')}")
        return {}, 0, 0

    tokens_in = result.get("tokens_input", 0)
    tokens_out = result.get("tokens_output", 0)

    try:
        content_text = result["content"].strip()
        # Strip markdown fences if present
        if content_text.startswith("```"):
            content_text = content_text.split("\n", 1)[1].rsplit("```", 1)[0]
        content = json.loads(content_text)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Failed to parse content JSON for {section_type}: {e}")
        return {}, tokens_in, tokens_out

    # Flatten to string dict for replace_placeholders
    flat = {}
    for k, v in content.items():
        if isinstance(v, list):
            flat[k] = v  # Keep lists for REPEAT expansion
        elif isinstance(v, dict):
            flat[k] = json.dumps(v, ensure_ascii=False)
        else:
            flat[k] = str(v)

    return flat, tokens_in, tokens_out

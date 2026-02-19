"""
Routes V2 - Component search (pgvector), generation pipeline, diversity dashboard, blueprints.
All endpoints use JWT auth and follow existing patterns from sites.py/generate.py.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func as sql_func, text as sql_text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.category_blueprint import CategoryBlueprint
from app.models.component_v2 import ComponentV2
from app.models.generation_log import GenerationLog
from app.models.generation_log_component import GenerationLogComponent
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["v2"])


# ============ SCHEMAS ============

class GenerateV2Request(BaseModel):
    """V2 generation request."""
    category: str
    description: str
    business_name: Optional[str] = ""
    logo_url: Optional[str] = None
    logo_base64: Optional[str] = None
    color_primary: Optional[str] = "#3b82f6"
    client_ref: Optional[str] = None


class ComponentBatchItem(BaseModel):
    name: str
    section_type: str
    variant_cluster: str
    html_code: str
    compatible_categories: List[str] = []
    incompatible_categories: List[str] = []
    is_special: bool = False
    mood_tags: List[str] = []
    density: Optional[str] = None
    typography_style: Optional[str] = None
    has_video: bool = False
    has_slider: bool = False
    animation_level: str = "moderate"
    css_variables: Dict[str, Any] = {}
    placeholders: List[str] = []
    gsap_effects: List[str] = []
    preview_url: Optional[str] = None
    reference_source: Optional[str] = None
    notes: Optional[str] = None


class ComponentBatchInsertRequest(BaseModel):
    components: List[ComponentBatchItem]
    generate_embeddings: bool = True


class BlueprintCreateRequest(BaseModel):
    category_slug: str
    category_name: str
    sections_required: List[str] = []
    sections_optional: List[str] = []
    sections_forbidden: List[str] = []
    default_variant_cluster: Optional[str] = None
    mood_required: List[str] = []
    mood_forbidden: List[str] = []
    style_names: List[str] = []


# ============ 1. GENERATE V2 ============

@router.post("/generate/")
async def generate_v2(
    data: GenerateV2Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Trigger v2 generation pipeline.
    Calls V2Generator: Style DNA -> pgvector search -> diversity ->
    content injection -> HTML assembly -> log generation.
    """
    # Validate category blueprint exists
    blueprint = db.query(CategoryBlueprint).filter(
        CategoryBlueprint.category_slug == data.category
    ).first()

    if not blueprint:
        raise HTTPException(
            status_code=400,
            detail=f"Categoria '{data.category}' non trovata. Usa GET /api/v2/blueprints/ per la lista.",
        )

    try:
        from app.services.v2_generator import V2Generator

        generator = V2Generator(db)
        result = await generator.generate(
            category=data.category,
            color_primary=data.color_primary or "#3b82f6",
            description=data.description,
            business_name=data.business_name or data.client_ref or "",
            logo_base64=data.logo_base64,
            client_ref=data.client_ref,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Errore nella generazione del sito"),
            )

        return {
            "success": True,
            "html": result["html"],
            "style_dna": result["style_dna"],
            "layout_hash": result["layout_hash"],
            "components_used": result["components_used"],
            "sections": result["sections"],
            "tokens_input": result.get("tokens_input", 0),
            "tokens_output": result.get("tokens_output", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"V2 generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Errore generazione v2: {str(e)}",
        )


# ============ 2. COMPONENT SEARCH (pgvector raw SQL) ============

@router.get("/components/search/")
async def search_components(
    query_text: str = Query(description="Semantic search query text"),
    section_type: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=5, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Query pgvector with embedding similarity search.
    Generates a query embedding, then uses cosine distance operator
    to find the closest matching components. Filters by section_type,
    category compatibility, and cooldown.
    """
    # Generate embedding for the query text
    from app.services.embedding_service import generate_embedding

    query_embedding = await generate_embedding(query_text)
    if not query_embedding:
        raise HTTPException(
            status_code=503,
            detail="Servizio embedding non disponibile. Controlla GEMINI_API_KEY.",
        )

    # Convert embedding list to pgvector literal format: '[0.1,0.2,...]'
    vec_literal = "[" + ",".join(str(v) for v in query_embedding) + "]"

    # Raw SQL with pgvector cosine distance
    sql = sql_text("""
        SELECT id, name, section_type, variant_cluster, mood_tags,
               1 - (embedding <=> :query_vec::vector) AS similarity_score
        FROM components_v2
        WHERE embedding IS NOT NULL
          AND (:section_type IS NULL OR section_type = :section_type)
          AND (cooldown_until IS NULL OR cooldown_until < NOW())
          AND (:category IS NULL OR :category = ANY(compatible_categories) OR compatible_categories IS NULL)
          AND NOT (:category IS NOT NULL AND :category = ANY(COALESCE(incompatible_categories, ARRAY[]::text[])))
        ORDER BY similarity_score DESC
        LIMIT :limit
    """)

    rows = db.execute(sql, {
        "query_vec": vec_literal,
        "section_type": section_type,
        "category": category,
        "limit": limit,
    }).fetchall()

    results = [
        {
            "id": str(row.id),
            "name": row.name,
            "section_type": row.section_type,
            "variant_cluster": row.variant_cluster,
            "mood_tags": row.mood_tags or [],
            "similarity_score": round(float(row.similarity_score), 4),
        }
        for row in rows
    ]

    return {
        "results": results,
        "total": len(results),
        "query": query_text,
    }


# ============ 3. BATCH INSERT COMPONENTS ============

@router.post("/components/batch-insert/")
async def batch_insert_components(
    data: ComponentBatchInsertRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Bulk insert components with optional auto-embedding generation.
    Admin-only endpoint. Upserts: skips components whose name already exists.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin possono inserire componenti.",
        )

    if not data.components:
        raise HTTPException(status_code=400, detail="Lista componenti vuota.")

    inserted = []
    skipped = []
    errors = []

    # Generate embeddings in batch if requested
    embeddings = [None] * len(data.components)
    if data.generate_embeddings:
        from app.services.embedding_service import generate_embeddings_batch, build_component_description

        descriptions = [
            build_component_description({
                "section_type": c.section_type,
                "variant_cluster": c.variant_cluster,
                "mood_tags": c.mood_tags,
                "density": c.density,
                "typography_style": c.typography_style,
                "animation_level": c.animation_level,
                "compatible_categories": c.compatible_categories,
                "gsap_effects": c.gsap_effects,
            })
            for c in data.components
        ]
        embeddings = await generate_embeddings_batch(descriptions)

    for i, item in enumerate(data.components):
        # Check if component name already exists (skip duplicates)
        existing = db.query(ComponentV2).filter(ComponentV2.name == item.name).first()
        if existing:
            skipped.append({"name": item.name, "reason": "already exists"})
            continue

        try:
            comp = ComponentV2(
                name=item.name,
                section_type=item.section_type,
                variant_cluster=item.variant_cluster,
                html_code=item.html_code,
                compatible_categories=item.compatible_categories,
                incompatible_categories=item.incompatible_categories,
                is_special=item.is_special,
                mood_tags=item.mood_tags,
                density=item.density,
                typography_style=item.typography_style,
                has_video=item.has_video,
                has_slider=item.has_slider,
                animation_level=item.animation_level,
                css_variables=item.css_variables,
                placeholders=item.placeholders,
                gsap_effects=item.gsap_effects,
                preview_url=item.preview_url,
                reference_source=item.reference_source,
                notes=item.notes,
                embedding=embeddings[i],
            )
            db.add(comp)
            db.flush()
            inserted.append({"name": item.name, "id": str(comp.id)})
        except Exception as e:
            db.rollback()
            errors.append({"name": item.name, "error": str(e)})
            logger.error(f"[V2] Error inserting component '{item.name}': {e}")

    if inserted:
        db.commit()

    return {
        "success": True,
        "inserted": len(inserted),
        "skipped": len(skipped),
        "errors": len(errors),
        "details": {
            "inserted": inserted,
            "skipped": skipped,
            "errors": errors,
        },
    }


# ============ 4. DIVERSITY DASHBOARD (admin-only) ============

@router.get("/diversity/dashboard/")
async def diversity_dashboard(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return diversity metrics: unique layouts per category, diversity_pct,
    components at risk of saturation, cooldown status.
    Admin-only endpoint.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin possono vedere le metriche di diversita'.",
        )

    now = datetime.now(timezone.utc)

    # --- Component counts ---
    comp_query = db.query(ComponentV2)
    if category:
        comp_query = comp_query.filter(ComponentV2.compatible_categories.any(category))
    total_components = comp_query.count()

    cooldown_count = comp_query.filter(
        ComponentV2.cooldown_until.isnot(None),
        ComponentV2.cooldown_until > now,
    ).count()

    # --- Components per section ---
    section_q = db.query(
        ComponentV2.section_type,
        sql_func.count(ComponentV2.id),
    ).group_by(ComponentV2.section_type)
    if category:
        section_q = section_q.filter(ComponentV2.compatible_categories.any(category))
    components_by_section = dict(section_q.all())

    # --- Diversity by category (from generation_logs) ---
    if category:
        total_gens = db.query(sql_func.count(GenerationLog.id)).filter(
            GenerationLog.category == category
        ).scalar() or 0
        unique_layouts = db.query(
            sql_func.count(sql_func.distinct(GenerationLog.layout_hash))
        ).filter(GenerationLog.category == category).scalar() or 0
        diversity_by_category = {
            category: {
                "total_generations": total_gens,
                "unique_layouts": unique_layouts,
                "diversity_pct": round((unique_layouts / total_gens * 100), 1) if total_gens > 0 else 0.0,
            }
        }
    else:
        # All categories
        cat_rows = db.query(
            GenerationLog.category,
            sql_func.count(GenerationLog.id).label("total"),
            sql_func.count(sql_func.distinct(GenerationLog.layout_hash)).label("unique"),
        ).group_by(GenerationLog.category).all()

        diversity_by_category = {}
        for row in cat_rows:
            diversity_by_category[row.category] = {
                "total_generations": row.total,
                "unique_layouts": row.unique,
                "diversity_pct": round((row.unique / row.total * 100), 1) if row.total > 0 else 0.0,
            }

    # --- Most-used components (at risk of saturation) ---
    at_risk_q = db.query(
        ComponentV2.id,
        ComponentV2.name,
        ComponentV2.section_type,
        ComponentV2.usage_count,
    ).filter(ComponentV2.usage_count > 0).order_by(ComponentV2.usage_count.desc()).limit(10)

    at_risk_components = [
        {
            "id": str(row.id),
            "name": row.name,
            "section_type": row.section_type,
            "usage_count": row.usage_count or 0,
        }
        for row in at_risk_q.all()
    ]

    # --- Components in cooldown ---
    cooldown_q = db.query(ComponentV2).filter(
        ComponentV2.cooldown_until.isnot(None),
        ComponentV2.cooldown_until > now,
    ).order_by(ComponentV2.cooldown_until.asc()).limit(20)
    if category:
        cooldown_q = cooldown_q.filter(ComponentV2.compatible_categories.any(category))

    cooldown_details = [
        {
            "id": str(c.id),
            "name": c.name,
            "section_type": c.section_type,
            "cooldown_until": c.cooldown_until.isoformat() if c.cooldown_until else None,
            "usage_count": c.usage_count or 0,
        }
        for c in cooldown_q.all()
    ]

    return {
        "total_components": total_components,
        "components_in_cooldown": cooldown_count,
        "components_available": total_components - cooldown_count,
        "components_by_section": components_by_section,
        "diversity_by_category": diversity_by_category,
        "at_risk_components": at_risk_components,
        "cooldown_details": cooldown_details,
        "category_filter": category,
    }


# ============ 5. LIST BLUEPRINTS ============

@router.get("/blueprints/")
async def list_blueprints(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all category blueprints."""
    blueprints = db.query(CategoryBlueprint).order_by(CategoryBlueprint.category_slug).all()

    return {
        "blueprints": [
            {
                "id": str(bp.id),
                "category_slug": bp.category_slug,
                "category_name": bp.category_name,
                "sections_required": bp.sections_required or [],
                "sections_optional": bp.sections_optional or [],
                "sections_forbidden": bp.sections_forbidden or [],
                "default_variant_cluster": bp.default_variant_cluster,
                "mood_required": bp.mood_required or [],
                "mood_forbidden": bp.mood_forbidden or [],
                "style_names": bp.style_names or [],
            }
            for bp in blueprints
        ],
        "total": len(blueprints),
    }


# ============ 6. CREATE/UPDATE BLUEPRINT (admin-only) ============

@router.post("/blueprints/")
async def upsert_blueprint(
    data: BlueprintCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create or update a category blueprint. Admin-only."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin possono gestire i blueprint.",
        )

    # Upsert: check if blueprint already exists
    existing = db.query(CategoryBlueprint).filter(
        CategoryBlueprint.category_slug == data.category_slug
    ).first()

    if existing:
        existing.category_name = data.category_name
        existing.sections_required = data.sections_required
        existing.sections_optional = data.sections_optional
        existing.sections_forbidden = data.sections_forbidden
        existing.default_variant_cluster = data.default_variant_cluster
        existing.mood_required = data.mood_required
        existing.mood_forbidden = data.mood_forbidden
        existing.style_names = data.style_names
        db.commit()

        return {
            "success": True,
            "action": "updated",
            "blueprint": {
                "id": str(existing.id),
                "category_slug": existing.category_slug,
                "category_name": existing.category_name,
            },
        }
    else:
        bp = CategoryBlueprint(
            category_slug=data.category_slug,
            category_name=data.category_name,
            sections_required=data.sections_required,
            sections_optional=data.sections_optional,
            sections_forbidden=data.sections_forbidden,
            default_variant_cluster=data.default_variant_cluster,
            mood_required=data.mood_required,
            mood_forbidden=data.mood_forbidden,
            style_names=data.style_names,
        )
        db.add(bp)
        db.commit()
        db.refresh(bp)

        return {
            "success": True,
            "action": "created",
            "blueprint": {
                "id": str(bp.id),
                "category_slug": bp.category_slug,
                "category_name": bp.category_name,
            },
        }

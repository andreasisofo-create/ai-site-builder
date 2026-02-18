"""Admin Panel API Routes"""

import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional, List
from jose import jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, PLAN_CONFIG
from app.models.site import Site
from app.models.site_version import SiteVersion
from app.models.service import ServiceCatalog, UserSubscription, PaymentHistory

router = APIRouter()

ALGORITHM = "HS256"


# ============= SCHEMAS =============

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    is_superuser: Optional[bool] = None
    generations_limit: Optional[int] = None
    refines_limit: Optional[int] = None
    pages_limit: Optional[int] = None


class SubscriptionUpdateRequest(BaseModel):
    status: Optional[str] = None
    monthly_amount_cents: Optional[int] = None
    notes: Optional[str] = None
    service_slug: Optional[str] = None


# ============= AUTH =============

def create_admin_token():
    """Create a JWT token for admin with role=admin claim."""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    data = {"sub": "admin", "role": "admin", "exp": expire}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_admin_token(token: str):
    """Verify admin JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            return None
        return payload
    except Exception:
        return None


async def require_admin(authorization: str = Header(...)):
    """Dependency to verify admin authentication."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.replace("Bearer ", "")
    payload = verify_admin_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired admin token")
    return payload


# ============= ROUTES =============

@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(data: AdminLoginRequest):
    """Admin login with separate credentials."""
    if data.username != settings.ADMIN_USERNAME or data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = create_admin_token()
    return {"access_token": token, "token_type": "bearer"}


@router.get("/stats")
async def admin_stats(
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    premium_users = db.query(func.count(User.id)).filter(User.is_premium == True).scalar() or 0

    total_sites = db.query(func.count(Site.id)).scalar() or 0
    published_sites = db.query(func.count(Site.id)).filter(Site.is_published == True).scalar() or 0
    ready_sites = db.query(func.count(Site.id)).filter(Site.status == "ready").scalar() or 0
    generating_sites = db.query(func.count(Site.id)).filter(Site.status == "generating").scalar() or 0

    # Plan distribution
    plan_dist = {}
    for plan_name in PLAN_CONFIG.keys():
        count = db.query(func.count(User.id)).filter(User.plan == plan_name).scalar() or 0
        plan_dist[plan_name] = count
    # Users with NULL plan count as free
    null_plan = db.query(func.count(User.id)).filter(User.plan == None).scalar() or 0
    plan_dist["free"] = plan_dist.get("free", 0) + null_plan

    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_users = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago
    ).scalar() or 0

    # Total generations used across all users
    total_generations = db.query(func.sum(User.generations_used)).scalar() or 0

    # AI cost tracking
    total_ai_cost = db.query(func.sum(Site.generation_cost)).scalar() or 0
    total_tokens_in = db.query(func.sum(Site.tokens_input)).scalar() or 0
    total_tokens_out = db.query(func.sum(Site.tokens_output)).scalar() or 0
    sites_with_cost = db.query(func.count(Site.id)).filter(Site.generation_cost > 0).scalar() or 0
    avg_cost = (total_ai_cost / sites_with_cost) if sites_with_cost > 0 else 0

    # ---- Subscription & Revenue stats ----
    active_subscriptions = db.query(func.count(UserSubscription.id)).filter(
        UserSubscription.status == "active"
    ).scalar() or 0

    # MRR: somma monthly_amount_cents di tutte le subscription attive (in centesimi)
    mrr_cents = db.query(func.sum(UserSubscription.monthly_amount_cents)).filter(
        UserSubscription.status == "active",
        UserSubscription.monthly_amount_cents > 0,
    ).scalar() or 0

    # Total revenue: somma di tutti i pagamenti completati (in centesimi)
    total_revenue_cents = db.query(func.sum(PaymentHistory.amount_cents)).filter(
        PaymentHistory.status == "completed"
    ).scalar() or 0

    # Subscription distribution by status
    sub_statuses = {}
    for st in ["pending_setup", "active", "paused", "cancelled", "expired"]:
        count = db.query(func.count(UserSubscription.id)).filter(
            UserSubscription.status == st
        ).scalar() or 0
        sub_statuses[st] = count

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "premium": premium_users,
            "recent_30d": recent_users,
        },
        "sites": {
            "total": total_sites,
            "published": published_sites,
            "ready": ready_sites,
            "generating": generating_sites,
        },
        "plans": plan_dist,
        "generations_total": total_generations,
        "ai_costs": {
            "total_usd": round(total_ai_cost, 4),
            "avg_per_site_usd": round(avg_cost, 4),
            "total_tokens_input": total_tokens_in,
            "total_tokens_output": total_tokens_out,
            "sites_tracked": sites_with_cost,
        },
        "revenue": {
            "mrr_cents": mrr_cents,
            "mrr_eur": round(mrr_cents / 100, 2),
            "total_revenue_cents": total_revenue_cents,
            "total_revenue_eur": round(total_revenue_cents / 100, 2),
            "active_subscriptions": active_subscriptions,
            "subscription_statuses": sub_statuses,
        },
    }


@router.get("/users")
async def admin_list_users(
    page: int = 1,
    per_page: int = 50,
    search: Optional[str] = None,
    plan: Optional[str] = None,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users with pagination and filters."""
    query = db.query(User)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_term)) | (User.full_name.ilike(search_term))
        )

    if plan:
        query = query.filter(User.plan == plan)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    # Preload subscription counts per user (avoid N+1 query)
    user_ids = [u.id for u in users]
    sub_counts = {}
    active_sub_counts = {}
    if user_ids:
        from sqlalchemy import case
        sub_stats = (
            db.query(
                UserSubscription.user_id,
                func.count(UserSubscription.id).label("total"),
                func.sum(case((UserSubscription.status == "active", 1), else_=0)).label("active"),
            )
            .filter(UserSubscription.user_id.in_(user_ids))
            .group_by(UserSubscription.user_id)
            .all()
        )
        for row in sub_stats:
            sub_counts[row.user_id] = row.total
            active_sub_counts[row.user_id] = row.active

    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "avatar_url": u.avatar_url,
                "plan": u.plan or "free",
                "is_premium": u.is_premium,
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "oauth_provider": u.oauth_provider,
                "generations_used": u.generations_used or 0,
                "generations_limit": u.generations_limit or 1,
                "refines_used": u.refines_used or 0,
                "refines_limit": u.refines_limit or 3,
                "pages_used": u.pages_used or 0,
                "pages_limit": u.pages_limit or 1,
                "email_verified": u.email_verified or False,
                "sites_count": len(u.sites) if u.sites else 0,
                "subscriptions_total": sub_counts.get(u.id, 0),
                "subscriptions_active": active_sub_counts.get(u.id, 0),
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "updated_at": u.updated_at.isoformat() if u.updated_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/users/{user_id}")
async def admin_get_user(
    user_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed user info including their sites."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sites = db.query(Site).filter(Site.owner_id == user_id).all()

    # Carica subscription dell'utente
    subscriptions = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id)
        .order_by(UserSubscription.created_at.desc())
        .all()
    )

    # Determina piano effettivo: se ha subscription attive, non e' "free"
    active_subs = [s for s in subscriptions if s.status == "active"]
    effective_plan = user.plan or "free"
    if active_subs and effective_plan == "free":
        effective_plan = "active_services"  # Ha servizi attivi anche se piano legacy e' free

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "plan": user.plan or "free",
        "effective_plan": effective_plan,
        "is_premium": user.is_premium,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "oauth_provider": user.oauth_provider,
        "oauth_id": user.oauth_id,
        "generations_used": user.generations_used or 0,
        "generations_limit": user.generations_limit or 1,
        "refines_used": user.refines_used or 0,
        "refines_limit": user.refines_limit or 3,
        "pages_used": user.pages_used or 0,
        "pages_limit": user.pages_limit or 1,
        "email_verified": user.email_verified or False,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "sites": [
            {
                "id": s.id,
                "name": s.name,
                "slug": s.slug,
                "status": s.status,
                "is_published": s.is_published,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sites
        ],
        "subscriptions": [
            {
                "id": sub.id,
                "service_slug": sub.service_slug,
                "status": sub.status,
                "setup_paid": sub.setup_paid or False,
                "monthly_amount_cents": sub.monthly_amount_cents or 0,
                "activated_by": sub.activated_by,
                "created_at": sub.created_at.isoformat() if sub.created_at else None,
            }
            for sub in subscriptions
        ],
    }


@router.put("/users/{user_id}")
async def admin_update_user(
    user_id: int,
    data: UserUpdateRequest,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user properties (plan, limits, active status, etc.)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)

    # If plan is being changed, also update limits
    if "plan" in update_data:
        plan_name = update_data["plan"]
        if plan_name in PLAN_CONFIG:
            config = PLAN_CONFIG[plan_name]
            if "generations_limit" not in update_data:
                user.generations_limit = config["generations_limit"]
            if "refines_limit" not in update_data:
                user.refines_limit = config["refines_limit"]
            if "pages_limit" not in update_data:
                user.pages_limit = config["pages_limit"]

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return {"message": "User updated", "user_id": user.id}


@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: int,
    data: dict,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reset a user's password (admin only)."""
    from app.core.security import get_password_hash

    new_password = data.get("password")
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": f"Password reset for {user.email}", "user_id": user.id}


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user and all their related data."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete in FK-safe order: payments -> subscriptions -> site versions -> sites -> user
    db.query(PaymentHistory).filter(PaymentHistory.user_id == user_id).delete(synchronize_session=False)
    db.query(UserSubscription).filter(UserSubscription.user_id == user_id).delete(synchronize_session=False)

    user_site_ids = [s.id for s in db.query(Site.id).filter(Site.owner_id == user_id).all()]
    if user_site_ids:
        db.query(SiteVersion).filter(SiteVersion.site_id.in_(user_site_ids)).delete(synchronize_session=False)
    db.query(Site).filter(Site.owner_id == user_id).delete(synchronize_session=False)

    db.delete(user)
    db.commit()

    return {"message": "User and their sites deleted"}


@router.get("/sites")
async def admin_list_sites(
    page: int = 1,
    per_page: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all sites with owner info."""
    query = db.query(Site)

    if status:
        query = query.filter(Site.status == status)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Site.name.ilike(search_term)) | (Site.slug.ilike(search_term))
        )

    total = query.count()
    sites = query.order_by(Site.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "sites": [
            {
                "id": s.id,
                "name": s.name,
                "slug": s.slug,
                "description": (s.description[:100] + "...") if s.description and len(s.description) > 100 else s.description,
                "status": s.status,
                "is_published": s.is_published,
                "template": s.template,
                "has_html": bool(s.html_content),
                "owner_id": s.owner_id,
                "owner_email": s.owner.email if s.owner else None,
                "owner_name": s.owner.full_name if s.owner else None,
                "generation_cost": s.generation_cost,
                "tokens_input": s.tokens_input,
                "tokens_output": s.tokens_output,
                "ai_model": s.ai_model,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in sites
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/sites/{site_id}")
async def admin_get_site(
    site_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get full site details including HTML content."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    return {
        "id": site.id,
        "name": site.name,
        "slug": site.slug,
        "description": site.description,
        "status": site.status,
        "is_published": site.is_published,
        "template": site.template,
        "html_content": site.html_content,
        "owner_id": site.owner_id,
        "owner_email": site.owner.email if site.owner else None,
        "owner_name": site.owner.full_name if site.owner else None,
        "domain": site.domain,
        "generation_cost": site.generation_cost,
        "tokens_input": site.tokens_input,
        "tokens_output": site.tokens_output,
        "ai_model": site.ai_model,
        "created_at": site.created_at.isoformat() if site.created_at else None,
        "updated_at": site.updated_at.isoformat() if site.updated_at else None,
    }


@router.delete("/sites/{site_id}")
async def admin_delete_site(
    site_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a site and its versions."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Delete versions first (no cascade on FK)
    db.query(SiteVersion).filter(SiteVersion.site_id == site_id).delete()
    db.delete(site)
    db.commit()

    return {"message": "Site deleted"}


# ============= SUBSCRIPTIONS =============

@router.get("/subscriptions")
async def admin_list_subscriptions(
    page: int = 1,
    per_page: int = 50,
    status: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all subscriptions with user info and service details.

    Filterable by status, category (from ServiceCatalog), and user_id.
    """
    query = db.query(UserSubscription)

    # Filter by status
    if status:
        query = query.filter(UserSubscription.status == status)

    # Filter by user_id
    if user_id:
        query = query.filter(UserSubscription.user_id == user_id)

    # Filter by category requires a join with ServiceCatalog
    if category:
        # Get slugs for services in this category
        category_slugs = [
            s.slug for s in
            db.query(ServiceCatalog.slug).filter(ServiceCatalog.category == category).all()
        ]
        if category_slugs:
            query = query.filter(UserSubscription.service_slug.in_(category_slugs))
        else:
            # No services in this category, return empty
            return {
                "subscriptions": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "pages": 0,
            }

    total = query.count()
    subscriptions = (
        query.order_by(UserSubscription.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    result = []
    for sub in subscriptions:
        # Load user info
        user = db.query(User).filter(User.id == sub.user_id).first()
        # Load service info
        service = db.query(ServiceCatalog).filter(ServiceCatalog.slug == sub.service_slug).first()

        result.append({
            "id": sub.id,
            "user_id": sub.user_id,
            "user_email": user.email if user else None,
            "user_full_name": user.full_name if user else None,
            "service_slug": sub.service_slug,
            "service_name": service.name if service else sub.service_slug,
            "service_category": service.category if service else None,
            "status": sub.status,
            "setup_paid": sub.setup_paid or False,
            "setup_order_id": sub.setup_order_id,
            "monthly_amount_cents": sub.monthly_amount_cents or 0,
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "next_billing_date": sub.next_billing_date.isoformat() if sub.next_billing_date else None,
            "activated_by": sub.activated_by,
            "notes": sub.notes,
            "created_at": sub.created_at.isoformat() if sub.created_at else None,
            "updated_at": sub.updated_at.isoformat() if sub.updated_at else None,
            "cancelled_at": sub.cancelled_at.isoformat() if sub.cancelled_at else None,
        })

    return {
        "subscriptions": result,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.put("/subscriptions/{subscription_id}")
async def admin_update_subscription(
    subscription_id: int,
    data: SubscriptionUpdateRequest,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a subscription (status, monthly amount, notes).

    Admin can force-activate a subscription by setting status="active".
    """
    subscription = db.query(UserSubscription).filter(
        UserSubscription.id == subscription_id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    update_data = data.model_dump(exclude_unset=True)
    now = datetime.now(timezone.utc)

    # Handle status changes
    new_status = update_data.get("status")
    if new_status:
        # Force activate: set period dates and activated_by
        if new_status == "active" and subscription.status != "active":
            subscription.status = "active"
            subscription.activated_by = "admin"
            subscription.setup_paid = True
            if not subscription.current_period_start:
                subscription.current_period_start = now
            if not subscription.current_period_end:
                subscription.current_period_end = now + timedelta(days=30)
            # Set next billing if there is a monthly amount
            if (subscription.monthly_amount_cents or 0) > 0 and not subscription.next_billing_date:
                subscription.next_billing_date = now + timedelta(days=30)

            # Apply service limits to user
            service = db.query(ServiceCatalog).filter(
                ServiceCatalog.slug == subscription.service_slug
            ).first()
            if service:
                user = db.query(User).filter(User.id == subscription.user_id).first()
                if user:
                    from app.api.routes.payments import _apply_service_limits
                    _apply_service_limits(user, service, db, commit=False)

        elif new_status == "cancelled":
            subscription.status = "cancelled"
            subscription.cancelled_at = now
        else:
            subscription.status = new_status

    # Handle service_slug change
    if "service_slug" in update_data and update_data["service_slug"]:
        new_slug = update_data["service_slug"]
        new_service = db.query(ServiceCatalog).filter(ServiceCatalog.slug == new_slug).first()
        if not new_service:
            raise HTTPException(status_code=400, detail=f"Service '{new_slug}' not found in catalog")
        old_slug = subscription.service_slug
        subscription.service_slug = new_slug
        subscription.monthly_amount_cents = new_service.monthly_price_cents or 0
        # Append change note
        change_note = f"[Admin] Service changed from '{old_slug}' to '{new_slug}'"
        if subscription.notes:
            subscription.notes = f"{subscription.notes}\n{change_note}"
        else:
            subscription.notes = change_note

    # Update other fields
    if "monthly_amount_cents" in update_data and "service_slug" not in update_data:
        # Only apply manual amount if not changing service (service change sets amount automatically)
        subscription.monthly_amount_cents = update_data["monthly_amount_cents"]
    if "notes" in update_data and "service_slug" not in update_data:
        # Only apply manual notes if not changing service (service change appends its own note)
        subscription.notes = update_data["notes"]

    db.commit()
    db.refresh(subscription)

    return {
        "message": "Subscription updated",
        "subscription_id": subscription.id,
        "status": subscription.status,
        "service_slug": subscription.service_slug,
        "monthly_amount_cents": subscription.monthly_amount_cents,
        "activated_by": subscription.activated_by,
    }


@router.delete("/subscriptions/{subscription_id}")
async def admin_delete_subscription(
    subscription_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a subscription and its related payment history."""
    subscription = db.query(UserSubscription).filter(
        UserSubscription.id == subscription_id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Delete related payment history first (FK-safe order)
    db.query(PaymentHistory).filter(
        PaymentHistory.subscription_id == subscription_id
    ).delete(synchronize_session=False)

    db.delete(subscription)
    db.commit()

    return {"message": "Subscription deleted"}


@router.get("/services-catalog")
async def admin_list_services_catalog(
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return all services from the catalog for admin dropdown."""
    services = (
        db.query(ServiceCatalog)
        .filter(ServiceCatalog.is_active == True)
        .order_by(ServiceCatalog.display_order, ServiceCatalog.name)
        .all()
    )
    return {
        "services": [
            {
                "slug": s.slug,
                "name": s.name,
                "category": s.category,
                "monthly_price_cents": s.monthly_price_cents or 0,
                "setup_price_cents": s.setup_price_cents or 0,
            }
            for s in services
        ]
    }

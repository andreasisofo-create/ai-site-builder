"""Admin Panel API Routes"""

from datetime import datetime, timedelta
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

router = APIRouter()

# Admin credentials (hardcoded - separate from user auth)
ADMIN_USERNAME = "E-quipe"
ADMIN_PASSWORD = "E-quipe!"
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


# ============= AUTH =============

def create_admin_token():
    """Create a JWT token for admin with role=admin claim."""
    expire = datetime.utcnow() + timedelta(hours=24)
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
    if data.username != ADMIN_USERNAME or data.password != ADMIN_PASSWORD:
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
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_users = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago
    ).scalar() or 0

    # Total generations used across all users
    total_generations = db.query(func.sum(User.generations_used)).scalar() or 0

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

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "plan": user.plan or "free",
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

    update_data = data.dict(exclude_unset=True)

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


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user and all their sites."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user's sites first
    db.query(Site).filter(Site.owner_id == user_id).delete()
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
        "created_at": site.created_at.isoformat() if site.created_at else None,
        "updated_at": site.updated_at.isoformat() if site.updated_at else None,
    }


@router.delete("/sites/{site_id}")
async def admin_delete_site(
    site_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a site."""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    db.delete(site)
    db.commit()

    return {"message": "Site deleted"}

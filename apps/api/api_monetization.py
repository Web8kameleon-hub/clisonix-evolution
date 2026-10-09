#!/usr/bin/env python3
"""
CLISONIX API MONETIZATION SYSTEM
Tier-based API access with rate limiting and usage tracking.

Plans:
  Free: 1,000 requests/day, public forums only
  Pro: 10,000 requests/day, full API access, €29/month
  Enterprise: 50,000 requests/day, analytics, support, custom
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APIMonetization")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./api_monetization.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# API Plan Limits
PLAN_LIMITS = {
    "free": {
        "name": "Free",
        "requests_per_day": 1_000,
        "requests_per_month": 20_000,
        "price_monthly": 0,
        "features": ["Public API", "Basic endpoints", "Community support"]
    },
    "pro": {
        "name": "Pro",
        "requests_per_day": 10_000,
        "requests_per_month": 200_000,
        "price_monthly": 2900,  # €29.00 in cents
        "features": ["Full API access", "Priority support", "Usage analytics", "No rate limiting"]
    },
    "enterprise": {
        "name": "Enterprise",
        "requests_per_day": 50_000,
        "requests_per_month": 1_000_000,
        "price_monthly": 9900,  # €99.00 in cents (custom)
        "features": ["Unlimited access", "Dedicated support", "SLA", "Custom integration"]
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class APIKey(Base):
    """API keys for tier-based access"""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    key_hash = Column(String, unique=True, index=True, nullable=False)  # Hashed key
    key_prefix = Column(String, index=True, nullable=False)  # First 8 chars for display
    plan = Column(String, default="free")  # free, pro, enterprise
    name = Column(String, nullable=True)  # User-friendly name
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

class APIUsage(Base):
    """Track API usage per key per day"""
    __tablename__ = "api_usage"

    id = Column(String, primary_key=True, index=True)
    api_key_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    date = Column(String, index=True, nullable=False)  # YYYY-MM-DD
    requests = Column(Integer, default=0)
    method = Column(String, nullable=True)  # GET, POST, etc
    endpoint = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class APISubscription(Base):
    """Track active subscriptions"""
    __tablename__ = "api_subscriptions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    plan = Column(String, default="free")  # free, pro, enterprise
    stripe_subscription_id = Column(String, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    renews_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(bind=engine)

# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class APIKeyCreate(BaseModel):
    name: Optional[str] = None
    plan: str = "free"

class APIKeyResponse(BaseModel):
    id: str
    key_prefix: str
    plan: str
    name: Optional[str]
    created_at: str
    is_active: bool

class APIUsageResponse(BaseModel):
    date: str
    requests: int
    limit: int
    percentage_used: float

class APIPlanInfo(BaseModel):
    name: str
    requests_per_day: int
    requests_per_month: int
    price_monthly: int  # cents
    features: List[str]

class APIKeyValidation(BaseModel):
    valid: bool
    plan: str
    user_id: str
    requests_today: int
    daily_limit: int
    rate_limited: bool

# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_api_key(key: str) -> str:
    """Hash API key using SHA256"""
    return hashlib.sha256(key.encode()).hexdigest()

def generate_api_key(user_id: str, plan: str) -> str:
    """Generate a new API key"""
    # Format: clx_[plan]_[random_hash]
    random_part = hashlib.sha256(f"{user_id}_{datetime.now()}".encode()).hexdigest()[:32]
    return f"clx_{plan}_{random_part}"

def validate_api_key(key: str, db: Session) -> Tuple[bool, Optional[APIKey], str]:
    """
    Validate API key and check rate limiting.
    Returns: (is_valid, api_key_obj, error_message)
    """
    if not key or not key.startswith("clx_"):
        return False, None, "Invalid API key format"

    key_hash = hash_api_key(key)
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

    if not api_key:
        return False, None, "API key not found"

    if not api_key.is_active:
        return False, None, "API key is revoked"

    if api_key.revoked_at:
        return False, None, "API key has been revoked"

    # Check rate limit
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    usage = db.query(APIUsage).filter(
        APIUsage.api_key_id == api_key.id,
        APIUsage.date == today
    ).first()

    daily_limit = PLAN_LIMITS[api_key.plan]["requests_per_day"]
    requests_today = usage.requests if usage else 0

    if requests_today >= daily_limit:
        return False, api_key, "Rate limit exceeded for today"

    return True, api_key, ""

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v1/api-access", tags=["API Monetization"])

# ═══════════════════════════════════════════════════════════════════════════════
# USER ENDPOINTS: API KEY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/plans")
async def get_plans() -> Dict[str, APIPlanInfo]:
    """Get available API plans"""
    return {
        tier: APIPlanInfo(
            name=info["name"],
            requests_per_day=info["requests_per_day"],
            requests_per_month=info["requests_per_month"],
            price_monthly=info["price_monthly"],
            features=info["features"]
        )
        for tier, info in PLAN_LIMITS.items()
    }

@router.post("/keys/create")
async def create_api_key(
    req: APIKeyCreate,
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
) -> Dict:
    """Create new API key for user"""
    try:
        # Generate key
        new_key = generate_api_key(user_id, req.plan)
        key_hash = hash_api_key(new_key)
        key_prefix = new_key[:12]  # Display: clx_pro_xxxxx

        # Save to DB
        api_key = APIKey(
            id=f"key_{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:12]}",
            user_id=user_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            plan=req.plan,
            name=req.name
        )
        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        logger.info(f"✅ API key created for user {user_id} ({req.plan})")

        return {
            "status": "created",
            "api_key": new_key,  # Only shown once!
            "key_prefix": key_prefix,
            "plan": req.plan,
            "message": "Save this key securely. You won't see it again."
        }
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/keys")
async def list_api_keys(
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
) -> List[APIKeyResponse]:
    """List all API keys for user"""
    try:
        keys = db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.revoked_at == None
        ).all()

        return [
            APIKeyResponse(
                id=k.id,
                key_prefix=k.key_prefix,
                plan=k.plan,
                name=k.name,
                created_at=k.created_at.isoformat(),
                is_active=k.is_active
            )
            for k in keys
        ]
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/keys/{key_id}/revoke")
async def revoke_api_key(
    key_id: str,
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
) -> Dict:
    """Revoke an API key"""
    try:
        api_key = db.query(APIKey).filter(
            APIKey.id == key_id,
            APIKey.user_id == user_id
        ).first()

        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        api_key.is_active = False
        api_key.revoked_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"🚫 API key revoked: {key_id}")

        return {"status": "revoked"}
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/{key_id}")
async def get_key_usage(
    key_id: str,
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get usage stats for an API key"""
    try:
        api_key = db.query(APIKey).filter(
            APIKey.id == key_id,
            APIKey.user_id == user_id
        ).first()

        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Today's usage
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_usage = db.query(APIUsage).filter(
            APIUsage.api_key_id == key_id,
            APIUsage.date == today
        ).first()

        # This month's usage
        first_day = datetime.now(timezone.utc).replace(day=1).strftime("%Y-%m-%d")
        month_usage = db.query(func.sum(APIUsage.requests)).filter(
            APIUsage.api_key_id == key_id,
            APIUsage.date >= first_day
        ).scalar() or 0

        daily_limit = PLAN_LIMITS[api_key.plan]["requests_per_day"]
        monthly_limit = PLAN_LIMITS[api_key.plan]["requests_per_month"]

        today_requests = today_usage.requests if today_usage else 0

        return {
            "plan": api_key.plan,
            "today": {
                "requests": today_requests,
                "limit": daily_limit,
                "percentage": (today_requests / daily_limit * 100) if daily_limit > 0 else 0
            },
            "month": {
                "requests": month_usage,
                "limit": monthly_limit,
                "percentage": (month_usage / monthly_limit * 100) if monthly_limit > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Error fetching usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/validate")
async def validate_key(
    api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> APIKeyValidation:
    """Validate an API key (used by middleware)"""
    is_valid, key_obj, error = validate_api_key(api_key, db)

    if key_obj:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        usage = db.query(APIUsage).filter(
            APIUsage.api_key_id == key_obj.id,
            APIUsage.date == today
        ).first()
        requests_today = usage.requests if usage else 0
        daily_limit = PLAN_LIMITS[key_obj.plan]["requests_per_day"]

        return APIKeyValidation(
            valid=is_valid,
            plan=key_obj.plan,
            user_id=key_obj.user_id,
            requests_today=requests_today,
            daily_limit=daily_limit,
            rate_limited=requests_today >= daily_limit
        )

    raise HTTPException(status_code=401, detail=error)

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/admin/users/{user_id}/summary")
async def get_user_monetization_summary(
    user_id: str,
    admin_token: str = Header(..., alias="X-Admin-Token"),
    db: Session = Depends(get_db)
) -> Dict:
    """Get monetization summary for a user"""
    # TODO: Verify admin_token
    try:
        subscription = db.query(APISubscription).filter(
            APISubscription.user_id == user_id
        ).first()

        keys = db.query(APIKey).filter(
            APIKey.user_id == user_id,
            APIKey.revoked_at == None
        ).all()

        total_usage = db.query(func.sum(APIUsage.requests)).filter(
            APIUsage.user_id == user_id
        ).scalar() or 0

        return {
            "user_id": user_id,
            "subscription": {
                "plan": subscription.plan if subscription else "free",
                "is_active": subscription.is_active if subscription else False,
                "renews_at": subscription.renews_at.isoformat() if subscription and subscription.renews_at else None
            },
            "api_keys_active": len(keys),
            "total_api_requests": total_usage
        }
    except Exception as e:
        logger.error(f"Error fetching user summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE-COMPATIBLE TRACKING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def track_api_usage(
    api_key_id: str,
    user_id: str,
    endpoint: str,
    method: str,
    status_code: int,
    db: Session
) -> None:
    """Track API usage (called from middleware)"""
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Get or create today's usage
        usage = db.query(APIUsage).filter(
            APIUsage.api_key_id == api_key_id,
            APIUsage.date == today,
            APIUsage.endpoint == endpoint,
            APIUsage.method == method
        ).first()

        if usage:
            usage.requests += 1
        else:
            usage = APIUsage(
                id=f"use_{hashlib.sha256(f'{api_key_id}_{today}'.encode()).hexdigest()[:12]}",
                api_key_id=api_key_id,
                user_id=user_id,
                date=today,
                endpoint=endpoint,
                method=method,
                requests=1,
                status_code=status_code
            )
            db.add(usage)

        db.commit()
    except Exception as e:
        logger.error(f"Error tracking usage: {e}")

if __name__ == "__main__":
    logger.info("✅ API Monetization module loaded")

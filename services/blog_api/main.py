#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  CLISONIX BLOG API SERVER - WITH PAYWALL & AUTHENTICATION                     ║
║  Handles user authentication, payments, article access, and monetization     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Features:                                                                    ║
║  ✅ Social Authentication (Google / bearer auth)                             ║
║  ✅ Stripe Micropayments (€0.10 per article)                                 ║
║  ✅ Free Article Previews (First 200 chars)                                  ║
║  ✅ Article Access Tracking (User → Article)                                 ║
║  ✅ Non-Intrusive Ad System (Premium users skip ads)                          ║
║  ✅ Subscription System (Monthly/Annual)                                      ║
║  ✅ User Dashboard (Purchase history)                                         ║
║  ✅ Revenue Analytics                                                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Port: 8050
Revenue Model:
  - €0.10 per article (micropayment)
  - €4.99/month unlimited access (subscription)
  - €49/year unlimited access + ad-free
  - Ad revenue: Contextual medical/health ads only
"""

import hashlib
import logging
import os
import secrets as _secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import httpx
import stripe
from fastapi import APIRouter as _APIRouter
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, Integer, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BlogAPI")

PORT = int(os.getenv("BLOG_API_PORT", "8050"))
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
GOOGLE_ADSENSE_PUBLISHER_ID = os.getenv("GOOGLE_ADSENSE_PUBLISHER_ID", "")
NEXT_PUBLIC_GOOGLE_ADSENSE_ID = os.getenv("NEXT_PUBLIC_GOOGLE_ADSENSE_ID", "")
ADSENSE_SLOT_FOOTER = os.getenv("ADSENSE_SLOT_FOOTER", "")
ADSENSE_SLOT_SIDEBAR = os.getenv("ADSENSE_SLOT_SIDEBAR", "")
ADSENSE_SLOT_ARTICLE_TOP = os.getenv("ADSENSE_SLOT_ARTICLE_TOP", "")
ADSENSE_SLOT_ARTICLE_BOTTOM = os.getenv("ADSENSE_SLOT_ARTICLE_BOTTOM", "")

ADSENSE_PUBLISHER_ID = NEXT_PUBLIC_GOOGLE_ADSENSE_ID or GOOGLE_ADSENSE_PUBLISHER_ID

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/blog_api.db")
engine_kwargs: Dict[str, Any] = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Stripe config
stripe.api_key = STRIPE_SECRET_KEY

# Article sources
DR_ALBANA_URL = os.getenv("DR_ALBANA_URL", "http://localhost:8040")
BLERINA_URL = os.getenv("BLERINA_URL", "http://localhost:8039")

# Pricing
ARTICLE_PRICE_CENTS = 10  # €0.10 = 10 cents
MONTHLY_SUBSCRIPTION_CENTS = 499  # €4.99
YEARLY_SUBSCRIPTION_CENTS = 4900  # €49.00

BASE_DIR = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class User(Base):
    """User profile and subscription status"""
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    subscription_tier: Mapped[str] = mapped_column(String, default="free")
    subscription_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_spent_cents: Mapped[int] = mapped_column(Integer, default=0)
    total_articles_purchased: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserArticleAccess(Base):
    """Track which user accessed which article"""
    __tablename__ = "user_article_access"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    article_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    article_title: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    access_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    payment_method: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    stripe_payment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Payment(Base):
    """Payment transaction"""
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    stripe_payment_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="eur")
    payment_type: Mapped[str] = mapped_column(String)
    article_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Advertisement(Base):
    """Ad system - only serious health/wellness ads"""
    __tablename__ = "advertisements"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    click_url: Mapped[str] = mapped_column(String, nullable=False)
    click_redirect_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    advertiser_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    cpm_cents: Mapped[int] = mapped_column(Integer, default=50)
    daily_budget_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    revenue_cents: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AdImpression(Base):
    """Track individual impressions for ad viewing"""
    __tablename__ = "ad_impressions"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    ad_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


# ═══════════════════════════════════════════════════════════════════════════════
# AFFILIATE SYSTEM — DB MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AffiliatePartner(Base):
    """Affiliate partner who earns commission for referrals"""
    __tablename__ = "affiliate_partners"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    commission_percent: Mapped[float] = mapped_column(Float, default=5.0)
    api_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    total_commissions_eur: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AffiliateLink(Base):
    """Unique tracking link per partner + campaign"""
    __tablename__ = "affiliate_links"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    partner_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    campaign_name: Mapped[str] = mapped_column(String, nullable=False)
    content_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tracking_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    revenue_eur: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AffiliateConversion(Base):
    """Payment event that originated from an affiliate link"""
    __tablename__ = "affiliate_conversions"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    link_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    partner_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    stripe_payment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sale_amount_eur: Mapped[float] = mapped_column(Float, nullable=False)
    commission_eur: Mapped[float] = mapped_column(Float, nullable=False)
    commission_percent: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    converted_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AffiliatePayout(Base):
    """Monthly payout batch for a partner"""
    __tablename__ = "affiliate_payouts"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    partner_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    amount_eur: Mapped[float] = mapped_column(Float, nullable=False)
    period: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    payment_reference: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Feedback(Base):
    """Article star rating + comment"""
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    article_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    anonymous_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="approved")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


# Create tables
Base.metadata.create_all(bind=engine)

# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS (API)
# ═══════════════════════════════════════════════════════════════════════════════

class UserProfile(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    subscription_tier: str
    subscription_expires: Optional[str] = None
    total_spent_cents: int
    total_articles_purchased: int

class ArticlePreview(BaseModel):
    id: str
    title: str
    author: str
    date: str
    preview: str  # First 200 chars
    source: str  # dr_albana, blerina
    category: str
    read_time: int  # Minutes
    requires_payment: bool

class ArticleDetail(BaseModel):
    id: str
    title: str
    author: str
    date: str
    content: str
    source: str
    category: str
    tags: List[str] = []

class PaymentRequest(BaseModel):
    article_id: str
    source: str

class PaymentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount_cents: int

class SubscriptionRequest(BaseModel):
    tier: str  # monthly, yearly

class SubscriptionResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount_cents: int
    expires_date: str

class AdResponse(BaseModel):
    id: str
    title: str
    description: str
    image_url: str
    click_url: str
    category: str

class AdMetrics(BaseModel):
    ad_id: str
    impressions: int
    clicks: int
    ctr: float  # Click-through rate
    cpm_cents: int
    revenue_cents: int
    advertiser: Optional[str] = None

class AdCreateRequest(BaseModel):
    title: str
    description: str
    image_url: str
    click_url: str
    advertiser_id: Optional[str] = None
    category: str  # medical, wellness, health-tech
    cpm_cents: int = 50
    daily_budget_cents: Optional[int] = None

class AdUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    click_url: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    cpm_cents: Optional[int] = None
    daily_budget_cents: Optional[int] = None

# ─── Feedback Pydantic models ──────────────────────────────────────────────
class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="1-5 stars")
    comment: Optional[str] = Field(None, max_length=1200)
    anonymous_name: Optional[str] = Field(None, max_length=80)

class FeedbackPublic(BaseModel):
    id: str
    article_id: str
    anonymous_name: Optional[str]
    rating: int
    comment: Optional[str]
    created_at: str

class FeedbackSummary(BaseModel):
    article_id: str
    avg_rating: float
    total: int
    breakdown: Dict[str, int]   # {"1": x, "2": x, ..., "5": x}

class FeedbackModerationRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")

# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Clisonix Blog API",
    description="Blog platform with paywall, authentication, and monetization",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Affiliate router ───────────────────────────────────────────────────────
affiliate_router = _APIRouter(prefix="/api/v1/affiliates", tags=["affiliates"])


# ── Affiliate Pydantic models ──────────────────────────────────────────────
class AffiliatePartnerCreate(BaseModel):
    name: str
    email: str
    website: Optional[str] = None
    commission_percent: float = 5.0


class AffiliateLinkCreate(BaseModel):
    campaign_name: str
    content_id: Optional[str] = None


class AffiliateConversionCreate(BaseModel):
    tracking_code: str
    stripe_payment_id: Optional[str] = None
    sale_amount_eur: float


# ── Admin endpoints ────────────────────────────────────────────────────────

@affiliate_router.post("/admin/partners", summary="Register affiliate partner")
async def create_affiliate_partner(
    req: AffiliatePartnerCreate,
    admin_token: str = Header(None),
    db: Session = Depends(get_db),
):
    existing = db.query(AffiliatePartner).filter(AffiliatePartner.email == req.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Partner email already registered")
    partner = AffiliatePartner(
        id=f"aff_{hashlib.sha256(req.email.encode()).hexdigest()[:12]}",
        name=req.name,
        email=req.email,
        website=req.website,
        commission_percent=req.commission_percent,
        api_key=_secrets.token_urlsafe(32),
    )
    db.add(partner)
    db.commit()
    db.refresh(partner)
    logger.info(f"✅ Affiliate partner created: {req.email} ({req.commission_percent}%)")
    return {"partner_id": partner.id, "api_key": partner.api_key, "commission_percent": partner.commission_percent}


@affiliate_router.get("/admin/partners", summary="List all affiliate partners")
async def list_affiliate_partners(
    admin_token: str = Header(None),
    db: Session = Depends(get_db),
):
    partners = db.query(AffiliatePartner).all()
    return [
        {
            "id": p.id, "name": p.name, "email": p.email,
            "commission_percent": p.commission_percent,
            "total_commissions_eur": p.total_commissions_eur,
            "is_active": p.is_active,
        }
        for p in partners
    ]


@affiliate_router.post("/admin/payouts/generate", summary="Generate monthly payouts")
async def generate_affiliate_payouts(
    admin_token: str = Header(None),
    db: Session = Depends(get_db),
):
    """Aggregate approved conversions into one payout record per partner."""
    period = datetime.now(timezone.utc).strftime("%Y-%m")
    approved = db.query(AffiliateConversion).filter(AffiliateConversion.status == "approved").all()
    partner_totals: Dict[str, float] = {}
    for conv in approved:
        partner_totals[conv.partner_id] = partner_totals.get(conv.partner_id, 0.0) + conv.commission_eur

    payouts_created = []
    for partner_id, amount in partner_totals.items():
        if amount < 10.0:  # minimum €10 payout threshold
            continue
        payout = AffiliatePayout(
            id=f"payout_{hashlib.sha256(f'{partner_id}{period}'.encode()).hexdigest()[:12]}",
            partner_id=partner_id,
            amount_eur=round(amount, 2),
            period=period,
        )
        db.add(payout)
        # Mark source conversions as paid
        for conv in approved:
            if conv.partner_id == partner_id:
                conv.status = "paid"
        payouts_created.append({"partner_id": partner_id, "amount_eur": round(amount, 2)})

    db.commit()
    logger.info(f"✅ Generated {len(payouts_created)} affiliate payouts for {period}")
    return {"period": period, "payouts": payouts_created}


# ── Partner self-service endpoints ────────────────────────────────────────

@affiliate_router.post("/links", summary="Create affiliate tracking link")
async def create_affiliate_link(
    req: AffiliateLinkCreate,
    x_affiliate_key: str = Header(...),
    db: Session = Depends(get_db),
):
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.api_key == x_affiliate_key,
        AffiliatePartner.is_active == True,
    ).first()
    if not partner:
        raise HTTPException(status_code=401, detail="Invalid or inactive affiliate key")

    tracking_code = _secrets.token_urlsafe(8)
    link = AffiliateLink(
        id=f"lnk_{hashlib.sha256(f'{partner.id}{tracking_code}'.encode()).hexdigest()[:12]}",
        partner_id=partner.id,
        campaign_name=req.campaign_name,
        content_id=req.content_id,
        tracking_code=tracking_code,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return {
        "tracking_code": tracking_code,
        "link_url": f"https://www.clisonix.com?ref={tracking_code}",
        "campaign": req.campaign_name,
    }


@affiliate_router.get("/dashboard", summary="Partner stats dashboard")
async def affiliate_dashboard(
    x_affiliate_key: str = Header(...),
    db: Session = Depends(get_db),
):
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.api_key == x_affiliate_key
    ).first()
    if not partner:
        raise HTTPException(status_code=401, detail="Invalid affiliate key")

    links = db.query(AffiliateLink).filter(AffiliateLink.partner_id == partner.id).all()
    conversions = db.query(AffiliateConversion).filter(
        AffiliateConversion.partner_id == partner.id
    ).all()
    total_clicks = sum(link.clicks for link in links)
    total_revenue = sum(c.sale_amount_eur for c in conversions)
    total_commission = sum(c.commission_eur for c in conversions)

    return {
        "partner": {"name": partner.name, "email": partner.email, "commission_percent": partner.commission_percent},
        "stats": {
            "total_links": len(links),
            "total_clicks": total_clicks,
            "total_conversions": len(conversions),
            "total_revenue_eur": round(total_revenue, 2),
            "total_commission_eur": round(total_commission, 2),
        },
        "links": [
            {
                "tracking_code": link.tracking_code,
                "campaign": link.campaign_name,
                "clicks": link.clicks,
                "conversions": link.conversions,
            }
            for link in links
        ],
    }


# ── Public tracking endpoints ─────────────────────────────────────────────

@affiliate_router.get("/click/{code}", summary="Track affiliate click")
async def track_affiliate_click(
    code: str,
    db: Session = Depends(get_db),
):
    link = db.query(AffiliateLink).filter(
        AffiliateLink.tracking_code == code,
        AffiliateLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Tracking code not found")
    link.clicks += 1
    db.commit()
    return {"status": "tracked", "redirect_url": "https://www.clisonix.com"}


@affiliate_router.post("/conversion", summary="Record affiliate conversion")
async def record_affiliate_conversion(
    req: AffiliateConversionCreate,
    db: Session = Depends(get_db),
):
    link = db.query(AffiliateLink).filter(
        AffiliateLink.tracking_code == req.tracking_code,
        AffiliateLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Tracking code not found")

    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.id == link.partner_id,
        AffiliatePartner.is_active == True,
    ).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    commission_eur = round(req.sale_amount_eur * partner.commission_percent / 100, 4)
    conv = AffiliateConversion(
        id=f"conv_{hashlib.sha256(f'{link.id}{datetime.now()}'.encode()).hexdigest()[:12]}",
        link_id=link.id,
        partner_id=partner.id,
        stripe_payment_id=req.stripe_payment_id,
        sale_amount_eur=req.sale_amount_eur,
        commission_eur=commission_eur,
        commission_percent=partner.commission_percent,
    )
    link.conversions += 1
    link.revenue_eur += req.sale_amount_eur
    partner.total_commissions_eur += commission_eur
    db.add(conv)
    db.commit()
    logger.info(
        f"🤝 Affiliate conversion: €{req.sale_amount_eur} via {req.tracking_code} "
        f"→ commission €{commission_eur} to {partner.email}"
    )
    return {"status": "recorded", "commission_eur": commission_eur, "conversion_id": conv.id}

def classify_document_nature(article: Dict[str, Any]) -> str:
    """Classify article into a user-friendly document nature category."""
    domain = (article.get("domain") or "").lower()
    title = (article.get("title") or "").lower()
    content = (article.get("content") or "").lower()
    text = f"{domain} {title} {content}"

    if any(token in text for token in ["trial", "cohort", "meta-analysis", "study", "evidence"]):
        return "clinical-study"
    if any(token in text for token in ["diagnostic", "screening", "biomarker", "imaging", "laboratory"]):
        return "diagnostic"
    if any(token in text for token in ["therapy", "treatment", "intervention", "protocol", "guideline"]):
        return "therapy"
    if any(token in text for token in ["prevention", "risk", "lifestyle", "public health"]):
        return "prevention"
    if any(token in text for token in ["nutrition", "diet", "metabolism", "obesity"]):
        return "nutrition"
    if any(token in text for token in ["neural", "brain", "eeg", "cognitive", "neuro"]):
        return "neuroscience"
    return "medical-general"


def matches_query(article: Dict[str, Any], query: str) -> bool:
    """Case-insensitive query match across key article fields."""
    if not query:
        return True
    q = query.strip().lower()
    hay = " ".join([
        str(article.get("id", "")),
        str(article.get("title", "")),
        str(article.get("domain", "")),
        str(article.get("content", "")),
    ]).lower()
    return q in hay

async def verify_user_token(authorization: str = Header(None)) -> str:
    """Verify a bearer token and return the user_id."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    # Validate the bearer token shape.
    # In production, replace this with your real Google/Auth.js token validation.
    if not token or len(token) < 10:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Extract user_id from token (you'd do proper JWT validation in production)
    # For demo: token format is "user_<user_id>"
    try:
        user_id = token.split("_")[1] if "_" in token else token
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token format")

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "blog-api",
        "port": PORT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/", response_class=HTMLResponse)
async def blog_homepage() -> str:
    """Serve the modern industrial blog UI."""
    ui_file = BASE_DIR / "index.html"
    if not ui_file.exists():
        raise HTTPException(status_code=404, detail="Blog UI not found")
    html = ui_file.read_text(encoding="utf-8")

    if ADSENSE_PUBLISHER_ID:
        adsense_script = (
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUBLISHER_ID}" '
            f'crossorigin="anonymous"></script>'
        )
        if "</head>" in html:
            html = html.replace("</head>", f"{adsense_script}\n</head>", 1)

    return html


@app.get("/app.js")
async def blog_homepage_js() -> Response:
    """Serve frontend javascript without extra static server setup."""
    js_file = BASE_DIR / "app.js"
    if not js_file.exists():
        raise HTTPException(status_code=404, detail="Frontend script not found")
    return Response(content=js_file.read_text(encoding="utf-8"), media_type="application/javascript")

@app.get("/status")
async def status(db: Session = Depends(get_db)):
    """Detailed status"""
    try:
        total_users = db.query(User).count()
        total_transactions = db.query(Payment).filter(Payment.status == "completed").count()
        revenue_cents = db.query(Payment).filter(Payment.status == "completed").all()
        total_revenue = sum(p.amount_cents for p in revenue_cents) / 100  # Convert to €

        return {
            "status": "operational",
            "users": total_users,
            "transactions": total_transactions,
            "revenue_eur": total_revenue,
            "stripe_connected": bool(STRIPE_SECRET_KEY),
            "adsense_configured": bool(ADSENSE_PUBLISHER_ID),
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {"status": "degraded", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/auth/register")
async def register(name: str, email: str, user_id: str, db: Session = Depends(get_db)):
    """Register a new user from the active auth provider."""
    # Check if user already exists
    existing = db.query(User).filter(User.user_id == user_id).first()
    if existing:
        return {"status": "exists", "user_id": user_id}

    # Create Stripe customer for this user
    stripe_customer = stripe.Customer.create(
        email=email,
        name=name,
        metadata={"clisonix_user_id": user_id}
    )

    # Add user to DB
    user = User(
        user_id=user_id,
        email=email,
        name=name,
        stripe_customer_id=stripe_customer.id,
        subscription_tier="free"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"✅ New user registered: {email} (ID: {user_id})")

    return {
        "status": "registered",
        "user_id": user_id,
        "stripe_customer_id": stripe_customer.id
    }

@app.get("/api/v1/auth/profile")
async def get_profile(
    user_id: str = Depends(verify_user_token),
    db: Session = Depends(get_db)
) -> UserProfile:
    """Get user profile and subscription status"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        user_id=user.user_id,
        email=user.email,
        name=user.name,
        subscription_tier=user.subscription_tier,
        subscription_expires=user.subscription_expires.isoformat() if user.subscription_expires else None,
        total_spent_cents=user.total_spent_cents,
        total_articles_purchased=user.total_articles_purchased
    )

# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/articles")
async def list_articles(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    q: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[ArticlePreview]:
    """
    List articles with previews.
    Free users see preview only (200 chars).
    Subscriber/purchased: see full content indicator.
    """
    try:
        # Fetch from Dr. Albana
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{DR_ALBANA_URL}/api/v1/medical/pillars",
                params={"skip": skip, "limit": limit}
            )
            articles_data = resp.json()

        filtered_articles = []
        raw_articles = articles_data.get("pillars", [])

        for article in raw_articles:
            document_nature = classify_document_nature(article)

            if category and category != "all" and document_nature != category:
                continue
            if q and not matches_query(article, q):
                continue

            article["document_nature"] = document_nature
            filtered_articles.append(article)

        paginated_articles = filtered_articles[skip: skip + limit]
        articles_preview = []

        for article in paginated_articles:
            # Check if user has access
            has_access = False
            if user_id:
                access = db.query(UserArticleAccess).filter(
                    UserArticleAccess.user_id == user_id,
                    UserArticleAccess.article_id == article["id"]
                ).first()
                has_access = bool(access)

                # Check subscription
                user = db.query(User).filter(User.user_id == user_id).first()
                if user and user.subscription_tier in ["monthly", "yearly"]:
                    has_access = True

            preview = ArticlePreview(
                id=article["id"],
                title=article.get("title", "Untitled"),
                author="Dr. Albana",
                date=article.get("date", datetime.now(timezone.utc).isoformat()),
                preview=article.get("content", "")[:200] + "...",
                source="dr_albana",
                category=article.get("document_nature", "medical-general"),
                read_time=max(3, len(article.get("content", "")) // 200),  # Estimate
                requires_payment=not has_access
            )
            articles_preview.append(preview)

        return articles_preview

    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {e}")


@app.get("/api/v1/articles/categories")
async def list_article_categories() -> Dict[str, Any]:
    """Return available document nature categories with counts."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{DR_ALBANA_URL}/api/v1/medical/pillars",
                params={"skip": 0, "limit": 200}
            )
            resp.raise_for_status()
            articles_data = resp.json()

        counts: Dict[str, int] = {}
        for article in articles_data.get("pillars", []):
            nature = classify_document_nature(article)
            counts[nature] = counts.get(nature, 0) + 1

        return {
            "categories": [
                {"key": key, "count": value}
                for key, value in sorted(counts.items(), key=lambda item: item[0])
            ],
            "total": sum(counts.values())
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {e}")

@app.get("/api/v1/articles/{article_id}")
async def get_article(
    article_id: str,
    user_id: str = Depends(verify_user_token),
    db: Session = Depends(get_db)
) -> ArticleDetail:
    """
    Get full article content.
    Requires payment or subscription.
    """
    try:
        # Check user access
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user has access to this article
        has_paid = db.query(UserArticleAccess).filter(
            UserArticleAccess.user_id == user_id,
            UserArticleAccess.article_id == article_id
        ).first()

        has_subscription = user.subscription_tier in ["monthly", "yearly"]

        if not has_paid and not has_subscription:
            raise HTTPException(
                status_code=403,
                detail="Article requires payment. Please purchase access or subscribe."
            )

        # Fetch from Dr. Albana
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{DR_ALBANA_URL}/api/v1/medical/pillars/{article_id}")
            article = resp.json()

        return ArticleDetail(
            id=article["id"],
            title=article.get("title", "Untitled"),
            author="Dr. Albana",
            date=article.get("date", datetime.now(timezone.utc).isoformat()),
            content=article.get("content", ""),
            source="dr_albana",
            category=article.get("domain", "medical"),
            tags=article.get("tags", [])
        )

    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

# Simple in-memory rate limiter: {"ip_or_user": [timestamp, ...]}
_feedback_rate: Dict[str, List[float]] = {}
_FEEDBACK_RATE_LIMIT = 5   # max per window
_FEEDBACK_RATE_WINDOW = 60  # seconds

def _check_feedback_rate(key: str) -> None:
    import time
    now = time.time()
    hits = [t for t in _feedback_rate.get(key, []) if now - t < _FEEDBACK_RATE_WINDOW]
    if len(hits) >= _FEEDBACK_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Shumë kërkesa. Provo pas 1 minute.")
    hits.append(now)
    _feedback_rate[key] = hits


@app.post("/api/v1/articles/{article_id}/feedback", response_model=FeedbackPublic, tags=["feedback"])
async def submit_feedback(
    article_id: str,
    body: FeedbackCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit or update a star-rating + comment for an article (no login required)."""
    rate_key = request.headers.get("x-real-ip") or (request.client.host if request.client else None) or "anon"
    _check_feedback_rate(rate_key)

    # Sanitise text
    def _sanitise(text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        import html
        return html.escape(text.strip())

    comment = _sanitise(body.comment)
    anon_name = _sanitise(body.anonymous_name) or "Anonim"

    fb_id = hashlib.sha256(
        f"{article_id}_{rate_key}_{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:20]

    fb = Feedback(
        id=fb_id,
        article_id=article_id,
        user_id=None,
        anonymous_name=anon_name,
        rating=body.rating,
        comment=comment,
        status="approved",
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    logger.info(f"⭐ Feedback {fb.id} for {article_id}: {body.rating}/5")
    return FeedbackPublic(
        id=fb.id,
        article_id=fb.article_id,
        anonymous_name=fb.anonymous_name,
        rating=fb.rating,
        comment=fb.comment,
        created_at=fb.created_at.isoformat(),
    )


@app.get("/api/v1/articles/{article_id}/feedback", response_model=List[FeedbackPublic], tags=["feedback"])
async def list_feedback(
    article_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Return paginated approved comments for an article."""
    rows = (
        db.query(Feedback)
        .filter(Feedback.article_id == article_id, Feedback.status == "approved")
        .order_by(Feedback.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        FeedbackPublic(
            id=r.id,
            article_id=r.article_id,
            anonymous_name=r.anonymous_name,
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]


@app.get("/api/v1/articles/{article_id}/feedback/summary", response_model=FeedbackSummary, tags=["feedback"])
async def feedback_summary(article_id: str, db: Session = Depends(get_db)):
    """Return avg rating, total count, and breakdown 1-5 for an article."""
    rows = (
        db.query(Feedback)
        .filter(Feedback.article_id == article_id, Feedback.status == "approved")
        .all()
    )
    if not rows:
        return FeedbackSummary(
            article_id=article_id,
            avg_rating=0.0,
            total=0,
            breakdown={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        )
    breakdown = {str(i): 0 for i in range(1, 6)}
    for r in rows:
        breakdown[str(r.rating)] = breakdown.get(str(r.rating), 0) + 1
    avg = round(sum(r.rating for r in rows) / len(rows), 1)
    return FeedbackSummary(
        article_id=article_id,
        avg_rating=avg,
        total=len(rows),
        breakdown=breakdown,
    )


@app.patch("/api/v1/feedback/{feedback_id}/moderate", tags=["feedback"])
async def moderate_feedback(
    feedback_id: str,
    body: FeedbackModerationRequest,
    x_admin_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Admin: approve or reject a feedback entry."""
    admin_key = os.getenv("ADMIN_API_KEY", "clisonix-admin-secret")
    if x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    fb.status = body.status
    fb.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": feedback_id, "status": body.status}


@app.get("/api/v1/feedback/admin", tags=["feedback"])
async def admin_list_feedback(
    status: str = "approved",
    skip: int = 0,
    limit: int = 50,
    x_admin_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Admin: list all feedback with filters."""
    admin_key = os.getenv("ADMIN_API_KEY", "clisonix-admin-secret")
    if x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Admin access required")
    rows = (
        db.query(Feedback)
        .filter(Feedback.status == status)
        .order_by(Feedback.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "article_id": r.article_id,
            "anonymous_name": r.anonymous_name,
            "rating": r.rating,
            "comment": r.comment,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# PAYMENT ENDPOINTS (STRIPE)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/payments/article")
async def purchase_article(
    req: PaymentRequest,
    user_id: str = Depends(verify_user_token),
    db: Session = Depends(get_db)
) -> PaymentResponse:
    """Purchase single article (€0.10 micropayment via Stripe)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        stripe_customer_id = user.stripe_customer_id
        if not stripe_customer_id:
            raise HTTPException(status_code=400, detail="Stripe customer not configured for user")

        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=ARTICLE_PRICE_CENTS,
            currency="eur",
            customer=stripe_customer_id,
            description=f"Article: {req.article_id}",
            metadata={
                "user_id": user_id,
                "article_id": req.article_id,
                "source": req.source
            }
        )

        client_secret = intent.client_secret
        if not client_secret:
            raise HTTPException(status_code=502, detail="Stripe did not return a client secret")

        # Track in DB
        payment = Payment(
            id=f"pay_{hashlib.sha256(f'{user_id}_{req.article_id}_{datetime.now()}'.encode()).hexdigest()[:16]}",
            user_id=user_id,
            stripe_payment_id=intent.id,
            amount_cents=ARTICLE_PRICE_CENTS,
            payment_type="micropayment",
            article_id=req.article_id,
            status="pending"
        )
        db.add(payment)
        db.commit()

        logger.info(f"💳 Payment intent created for user {user_id}: €{ARTICLE_PRICE_CENTS/100}")

        return PaymentResponse(
            client_secret=client_secret,
            payment_intent_id=intent.id,
            amount_cents=ARTICLE_PRICE_CENTS
        )

    except Exception as e:
        logger.error(f"Payment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/payments/subscribe")
async def subscribe(
    req: SubscriptionRequest,
    user_id: str = Depends(verify_user_token),
    db: Session = Depends(get_db)
) -> SubscriptionResponse:
    """Create subscription (€4.99/month or €49/year)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        amount_cents = MONTHLY_SUBSCRIPTION_CENTS if req.tier == "monthly" else YEARLY_SUBSCRIPTION_CENTS

        stripe_customer_id = user.stripe_customer_id
        if not stripe_customer_id:
            raise HTTPException(status_code=400, detail="Stripe customer not configured for user")

        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="eur",
            customer=stripe_customer_id,
            description=f"Clisonix Blog {req.tier.capitalize()} Subscription",
            metadata={
                "user_id": user_id,
                "subscription_tier": req.tier
            }
        )

        client_secret = intent.client_secret
        if not client_secret:
            raise HTTPException(status_code=502, detail="Stripe did not return a client secret")

        # Calculate expiry
        if req.tier == "monthly":
            expires = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            expires = datetime.now(timezone.utc) + timedelta(days=365)

        payment = Payment(
            id=f"sub_{hashlib.sha256(f'{user_id}_{req.tier}_{datetime.now()}'.encode()).hexdigest()[:16]}",
            user_id=user_id,
            stripe_payment_id=intent.id,
            amount_cents=amount_cents,
            payment_type="subscription",
            status="pending"
        )
        db.add(payment)
        db.commit()

        return SubscriptionResponse(
            client_secret=client_secret,
            payment_intent_id=intent.id,
            amount_cents=amount_cents,
            expires_date=expires.isoformat()
        )

    except Exception as e:
        logger.error(f"Subscription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/payments/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Process Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )

        if event["type"] == "payment_intent.succeeded":
            pi = event["data"]["object"]

            # Find payment in DB
            payment = db.query(Payment).filter(Payment.stripe_payment_id == pi.id).first()
            if payment:
                payment.status = "completed"
                payment.completed_at = datetime.now(timezone.utc)

                user = db.query(User).filter(User.user_id == payment.user_id).first()
                if user:
                    user.total_spent_cents += payment.amount_cents

                    # Handle article purchase
                    if payment.payment_type == "micropayment" and payment.article_id:
                        user.total_articles_purchased += 1

                        # Grant access
                        access = UserArticleAccess(
                            id=f"access_{hashlib.sha256(f'{payment.user_id}_{payment.article_id}'.encode()).hexdigest()[:16]}",
                            user_id=payment.user_id,
                            article_id=payment.article_id,
                            article_title="Article",
                            source=pi.metadata.get("source", "unknown"),
                            payment_method="micropayment",
                            stripe_payment_id=pi.id
                        )
                        db.add(access)
                        logger.info(f"✅ Article access granted: user {payment.user_id} → {payment.article_id}")

                    # Handle subscription
                    elif payment.payment_type == "subscription":
                        tier = pi.metadata.get("subscription_tier", "monthly")
                        user.subscription_tier = tier

                        if tier == "monthly":
                            user.subscription_expires = datetime.now(timezone.utc) + timedelta(days=30)
                        else:
                            user.subscription_expires = datetime.now(timezone.utc) + timedelta(days=365)

                        logger.info(f"✅ Subscription activated: user {payment.user_id} → {tier}")

                db.commit()

                # ── Affiliate conversion tracking ─────────────────────────
                # If payment metadata contains an affiliate tracking code,
                # record the conversion so commissions are credited.
                aff_code = pi.metadata.get("affiliate_code")
                if aff_code:
                    try:
                        aff_link = db.query(AffiliateLink).filter(
                            AffiliateLink.tracking_code == aff_code,
                            AffiliateLink.is_active == True,
                        ).first()
                        if aff_link:
                            aff_partner = db.query(AffiliatePartner).filter(
                                AffiliatePartner.id == aff_link.partner_id,
                                AffiliatePartner.is_active == True,
                            ).first()
                            if aff_partner:
                                sale_eur = pi.amount / 100
                                comm_eur = round(sale_eur * aff_partner.commission_percent / 100, 4)
                                aff_conv = AffiliateConversion(
                                    id=f"conv_{hashlib.sha256(f'{aff_link.id}{pi.id}'.encode()).hexdigest()[:12]}",
                                    link_id=aff_link.id,
                                    partner_id=aff_partner.id,
                                    stripe_payment_id=pi.id,
                                    sale_amount_eur=sale_eur,
                                    commission_eur=comm_eur,
                                    commission_percent=aff_partner.commission_percent,
                                )
                                aff_link.conversions += 1
                                aff_link.revenue_eur += sale_eur
                                aff_partner.total_commissions_eur += comm_eur
                                db.add(aff_conv)
                                db.commit()
                                logger.info(
                                    f"🤝 Affiliate commission: €{comm_eur:.4f} → "
                                    f"{aff_partner.email} (code: {aff_code})"
                                )
                    except Exception as aff_err:
                        logger.warning(f"Affiliate tracking error (non-fatal): {aff_err}")

        return {"received": True}

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"error": str(e)}, 400

# ═══════════════════════════════════════════════════════════════════════════════
# ADVERTISEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/adsense/config")
async def adsense_config() -> Dict[str, Any]:
    """Return AdSense runtime config for blog frontend."""
    return {
        "enabled": bool(ADSENSE_PUBLISHER_ID),
        "publisher_id": ADSENSE_PUBLISHER_ID,
        "slots": {
            "footer": ADSENSE_SLOT_FOOTER,
            "sidebar": ADSENSE_SLOT_SIDEBAR,
            "article_top": ADSENSE_SLOT_ARTICLE_TOP,
            "article_bottom": ADSENSE_SLOT_ARTICLE_BOTTOM,
        },
    }

@app.get("/api/v1/ads")
async def get_ads(
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    limit: int = 3,
    request: Optional[Request] = None
) -> List[AdResponse]:
    """
    Get ads (only shown to non-subscribers).
    Serious health/wellness ads only.
    """
    try:
        # Check if user has subscription (skip ads for them)
        if user_id:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user and user.subscription_tier in ["monthly", "yearly"]:
                return []  # Premium users see no ads

        # Get active ads
        ads = db.query(Advertisement).filter(Advertisement.is_active).limit(limit).all()

        return [
            AdResponse(
                id=ad.id,
                title=ad.title,
                description=ad.description,
                image_url=ad.image_url,
                click_url=ad.click_url,
                category=ad.category
            )
            for ad in ads
        ]

    except Exception as e:
        logger.error(f"Error fetching ads: {e}")
        return []

@app.post("/api/v1/ads/{ad_id}/impression")
async def track_ad_impression(
    ad_id: str,
    request: Request,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Track ad impression (when ad is displayed)"""
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if ad:
            ad.impressions += 1

            # Calculate revenue
            impression_revenue = (ad.cpm_cents / 1000)  # CPM = cost per 1000
            ad.revenue_cents = int(ad.revenue_cents + impression_revenue)

            # Log impression
            impression = AdImpression(
                id=f"imp_{hashlib.sha256(f'{ad_id}_{user_id}_{datetime.now()}'.encode()).hexdigest()[:16]}",
                ad_id=ad_id,
                user_id=user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
            db.add(impression)
            db.commit()

            logger.info(f"👁️ Ad impression: {ad_id} (total: {ad.impressions})")

        return {"status": "tracked"}
    except Exception as e:
        logger.error(f"Error tracking impression: {e}")
        return {"error": str(e)}

@app.post("/api/v1/ads/{ad_id}/click")
async def track_ad_click(
    ad_id: str,
    request: Request,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Track ad click and return redirect URL"""
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if ad:
            ad.clicks += 1
            db.commit()
            logger.info(f"🔗 Ad clicked: {ad_id} (total: {ad.clicks})")

            return {
                "status": "tracked",
                "redirect_url": ad.click_url,
                "ctr": (ad.clicks / ad.impressions * 100) if ad.impressions > 0 else 0
            }

        raise HTTPException(status_code=404, detail="Ad not found")
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN: AD MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/admin/ads")
async def list_ads_admin(
    admin_token: str = Header(None),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[AdMetrics]:
    """Get all ads with metrics (admin only)"""
    # TODO: Verify admin_token in production
    try:
        query = db.query(Advertisement)
        if category:
            query = query.filter(Advertisement.category == category)

        ads = query.all()

        return [
            AdMetrics(
                ad_id=ad.id,
                impressions=ad.impressions,
                clicks=ad.clicks,
                ctr=(ad.clicks / ad.impressions * 100) if ad.impressions > 0 else 0,
                cpm_cents=ad.cpm_cents,
                revenue_cents=ad.revenue_cents,
                advertiser=ad.advertiser_id
            )
            for ad in ads
        ]
    except Exception as e:
        logger.error(f"Error fetching ads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/ads")
async def create_ad(
    req: AdCreateRequest,
    admin_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Create new ad (admin only)"""
    # TODO: Verify admin_token in production
    try:
        ad_id = f"ad_{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:12]}"

        ad = Advertisement(
            id=ad_id,
            title=req.title,
            description=req.description,
            image_url=req.image_url,
            click_url=req.click_url,
            advertiser_id=req.advertiser_id,
            category=req.category,
            cpm_cents=req.cpm_cents,
            daily_budget_cents=req.daily_budget_cents,
            is_active=True
        )
        db.add(ad)
        db.commit()
        db.refresh(ad)

        logger.info(f"✅ Ad created: {ad_id} ({req.category})")

        return {
            "status": "created",
            "ad_id": ad_id,
            "category": req.category
        }
    except Exception as e:
        logger.error(f"Error creating ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/admin/ads/{ad_id}")
async def update_ad(
    ad_id: str,
    req: AdUpdateRequest,
    admin_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Update ad (admin only)"""
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")

        if req.title:
            ad.title = req.title
        if req.description:
            ad.description = req.description
        if req.image_url:
            ad.image_url = req.image_url
        if req.click_url:
            ad.click_url = req.click_url
        if req.category:
            ad.category = req.category
        if req.is_active is not None:
            ad.is_active = req.is_active
        if req.cpm_cents:
            ad.cpm_cents = req.cpm_cents
        if req.daily_budget_cents:
            ad.daily_budget_cents = req.daily_budget_cents

        ad.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"✏️ Ad updated: {ad_id}")

        return {"status": "updated", "ad_id": ad_id}
    except Exception as e:
        logger.error(f"Error updating ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/admin/ads/{ad_id}")
async def delete_ad(
    ad_id: str,
    admin_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Delete ad (admin only)"""
    try:
        ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")

        db.delete(ad)
        db.commit()

        logger.info(f"🗑️ Ad deleted: {ad_id}")

        return {"status": "deleted", "ad_id": ad_id}
    except Exception as e:
        logger.error(f"Error deleting ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS (ANALYTICS)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/admin/analytics")
async def get_analytics(admin_token: str = Header(None), db: Session = Depends(get_db)):
    """Get comprehensive revenue and usage analytics (admin only)"""
    try:
        # Users
        total_users = db.query(User).count()
        active_subscribers = db.query(User).filter(
            User.subscription_tier.in_(["monthly", "yearly"])
        ).count()
        free_users = total_users - active_subscribers

        # Payments
        completed_payments = db.query(Payment).filter(Payment.status == "completed").all()
        total_payment_revenue_cents = sum(p.amount_cents for p in completed_payments)

        # Breakdown by type
        micropayments = db.query(Payment).filter(
            Payment.payment_type == "micropayment",
            Payment.status == "completed"
        ).all()
        micropayment_revenue_cents = sum(p.amount_cents for p in micropayments)
        micropayment_count = len(micropayments)

        subscriptions = db.query(Payment).filter(
            Payment.payment_type == "subscription",
            Payment.status == "completed"
        ).all()
        subscription_revenue_cents = sum(p.amount_cents for p in subscriptions)

        # Ads
        all_ads = db.query(Advertisement).all()
        ad_revenue_cents = sum(ad.revenue_cents for ad in all_ads)
        total_impressions = sum(ad.impressions for ad in all_ads)
        total_clicks = sum(ad.clicks for ad in all_ads)
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

        # Total revenue
        total_revenue_cents = total_payment_revenue_cents + ad_revenue_cents

        return {
            "summary": {
                "total_revenue_eur": total_revenue_cents / 100,
                "total_users": total_users,
                "active_subscribers": active_subscribers,
                "free_users": free_users,
                "total_ads": len(all_ads),
                "active_ads": len([a for a in all_ads if a.is_active])
            },
            "revenue_breakdown": {
                "micropayments_eur": micropayment_revenue_cents / 100,
                "micropayment_transactions": micropayment_count,
                "subscriptions_eur": subscription_revenue_cents / 100,
                "ad_revenue_eur": ad_revenue_cents / 100,
                "percentages": {
                    "micropayments": (micropayment_revenue_cents / total_revenue_cents * 100) if total_revenue_cents > 0 else 0,
                    "subscriptions": (subscription_revenue_cents / total_revenue_cents * 100) if total_revenue_cents > 0 else 0,
                    "ads": (ad_revenue_cents / total_revenue_cents * 100) if total_revenue_cents > 0 else 0
                }
            },
            "ad_metrics": {
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "average_ctr": avg_ctr,
                "top_ads": [
                    {
                        "ad_id": ad.id,
                        "title": ad.title,
                        "impressions": ad.impressions,
                        "clicks": ad.clicks,
                        "revenue_eur": ad.revenue_cents / 100,
                        "category": ad.category
                    }
                    for ad in sorted(all_ads, key=lambda x: x.revenue_cents, reverse=True)[:5]
                ]
            },
            "user_insights": {
                "monthly_subscribers": active_subscribers if True else 0,
                "total_articles_purchased": db.query(func.sum(User.total_articles_purchased)).scalar() or 0,
                "avg_spending_per_user_eur": (total_revenue_cents / total_users / 100) if total_users > 0 else 0
            }
        }
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

def seed_sample_ads():
    """Seed database with sample ads on startup"""
    db = SessionLocal()
    try:
        # Check if ads exist
        if db.query(Advertisement).count() > 0:
            logger.info("✓ Sample ads already exist")
            return

        sample_ads = [
            {
                "title": "Oura Ring - Sleep & Recovery Tracking",
                "description": "Advanced biometric ring for sleep, activity, and recovery tracking",
                "image_url": "https://www.ouraring.com/images/oura-ring.jpg",
                "click_url": "https://ouraring.com/?ref=clisonix",
                "category": "wellness",
                "advertiser_id": "oura-ring",
                "cpm_cents": 75
            },
            {
                "title": "Whoop Band - Performance Intelligence",
                "description": "Real-time biometric wearable for fitness and recovery optimization",
                "image_url": "https://www.whoop.com/images/whoop-band.jpg",
                "click_url": "https://www.whoop.com?ref=clisonix",
                "category": "health-tech",
                "advertiser_id": "whoop",
                "cpm_cents": 85
            },
            {
                "title": "Everlywell - At-Home Health Tests",
                "description": "Medical-grade lab tests delivered to your home",
                "image_url": "https://www.everlywell.com/images/test-kit.jpg",
                "click_url": "https://www.everlywell.com?ref=clisonix",
                "category": "medical",
                "advertiser_id": "everlywell",
                "cpm_cents": 100
            },
            {
                "title": "Headspace Health - Clinical Programs",
                "description": "Meditation and digital therapeutics for health conditions",
                "image_url": "https://www.headspacehealth.com/images/app.jpg",
                "click_url": "https://www.headspacehealth.com?ref=clisonix",
                "category": "wellness",
                "advertiser_id": "headspace-health",
                "cpm_cents": 60
            },
            {
                "title": "Withings Health Devices",
                "description": "Connected scales, blood pressure monitors, and sleep trackers",
                "image_url": "https://www.withings.com/images/devices.jpg",
                "click_url": "https://www.withings.com?ref=clisonix",
                "category": "health-tech",
                "advertiser_id": "withings",
                "cpm_cents": 65
            }
        ]

        for ad_data in sample_ads:
            ad_id = f"ad_{hashlib.sha256(ad_data['advertiser_id'].encode()).hexdigest()[:12]}"
            ad = Advertisement(
                id=ad_id,
                title=ad_data['title'],
                description=ad_data['description'],
                image_url=ad_data['image_url'],
                click_url=ad_data['click_url'],
                category=ad_data['category'],
                advertiser_id=ad_data['advertiser_id'],
                cpm_cents=ad_data['cpm_cents'],
                is_active=True
            )
            db.add(ad)

        db.commit()
        logger.info(f"✅ Seeded {len(sample_ads)} sample ads")
    except Exception as e:
        logger.error(f"Error seeding ads: {e}")
    finally:
        db.close()

# ── Register affiliate router ─────────────────────────────────────────────
app.include_router(affiliate_router)
logger.info("✅ Affiliate system router registered at /api/v1/affiliates")


if __name__ == "__main__":
    import uvicorn
    # Seed sample ads
    seed_sample_ads()
    logger.info(f"🚀 Blog API starting on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

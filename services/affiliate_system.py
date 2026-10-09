#!/usr/bin/env python3
"""
Affiliate System Endpoints
--------------------------
Track affiliate links, commissions, and payouts
Add these endpoints to services/blog_api/main.py
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

Base = declarative_base()

class AffiliatePartner(Base):
    """Affiliate partner registration"""
    __tablename__ = "affiliate_partners"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    website = Column(String(255), nullable=True)
    commission_percent = Column(Float, default=5.0)  # 5% default
    api_key = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    total_commissions = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class AffiliateLink(Base):
    """Tracking link for affiliate"""
    __tablename__ = "affiliate_links"
    
    id = Column(String(36), primary_key=True)
    partner_id = Column(String(36), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    content_id = Column(String(255), nullable=True)  # Article/content being promoted
    tracking_code = Column(String(50), unique=True, nullable=False)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

class AffiliateConversion(Base):
    """Conversion event (subscription/purchase through affiliate link)"""
    __tablename__ = "affiliate_conversions"
    
    id = Column(String(36), primary_key=True)
    link_id = Column(String(36), nullable=False)
    partner_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    amount_eur = Column(Float, nullable=False)
    commission_percent = Column(Float, nullable=False)
    commission_amount = Column(Float, nullable=False)
    event_type = Column(String(50), default="subscription")  # subscription, one_time, upgrade
    created_at = Column(DateTime, default=datetime.now)

class AffiliatePayout(Base):
    """Payout to affiliate partner"""
    __tablename__ = "affiliate_payouts"
    
    id = Column(String(36), primary_key=True)
    partner_id = Column(String(36), nullable=False)
    amount_eur = Column(Float, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, failed
    payment_method = Column(String(50), default="stripe")  # stripe, bank_transfer
    stripe_payout_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    paid_at = Column(DateTime, nullable=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AffiliatePartnerCreate(BaseModel):
    """Create affiliate partner"""
    name: str
    email: EmailStr
    website: Optional[str] = None
    commission_percent: float = 5.0

class AffiliatePartnerResponse(BaseModel):
    """Affiliate partner info"""
    id: str
    name: str
    email: str
    website: Optional[str]
    commission_percent: float
    api_key: str
    is_active: bool
    total_commissions: float
    created_at: str
    
    class Config:
        from_attributes = True

class AffiliateLinkCreate(BaseModel):
    """Create tracking link"""
    campaign_name: str
    content_id: Optional[str] = None

class AffiliateLinkResponse(BaseModel):
    """Tracking link info"""
    id: str
    tracking_code: str
    campaign_name: str
    clicks: int
    conversions: int
    revenue: float
    link_url: str  # Generated URL

class AffiliateStatsResponse(BaseModel):
    """Affiliate dashboard stats"""
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    total_revenue: float
    pending_commission: float
    paid_commission: float
    top_links: List[AffiliateLinkResponse]

class AffiliatePayoutResponse(BaseModel):
    """Payout info"""
    id: str
    amount_eur: float
    period_start: str
    period_end: str
    status: str
    created_at: str

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v1/affiliates", tags=["affiliates"])

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS (Create & Manage Partners)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/admin/partners", response_model=AffiliatePartnerResponse, tags=["admin"])
async def register_affiliate_partner(
    partner: AffiliatePartnerCreate,
    db: Session = Depends(get_db)
):
    """Register new affiliate partner (admin only)"""
    import uuid
    
    # Check if partner exists
    existing = db.query(AffiliatePartner).filter(
        AffiliatePartner.email == partner.email
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Partner already exists")
    
    # Generate API key
    api_key = f"aff_{uuid.uuid4().hex[:32]}"
    
    new_partner = AffiliatePartner(
        id=str(uuid.uuid4()),
        name=partner.name,
        email=partner.email,
        website=partner.website,
        commission_percent=partner.commission_percent,
        api_key=api_key
    )
    db.add(new_partner)
    db.commit()
    db.refresh(new_partner)
    
    return {
        "id": new_partner.id,
        "name": new_partner.name,
        "email": new_partner.email,
        "website": new_partner.website,
        "commission_percent": new_partner.commission_percent,
        "api_key": new_partner.api_key,
        "is_active": new_partner.is_active,
        "total_commissions": new_partner.total_commissions,
        "created_at": new_partner.created_at.isoformat()
    }

@router.get("/admin/partners", tags=["admin"])
async def list_affiliate_partners(db: Session = Depends(get_db)):
    """List all affiliate partners (admin)"""
    partners = db.query(AffiliatePartner).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "commissions": p.total_commissions,
            "active": p.is_active
        }
        for p in partners
    ]

@router.put("/admin/partners/{partner_id}", tags=["admin"])
async def update_affiliate_partner(
    partner_id: str,
    update: dict,
    db: Session = Depends(get_db)
):
    """Update partner settings (admin)"""
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.id == partner_id
    ).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    for key, value in update.items():
        if hasattr(partner, key):
            setattr(partner, key, value)
    
    partner.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "updated", "partner_id": partner_id}

# ═══════════════════════════════════════════════════════════════════════════════
# PARTNER ENDPOINTS (Self-Service)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/links")
async def create_tracking_link(
    link_request: AffiliateLinkCreate,
    x_affiliate_key: str = Header(None),
    db: Session = Depends(get_db)
):
    """Create new tracking link for partner"""
    if not x_affiliate_key:
        raise HTTPException(status_code=401, detail="Missing affiliate key")
    
    # Verify affiliate key
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.api_key == x_affiliate_key,
        AffiliatePartner.is_active == True
    ).first()
    if not partner:
        raise HTTPException(status_code=401, detail="Invalid affiliate key")
    
    import uuid
    tracking_code = f"aff_{uuid.uuid4().hex[:16]}"
    
    new_link = AffiliateLink(
        id=str(uuid.uuid4()),
        partner_id=partner.id,
        campaign_name=link_request.campaign_name,
        content_id=link_request.content_id,
        tracking_code=tracking_code
    )
    db.add(new_link)
    db.commit()
    
    return {
        "id": new_link.id,
        "tracking_code": tracking_code,
        "campaign_name": link_request.campaign_name,
        "link_url": f"https://clisonix.com/?ref={tracking_code}",
        "clicks": 0,
        "conversions": 0,
        "revenue": 0
    }

@router.get("/links")
async def list_partner_links(
    x_affiliate_key: str = Header(None),
    db: Session = Depends(get_db)
):
    """List partner's tracking links"""
    if not x_affiliate_key:
        raise HTTPException(status_code=401, detail="Missing affiliate key")
    
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.api_key == x_affiliate_key
    ).first()
    if not partner:
        raise HTTPException(status_code=401, detail="Invalid affiliate key")
    
    links = db.query(AffiliateLink).filter(
        AffiliateLink.partner_id == partner.id
    ).all()
    
    return [
        {
            "id": link.id,
            "tracking_code": link.tracking_code,
            "campaign_name": link.campaign_name,
            "link_url": f"https://clisonix.com/?ref={link.tracking_code}",
            "clicks": link.clicks,
            "conversions": link.conversions,
            "revenue": link.revenue
        }
        for link in links
    ]

@router.get("/dashboard")
async def affiliate_dashboard(
    x_affiliate_key: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get affiliate dashboard stats"""
    if not x_affiliate_key:
        raise HTTPException(status_code=401, detail="Missing affiliate key")
    
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.api_key == x_affiliate_key
    ).first()
    if not partner:
        raise HTTPException(status_code=401, detail="Invalid affiliate key")
    
    # Calculate stats
    links = db.query(AffiliateLink).filter(
        AffiliateLink.partner_id == partner.id
    ).all()
    
    total_clicks = sum(link.clicks for link in links)
    total_conversions = sum(link.conversions for link in links)
    total_revenue = sum(link.revenue for link in links)
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    
    # Calculate pending commission
    pending_conversions = db.query(AffiliateConversion).filter(
        AffiliateConversion.partner_id == partner.id
    ).all()
    
    pending_commission = sum(c.commission_amount for c in pending_conversions)
    paid_commission = partner.total_commissions - pending_commission
    
    # Top links
    top_links = sorted(links, key=lambda l: l.revenue, reverse=True)[:5]
    
    return {
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "conversion_rate": round(conversion_rate, 2),
        "total_revenue": total_revenue,
        "pending_commission": round(pending_commission, 2),
        "paid_commission": round(paid_commission, 2),
        "top_links": [
            {
                "campaign_name": link.campaign_name,
                "clicks": link.clicks,
                "conversions": link.conversions,
                "revenue": link.revenue
            }
            for link in top_links
        ]
    }

@router.get("/payouts")
async def get_payouts(
    x_affiliate_key: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get payout history"""
    if not x_affiliate_key:
        raise HTTPException(status_code=401, detail="Missing affiliate key")
    
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.api_key == x_affiliate_key
    ).first()
    if not partner:
        raise HTTPException(status_code=401, detail="Invalid affiliate key")
    
    payouts = db.query(AffiliatePayout).filter(
        AffiliatePayout.partner_id == partner.id
    ).order_by(AffiliatePayout.created_at.desc()).all()
    
    return [
        {
            "id": p.id,
            "amount_eur": p.amount_eur,
            "period": f"{p.period_start.date()} to {p.period_end.date()}",
            "status": p.status,
            "created_at": p.created_at.isoformat(),
            "paid_at": p.paid_at.isoformat() if p.paid_at else None
        }
        for p in payouts
    ]

# ═══════════════════════════════════════════════════════════════════════════════
# TRACKING ENDPOINTS (Public)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/click/{tracking_code}")
async def track_click(
    tracking_code: str,
    redirect_to: str = "https://clisonix.com",
    db: Session = Depends(get_db)
):
    """Track affiliate click"""
    link = db.query(AffiliateLink).filter(
        AffiliateLink.tracking_code == tracking_code
    ).first()
    
    if link:
        link.clicks += 1
        db.commit()
    
    # Return redirect URL with tracking parameter
    return {
        "redirect": redirect_to,
        "tracking_code": tracking_code
    }

@router.post("/conversion")
async def record_conversion(
    conversion_data: dict,
    db: Session = Depends(get_db)
):
    """
    Record conversion (called by payment webhook)
    
    Expected data:
    {
        "tracking_code": "aff_...",
        "user_id": "user_...",
        "amount_eur": 4.99,
        "event_type": "subscription"
    }
    """
    import uuid
    
    link = db.query(AffiliateLink).filter(
        AffiliateLink.tracking_code == conversion_data.get("tracking_code")
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Tracking code not found")
    
    partner = db.query(AffiliatePartner).filter(
        AffiliatePartner.id == link.partner_id
    ).first()
    
    amount = float(conversion_data.get("amount_eur", 0))
    commission_amount = amount * (partner.commission_percent / 100)
    
    # Record conversion
    conversion = AffiliateConversion(
        id=str(uuid.uuid4()),
        link_id=link.id,
        partner_id=link.partner_id,
        user_id=conversion_data.get("user_id"),
        amount_eur=amount,
        commission_percent=partner.commission_percent,
        commission_amount=commission_amount,
        event_type=conversion_data.get("event_type", "subscription")
    )
    
    # Update link stats
    link.conversions += 1
    link.revenue += commission_amount
    
    # Update partner total
    partner.total_commissions += commission_amount
    
    db.add(conversion)
    db.commit()
    
    return {
        "status": "recorded",
        "commission_amount": round(commission_amount, 2)
    }

# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN PAYOUT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_db():
    """Get database session (stub)"""
    # This would be implemented with actual database connection
    pass

@router.get("/admin/payouts", tags=["admin"])
async def view_all_payouts(db: Session = Depends(get_db)):
    """View all pending payouts (admin)"""
    payouts = db.query(AffiliatePayout).filter(
        AffiliatePayout.status == "pending"
    ).all()
    return [
        {
            "id": p.id,
            "partner_name": db.query(AffiliatePartner).filter(
                AffiliatePartner.id == p.partner_id
            ).first().name,
            "amount_eur": p.amount_eur,
            "period": f"{p.period_start.date()} - {p.period_end.date()}",
            "created_at": p.created_at.isoformat()
        }
        for p in payouts
    ]

@router.post("/admin/generate-payouts", tags=["admin"])
async def generate_monthly_payouts(db: Session = Depends(get_db)):
    """Generate monthly payouts for all partners (admin)"""
    import uuid

    from dateutil.relativedelta import relativedelta
    
    now = datetime.now(timezone.utc)
    period_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    period_end = (period_start + relativedelta(months=1)) - timedelta(days=1)
    
    partners = db.query(AffiliatePartner).filter(
        AffiliatePartner.is_active == True
    ).all()
    
    created_count = 0
    for partner in partners:
        # Get conversions this month
        conversions = db.query(AffiliateConversion).filter(
            AffiliateConversion.partner_id == partner.id,
            AffiliateConversion.created_at >= period_start,
            AffiliateConversion.created_at <= period_end
        ).all()
        
        total_commission = sum(c.commission_amount for c in conversions)
        
        if total_commission > 0:
            payout = AffiliatePayout(
                id=str(uuid.uuid4()),
                partner_id=partner.id,
                amount_eur=total_commission,
                period_start=period_start,
                period_end=period_end
            )
            db.add(payout)
            created_count += 1
    
    db.commit()
    return {"payouts_created": created_count}

@router.post("/admin/payouts/{payout_id}/pay", tags=["admin"])
async def mark_payout_paid(payout_id: str, db: Session = Depends(get_db)):
    """Mark payout as paid (admin)"""
    payout = db.query(AffiliatePayout).filter(
        AffiliatePayout.id == payout_id
    ).first()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    payout.status = "paid"
    payout.paid_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"status": "payout_marked_paid"}

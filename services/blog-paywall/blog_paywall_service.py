"""
Clisonix Blog Paywall Service
Premium content access control with Stripe subscriptions
"""

import hashlib
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    import stripe  # type: ignore[import-not-found]
except ImportError:
    stripe = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"      # 3.99€/month
    PRO = "pro"          # 10.00€/month
    PRO_YEARLY = "pro_yearly"  # 99.00€/year


@dataclass
class TierConfig:
    name: str
    price_cents: int
    currency: str
    billing_interval: str
    features: list[str]
    stripe_price_id: str


TIER_CONFIG: dict[SubscriptionTier, TierConfig] = {
    SubscriptionTier.FREE: TierConfig(
        name="Free",
        price_cents=0,
        currency="eur",
        billing_interval="month",
        features=[
            "Public blog posts",
            "Basic documentation",
            "Community support"
        ],
        stripe_price_id=""
    ),
    SubscriptionTier.BASIC: TierConfig(
        name="Blog Basic",
        price_cents=399,  # 3.99€
        currency="eur",
        billing_interval="month",
        features=[
            "All Free features",
            "Premium blog articles",
            "Medical research notes",
            "Monthly newsletter",
            "Cancel anytime"
        ],
        stripe_price_id=os.getenv(
            "STRIPE_PRICE_BLOG_BASIC_MONTHLY",
            os.getenv("STRIPE_PRICE_BASIC", "price_blog_basic_monthly")
        )
    ),
    SubscriptionTier.PRO: TierConfig(
        name="Blog Pro Monthly",
        price_cents=1000,  # 10.00€
        currency="eur",
        billing_interval="month",
        features=[
            "All Basic features",
            "All premium article categories",
            "Early-access publications",
            "Priority support",
            "Cancel anytime"
        ],
        stripe_price_id=os.getenv(
            "STRIPE_PRICE_BLOG_PRO_MONTHLY",
            os.getenv("STRIPE_PRICE_PRO", "price_blog_pro_monthly")
        )
    ),
    SubscriptionTier.PRO_YEARLY: TierConfig(
        name="Blog Pro Yearly",
        price_cents=9900,  # 99.00€
        currency="eur",
        billing_interval="year",
        features=[
            "All Pro features",
            "Annual billing discount",
            "Priority support",
            "Cancel anytime"
        ],
        stripe_price_id=os.getenv(
            "STRIPE_PRICE_BLOG_PRO_YEARLY",
            os.getenv("STRIPE_PRICE_PRO_YEARLY", "price_blog_pro_yearly")
        )
    )
}

# ============================================
# MODELS
# ============================================

class SubscriptionRequest(BaseModel):
    email: str
    tier: SubscriptionTier


class ContentAccessRequest(BaseModel):
    article_id: str
    user_token: str


class WebhookEvent(BaseModel):
    type: str
    data: dict[str, Any]


class CancelSubscriptionRequest(BaseModel):
    email: str
    immediate: bool = False


# ============================================
# PAYWALL SERVICE
# ============================================

class BlogPaywallService:
    """Manages blog subscriptions and content access"""

    def __init__(self):
        self.stripe_api_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

        if self.stripe_api_key and stripe:
            stripe.api_key = self.stripe_api_key
            logger.info("✅ Stripe initialized for Blog Paywall")

        # In-memory cache (use Redis in production)
        self._subscriptions: dict[str, dict[str, Any]] = {}
        self._article_tiers: dict[str, SubscriptionTier] = {}

    def get_tier_config(self, tier: SubscriptionTier) -> TierConfig:
        """Get configuration for a subscription tier"""
        return TIER_CONFIG[tier]

    def create_checkout_session(
        self,
        email: str,
        tier: SubscriptionTier,
        success_url: str = "https://clisonix.com/subscription/success",
        cancel_url: str = "https://clisonix.com/subscription/cancel"
    ) -> dict[str, Any]:
        """Create Stripe Checkout session for subscription"""
        if not stripe:
            return {"status": "error", "message": "Stripe not available"}

        tier_config = self.get_tier_config(tier)

        if tier == SubscriptionTier.FREE:
            return {"status": "error", "message": "Free tier doesn't require payment"}

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                customer_email=email,
                line_items=[{
                    "price": tier_config.stripe_price_id,
                    "quantity": 1
                }],
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={
                    "tier": tier.value,
                    "source": "blog_paywall"
                }
            )

            logger.info(f"✅ Checkout session created: {session.id} for {email}")

            return {
                "status": "success",
                "session_id": session.id,
                "checkout_url": session.url,
                "tier": tier.value,
                "price": tier_config.price_cents / 100,
                "billing_interval": tier_config.billing_interval,
                "cancel_anytime": True
            }

        except stripe.error.StripeError as e:  # type: ignore[union-attr]
            logger.error(f"Stripe error: {e}")
            return {"status": "error", "message": str(e)}

    def verify_subscription(self, user_email: str) -> dict[str, Any]:
        """Verify user's subscription status"""
        if not stripe:
            return {"status": "error", "tier": SubscriptionTier.FREE.value}

        try:
            # Find customer by email
            customers = stripe.Customer.list(email=user_email, limit=1)

            if not customers.data:
                return {
                    "status": "active",
                    "tier": SubscriptionTier.FREE.value,
                    "message": "No subscription found"
                }

            customer = customers.data[0]

            # Get active subscriptions
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status="active",
                limit=1
            )

            if not subscriptions.data:
                return {
                    "status": "active",
                    "tier": SubscriptionTier.FREE.value,
                    "message": "No active subscription"
                }

            sub = subscriptions.data[0]
            tier_value = sub.metadata.get("tier", "basic")
            sub_any: Any = sub
            current_period_end = sub_any.current_period_end

            return {
                "status": "active",
                "tier": tier_value,
                "subscription_id": sub.id,
                "current_period_end": datetime.fromtimestamp(int(current_period_end)).isoformat() if current_period_end else None,
                "cancel_at_period_end": sub.cancel_at_period_end
            }

        except Exception as e:
            logger.error(f"Subscription verification error: {e}")
            return {"status": "error", "tier": SubscriptionTier.FREE.value}

    def check_content_access(
        self,
        article_id: str,
        user_email: str
    ) -> dict[str, Any]:
        """Check if user has access to specific content"""

        # Get article's required tier
        required_tier = self._article_tiers.get(article_id, SubscriptionTier.FREE)

        # Get user's subscription
        sub_status = self.verify_subscription(user_email)
        user_tier = SubscriptionTier(sub_status.get("tier", "free"))

        # Tier hierarchy
        tier_levels = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.PRO_YEARLY: 2
        }

        has_access = tier_levels[user_tier] >= tier_levels[required_tier]

        return {
            "article_id": article_id,
            "has_access": has_access,
            "required_tier": required_tier.value,
            "user_tier": user_tier.value,
            "upgrade_url": f"https://clisonix.com/subscribe/{required_tier.value}"
            if not has_access else None
        }

    def cancel_subscription(self, email: str, immediate: bool = False) -> dict[str, Any]:
        """Cancel an active subscription by email."""
        if not stripe:
            return {"status": "error", "message": "Stripe not available"}

        try:
            customers = stripe.Customer.list(email=email, limit=1)
            if not customers.data:
                return {
                    "status": "not_found",
                    "message": "Customer not found",
                    "email": email,
                }

            customer = customers.data[0]
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status="active",
                limit=1,
            )

            if not subscriptions.data:
                return {
                    "status": "not_found",
                    "message": "No active subscription",
                    "email": email,
                }

            sub = subscriptions.data[0]
            if immediate:
                subscription_api: Any = stripe.Subscription
                canceled = subscription_api.delete(sub.id)
                canceled_any: Any = canceled
                return {
                    "status": "cancelled",
                    "subscription_id": sub.id,
                    "email": email,
                    "immediate": True,
                    "cancelled_at": datetime.utcfromtimestamp(int(canceled_any.canceled_at)).isoformat() if getattr(canceled_any, "canceled_at", None) else datetime.utcnow().isoformat(),
                }

            updated = stripe.Subscription.modify(sub.id, cancel_at_period_end=True)
            updated_any: Any = updated
            current_period_end = getattr(updated_any, "current_period_end", None)
            return {
                "status": "scheduled_cancel",
                "subscription_id": sub.id,
                "email": email,
                "immediate": False,
                "cancel_at_period_end": True,
                "current_period_end": datetime.utcfromtimestamp(int(current_period_end)).isoformat() if current_period_end else None,
            }

        except Exception as e:
            logger.error(f"Subscription cancel error: {e}")
            return {"status": "error", "message": str(e), "email": email}

    def bootstrap_products_and_prices(self) -> dict[str, Any]:
        """Create named Stripe products/prices if env price IDs are not configured."""
        if not stripe:
            return {"status": "error", "message": "Stripe not available"}

        plans = [
            (SubscriptionTier.BASIC, "Clisonix Blog Basic", 399, "month", "STRIPE_PRICE_BLOG_BASIC_MONTHLY"),
            (SubscriptionTier.PRO, "Clisonix Blog Pro Monthly", 1000, "month", "STRIPE_PRICE_BLOG_PRO_MONTHLY"),
            (SubscriptionTier.PRO_YEARLY, "Clisonix Blog Pro Yearly", 9900, "year", "STRIPE_PRICE_BLOG_PRO_YEARLY"),
        ]

        created: list[dict[str, Any]] = []
        existing_from_env: list[dict[str, Any]] = []

        try:
            for tier, product_name, amount, interval, env_var in plans:
                configured_price_id = os.getenv(env_var, "").strip()
                if configured_price_id:
                    existing_from_env.append({
                        "tier": tier.value,
                        "env_var": env_var,
                        "price_id": configured_price_id,
                        "product_name": product_name,
                        "amount": amount / 100,
                        "interval": interval,
                    })
                    continue

                product = stripe.Product.create(
                    name=product_name,
                    metadata={"tier": tier.value, "source": "blog_paywall"},
                )
                recurring_interval: Literal["month", "year"] = "year" if interval == "year" else "month"
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=amount,
                    currency="eur",
                    recurring={"interval": recurring_interval},
                    metadata={"tier": tier.value, "source": "blog_paywall"},
                )
                created.append({
                    "tier": tier.value,
                    "product_name": product_name,
                    "product_id": product.id,
                    "price_id": price.id,
                    "amount": amount / 100,
                    "interval": interval,
                    "set_env": env_var,
                })

            return {
                "status": "success",
                "created": created,
                "existing_from_env": existing_from_env,
                "message": "Use returned set_env keys to store new price IDs in environment",
            }
        except Exception as e:
            logger.error(f"Bootstrap Stripe product/price error: {e}")
            return {"status": "error", "message": str(e)}

    def set_article_tier(self, article_id: str, tier: SubscriptionTier) -> None:
        """Set the required tier for an article"""
        self._article_tiers[article_id] = tier
        logger.info(f"📝 Article {article_id} set to tier: {tier.value}")

    def handle_webhook(self, payload: bytes, sig_header: str) -> dict[str, Any]:
        """Handle Stripe webhook events"""
        if not stripe:
            return {"status": "error", "message": "Stripe not available"}

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.stripe_webhook_secret
            )
        except stripe.error.SignatureVerificationError:  # type: ignore[union-attr]
            return {"status": "error", "message": "Invalid signature"}

        event_type = event["type"]
        data = event["data"]["object"]

        if event_type == "checkout.session.completed":
            customer_email = data.get("customer_email")
            tier = data.get("metadata", {}).get("tier", "basic")
            logger.info(f"✅ New subscription: {customer_email} -> {tier}")

            # Cache subscription
            self._subscriptions[customer_email] = {
                "tier": tier,
                "activated_at": datetime.utcnow().isoformat()
            }

        elif event_type == "customer.subscription.deleted":
            customer_id = data.get("customer")
            logger.info(f"❌ Subscription cancelled: {customer_id}")

        elif event_type == "invoice.payment_failed":
            customer_email = data.get("customer_email")
            logger.warning(f"⚠️ Payment failed: {customer_email}")

        return {"status": "success", "event_type": event_type}

    def generate_access_token(self, email: str) -> str:
        """Generate a simple access token for content"""
        secret = os.getenv("PAYWALL_SECRET", "clisonix-paywall-secret")
        timestamp = datetime.utcnow().isoformat()
        raw = f"{email}:{timestamp}:{secret}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Clisonix Blog Paywall",
    description="Premium content access with Stripe subscriptions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://clisonix.com", "https://www.clisonix.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

paywall = BlogPaywallService()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "blog-paywall",
        "timestamp": datetime.utcnow().isoformat(),
        "stripe_configured": bool(paywall.stripe_api_key)
    }


@app.get("/api/tiers")
async def get_tiers():
    """Get all subscription tiers"""
    return {
        "cancel_anytime": True,
        "tiers": {
            tier.value: {
                "name": config.name,
                "price": config.price_cents / 100,
                "currency": config.currency,
                "billing_interval": config.billing_interval,
                "features": config.features
            }
            for tier, config in TIER_CONFIG.items()
        }
    }


@app.post("/api/subscribe")
async def create_subscription(request: SubscriptionRequest):
    """Create a subscription checkout session"""
    result = paywall.create_checkout_session(
        email=request.email,
        tier=request.tier
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.get("/api/subscription/{email}")
async def check_subscription(email: str):
    """Check subscription status for a user"""
    return paywall.verify_subscription(email)


@app.post("/api/subscription/cancel")
async def cancel_subscription(request: CancelSubscriptionRequest):
    """Cancel a subscription immediately or at period end."""
    result = paywall.cancel_subscription(email=request.email, immediate=request.immediate)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to cancel subscription"))
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result.get("message", "No active subscription"))
    return result


@app.post("/api/stripe/bootstrap-products")
async def bootstrap_products():
    """Create Stripe products/prices with explicit names for blog plans."""
    result = paywall.bootstrap_products_and_prices()
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to bootstrap Stripe products"))
    return result


@app.post("/api/access/check")
async def check_access(request: ContentAccessRequest):
    """Check if user has access to content"""
    # In production, decode token to get email
    # For now, treat token as email
    return paywall.check_content_access(
        article_id=request.article_id,
        user_email=request.user_token
    )


@app.post("/api/articles/{article_id}/tier")
async def set_article_tier(article_id: str, tier: SubscriptionTier):
    """Set the required tier for an article (admin only)"""
    paywall.set_article_tier(article_id, tier)
    return {"status": "success", "article_id": article_id, "tier": tier.value}


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    result = paywall.handle_webhook(payload, sig_header)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


# ============================================
# ARTICLE TIER EXAMPLES
# ============================================

# Pre-configure some article tiers
PREMIUM_ARTICLES = {
    # Basic tier articles
    "eeg-signal-processing-deep-dive": SubscriptionTier.BASIC,
    "neural-mesh-architecture": SubscriptionTier.BASIC,
    "healthcare-ai-compliance": SubscriptionTier.BASIC,

    # Pro tier articles
    "alda-labor-array-whitepaper": SubscriptionTier.PRO,
    "liam-binary-algebra-guide": SubscriptionTier.PRO,
    "distributed-inference-patterns": SubscriptionTier.PRO,

    # Pro yearly-aligned long-form collections
    "clisonix-architecture-blueprint": SubscriptionTier.PRO_YEARLY,
    "custom-integration-guide": SubscriptionTier.PRO_YEARLY,
}

# Initialize article tiers
for article_id, tier in PREMIUM_ARTICLES.items():
    paywall.set_article_tier(article_id, tier)


if __name__ == "__main__":
    import uvicorn
    print("🔒 Clisonix Blog Paywall Service")
    print("=" * 50)
    print("Tiers:")
    for tier, config in TIER_CONFIG.items():
        print(f"  {tier.value}: {config.price_cents/100}€/{config.billing_interval} - {config.name}")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8020)

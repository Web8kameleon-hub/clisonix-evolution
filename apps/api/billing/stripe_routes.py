# -*- coding: utf-8 -*-
"""
Clisonix Stripe Billing Routes (Standalone)
============================================
Routes për Stripe billing që funksionojnë pa varësi të jashtme.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from ..auth.models import (
        OneTimePurchase,
        Subscription,
        SubscriptionPlan,
        SubscriptionStatus,
        User,
    )
    from ..database.session import get_db
except ImportError:
    from auth.models import (
        OneTimePurchase,
        Subscription,
        SubscriptionPlan,
        SubscriptionStatus,
        User,
    )
    from database.session import get_db

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe = None
STRIPE_CONFIGURED = False

try:
    import stripe as stripe_lib
    api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if api_key and api_key.startswith("sk_"):
        stripe_lib.api_key = api_key
        stripe = stripe_lib
        STRIPE_CONFIGURED = True
        logger.info("✅ Stripe billing routes initialized")
    else:
        logger.warning("⚠️ Stripe API key not configured")
except ImportError:
    logger.warning("⚠️ Stripe SDK not installed")

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


class InternalSubscriptionSyncRequest(BaseModel):
    email: Optional[str] = None
    stripeCustomerId: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    subscriptionId: Optional[str] = None
    subscription_id: Optional[str] = None
    plan: Optional[str] = None
    status: str = "active"
    currentPeriodEnd: Optional[datetime] = None
    current_period_end: Optional[datetime] = None


class InternalOneTimePaymentSyncRequest(BaseModel):
    stripeEventId: Optional[str] = None
    stripe_event_id: Optional[str] = None
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    paymentIntentId: Optional[str] = None
    payment_intent_id: Optional[str] = None
    stripeCustomerId: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    customerEmail: Optional[str] = None
    customer_email: Optional[str] = None
    amountTotal: Optional[int] = None
    amount_total: Optional[int] = None
    currency: Optional[str] = None
    paymentStatus: Optional[str] = None
    payment_status: Optional[str] = None
    productId: Optional[str] = None
    product_id: Optional[str] = None
    priceId: Optional[str] = None
    price_id: Optional[str] = None
    quantity: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


def _map_plan(plan: Optional[str]) -> SubscriptionPlan:
    if not plan:
        return SubscriptionPlan.FREE

    normalized = plan.lower()
    mapping = {
        "free": SubscriptionPlan.FREE,
        "starter": SubscriptionPlan.STANDARD,
        "standard": SubscriptionPlan.STANDARD,
        "basic": SubscriptionPlan.STANDARD,
        "pro": SubscriptionPlan.PROFESSIONAL,
        "professional": SubscriptionPlan.PROFESSIONAL,
        "enterprise": SubscriptionPlan.ENTERPRISE,
    }
    return mapping.get(normalized, SubscriptionPlan.FREE)


def _map_status(status: Optional[str]) -> SubscriptionStatus:
    if not status:
        return SubscriptionStatus.INACTIVE

    normalized = status.lower()
    mapping = {
        "active": SubscriptionStatus.ACTIVE,
        "trialing": SubscriptionStatus.TRIALING,
        "past_due": SubscriptionStatus.PAST_DUE,
        "cancelled": SubscriptionStatus.CANCELLED,
        "canceled": SubscriptionStatus.CANCELLED,
        "incomplete": SubscriptionStatus.INACTIVE,
        "incomplete_expired": SubscriptionStatus.INACTIVE,
        "unpaid": SubscriptionStatus.PAST_DUE,
        "inactive": SubscriptionStatus.INACTIVE,
    }
    return mapping.get(normalized, SubscriptionStatus.INACTIVE)


def _plan_from_price_id(price_id: Optional[str]) -> SubscriptionPlan:
    if not price_id:
        return SubscriptionPlan.FREE

    mapping = {
        os.getenv("STRIPE_PRICE_STANDARD") or "": SubscriptionPlan.STANDARD,
        os.getenv("STRIPE_PRICE_PROFESSIONAL") or "": SubscriptionPlan.PROFESSIONAL,
        os.getenv("STRIPE_PRICE_ENTERPRISE") or "": SubscriptionPlan.ENTERPRISE,
        os.getenv("STRIPE_PRICE_STARTER_MONTHLY") or "": SubscriptionPlan.STANDARD,
        os.getenv("STRIPE_PRICE_STARTER_YEARLY") or "": SubscriptionPlan.STANDARD,
        os.getenv("STRIPE_PRICE_PROFESSIONAL_MONTHLY") or "": SubscriptionPlan.PROFESSIONAL,
        os.getenv("STRIPE_PRICE_PROFESSIONAL_YEARLY") or "": SubscriptionPlan.PROFESSIONAL,
        os.getenv("STRIPE_PRICE_ENTERPRISE_MONTHLY") or "": SubscriptionPlan.ENTERPRISE,
        os.getenv("STRIPE_PRICE_ENTERPRISE_YEARLY") or "": SubscriptionPlan.ENTERPRISE,
    }
    return mapping.get(price_id, SubscriptionPlan.FREE)


def _epoch_to_datetime(epoch_value: Optional[int]) -> datetime:
    if not epoch_value:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(epoch_value, tz=timezone.utc)


async def _find_user(
    db: AsyncSession,
    stripe_customer_id: Optional[str],
    email: Optional[str],
) -> Optional[User]:
    user = None

    if stripe_customer_id:
        user_result = await db.execute(
            select(User).where(User.stripe_customer_id == stripe_customer_id)
        )
        user = user_result.scalar_one_or_none()

    if not user and email:
        user_result = await db.execute(select(User).where(User.email == email))
        user = user_result.scalar_one_or_none()

    return user


async def _upsert_subscription_state(
    db: AsyncSession,
    email: Optional[str],
    stripe_customer_id: Optional[str],
    subscription_id: Optional[str],
    plan: Optional[SubscriptionPlan],
    status: SubscriptionStatus,
    current_period_end: Optional[datetime],
) -> Dict[str, Any]:
    user = await _find_user(db, stripe_customer_id, email)
    if not user:
        return {
            "success": False,
            "error": "User not found for subscription sync",
            "email": email,
            "stripe_customer_id": stripe_customer_id,
        }

    if stripe_customer_id and not user.stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id

    target_plan = plan or SubscriptionPlan.FREE
    if status in [SubscriptionStatus.CANCELLED, SubscriptionStatus.INACTIVE]:
        user.subscription_plan = SubscriptionPlan.FREE
    else:
        user.subscription_plan = target_plan

    if subscription_id:
        sub_result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        sub = sub_result.scalar_one_or_none()

        period_end = current_period_end or datetime.now(timezone.utc)
        period_start = datetime.now(timezone.utc)

        if sub:
            sub.status = status
            sub.plan = target_plan
            sub.current_period_end = period_end
            if status == SubscriptionStatus.CANCELLED:
                sub.cancel_at_period_end = True
                sub.cancelled_at = datetime.now(timezone.utc)
        else:
            sub = Subscription(
                user_id=user.id,
                stripe_subscription_id=subscription_id,
                stripe_customer_id=(stripe_customer_id or user.stripe_customer_id or ""),
                status=status,
                plan=target_plan,
                current_period_start=period_start,
                current_period_end=period_end,
                cancel_at_period_end=(status == SubscriptionStatus.CANCELLED),
                cancelled_at=(datetime.now(timezone.utc) if status == SubscriptionStatus.CANCELLED else None),
            )
            db.add(sub)

    await db.commit()

    return {
        "success": True,
        "user_id": user.id,
        "subscription_plan": str(user.subscription_plan),
        "status": str(status),
        "subscription_id": subscription_id,
    }


async def _upsert_one_time_purchase(
    db: AsyncSession,
    *,
    stripe_event_id: str,
    checkout_session_id: str,
    payment_intent_id: Optional[str],
    stripe_customer_id: Optional[str],
    customer_email: Optional[str],
    amount_total: Optional[int],
    currency: Optional[str],
    payment_status: Optional[str],
    product_id: Optional[str],
    price_id: Optional[str],
    quantity: Optional[int],
    metadata: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    existing_by_event = await db.execute(
        select(OneTimePurchase).where(OneTimePurchase.stripe_event_id == stripe_event_id)
    )
    if existing_by_event.scalar_one_or_none():
        return {
            "success": True,
            "idempotent": True,
            "message": "Event already processed",
            "stripe_event_id": stripe_event_id,
        }

    existing_by_session = await db.execute(
        select(OneTimePurchase).where(
            OneTimePurchase.stripe_checkout_session_id == checkout_session_id
        )
    )
    if existing_by_session.scalar_one_or_none():
        return {
            "success": True,
            "idempotent": True,
            "message": "Checkout session already persisted",
            "stripe_checkout_session_id": checkout_session_id,
        }

    user = await _find_user(db, stripe_customer_id, customer_email)
    if not user:
        return {
            "success": False,
            "error": "User not found for one-time payment sync",
            "stripe_customer_id": stripe_customer_id,
            "customer_email": customer_email,
        }

    record = OneTimePurchase(
        user_id=user.id,
        stripe_event_id=stripe_event_id,
        stripe_checkout_session_id=checkout_session_id,
        stripe_payment_intent_id=payment_intent_id,
        stripe_customer_id=stripe_customer_id,
        amount_total=amount_total,
        currency=(currency.upper() if currency else None),
        payment_status=payment_status,
        customer_email=customer_email,
        product_id=product_id,
        price_id=price_id,
        quantity=quantity,
        metadata_json=(json.dumps(metadata) if metadata else None),
    )
    db.add(record)
    await db.commit()

    return {
        "success": True,
        "idempotent": False,
        "user_id": user.id,
        "stripe_event_id": stripe_event_id,
        "checkout_session_id": checkout_session_id,
    }


@router.get("/status")
async def billing_status():
    """Check Stripe billing status."""
    return {
        "stripe_configured": STRIPE_CONFIGURED,
        "webhook_url": "https://api.clisonix.com/api/v1/billing/webhook",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/payment-intent")
async def create_payment_intent(
    amount: int = 2900,  # Default 29.00 EUR
    currency: str = "eur",
    description: str = "Clisonix Subscription"
):
    """
    Create a Stripe Payment Intent.

    Args:
        amount: Amount in cents (2900 = 29.00 EUR)
        currency: Currency code (default: eur)
        description: Payment description
    """
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            description=description,
            metadata={
                "product": "clisonix",
                "environment": os.getenv("ENVIRONMENT", "production")
            }
        )

        return {
            "status": "success",
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": amount,
            "currency": currency
        }
    except Exception as e:
        logger.error(f"Payment intent creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Stripe webhook events.

    Configured webhook URL: https://api.clisonix.com/api/v1/billing/webhook
    """
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        if webhook_secret and sig_header:
            # Verify signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # Development mode - parse without verification
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)

        # Handle events
        event_type = event.type
        event_data = event.data.object

        logger.info(f"📩 Stripe webhook received: {event_type}")

        if event_type == "payment_intent.succeeded":
            logger.info(f"✅ Payment succeeded: {event_data.id}")

        elif event_type == "payment_intent.payment_failed":
            logger.warning(f"❌ Payment failed: {event_data.id}")

        elif event_type == "customer.subscription.created":
            logger.info(f"📝 Subscription created: {event_data.id}")
            price_id = None
            if getattr(event_data, "items", None) and getattr(event_data.items, "data", None):
                first_item = event_data.items.data[0]
                if getattr(first_item, "price", None):
                    price_id = first_item.price.id

            await _upsert_subscription_state(
                db=db,
                email=None,
                stripe_customer_id=getattr(event_data, "customer", None),
                subscription_id=getattr(event_data, "id", None),
                plan=_plan_from_price_id(price_id),
                status=_map_status(getattr(event_data, "status", "active")),
                current_period_end=_epoch_to_datetime(
                    getattr(event_data, "current_period_end", None)
                ),
            )

        elif event_type == "customer.subscription.updated":
            logger.info(f"🔄 Subscription updated: {event_data.id}")
            price_id = None
            if getattr(event_data, "items", None) and getattr(event_data.items, "data", None):
                first_item = event_data.items.data[0]
                if getattr(first_item, "price", None):
                    price_id = first_item.price.id

            await _upsert_subscription_state(
                db=db,
                email=None,
                stripe_customer_id=getattr(event_data, "customer", None),
                subscription_id=getattr(event_data, "id", None),
                plan=_plan_from_price_id(price_id),
                status=_map_status(getattr(event_data, "status", "active")),
                current_period_end=_epoch_to_datetime(
                    getattr(event_data, "current_period_end", None)
                ),
            )

        elif event_type == "customer.subscription.deleted":
            logger.warning(f"🗑️ Subscription cancelled: {event_data.id}")
            await _upsert_subscription_state(
                db=db,
                email=None,
                stripe_customer_id=getattr(event_data, "customer", None),
                subscription_id=getattr(event_data, "id", None),
                plan=SubscriptionPlan.FREE,
                status=SubscriptionStatus.CANCELLED,
                current_period_end=datetime.now(timezone.utc),
            )

        elif event_type == "checkout.session.completed":
            logger.info(f"🛒 Checkout completed: {event_data.id}")
            metadata = getattr(event_data, "metadata", {}) or {}
            await _upsert_subscription_state(
                db=db,
                email=getattr(event_data, "customer_email", None),
                stripe_customer_id=getattr(event_data, "customer", None),
                subscription_id=getattr(event_data, "subscription", None),
                plan=_map_plan(metadata.get("plan")),
                status=SubscriptionStatus.ACTIVE,
                current_period_end=datetime.now(timezone.utc),
            )

        elif event_type == "invoice.paid":
            logger.info(f"💰 Invoice paid: {event_data.id}")
            await _upsert_subscription_state(
                db=db,
                email=getattr(event_data, "customer_email", None),
                stripe_customer_id=getattr(event_data, "customer", None),
                subscription_id=getattr(event_data, "subscription", None),
                plan=None,
                status=SubscriptionStatus.ACTIVE,
                current_period_end=datetime.now(timezone.utc),
            )

        elif event_type == "invoice.payment_failed":
            logger.warning(f"⚠️ Invoice payment failed: {event_data.id}")
            await _upsert_subscription_state(
                db=db,
                email=getattr(event_data, "customer_email", None),
                stripe_customer_id=getattr(event_data, "customer", None),
                subscription_id=getattr(event_data, "subscription", None),
                plan=None,
                status=SubscriptionStatus.PAST_DUE,
                current_period_end=datetime.now(timezone.utc),
            )

        return {"status": "success", "event_type": event_type}

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-subscription")
async def create_subscription(
    customer_id: str,
    price_id: str
):
    """
    Create a subscription for a customer.

    Available Price IDs:
    - price_1SqCxnJQa06Hh2HGsVfGS1an (Free - 0 EUR)
    - price_1SqCxzJQa06Hh2HGwhxR7Zld (Pro - 29 EUR/month)
    - price_1SqCyFJQa06Hh2HGhs2ZSBIp (Enterprise Base - 99 EUR/month)
    """
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        # Create subscription - Stripe API v2 compatible
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice"]
        )

        # Get payment intent from invoice if available
        client_secret = None
        if subscription.latest_invoice:
            invoice = stripe.Invoice.retrieve(subscription.latest_invoice.id)
            if hasattr(invoice, 'payment_intent') and invoice.payment_intent:
                pi = stripe.PaymentIntent.retrieve(invoice.payment_intent)
                client_secret = pi.client_secret

        return {
            "status": "success",
            "subscription_id": subscription.id,
            "subscription_status": subscription.status,
            "client_secret": client_secret,
            "invoice_id": subscription.latest_invoice.id if subscription.latest_invoice else None
        }
    except Exception as e:
        logger.error(f"Subscription creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-customer")
async def create_customer(
    email: str,
    name: Optional[str] = None
):
    """Create a new Stripe customer."""
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"source": "clisonix_api"}
        )

        return {
            "status": "success",
            "customer_id": customer.id,
            "email": email
        }
    except Exception as e:
        logger.error(f"Customer creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
async def list_products():
    """List all Clisonix products."""
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        products = stripe.Product.list(limit=10)
        prices = stripe.Price.list(limit=20)

        result = []
        for product in products.data:
            product_prices = [p for p in prices.data if p.product == product.id]
            result.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "prices": [{
                    "id": p.id,
                    "amount": p.unit_amount,
                    "currency": p.currency,
                    "interval": p.recurring.interval if p.recurring else None,
                    "nickname": p.nickname
                } for p in product_prices]
            })

        return {"products": result}
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkout")
async def create_checkout_session(request: Request):
    """
    Create a Stripe Checkout Session.

    Body:
        price_id: Price ID from Stripe
        customer_email: Customer email (optional)
        success_url: Redirect URL on success
        cancel_url: Redirect URL on cancel
    """
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        body = await request.json()
        price_id = body.get("price_id")
        customer_email = body.get("customer_email")
        success_url = body.get("success_url", "https://clisonix.com/success")
        cancel_url = body.get("cancel_url", "https://clisonix.com/cancel")

        if not price_id:
            raise HTTPException(status_code=400, detail="price_id required")

        session_params = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": cancel_url,
            "payment_method_types": ["card"],
        }

        if customer_email:
            session_params["customer_email"] = customer_email

        session = stripe.checkout.Session.create(**session_params)

        return {
            "status": "success",
            "session_id": session.id,
            "url": session.url,
            "expires_at": session.expires_at
        }
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checkout/{session_id}")
async def get_checkout_session(session_id: str):
    """Get checkout session status."""
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        return {
            "id": session.id,
            "status": session.status,
            "payment_status": session.payment_status,
            "customer": session.customer,
            "subscription": session.subscription
        }
    except Exception as e:
        logger.error(f"Failed to retrieve checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Report usage for metered billing
@router.post("/report-usage")
async def report_usage(
    subscription_item_id: str,
    quantity: int,
    timestamp: Optional[int] = None
):
    """
    Report usage for metered billing.

    Args:
        subscription_item_id: The subscription item ID (si_xxx)
        quantity: Usage quantity
        timestamp: Unix timestamp (optional, defaults to now)
    """
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        usage = stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            timestamp=timestamp or int(datetime.now(timezone.utc).timestamp()),
            action="increment"
        )

        return {
            "status": "success",
            "usage_record_id": usage.id,
            "quantity": quantity
        }
    except Exception as e:
        logger.error(f"Usage report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/internal/update-subscription")
async def internal_update_subscription(
    payload: InternalSubscriptionSyncRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Internal endpoint used by webhook bridges to sync user subscription state."""
    expected_key = os.getenv("INTERNAL_API_KEY")
    provided_key = request.headers.get("X-Internal-Key")

    if expected_key and provided_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid internal API key")

    stripe_customer_id = payload.stripe_customer_id or payload.stripeCustomerId
    subscription_id = payload.subscription_id or payload.subscriptionId
    current_period_end = payload.current_period_end or payload.currentPeriodEnd

    result = await _upsert_subscription_state(
        db=db,
        email=payload.email,
        stripe_customer_id=stripe_customer_id,
        subscription_id=subscription_id,
        plan=_map_plan(payload.plan) if payload.plan else None,
        status=_map_status(payload.status),
        current_period_end=current_period_end,
    )

    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Sync failed"))

    return result


@router.post("/internal/record-one-time-payment")
async def internal_record_one_time_payment(
    payload: InternalOneTimePaymentSyncRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Internal endpoint to persist one-time checkout payments with idempotency."""
    expected_key = os.getenv("INTERNAL_API_KEY")
    provided_key = request.headers.get("X-Internal-Key")

    if expected_key and provided_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid internal API key")

    stripe_event_id = payload.stripe_event_id or payload.stripeEventId
    session_id = payload.session_id or payload.sessionId

    if not stripe_event_id or not session_id:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: stripe_event_id and session_id",
        )

    result = await _upsert_one_time_purchase(
        db=db,
        stripe_event_id=stripe_event_id,
        checkout_session_id=session_id,
        payment_intent_id=(payload.payment_intent_id or payload.paymentIntentId),
        stripe_customer_id=(payload.stripe_customer_id or payload.stripeCustomerId),
        customer_email=(payload.customer_email or payload.customerEmail),
        amount_total=(payload.amount_total or payload.amountTotal),
        currency=payload.currency,
        payment_status=(payload.payment_status or payload.paymentStatus),
        product_id=(payload.product_id or payload.productId),
        price_id=(payload.price_id or payload.priceId),
        quantity=payload.quantity,
        metadata=payload.metadata,
    )

    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Sync failed"))

    return result

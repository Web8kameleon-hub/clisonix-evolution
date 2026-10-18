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

try:
    from .stripe_events import handle_webhook, persist_event, require_internal_key, as_dict
except ImportError:
    from billing.stripe_events import handle_webhook, persist_event, require_internal_key, as_dict

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


@router.get("/status")
async def billing_status():
    """Check Stripe billing status."""
    return {
        "stripe_configured": STRIPE_CONFIGURED,
        "webhook_url": (os.getenv("PUBLIC_WEB_URL") or os.getenv("NEXT_PUBLIC_APP_URL") or "https://www.clisonix.com").rstrip("/") + "/api/webhooks/stripe",
        "webhook_signing_configured": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
        "persistence_configured": bool(os.getenv("AUTH_INTERNAL_URL") and os.getenv("INTERNAL_API_KEY")),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/payment-intent", dependencies=[Depends(require_internal_key)])
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
async def stripe_webhook(request: Request):
    if not STRIPE_CONFIGURED:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    return await handle_webhook(request, stripe)


@router.post("/create-subscription", dependencies=[Depends(require_internal_key)])
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


@router.post("/create-customer", dependencies=[Depends(require_internal_key)])
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


@router.post("/checkout", dependencies=[Depends(require_internal_key)])
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


@router.get("/checkout/{session_id}", dependencies=[Depends(require_internal_key)])
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
@router.post("/report-usage", dependencies=[Depends(require_internal_key)])
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


@router.post("/internal/update-subscription", dependencies=[Depends(require_internal_key)])
async def internal_update_subscription(payload: InternalSubscriptionSyncRequest):
    import hashlib
    data = payload.model_dump(mode="json", exclude_none=True)
    customer_id = payload.stripe_customer_id or payload.stripeCustomerId
    subscription_id = payload.subscription_id or payload.subscriptionId
    if not STRIPE_CONFIGURED or not subscription_id:
        raise HTTPException(503, "Stripe subscription reconciliation is unavailable")
    # Retrieve authoritative status/plan instead of accepting a caller's entitlement.
    try:
        from .stripe_events import subscription_data
    except ImportError:
        from billing.stripe_events import subscription_data
    normalized = await subscription_data(stripe, subscription_id, {"customer_email": payload.email})
    if customer_id and normalized["customer_id"] != customer_id:
        raise HTTPException(409, "Subscription customer does not match")
    return await persist_event({
        "event_id": "sync:" + hashlib.sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest(),
        "created": int(datetime.now(timezone.utc).timestamp()), "kind": "subscription", "data": normalized,
    })


@router.post("/internal/record-one-time-payment", dependencies=[Depends(require_internal_key)])
async def internal_record_one_time_payment(payload: InternalOneTimePaymentSyncRequest):
    session_id = payload.session_id or payload.sessionId
    event_id = payload.stripe_event_id or payload.stripeEventId
    if not session_id or not event_id:
        raise HTTPException(400, "Checkout session and Stripe event IDs are required")
    if not STRIPE_CONFIGURED:
        raise HTTPException(503, "Stripe not configured")
    from starlette.concurrency import run_in_threadpool
    session = as_dict(await run_in_threadpool(stripe.checkout.Session.retrieve, session_id))
    if session.get("mode") != "payment" or session.get("payment_status") != "paid":
        raise HTTPException(409, "Checkout payment is not confirmed")
    metadata = session.get("metadata") or {}
    return await persist_event({
        "event_id": event_id, "created": session["created"], "kind": "purchase", "data": {
            "session_id": session_id, "user_id": metadata.get("user_id"),
            "email": session.get("customer_email") or (session.get("customer_details") or {}).get("email"),
            "customer_id": session.get("customer"), "payment_status": "paid",
            "payment_intent_id": session.get("payment_intent"), "amount_total": session.get("amount_total"),
            "currency": session.get("currency"), "price_id": metadata.get("price_id"), "metadata": metadata,
        },
    })

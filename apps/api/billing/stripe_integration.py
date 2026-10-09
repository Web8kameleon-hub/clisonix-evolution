import os
from typing import Optional

import stripe
from fastapi import HTTPException

STRIPE_API_KEY = (os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY") or "").strip()
if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY


def _require_stripe_configured() -> None:
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

# Example: create a customer

def create_customer(email: str, name: Optional[str] = None):
    _require_stripe_configured()
    try:
        if name is not None:
            customer = stripe.Customer.create(email=email, name=name)
        else:
            customer = stripe.Customer.create(email=email)
        return customer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Example: create a subscription

def create_subscription(customer_id: str, price_id: str):
    _require_stripe_configured()
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
        return subscription
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Example: retrieve usage

def get_customer_usage(customer_id: str):
    _require_stripe_configured()
    raise HTTPException(
        status_code=501,
        detail="Customer usage endpoint is not implemented for this integration",
    )



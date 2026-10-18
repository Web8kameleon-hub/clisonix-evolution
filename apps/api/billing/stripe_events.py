"""Verify Stripe events and persist them through the central SQLite user service."""
from datetime import datetime, timezone
import os
import secrets

import httpx
from fastapi import HTTPException, Request
from starlette.concurrency import run_in_threadpool


def require_internal_key(request: Request):
    expected = os.getenv("INTERNAL_API_KEY", "").strip()
    if not expected:
        raise HTTPException(503, "Internal billing key is not configured")
    provided = request.headers.get("X-Internal-Key", "")
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(401, "Invalid internal API key")


async def persist_event(event: dict):
    base = os.getenv("AUTH_INTERNAL_URL", "").strip().rstrip("/")
    key = os.getenv("INTERNAL_API_KEY", "").strip()
    if not base or not key:
        raise HTTPException(503, "Central billing persistence is not configured")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(base + "/api/internal/billing/events", json=event,
                                         headers={"X-Internal-Key": key})
    except httpx.RequestError as exc:
        raise HTTPException(503, "Central billing persistence is unavailable") from exc
    if response.status_code >= 400:
        # A failed write must be retried by Stripe, never acknowledged as paid.
        raise HTTPException(503, "Billing event was not persisted; retry required")
    result = response.json()
    if result.get("success") is not True:
        raise HTTPException(503, "Billing event persistence was not confirmed")
    return result


def object_id(value):
    return value if isinstance(value, str) else (value or {}).get("id")


def as_dict(value):
    # SDK 14+ resources are no longer dictionaries. Older SDKs use the other helper.
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "to_dict_recursive"):
        return value.to_dict_recursive()
    return value


def plan_for_price(price_id: str | None):
    for name, value in os.environ.items():
        if name.startswith("STRIPE_PRICE_") and value and value == price_id:
            label = name.removeprefix("STRIPE_PRICE_").split("_")[0].lower()
            label = {"pro": "professional"}.get(label, label)
            if label in {"free", "starter", "standard", "professional", "enterprise"}:
                return label
    raise HTTPException(503, "Stripe subscription price has no configured plan mapping")


async def subscription_data(sdk, subscription_id, context):
    sub = as_dict(await run_in_threadpool(sdk.Subscription.retrieve, subscription_id))
    customer_id = object_id(sub.get("customer"))
    metadata = sub.get("metadata") or {}
    items = sub.get("items", {}).get("data", [])
    period_end = sub.get("current_period_end") or (items[0].get("current_period_end") if items else None)
    status = sub.get("status")
    if status in ("active", "trialing"):
        plan = plan_for_price(object_id(items[0].get("price")) if items else None)
        if not period_end:
            raise HTTPException(503, "Stripe subscription billing period is missing")
    else:
        plan = "free"
    email = context.get("customer_email") or (context.get("customer_details") or {}).get("email")
    if not email and not metadata.get("user_id"):
        customer = as_dict(await run_in_threadpool(sdk.Customer.retrieve, customer_id))
        email = customer.get("email")
    return {
        "user_id": metadata.get("user_id") or (context.get("metadata") or {}).get("user_id"),
        "email": email, "customer_id": customer_id, "subscription_id": sub["id"],
        "status": status, "plan": plan,
        "current_period_end": datetime.fromtimestamp(period_end, timezone.utc).isoformat() if period_end else None,
    }


async def handle_webhook(request: Request, sdk):
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        raise HTTPException(503, "Stripe webhook signing secret is not configured")
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(400, "Missing Stripe signature")
    try:
        event = as_dict(sdk.Webhook.construct_event(await request.body(), signature, secret))
    except (ValueError, sdk.SignatureVerificationError) as exc:
        raise HTTPException(400, "Invalid Stripe webhook signature or payload") from exc
    data = event["data"]["object"]
    event_type = event["type"]
    record = {"event_id": event["id"], "created": event["created"]}
    if event_type.startswith("customer.subscription.") and event_type in {
        "customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted",
        "customer.subscription.paused", "customer.subscription.resumed",
    }:
        record.update(kind="subscription", data=await subscription_data(sdk, data["id"], data))
    elif event_type in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        if data.get("mode") == "subscription":
            sub_id = object_id(data.get("subscription"))
            if not sub_id:
                raise HTTPException(503, "Checkout subscription is not available yet")
            record.update(kind="subscription", data=await subscription_data(sdk, sub_id, data))
        elif data.get("mode") == "payment" and data.get("payment_status") == "paid":
            metadata = data.get("metadata") or {}
            record.update(kind="purchase", data={
                "user_id": metadata.get("user_id"), "customer_id": object_id(data.get("customer")),
                "email": data.get("customer_email") or (data.get("customer_details") or {}).get("email"),
                "session_id": data["id"], "payment_status": "paid",
                "payment_intent_id": object_id(data.get("payment_intent")),
                "amount_total": data.get("amount_total"), "currency": data.get("currency"),
                "price_id": metadata.get("price_id"), "metadata": metadata,
            })
        else:
            return {"received": True, "ignored": "Checkout payment is not paid"}
    elif event_type in {"invoice.paid", "invoice.payment_succeeded", "invoice.payment_failed"}:
        parent = data.get("parent") or {}
        sub_id = object_id(data.get("subscription")) or object_id(
            (parent.get("subscription_details") or {}).get("subscription"))
        if not sub_id:
            return {"received": True, "ignored": "Invoice has no subscription"}
        record.update(kind="subscription", data=await subscription_data(sdk, sub_id, data))
    elif event_type in {"charge.refunded", "charge.dispute.created", "charge.dispute.closed"}:
        if event_type == "charge.refunded":
            status = "refunded" if data.get("refunded") else "partially_refunded"
        else:
            status = "paid" if data.get("status") == "won" else "disputed"
        record.update(kind="payment_adjustment", data={
            "payment_intent_id": object_id(data.get("payment_intent")), "payment_status": status,
        })
    else:
        return {"received": True, "ignored": event_type}
    result = await persist_event(record)
    return {"received": True, **result}

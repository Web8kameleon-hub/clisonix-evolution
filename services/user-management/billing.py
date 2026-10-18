"""Billing ledger in the same SQLite database as the existing user registry."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import secrets
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

import db
from user_core import SubscriptionPlan, UserRegistry

router = APIRouter(prefix="/api/internal/billing", tags=["internal-billing"])

SCHEMA = """
CREATE TABLE IF NOT EXISTS billing_events (
 event_id TEXT PRIMARY KEY, created INTEGER NOT NULL, result TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS stripe_customers (
 customer_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES accounts(user_id)
);
CREATE TABLE IF NOT EXISTS billing_subscriptions (
 subscription_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES accounts(user_id),
 customer_id TEXT NOT NULL, plan TEXT NOT NULL, status TEXT NOT NULL,
 period_end TEXT, event_created INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS billing_purchases (
 session_id TEXT PRIMARY KEY, event_id TEXT NOT NULL UNIQUE,
 user_id TEXT NOT NULL REFERENCES accounts(user_id), payment_intent_id TEXT UNIQUE,
 customer_id TEXT, amount_total INTEGER, currency TEXT, status TEXT NOT NULL,
 price_id TEXT, metadata TEXT NOT NULL
);
"""


class BillingEvent(BaseModel):
    event_id: str = Field(min_length=1, max_length=255)
    created: int = Field(ge=0)
    kind: str
    data: dict[str, Any]


def authorize_internal(x_internal_key: str | None) -> None:
    expected = os.getenv("INTERNAL_API_KEY", "").strip()
    if not expected:
        raise HTTPException(503, "Internal billing key is not configured")
    if not x_internal_key or not secrets.compare_digest(x_internal_key, expected):
        raise HTTPException(401, "Invalid internal API key")


def apply_event(event: BillingEvent) -> dict:
    db.init_schema()
    with db.get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.execute("BEGIN IMMEDIATE")
        previous = conn.execute("SELECT result FROM billing_events WHERE event_id = ?",
                                (event.event_id,)).fetchone()
        if previous:
            return {**json.loads(previous["result"]), "idempotent": True}
        data = event.data
        if event.kind == "payment_adjustment":
            status = data.get("payment_status")
            if status not in ("refunded", "partially_refunded", "disputed", "paid"):
                raise HTTPException(422, "Invalid payment adjustment")
            updated = conn.execute(
                "UPDATE billing_purchases SET status = ? WHERE payment_intent_id = ?",
                (status, data.get("payment_intent_id")),
            ).rowcount
            if not updated:
                raise HTTPException(409, "Purchase not yet persisted; retry event")
            result = {"success": True, "status": status}
        else:
            account = None
            user_id = data.get("user_id")
            customer_id = data.get("customer_id")
            email = data.get("email")
            # The Stripe metadata user ID is set only by authenticated checkout.
            if user_id:
                account = conn.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,)).fetchone()
            if customer_id and not account:
                account = conn.execute(
                    "SELECT a.* FROM accounts a JOIN stripe_customers c ON c.user_id=a.user_id "
                    "WHERE c.customer_id = ?", (customer_id,),
                ).fetchone()
            if email and not account:
                account = conn.execute("SELECT * FROM accounts WHERE email = ?", (email.lower(),)).fetchone()
            if not account:
                raise HTTPException(409, "Registered billing account not found; retry event")
            user_id = account["user_id"]
            if customer_id:
                owner = conn.execute("SELECT user_id FROM stripe_customers WHERE customer_id = ?",
                                     (customer_id,)).fetchone()
                if owner and owner["user_id"] != user_id:
                    raise HTTPException(409, "Stripe customer belongs to another account")
                conn.execute("INSERT OR IGNORE INTO stripe_customers VALUES (?, ?)", (customer_id, user_id))
            if event.kind == "subscription":
                status = data.get("status")
                if status not in {"active", "trialing", "past_due", "unpaid", "canceled",
                                   "incomplete", "incomplete_expired", "paused"}:
                    raise HTTPException(422, "Unknown Stripe subscription status")
                try:
                    plan = SubscriptionPlan(data["plan"])
                except (KeyError, ValueError):
                    raise HTTPException(422, "Unknown billing plan")
                sub_id = data.get("subscription_id")
                if not sub_id or not customer_id:
                    raise HTTPException(422, "Subscription and customer IDs are required")
                old = conn.execute("SELECT * FROM billing_subscriptions WHERE subscription_id = ?",
                                   (sub_id,)).fetchone()
                if old and old["user_id"] != user_id:
                    raise HTTPException(409, "Subscription belongs to another account")
                if old and old["event_created"] > event.created:
                    result = {"success": True, "stale": True, "user_id": user_id}
                else:
                    period_end = data.get("current_period_end")
                    if period_end:
                        period_end = datetime.fromisoformat(str(period_end).replace("Z", "+00:00")).isoformat()
                    conn.execute(
                        "INSERT INTO billing_subscriptions VALUES (?, ?, ?, ?, ?, ?, ?) "
                        "ON CONFLICT(subscription_id) DO UPDATE SET plan=excluded.plan, status=excluded.status, "
                        "period_end=excluded.period_end, event_created=excluded.event_created",
                        (sub_id, user_id, customer_id, plan.value, status, period_end, event.created),
                    )
                    # Keep access from another active subscription when an older one is canceled.
                    now = datetime.now(timezone.utc).isoformat()
                    active = conn.execute(
                        "SELECT plan, period_end FROM billing_subscriptions WHERE user_id=? "
                        "AND status IN ('active','trialing') AND period_end > ? "
                        "ORDER BY event_created DESC LIMIT 1", (user_id, now),
                    ).fetchone()
                    effective = SubscriptionPlan(active["plan"]) if active else SubscriptionPlan.FREE
                    conn.execute(
                        "UPDATE accounts SET plan=?, plan_expires_at=?, updated_at=? WHERE user_id=?",
                        (effective.value, active["period_end"] if active else None, now, user_id),
                    )
                    # Webhook retries and renewals must never add credits repeatedly.
                    conn.execute("UPDATE usage SET storage_limit_mb=? WHERE user_id=?",
                                 (UserRegistry._get_storage_limit(effective), user_id))
                    result = {"success": True, "user_id": user_id, "subscription_plan": effective.value}
            elif event.kind == "purchase":
                if data.get("payment_status") != "paid":
                    raise HTTPException(422, "Purchase must have a confirmed paid status")
                if not data.get("session_id"):
                    raise HTTPException(422, "Checkout session ID is required")
                existing = conn.execute("SELECT user_id FROM billing_purchases WHERE session_id=?",
                                        (data["session_id"],)).fetchone()
                if existing and existing["user_id"] != user_id:
                    raise HTTPException(409, "Checkout belongs to another account")
                if data.get("payment_intent_id"):
                    owner = conn.execute("SELECT user_id FROM billing_purchases WHERE payment_intent_id=?",
                                         (data["payment_intent_id"],)).fetchone()
                    if owner and owner["user_id"] != user_id:
                        raise HTTPException(409, "Payment intent belongs to another account")
                conn.execute(
                    "INSERT OR IGNORE INTO billing_purchases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (data["session_id"], event.event_id, user_id, data.get("payment_intent_id"),
                     customer_id, data.get("amount_total"), data.get("currency"), "paid",
                     data.get("price_id"), json.dumps(data.get("metadata") or {})),
                )
                result = {"success": True, "user_id": user_id, "session_id": data["session_id"]}
            else:
                raise HTTPException(422, "Unsupported billing event kind")
        conn.execute("INSERT INTO billing_events VALUES (?, ?, ?)",
                     (event.event_id, event.created, json.dumps(result)))
        return result


@router.post("/events")
def receive_event(event: BillingEvent, x_internal_key: str | None = Header(None)):
    authorize_internal(x_internal_key)
    return apply_event(event)

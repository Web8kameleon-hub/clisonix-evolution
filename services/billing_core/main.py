# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

try:
    import stripe as stripe_lib
except Exception:  # pragma: no cover
    stripe_lib = None

APP_NAME = "clisonix-billing-core"
PORT = int(os.getenv("PORT", "8095"))
DATA_DIR = Path(os.getenv("BILLING_DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "billing.db"
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
PUBLIC_URL = os.getenv("BILLING_PUBLIC_URL", "http://localhost:8095")

DATA_DIR.mkdir(parents=True, exist_ok=True)
_db_lock = threading.Lock()

PLANS: Dict[str, Dict[str, Any]] = {
    "free": {
        "name": "Free",
        "price_cents": 0,
        "currency": "eur",
        "requests_per_day": 100,
        "features": ["basic_chat"],
        "stripe_price_id": None,
    },
    "starter": {
        "name": "Starter",
        "price_cents": 1999,
        "currency": "eur",
        "requests_per_day": 1000,
        "features": ["basic_chat", "web_search", "file_upload"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_STARTER", ""),
    },
    "professional": {
        "name": "Professional",
        "price_cents": 4999,
        "currency": "eur",
        "requests_per_day": 10000,
        "features": ["basic_chat", "web_search", "file_upload", "advanced_models"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_PROFESSIONAL", ""),
    },
    "business": {
        "name": "Business",
        "price_cents": 19999,
        "currency": "eur",
        "requests_per_day": 100000,
        "features": ["all_features", "priority_support", "sla"],
        "stripe_price_id": os.getenv("STRIPE_PRICE_BUSINESS", ""),
    },
}


class RegisterRequest(BaseModel):
    email: EmailStr
    plan: str = Field(default="free")


class CheckoutRequest(BaseModel):
    email: EmailStr
    plan: str
    success_url: str
    cancel_url: str


class EntitlementResponse(BaseModel):
    ok: bool
    source: str
    user_id: Optional[str] = None
    plan: str
    requests_per_day: int
    features: list[str]
    api_key_status: str


@contextmanager
def db_conn():
    with _db_lock:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    with db_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                plan TEXT NOT NULL,
                api_key_hash TEXT UNIQUE NOT NULL,
                api_key_prefix TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_ref TEXT,
                status TEXT NOT NULL,
                plan TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_events (
                event_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                event_type TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
            """
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def issue_api_key() -> tuple[str, str, str]:
    raw = f"clx_{uuid.uuid4().hex}_{uuid.uuid4().hex[:12]}"
    key_hash = hash_key(raw)
    prefix = raw[:16]
    return raw, key_hash, prefix


def find_user_by_api_key(raw_key: str) -> Optional[sqlite3.Row]:
    key_hash = hash_key(raw_key)
    with db_conn() as conn:
        return conn.execute(
            "SELECT user_id, email, plan, active FROM users WHERE api_key_hash = ?",
            (key_hash,),
        ).fetchone()


def stripe_enabled() -> bool:
    return bool(stripe_lib and STRIPE_SECRET_KEY.startswith("sk_"))


app = FastAPI(title=APP_NAME, version="1.0.0")


@app.on_event("startup")
async def startup() -> None:
    init_db()
    if stripe_enabled():
        stripe_lib.api_key = STRIPE_SECRET_KEY


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": APP_NAME,
        "time": now_iso(),
        "stripe_enabled": stripe_enabled(),
        "public_url": PUBLIC_URL,
    }


@app.get("/api/v1/plans")
async def plans() -> Dict[str, Any]:
    return {
        "plans": [
            {
                "id": plan_id,
                "name": cfg["name"],
                "price_cents": cfg["price_cents"],
                "currency": cfg["currency"],
                "requests_per_day": cfg["requests_per_day"],
                "features": cfg["features"],
            }
            for plan_id, cfg in PLANS.items()
        ]
    }


@app.post("/api/v1/register")
async def register(req: RegisterRequest) -> Dict[str, Any]:
    plan = req.plan if req.plan in PLANS else "free"
    user_id = str(uuid.uuid4())
    raw_key, key_hash, prefix = issue_api_key()

    with db_conn() as conn:
        existing = conn.execute("SELECT user_id FROM users WHERE email = ?", (str(req.email),)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        conn.execute(
            """
            INSERT INTO users (user_id, email, plan, api_key_hash, api_key_prefix, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (user_id, str(req.email), plan, key_hash, prefix, now_iso(), now_iso()),
        )

    return {
        "ok": True,
        "user_id": user_id,
        "plan": plan,
        "api_key": raw_key,
        "message": "Save this API key now. It will not be shown again.",
    }


@app.post("/api/v1/checkout")
async def create_checkout(req: CheckoutRequest) -> Dict[str, Any]:
    if req.plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if req.plan == "free":
        return {"ok": True, "checkout": "not_required", "plan": "free"}

    plan_cfg = PLANS[req.plan]
    price_id = plan_cfg.get("stripe_price_id")
    if not price_id:
        raise HTTPException(status_code=400, detail="Stripe price id missing for plan")
    if not stripe_enabled():
        raise HTTPException(status_code=503, detail="Stripe is not configured")

    session = stripe_lib.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=req.success_url,
        cancel_url=req.cancel_url,
        customer_email=str(req.email),
        metadata={"plan": req.plan, "source": APP_NAME},
    )

    return {"ok": True, "checkout_url": session.url, "session_id": session.id}


@app.post("/api/v1/webhooks/stripe")
async def stripe_webhook(request: Request) -> Dict[str, Any]:
    if not stripe_enabled():
        raise HTTPException(status_code=503, detail="Stripe is not configured")

    payload = await request.body()
    signature = request.headers.get("Stripe-Signature", "")

    try:
        if WEBHOOK_SECRET:
            event = stripe_lib.Webhook.construct_event(payload, signature, WEBHOOK_SECRET)
        else:
            event = json.loads(payload.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid webhook: {exc}")

    event_id = event.get("id")
    event_type = event.get("type", "unknown")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing event id")

    with db_conn() as conn:
        exists = conn.execute("SELECT event_id FROM webhook_events WHERE event_id = ?", (event_id,)).fetchone()
        if exists:
            return {"ok": True, "deduplicated": True, "event_id": event_id}

        conn.execute(
            "INSERT INTO webhook_events (event_id, provider, event_type, processed_at) VALUES (?, 'stripe', ?, ?)",
            (event_id, event_type, now_iso()),
        )

        if event_type == "checkout.session.completed":
            obj = event.get("data", {}).get("object", {})
            email = obj.get("customer_email")
            plan = obj.get("metadata", {}).get("plan", "professional")
            if email:
                user = conn.execute("SELECT user_id FROM users WHERE email = ?", (email,)).fetchone()
                if user:
                    conn.execute(
                        "UPDATE users SET plan = ?, updated_at = ? WHERE user_id = ?",
                        (plan if plan in PLANS else "professional", now_iso(), user["user_id"]),
                    )
                else:
                    user_id = str(uuid.uuid4())
                    raw_key, key_hash, prefix = issue_api_key()
                    conn.execute(
                        """
                        INSERT INTO users (user_id, email, plan, api_key_hash, api_key_prefix, active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                        """,
                        (user_id, email, plan if plan in PLANS else "professional", key_hash, prefix, now_iso(), now_iso()),
                    )

    return {"ok": True, "event_id": event_id, "event_type": event_type}


@app.get("/api/v1/entitlements/{api_key}", response_model=EntitlementResponse)
async def get_entitlements(api_key: str) -> EntitlementResponse:
    user = find_user_by_api_key(api_key)
    if not user:
        return EntitlementResponse(
            ok=False,
            source="billing-core",
            user_id=None,
            plan="free",
            requests_per_day=PLANS["free"]["requests_per_day"],
            features=PLANS["free"]["features"],
            api_key_status="invalid",
        )

    plan = user["plan"] if user["plan"] in PLANS else "free"
    return EntitlementResponse(
        ok=True,
        source="billing-core",
        user_id=user["user_id"],
        plan=plan,
        requests_per_day=PLANS[plan]["requests_per_day"],
        features=PLANS[plan]["features"],
        api_key_status="active" if user["active"] else "disabled",
    )


@app.get("/api/v1/entitlements/resolve")
async def resolve_entitlements(request: Request) -> EntitlementResponse:
    raw = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not raw:
        return EntitlementResponse(
            ok=False,
            source="billing-core",
            user_id=None,
            plan="free",
            requests_per_day=PLANS["free"]["requests_per_day"],
            features=PLANS["free"]["features"],
            api_key_status="missing",
        )
    return await get_entitlements(raw)


@app.exception_handler(Exception)
async def fallback_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})

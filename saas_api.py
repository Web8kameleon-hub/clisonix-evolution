#!/usr/bin/env python3
"""SaaS API Gateway Service - Clisonix Cloud."""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from billing_plans import check_usage, get_plan, plans

PORT = int(os.getenv("PORT", "8056"))
DB_PATH = Path(os.getenv("SAAS_DB_PATH", "./data/saas_api.db"))


class SubscriptionRequest(BaseModel):
    tenant_id: str
    plan: str = "free"


class UsageRequest(BaseModel):
    tenant_id: str
    requests_today: int = Field(ge=0)


class FeatureCheckRequest(BaseModel):
    tenant_id: str
    feature: str


class SaaSStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subscriptions (
                    tenant_id TEXT PRIMARY KEY,
                    plan TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert_subscription(self, tenant_id: str, plan: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions (tenant_id, plan, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(tenant_id) DO UPDATE SET
                    plan = excluded.plan,
                    updated_at = excluded.updated_at
                """,
                (tenant_id, plan, now, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT tenant_id, plan, created_at, updated_at FROM subscriptions WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()
        return dict(row) if row else {}

    def get_subscription(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT tenant_id, plan, created_at, updated_at FROM subscriptions WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()
        return dict(row) if row else None

    def list_subscriptions(self, limit: int = 200) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT tenant_id, plan, created_at, updated_at FROM subscriptions ORDER BY updated_at DESC LIMIT ?",
                (max(1, min(limit, 500)),),
            ).fetchall()
        return [dict(row) for row in rows]


app = FastAPI(title="Clisonix SaaS API", version="1.0.0")
store = SaaSStore(DB_PATH)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "saas-api",
        "status": "online",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/plans",
            "/subscriptions",
            "/subscriptions/{tenant_id}",
            "/usage/check",
            "/features/check",
        ],
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "saas-api",
        "db_path": str(DB_PATH),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/plans")
def list_plans() -> Dict[str, Any]:
    return {"plans": plans, "count": len(plans)}


@app.post("/subscriptions")
def create_or_update_subscription(payload: SubscriptionRequest) -> Dict[str, Any]:
    plan_name = payload.plan.lower().strip()
    if plan_name not in plans:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {plan_name}")

    subscription = store.upsert_subscription(payload.tenant_id, plan_name)
    subscription["plan_details"] = get_plan(plan_name)
    return {"ok": True, "subscription": subscription}


@app.get("/subscriptions")
def subscriptions(limit: int = 100) -> Dict[str, Any]:
    items = store.list_subscriptions(limit)
    return {"subscriptions": items, "count": len(items)}


@app.get("/subscriptions/{tenant_id}")
def get_subscription(tenant_id: str) -> Dict[str, Any]:
    sub = store.get_subscription(tenant_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    sub["plan_details"] = get_plan(sub["plan"])
    return {"subscription": sub}


@app.post("/usage/check")
def usage_check(payload: UsageRequest) -> Dict[str, Any]:
    sub = store.get_subscription(payload.tenant_id)
    plan_name = (sub or {}).get("plan", "free")
    result = check_usage(plan_name, payload.requests_today)
    return {
        "tenant_id": payload.tenant_id,
        "plan": plan_name,
        "usage_today": payload.requests_today,
        "result": result,
    }


@app.post("/features/check")
def feature_check(payload: FeatureCheckRequest) -> Dict[str, Any]:
    sub = store.get_subscription(payload.tenant_id)
    plan_name = (sub or {}).get("plan", "free")
    plan = get_plan(plan_name)
    features = plan.get("features", [])
    enabled = payload.feature in features
    return {
        "tenant_id": payload.tenant_id,
        "plan": plan_name,
        "feature": payload.feature,
        "enabled": enabled,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

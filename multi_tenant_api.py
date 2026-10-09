#!/usr/bin/env python3
"""Multi-Tenant API Service - Clisonix Cloud."""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PORT = int(os.getenv("PORT", "8067"))
DB_PATH = Path(os.getenv("TENANT_DB_PATH", "./data/multi_tenant.db"))


class TenantCreate(BaseModel):
    tenant_id: str
    name: str
    plan: str = "free"
    active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class TenantStore:
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
                CREATE TABLE IF NOT EXISTS tenants (
                    tenant_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    active INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create(self, payload: TenantCreate) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO tenants (tenant_id, name, plan, active, metadata_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload.tenant_id,
                        payload.name,
                        payload.plan,
                        1 if payload.active else 0,
                        __import__("json").dumps(payload.metadata, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
                conn.commit()
            except sqlite3.IntegrityError as exc:
                raise HTTPException(status_code=409, detail="Tenant already exists") from exc
        return self.get(payload.tenant_id) or {}

    def get(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM tenants WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()
        if not row:
            return None
        return self._row_to_tenant(row)

    def update(self, tenant_id: str, payload: TenantUpdate) -> Optional[Dict[str, Any]]:
        existing = self.get(tenant_id)
        if not existing:
            return None

        merged = {
            "name": payload.name if payload.name is not None else existing["name"],
            "plan": payload.plan if payload.plan is not None else existing["plan"],
            "active": payload.active if payload.active is not None else existing["active"],
            "metadata": payload.metadata if payload.metadata is not None else existing["metadata"],
        }

        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE tenants
                SET name = ?, plan = ?, active = ?, metadata_json = ?, updated_at = ?
                WHERE tenant_id = ?
                """,
                (
                    merged["name"],
                    merged["plan"],
                    1 if merged["active"] else 0,
                    __import__("json").dumps(merged["metadata"], ensure_ascii=False),
                    now,
                    tenant_id,
                ),
            )
            conn.commit()
        return self.get(tenant_id)

    def list(self, limit: int = 200) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tenants ORDER BY updated_at DESC LIMIT ?",
                (max(1, min(limit, 500)),),
            ).fetchall()
        return [self._row_to_tenant(row) for row in rows]

    @staticmethod
    def _row_to_tenant(row: sqlite3.Row) -> Dict[str, Any]:
        import json

        return {
            "tenant_id": row["tenant_id"],
            "name": row["name"],
            "plan": row["plan"],
            "active": bool(row["active"]),
            "metadata": json.loads(row["metadata_json"] or "{}"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


app = FastAPI(title="Clisonix Multi-Tenant API", version="1.0.0")
store = TenantStore(DB_PATH)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "multi-tenant",
        "status": "online",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/tenants",
            "/tenants/{tenant_id}",
        ],
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "multi-tenant",
        "db_path": str(DB_PATH),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tenants")
def create_tenant(payload: TenantCreate) -> Dict[str, Any]:
    tenant = store.create(payload)
    return {"ok": True, "tenant": tenant}


@app.get("/tenants")
def list_tenants(limit: int = 100) -> Dict[str, Any]:
    tenants = store.list(limit)
    return {"tenants": tenants, "count": len(tenants)}


@app.get("/tenants/{tenant_id}")
def get_tenant(tenant_id: str) -> Dict[str, Any]:
    tenant = store.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"tenant": tenant}


@app.patch("/tenants/{tenant_id}")
def update_tenant(tenant_id: str, payload: TenantUpdate) -> Dict[str, Any]:
    tenant = store.update(tenant_id, payload)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"ok": True, "tenant": tenant}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

#!/usr/bin/env python3
"""Controlled local upstream stub for Kloud bridge proof-of-life testing.

This is not a fake product response layer. It is a deterministic local integration target
used to validate the real bridge flow when the sovereign upstream is unavailable.

Endpoints:
- GET /status
- GET /peers
- GET /state
- POST /submit
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, Request

app = FastAPI(title="Kloud Upstream Stub", version="0.1.0")
STARTED_AT = time.time()
RECEIVED_SUBMITS: List[Dict[str, Any]] = []


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/status")
async def status() -> Dict[str, Any]:
    last_submit = RECEIVED_SUBMITS[-1] if RECEIVED_SUBMITS else None
    return {
        "status": "ok",
        "runtime": "kloud-upstream-stub",
        "purpose": "Controlled response target for bridge proof-of-life verification.",
        "uptime_seconds": round(time.time() - STARTED_AT, 2),
        "sync": "ready" if last_submit else "waiting",
        "received_submit_count": len(RECEIVED_SUBMITS),
        "last_submit_at": last_submit["received_at"] if last_submit else None,
        "nodes": [
            {"id": "kloud-stub-node-a", "state": "online", "role": "sovereign-sync"},
        ],
    }


@app.get("/peers")
async def peers() -> Dict[str, Any]:
    return {
        "peers": [
            {"id": "kloud-stub-node-a", "role": "sovereign-sync", "reachable": True},
            {"id": "kloud-stub-node-b", "role": "replica", "reachable": True},
        ],
        "count": 2,
    }


@app.get("/state")
async def state() -> Dict[str, Any]:
    last_submit = RECEIVED_SUBMITS[-1] if RECEIVED_SUBMITS else None
    return {
        "state": "synchronized" if last_submit else "idle",
        "last_submit_at": last_submit["received_at"] if last_submit else None,
        "last_submit_source": last_submit["source"] if last_submit else None,
        "received_submit_count": len(RECEIVED_SUBMITS),
        "proof_of_life": bool(last_submit),
    }


@app.post("/submit")
async def submit(request: Request) -> Dict[str, Any]:
    body = await request.json()
    entry = {
        "received_at": _now_iso(),
        "source": body.get("source", "bridge"),
        "ops": body.get("ops", []),
        "payload_present": bool(body.get("payload")),
        "raw": body,
    }
    RECEIVED_SUBMITS.append(entry)
    return {
        "accepted": True,
        "status": "queued",
        "received_at": entry["received_at"],
        "received_submit_count": len(RECEIVED_SUBMITS),
        "echo": {
            "ops": entry["ops"],
            "payload_present": entry["payload_present"],
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9081)

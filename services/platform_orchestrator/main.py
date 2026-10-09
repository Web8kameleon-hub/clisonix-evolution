from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI

app = FastAPI(title="Clisonix Platform Orchestrator", version="1.0.0")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _targets() -> List[str]:
    raw = os.getenv("ORCHESTRATOR_TARGETS", "").strip()
    if not raw:
        return [
            "http://clisonix-api:8000/health",
            "http://clisonix-web:3000/modules",
            "http://clisonix-ocean-core:8030/health",
            "http://clisonix-openmind:9999/health",
            "http://clisonix-shopping-therapy:7300/health",
            "http://clisonix-kitchen-api:8065/health",
            "http://clisonix-zurich-engine:9122/health",
            "http://clisonix-nanogrid-zeiss:8043/health",
        ]

    return [item.strip() for item in raw.split(",") if item.strip()]


async def _probe(url: str, timeout_seconds: float) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds)) as client:
            response = await client.get(url)
        ok = response.is_success
        return {
            "target": url,
            "ok": ok,
            "status_code": response.status_code,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "target": url,
            "ok": False,
            "error": str(exc),
        }


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "platform-orchestrator",
        "timestamp": _utcnow(),
    }


@app.get("/api/v1/orchestrator/status")
async def orchestrator_status() -> Dict[str, Any]:
    return {
        "service": "platform-orchestrator",
        "targets": _targets(),
        "target_count": len(_targets()),
        "timestamp": _utcnow(),
    }


@app.get("/api/v1/orchestrator/health")
async def orchestrator_health() -> Dict[str, Any]:
    timeout_seconds = float(os.getenv("ORCHESTRATOR_TIMEOUT_SECONDS", "4"))
    checks = [await _probe(url, timeout_seconds) for url in _targets()]
    healthy = sum(1 for item in checks if item.get("ok"))
    total = len(checks)

    overall = "healthy" if healthy == total and total > 0 else "degraded"
    if total == 0:
        overall = "degraded"

    return {
        "status": overall,
        "service": "platform-orchestrator",
        "healthy_targets": healthy,
        "total_targets": total,
        "checks": checks,
        "timestamp": _utcnow(),
    }

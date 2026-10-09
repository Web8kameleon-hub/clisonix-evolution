from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from adaptive_persona_router import CognitiveLevel, get_adaptive_router


class RouteRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    force_level: Optional[str] = None


app = FastAPI(
    title="Clisonix Adaptive Router API",
    description="Real adaptive persona routing service",
    version="1.0.0",
)


def _parse_level(value: Optional[str]) -> Optional[CognitiveLevel]:
    if not value:
        return None
    normalized = value.strip().lower()
    for level in CognitiveLevel:
        if level.value == normalized:
            return level
    return None


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "adaptive-router",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "adaptive-router",
        "status": "operational",
        "endpoints": ["/health", "/route"],
    }


@app.post("/route")
async def route(payload: RouteRequest) -> Dict[str, Any]:
    try:
        router = get_adaptive_router()
        level = _parse_level(payload.force_level)
        decision = router.route(payload.query, force_level=level)
        return {
            "query": payload.query,
            "routing": decision.to_dict(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Adaptive routing failed: {exc}")

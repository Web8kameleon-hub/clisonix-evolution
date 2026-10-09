from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from cognitive_signature_engine import get_cognitive_engine


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    context: Optional[str] = None


app = FastAPI(
    title="Clisonix Cognitive Engine API",
    description="Real cognitive signature analysis service",
    version="1.0.0",
)


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "cognitive-engine",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "cognitive-engine",
        "status": "operational",
        "endpoints": ["/health", "/analyze"],
    }


@app.post("/analyze")
async def analyze(payload: AnalyzeRequest) -> Dict[str, Any]:
    try:
        engine = get_cognitive_engine()
        signature = engine.analyze(payload.query)
        return {
            "query": payload.query,
            "signature": signature.to_dict(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cognitive analysis failed: {exc}")

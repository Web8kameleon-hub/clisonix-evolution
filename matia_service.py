"""
matia_service.py — Matia Engine FastAPI Server (Port 7200)
===========================================================
Endpoints:
  GET  /            → root info
  GET  /health      → liveness
  GET  /status      → engine state + last insight stats
  POST /api/v1/analyse         → full analysis (JSON response)
  POST /api/v1/stream          → SSE streaming analysis
  POST /api/v1/screen          → quick screen-only read (no metric pull)
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from matia_core import MatiaEngine, MatiaInsight

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("matia")

# ═════════════════════════════════════════════════
# APP SETUP
# ═════════════════════════════════════════════════

app = FastAPI(
    title="Matia Engine",
    version="1.0.0",
    description=(
        "Metric-Analyse-Teorie-Implementation-Answer + Screen Reader. "
        "Lexon ekranin dhe analizon sistemin."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()
engine = MatiaEngine()


# ═════════════════════════════════════════════════
# PYDANTIC MODELS
# ═════════════════════════════════════════════════

class AnalyseRequest(BaseModel):
    screen_text: str = Field(default="", description="Text visible on the user's screen")
    question: str = Field(default="", description="The user's question or query")
    pull_metrics: bool = Field(default=True, description="Whether to collect live service metrics")
    language: str = Field(default="sq", description="Response language (sq=Albanian, en=English)")

class StreamRequest(BaseModel):
    screen_text: str = Field(default="")
    question: str = Field(default="")
    pull_metrics: bool = Field(default=True)
    language: str = Field(default="sq")

class ScreenRequest(BaseModel):
    screen_text: str = Field(..., description="Raw text content from the screen")
    language: str = Field(default="sq")


# ═════════════════════════════════════════════════
# ROOT + HEALTH
# ═════════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "service": "matia",
        "version": "1.0.0",
        "description": "Metric-Analyse-Teorie-Implementation-Answer Engine",
        "status": "running",
        "uptime_s": round(time.time() - START_TIME, 1),
        "endpoints": {
            "analyse":  "POST /api/v1/analyse",
            "stream":   "POST /api/v1/stream",
            "screen":   "POST /api/v1/screen",
            "health":   "GET /health",
            "status":   "GET /status",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "engine": "matia",
        "uptime_s": round(time.time() - START_TIME, 1),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


@app.get("/status")
async def status():
    s = engine.status_dict()
    s["uptime_s"] = round(time.time() - START_TIME, 1)
    s["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return s


# ═════════════════════════════════════════════════
# ANALYSE — JSON response
# ═════════════════════════════════════════════════

@app.post("/api/v1/analyse")
async def analyse(req: AnalyseRequest):
    """Full analysis: screen + metrics + theories + implementation steps."""
    try:
        insight: MatiaInsight = await engine.analyse(
            screen_text=req.screen_text,
            question=req.question,
            pull_metrics=req.pull_metrics,
        )
        return {
            "request_id": uuid.uuid4().hex[:12],
            "timestamp": insight.timestamp,
            "ttft_ms": round(insight.ttft_ms),
            "screen_context": insight.screen_context,
            "metrics_summary": insight.metrics_summary,
            "anomalies": insight.anomalies,
            "theories": [
                {
                    "name": t.name,
                    "confidence": round(t.confidence, 3),
                    "description": t.description,
                    "evidence": t.evidence,
                }
                for t in insight.theories
            ],
            "implementation_steps": insight.implementation_steps,
            "answer": insight.answer,
        }
    except Exception as exc:
        logger.error("analyse error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ═════════════════════════════════════════════════
# STREAM — SSE streaming response
# ═════════════════════════════════════════════════

@app.post("/api/v1/stream")
async def stream(req: StreamRequest):
    """
    Server-Sent Events stream of Matia analysis.
    Each data: line is a JSON object with one of:
      {"metric": "ttft", "ms": N}
      {"chunk": "<text>"}
      {"done": true, "anomalies": [...], "steps": [...], "theory_count": N}
    """
    async def event_generator():
        try:
            async for chunk in engine.analyse_stream(
                screen_text=req.screen_text,
                question=req.question,
                pull_metrics=req.pull_metrics,
            ):
                yield chunk
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("stream error: %s", exc, exc_info=True)
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ═════════════════════════════════════════════════
# SCREEN — quick screen-only read (no metrics)
# ═════════════════════════════════════════════════

@app.post("/api/v1/screen")
async def screen_read(req: ScreenRequest):
    """
    Quick screen analysis without pulling live metrics.
    Useful for instant feedback while the user types.
    """
    try:
        insight: MatiaInsight = await engine.analyse(
            screen_text=req.screen_text,
            question="",
            pull_metrics=False,
        )
        return {
            "screen_context": insight.screen_context,
            "theories": [
                {"name": t.name, "confidence": round(t.confidence, 3)}
                for t in insight.theories
            ],
            "anomalies": insight.anomalies,
            "ttft_ms": round(insight.ttft_ms),
        }
    except Exception as exc:
        logger.error("screen error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ═════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("matia_service:app", host="0.0.0.0", port=7200, reload=False)

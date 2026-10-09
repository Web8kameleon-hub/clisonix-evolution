"""
CLX.I standalone image/icon analysis service.

- Independent service profile for CLX image intelligence.
- LLaVA-compatible transport via Ollama /api/generate with images[].
- No fake fallbacks: upstream/model errors return real HTTP errors.
"""

from __future__ import annotations

import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field

APP_NAME = "clx-i"
APP_VERSION = "0.1.0"

OLLAMA_HOST = os.getenv("CLXI_OLLAMA_HOST", "http://localhost:11434")
VISION_MODEL = os.getenv("CLXI_VISION_MODEL", "clx-i:latest")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("CLXI_TIMEOUT_SECONDS", "60"))
MAX_IMAGE_BASE64_LEN = int(os.getenv("CLXI_MAX_IMAGE_BASE64_LEN", "15000000"))
MIRROR_FILE_PATH = Path(os.getenv("CLXI_MIRROR_FILE", ".clx_i/mirror_events.jsonl"))
CLXI_MODE = os.getenv("CLXI_MODE", "wwwmmm_ndb").strip() or "wwwmmm_ndb"
SELFLEARNING_ENABLED = os.getenv("CLXI_SELFLEARNING_ENABLED", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SELFLEARNING_FILE_PATH = Path(os.getenv("CLXI_SELFLEARNING_FILE", ".clx_i/selflearning_events.jsonl"))


CLXI_REQUESTS_TOTAL = Counter(
    "clx_i_requests_total",
    "Total CLX.I analyze requests",
    ["status", "mode"],
)
CLXI_REQUEST_DURATION_SECONDS = Histogram(
    "clx_i_request_duration_seconds",
    "CLX.I analyze request duration in seconds",
    ["mode"],
)
CLXI_RESONANCE_NDB = Gauge(
    "clx_i_resonance_ndb",
    "Latest CLX.I resonance in nanodecibel",
    ["mode"],
)
CLXI_SELFLEARNING_EVENTS_TOTAL = Counter(
    "clx_i_selflearning_events_total",
    "Total persisted CLX.I selflearning events",
    ["mode"],
)
CLXI_MODE_INFO = Gauge(
    "clx_i_mode_info",
    "CLX.I active mode info (value is always 1)",
    ["mode"],
)
CLXI_MODE_INFO.labels(mode=CLXI_MODE).set(1)


class AnalyzeIconRequest(BaseModel):
    image_base64: str = Field(..., min_length=64, max_length=MAX_IMAGE_BASE64_LEN)
    prompt: str = Field(
        default="Analyze this icon and describe purpose, style, and probable use-case.",
        min_length=3,
        max_length=1200,
    )
    stigma_level: int = Field(default=2, ge=1, le=3)
    mirror_level: int = Field(default=1, ge=1, le=3)


class AnalyzeIconResponse(BaseModel):
    request_id: str
    model: str
    mode: str
    stigma_level: int
    mirror_level: int
    output: str
    resonance_ndb: float
    resonance_decibel: float
    processing_time_ms: float
    created_at: str


app = FastAPI(title=APP_NAME, version=APP_VERSION)


def _stigma_instruction(level: int) -> str:
    if level == 1:
        return "Respond in 4-6 concise sentences."
    if level == 2:
        return "Respond with 6-10 bullet points, concise and practical."
    return "Respond in ultra-compact format: max 8 short lines, each under 10 words."


def _safe_text(value: Any, limit: int = 4000) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[:limit]


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def _compute_resonance_score(prompt: str, output: str, stigma_level: int) -> float:
    merged = f"{prompt} {output}".strip()
    if not merged:
        return 0.75

    alnum_ratio = sum(1 for ch in merged if ch.isalnum()) / max(1, len(merged))
    length_bonus = min(0.08, len(output) / 4000.0)
    stigma_adjust = {1: 0.01, 2: 0.02, 3: 0.015}.get(stigma_level, 0.01)
    base = 0.82 + (alnum_ratio * 0.12) + length_bonus + stigma_adjust
    return _clamp(base, 0.75, 0.99)


def _score_to_decibel(score: float) -> float:
    safe = _clamp(score, 1e-12, 1.0)
    return 20.0 * math.log10(safe)


def _score_to_ndb(score: float) -> float:
    return _score_to_decibel(score) * 1_000_000_000.0


def _mirror_event(level: int, payload: dict[str, Any]) -> None:
    event: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "request_id": payload.get("request_id"),
        "model": payload.get("model"),
        "status": payload.get("status", "ok"),
    }
    if level >= 2:
        event["prompt"] = _safe_text(payload.get("prompt"), 1200)
        event["stigma_level"] = payload.get("stigma_level")
    if level >= 3:
        event["response"] = _safe_text(payload.get("response"), 5000)

    MIRROR_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MIRROR_FILE_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=True) + "\n")


def _selflearning_event(payload: dict[str, Any]) -> None:
    if not SELFLEARNING_ENABLED:
        return

    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "request_id": payload.get("request_id"),
        "model": payload.get("model"),
        "stigma_level": int(payload.get("stigma_level", 2)),
        "mirror_level": int(payload.get("mirror_level", 1)),
        "prompt_len": len(str(payload.get("prompt") or "")),
        "output_len": len(str(payload.get("response") or "")),
        "learning_signal": "success",
    }

    SELFLEARNING_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SELFLEARNING_FILE_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=True) + "\n")
    CLXI_SELFLEARNING_EVENTS_TOTAL.labels(mode=CLXI_MODE).inc()


async def _call_ollama_vision(image_base64: str, prompt: str, stigma_level: int) -> str:
    instruction = _stigma_instruction(stigma_level)
    final_prompt = f"{prompt}\n\nOutput rule: {instruction}"

    body = {
        "model": VISION_MODEL,
        "prompt": final_prompt,
        "images": [image_base64],
        "stream": False,
    }

    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=body)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=503, detail=f"ollama_unreachable: {exc}") from exc

    if response.status_code != 200:
        raise HTTPException(status_code=503, detail=f"ollama_error_status: {response.status_code}")

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="ollama_invalid_json") from exc

    text = str(payload.get("response") or "").strip()
    if not text:
        raise HTTPException(status_code=503, detail="ollama_empty_response")
    return text


@app.get("/health")
async def health() -> dict[str, Any]:
    timeout = httpx.Timeout(8.0)
    status = "down"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{OLLAMA_HOST}/api/tags")
            if r.status_code == 200:
                status = "up"
    except httpx.HTTPError:
        status = "down"

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "healthy" if status == "up" else "degraded",
        "mode": CLXI_MODE,
        "ollama": OLLAMA_HOST,
        "vision_model": VISION_MODEL,
        "selflearning_enabled": SELFLEARNING_ENABLED,
        "dependencies": {"ollama": status},
    }


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/icons/analyze", response_model=AnalyzeIconResponse)
async def analyze_icon(req: AnalyzeIconRequest, request: Request) -> AnalyzeIconResponse:
    started = time.perf_counter()
    request_id = f"clxi_{int(time.time() * 1000)}"

    # Basic guard: reject giant payloads before upstream call.
    if len(req.image_base64) > MAX_IMAGE_BASE64_LEN:
        raise HTTPException(status_code=413, detail="image_payload_too_large")

    status_label = "success"
    try:
        output = await _call_ollama_vision(
            image_base64=req.image_base64,
            prompt=req.prompt,
            stigma_level=req.stigma_level,
        )
    except HTTPException:
        status_label = "error"
        raise
    finally:
        CLXI_REQUESTS_TOTAL.labels(status=status_label, mode=CLXI_MODE).inc()

    elapsed_seconds = time.perf_counter() - started
    elapsed_ms = elapsed_seconds * 1000.0
    CLXI_REQUEST_DURATION_SECONDS.labels(mode=CLXI_MODE).observe(elapsed_seconds)

    resonance_score = _compute_resonance_score(req.prompt, output, req.stigma_level)
    resonance_decibel = _score_to_decibel(resonance_score)
    resonance_ndb = _score_to_ndb(resonance_score)
    CLXI_RESONANCE_NDB.labels(mode=CLXI_MODE).set(resonance_ndb)

    _mirror_event(
        req.mirror_level,
        {
            "request_id": request_id,
            "status": "ok",
            "model": VISION_MODEL,
            "prompt": req.prompt,
            "response": output,
            "stigma_level": req.stigma_level,
            "client": request.client.host if request.client else "unknown",
        },
    )

    _selflearning_event(
        {
            "request_id": request_id,
            "model": VISION_MODEL,
            "prompt": req.prompt,
            "response": output,
            "stigma_level": req.stigma_level,
            "mirror_level": req.mirror_level,
        }
    )

    return AnalyzeIconResponse(
        request_id=request_id,
        model=VISION_MODEL,
        mode=CLXI_MODE,
        stigma_level=req.stigma_level,
        mirror_level=req.mirror_level,
        output=output,
        resonance_ndb=round(resonance_ndb, 3),
        resonance_decibel=round(resonance_decibel, 9),
        processing_time_ms=round(elapsed_ms, 3),
        created_at=datetime.now(timezone.utc).isoformat(),
    )

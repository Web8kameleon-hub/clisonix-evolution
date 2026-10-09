from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class NanoGridVisionRequest(BaseModel):
    image_base64: str
    prompt: Optional[str] = None
    extract_text: bool = True
    language: Optional[str] = None
    user_id: Optional[str] = None
    session_topic: Optional[str] = None


app = FastAPI(title="Clisonix NanoGrid ZEISS", version="1.0.0")


def _upstream_base() -> str:
    return os.getenv("NANOGRID_UPSTREAM", "http://clisonix-ocean-core-multimodal:8033").rstrip("/")


def _timeout_seconds(default_value: float) -> float:
    raw = os.getenv("NANOGRID_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return default_value
    try:
        value = float(raw)
        return value if value > 0 else default_value
    except ValueError:
        return default_value


@app.get("/health")
async def health() -> Dict[str, Any]:
    upstream = _upstream_base()
    last_error: Optional[str] = None
    candidates = ["/health", "/api/v1/status", "/"]

    async with httpx.AsyncClient(timeout=httpx.Timeout(_timeout_seconds(5.0))) as client:
        for path in candidates:
            try:
                resp = await client.get(f"{upstream}{path}")
                if resp.is_success:
                    return {
                        "status": "healthy",
                        "service": "nanogrid-zeiss",
                        "upstream": upstream,
                        "checked_path": path,
                    }
                last_error = f"{path} -> {resp.status_code}"
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)

    return {
        "status": "degraded",
        "service": "nanogrid-zeiss",
        "upstream": upstream,
        "error": last_error or "upstream_unavailable",
    }


@app.get("/api/v1/nanogrid/status")
async def nanogrid_status() -> Dict[str, Any]:
    upstream = _upstream_base()

    async with httpx.AsyncClient(timeout=httpx.Timeout(_timeout_seconds(5.0))) as client:
        for path in ("/health", "/api/v1/status", "/"):
            try:
                resp = await client.get(f"{upstream}{path}")
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=503, detail=f"NanoGrid upstream unavailable: {exc}") from exc

            if resp.is_success:
                payload: Dict[str, Any]
                try:
                    parsed = resp.json()
                    payload = parsed if isinstance(parsed, dict) else {"raw": parsed}
                except Exception:  # noqa: BLE001
                    payload = {"raw": resp.text[:500]}

                return {
                    "available": True,
                    "module": "NanoGrid ZEISS",
                    "service": "nanogrid-zeiss",
                    "upstream": upstream,
                    "payload": payload,
                }

    raise HTTPException(status_code=503, detail="NanoGrid upstream unavailable")


@app.post("/api/v1/nanogrid/vision/analyze")
async def nanogrid_vision_analyze(req: NanoGridVisionRequest) -> Dict[str, Any]:
    upstream = _upstream_base()
    payload = {
        "image_base64": req.image_base64,
        "prompt": req.prompt,
        "extract_text": req.extract_text,
        "language": req.language,
        "user_id": req.user_id,
        "session_topic": req.session_topic,
    }

    targets = [f"{upstream}/api/v1/vision/analyze", f"{upstream}/api/v1/vision"]

    async with httpx.AsyncClient(timeout=httpx.Timeout(_timeout_seconds(120.0))) as client:
        for target in targets:
            try:
                resp = await client.post(target, json=payload)
            except Exception as exc:  # noqa: BLE001
                continue

            if resp.status_code == 404:
                continue

            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text[:1000] or "NanoGrid vision error")

            try:
                parsed = resp.json()
            except Exception:  # noqa: BLE001
                parsed = {"response": resp.text}

            if isinstance(parsed, dict):
                parsed.setdefault("module", "NanoGrid ZEISS")
                parsed.setdefault("service", "nanogrid-zeiss")
                parsed.setdefault("upstream", target)
                return parsed

            return {
                "module": "NanoGrid ZEISS",
                "service": "nanogrid-zeiss",
                "upstream": target,
                "response": parsed,
            }

    raise HTTPException(status_code=503, detail="NanoGrid vision upstream unavailable")

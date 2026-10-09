from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel


class ZurichRequest(BaseModel):
    prompt: str


app = FastAPI(title="Clisonix Zurich Engine", version="1.0.0")


def _parse_csv(value: str) -> List[str]:
    return [item.strip().rstrip("/") for item in value.split(",") if item.strip()]


def _upstream_targets() -> List[str]:
    configured = _parse_csv(os.getenv("ZURICH_UPSTREAMS", ""))
    if configured:
        return configured
    return ["http://clisonix-web:3000"]


def _timeout_seconds(default_value: float) -> float:
    raw = os.getenv("ZURICH_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return default_value
    try:
        parsed = float(raw)
        return parsed if parsed > 0 else default_value
    except ValueError:
        return default_value


@app.get("/health")
async def health() -> Dict[str, Any]:
    last_error: Optional[str] = None
    for base in _upstream_targets():
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(_timeout_seconds(4.0))) as client:
                upstream = await client.get(f"{base}/api/zurich")
            if upstream.status_code in (200, 405):
                return {
                    "status": "healthy",
                    "engine": "zurich-engine",
                    "upstream": base,
                }
            last_error = f"{base} -> {upstream.status_code}"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)

    return {
        "status": "degraded",
        "engine": "zurich-engine",
        "error": last_error or "No upstream available",
    }


@app.post("/api/zurich")
async def zurich_query(payload: ZurichRequest) -> Dict[str, Any]:
    prompt = (payload.prompt or "").strip()
    if not prompt:
        return {"error": "prompt is required"}

    started = time.perf_counter()
    last_error: Optional[str] = None

    for base in _upstream_targets():
        url = f"{base}/api/zurich"
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(_timeout_seconds(45.0))) as client:
                upstream = await client.post(url, json={"prompt": prompt})

            if upstream.is_success:
                data = upstream.json()
                if isinstance(data, dict):
                    data.setdefault("engine_proxy", "clisonix-zurich-engine")
                    data.setdefault("proxy_processing_ms", round((time.perf_counter() - started) * 1000, 2))
                    return data
                return {
                    "ok": True,
                    "output": str(data),
                    "engine_proxy": "clisonix-zurich-engine",
                }

            if 400 <= upstream.status_code < 500:
                try:
                    return upstream.json()
                except Exception:  # noqa: BLE001
                    return {"error": upstream.text or "Zurich client error"}

            last_error = f"{url} -> {upstream.status_code}"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)

    return {
        "error": "Zurich upstream unavailable",
        "details": last_error or "No upstream target reachable",
    }

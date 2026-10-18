import os
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(prefix="/api", tags=["extended"])

EXTENDED_UPSTREAM_URL = os.getenv("EXTENDED_UPSTREAM_URL", "").strip().rstrip("/")
EXTENDED_UPSTREAM_TOKEN = os.getenv("EXTENDED_UPSTREAM_TOKEN", "").strip()
EXTENDED_TIMEOUT = float(os.getenv("EXTENDED_TIMEOUT", "30"))


def _assert_extended_config() -> None:
    if not EXTENDED_UPSTREAM_URL:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "configuration_error",
                "message": "EXTENDED_UPSTREAM_URL is required for extended endpoints",
            },
        )


def _headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if EXTENDED_UPSTREAM_TOKEN:
        headers["Authorization"] = f"Bearer {EXTENDED_UPSTREAM_TOKEN}"
    return headers


async def _proxy_get(path: str, params: dict[str, Any] | None = None) -> Any:
    _assert_extended_config()
    try:
        async with httpx.AsyncClient(timeout=EXTENDED_TIMEOUT) as client:
            response = await client.get(
                f"{EXTENDED_UPSTREAM_URL}{path}",
                headers=_headers(),
                params=params or {},
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "error": "upstream_request_failed",
                    "path": path,
                    "status": response.status_code,
                },
            )
        return response.json()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_unavailable",
                "path": path,
                "message": str(error),
            },
        )


async def _proxy_post(path: str, body: dict[str, Any]) -> Any:
    _assert_extended_config()
    try:
        async with httpx.AsyncClient(timeout=EXTENDED_TIMEOUT) as client:
            response = await client.post(
                f"{EXTENDED_UPSTREAM_URL}{path}",
                headers={**_headers(), "Content-Type": "application/json"},
                json=body,
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "error": "upstream_request_failed",
                    "path": path,
                    "status": response.status_code,
                },
            )
        return response.json()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_unavailable",
                "path": path,
                "message": str(error),
            },
        )


@router.get("/ping")
async def ping():
    return {
        "status": "ok",
        "service": "ultracom-extended-proxy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/system-status")
async def system_status():
    return await _proxy_get("/api/system-status")


@router.post("/ocean")
async def ocean_chat(request: Request):
    return await _proxy_post("/api/ocean", await request.json())


@router.post("/vision")
async def vision_analyze(request: Request):
    return await _proxy_post("/api/vision", await request.json())


@router.post("/audio/transcribe")
async def audio_transcribe(request: Request):
    return await _proxy_post("/api/audio/transcribe", await request.json())


@router.get("/asi/health")
async def asi_health():
    return await _proxy_get("/api/asi/health")


@router.get("/asi/trinity")
async def asi_trinity():
    return await _proxy_get("/api/asi/trinity")


@router.get("/reporting/health")
async def reporting_health():
    return await _proxy_get("/api/reporting/health")


@router.get("/reporting/dashboard")
async def reporting_dashboard():
    return await _proxy_get("/api/reporting/dashboard")


@router.get("/reporting/metrics")
async def reporting_metrics():
    return await _proxy_get("/api/reporting/metrics")


@router.get("/pulse")
async def pulse():
    return await _proxy_get("/api/pulse")


@router.get("/grid")
async def grid():
    return await _proxy_get("/api/grid")


@router.get("/mesh/status")
async def mesh_status():
    return await _proxy_get("/api/mesh/status")


@router.get("/mesh/nodes")
async def mesh_nodes(limit: int = Query(default=100, ge=1, le=500)):
    return await _proxy_get("/api/mesh/nodes", params={"limit": limit})


@router.get("/global-news/breaking")
async def global_news_breaking():
    return await _proxy_get("/api/global-news/breaking")


@router.get("/global-news/financial")
async def global_news_financial():
    return await _proxy_get("/api/global-news/financial")


@router.get("/quantum/status")
async def quantum_status():
    return await _proxy_get("/api/quantum/status")


@router.post("/quantum/simulate")
async def quantum_simulate(request: Request):
    return await _proxy_post("/api/quantum/simulate", await request.json())


@router.get("/neural/models")
async def neural_models():
    return await _proxy_get("/api/neural/models")


@router.get("/neural/stats")
async def neural_stats():
    return await _proxy_get("/api/neural/stats")


@router.get("/billing/usage")
async def billing_usage():
    return await _proxy_get("/api/billing/usage")


@router.get("/billing/plans")
async def billing_plans():
    return await _proxy_get("/api/billing/plans")

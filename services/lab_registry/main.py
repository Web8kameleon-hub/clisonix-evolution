import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

REGISTRY_PATH = Path(os.getenv("CITY_LABS_REGISTRY", "/app/config/city-labs.registry.json"))
INTERNAL_PORT = int(os.getenv("CITY_LABS_INTERNAL_PORT", "9100"))
PROBE_TIMEOUT = float(os.getenv("CITY_LABS_PROBE_TIMEOUT", "2.5"))
ANALYSIS_TIMEOUT = float(os.getenv("CITY_LABS_ANALYSIS_TIMEOUT", "50"))

app = FastAPI(
    title="Clisonix City Labs Registry",
    version="1.1.0",
    description="Canonical discovery, live health aggregation and private execution gateway for Kameleon City Labs.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CITY_LABS_CORS", "*").split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise RuntimeError(f"City Labs registry not found: {REGISTRY_PATH}")
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema") != "clisonix.city-labs.registry/v1":
        raise RuntimeError("Unsupported City Labs registry schema")
    if not isinstance(payload.get("labs"), list):
        raise RuntimeError("City Labs registry has no labs list")
    return payload


def find_lab(lab_id: str) -> Dict[str, Any]:
    registry = load_registry()
    lab = next((item for item in registry["labs"] if item["lab_id"].lower() == lab_id.lower()), None)
    if lab is None:
        raise HTTPException(status_code=404, detail=f"Unknown laboratory: {lab_id}")
    return lab


def internal_url(lab: Dict[str, Any], path: str = "/health") -> str:
    service = lab["service"]
    return f"http://{service}:{INTERNAL_PORT}{path}"


async def probe_lab(client: httpx.AsyncClient, lab: Dict[str, Any]) -> Dict[str, Any]:
    started = asyncio.get_running_loop().time()
    result: Dict[str, Any] = {
        **lab,
        "status": "unavailable",
        "latency_ms": None,
        "health": None,
        "analysis_ready": False,
        "checked_at": now_iso(),
    }
    try:
        response = await client.get(internal_url(lab), timeout=PROBE_TIMEOUT)
        result["latency_ms"] = round((asyncio.get_running_loop().time() - started) * 1000, 2)
        if response.status_code == 200:
            result["status"] = "healthy"
            try:
                result["health"] = response.json()
                result["analysis_ready"] = bool(result["health"].get("analysis_ready"))
            except ValueError:
                result["health"] = {"raw": response.text[:500]}
        else:
            result["status"] = "degraded"
            result["health"] = {"http_status": response.status_code}
    except httpx.HTTPError as exc:
        result["latency_ms"] = round((asyncio.get_running_loop().time() - started) * 1000, 2)
        result["health"] = {"error": str(exc)}
    return result


async def snapshot() -> Dict[str, Any]:
    registry = load_registry()
    async with httpx.AsyncClient() as client:
        observations = await asyncio.gather(*(probe_lab(client, lab) for lab in registry["labs"]))
    healthy = sum(1 for lab in observations if lab["status"] == "healthy")
    degraded = sum(1 for lab in observations if lab["status"] == "degraded")
    unavailable = len(observations) - healthy - degraded
    analysis_ready = sum(1 for lab in observations if lab.get("analysis_ready"))
    return {
        "schema": "clisonix.city-labs.snapshot/v1",
        "status": "healthy" if healthy == len(observations) else ("degraded" if healthy else "unavailable"),
        "total": len(observations),
        "healthy": healthy,
        "degraded": degraded,
        "unavailable": unavailable,
        "analysis_ready": analysis_ready,
        "fully_operational": healthy == len(observations) and analysis_ready == len(observations),
        "laboratories": observations,
        "timestamp": now_iso(),
    }


@app.get("/")
async def root() -> Dict[str, Any]:
    registry = load_registry()
    return {
        "service": "clisonix-city-labs-registry",
        "schema": registry["schema"],
        "registered": len(registry["labs"]),
        "internal_port": INTERNAL_PORT,
        "timestamp": now_iso(),
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    registry = load_registry()
    return {"status": "healthy", "registered": len(registry["labs"]), "timestamp": now_iso()}


@app.get("/api/v1/labs")
async def list_labs(live: bool = True) -> Dict[str, Any]:
    if live:
        return await snapshot()
    registry = load_registry()
    return {
        "schema": registry["schema"],
        "total": len(registry["labs"]),
        "laboratories": registry["labs"],
        "timestamp": now_iso(),
    }


@app.get("/api/v1/labs/{lab_id}")
async def get_lab(lab_id: str, live: bool = True) -> Dict[str, Any]:
    lab = find_lab(lab_id)
    if not live:
        return lab
    async with httpx.AsyncClient() as client:
        observation = await probe_lab(client, lab)
        if observation["status"] == "healthy":
            try:
                manifest_response = await client.get(internal_url(lab, "/manifest"), timeout=PROBE_TIMEOUT)
                if manifest_response.status_code == 200:
                    observation["manifest"] = manifest_response.json()
            except httpx.HTTPError:
                pass
        return observation


@app.post("/api/v1/labs/{lab_id}/analyze")
async def analyze_lab(lab_id: str, request: Request) -> Dict[str, Any]:
    lab = find_lab(lab_id)
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="Analysis request must be a JSON object")

    trace_id = request.headers.get("x-trace-id") or body.get("trace_id") or str(uuid.uuid4())
    body["trace_id"] = trace_id
    headers = {"x-trace-id": trace_id, "content-type": "application/json"}

    try:
        timeout = httpx.Timeout(ANALYSIS_TIMEOUT, connect=min(5.0, ANALYSIS_TIMEOUT))
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(internal_url(lab, "/analyze"), json=body, headers=headers)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail=f"Laboratory {lab_id} analysis timed out") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Laboratory {lab_id} unavailable: {exc}") from exc

    try:
        payload: Any = response.json()
    except ValueError:
        payload = {"raw": response.text[:2000]}
    if response.status_code >= 400:
        detail = payload.get("detail") if isinstance(payload, dict) else payload
        raise HTTPException(status_code=response.status_code, detail=detail)
    return payload


@app.get("/api/v1/labs/{lab_id}/traces")
async def lab_traces(lab_id: str, limit: int = Query(default=50, ge=1, le=500)) -> Dict[str, Any]:
    lab = find_lab(lab_id)
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT * 2) as client:
            response = await client.get(internal_url(lab, "/traces"), params={"limit": limit})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Laboratory trace surface unavailable: {exc}") from exc


@app.get("/api/v1/labs/{lab_id}/traces/{trace_id}")
async def lab_trace(lab_id: str, trace_id: str) -> Dict[str, Any]:
    lab = find_lab(lab_id)
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT * 2) as client:
            response = await client.get(internal_url(lab, f"/traces/{trace_id}"))
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Trace not found: {trace_id}")
            response.raise_for_status()
            return response.json()
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Laboratory trace surface unavailable: {exc}") from exc


@app.get("/api/v1/snapshot")
async def get_snapshot() -> Dict[str, Any]:
    return await snapshot()

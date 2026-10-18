"""
CLX Hybrid Scanner-Printer service.

Hybrid old/new technology bridge:
- Uses CLX Hotguard Scanner-Printer phases (WWWMMM + nanodecibel).
- Computes stigma profile from real resonance values.
- Applies Tide-style routing between old/new/hybrid paths.
- Optional NodeDB fluid event sink for persistence.

No fake data policy:
- No mock/fallback payloads.
- Optional dependencies are reported as not_configured/error with real status.
"""

from __future__ import annotations

import struct
import time
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import httpx
from clx.hotguard import (
    ScannerPrinterStream,
    get_profile_for_resonance,
    resonance_to_decibel,
    resonance_to_nanodecibel,
)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_NAME = "clx-hybrid"
APP_VERSION = "0.1.0"

API_URL = "http://clisonix-api:8000"
OCEAN_URL = "http://clisonix-ocean-core:8030"
CLX_AGENT_URL = "http://clisonix-clx-agent:11435"
CLXI_URL = "http://clisonix-clx-i:11437"
NODEDB_FLUID_URL = ""
NODEDB_FLUID_TRANSPORT = "auto"
NODEDB_FLUID_ROLE = "operator"
REQUIRE_NODEDB_FLUID = "1"
REQUEST_TIMEOUT_SECONDS = 8.0


class HybridScanRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    route_name: str = Field(default="hybrid_route", min_length=1, max_length=120)
    resonance_score: float | None = Field(default=None, ge=0.0, le=1.0)
    stigma_level: int = Field(default=2, ge=1, le=3)
    tide_mode: str = Field(default="auto", pattern="^(auto|old|new|hybrid)$")
    mirror_level: int = Field(default=1, ge=1, le=3)


class DependencyStatus(BaseModel):
    status: str
    message: str | None = None


class HybridScanResponse(BaseModel):
    service: str
    version: str
    request_id: str
    timestamp: str
    resonance_score: float
    resonance_decibel: float
    resonance_ndb: float
    stigma: dict[str, Any]
    tide: dict[str, Any]
    transport: dict[str, Any]
    phases: list[dict[str, Any]]
    nodedb_fluid: dict[str, Any]


app = FastAPI(title=APP_NAME, version=APP_VERSION)


def _env(name: str, default: str) -> str:
    import os

    return (os.getenv(name, default) or default).strip()


def _env_bool(name: str, default: str) -> bool:
    return _env(name, default).lower() in {"1", "true", "yes", "on"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _derive_resonance_score(text: str, stigma_level: int) -> float:
    alnum_ratio = sum(1 for ch in text if ch.isalnum()) / max(1, len(text))
    length_bonus = min(0.08, len(text) / 5000.0)
    stigma_bonus = {1: 0.01, 2: 0.02, 3: 0.015}.get(stigma_level, 0.01)
    score = 0.80 + (alnum_ratio * 0.15) + length_bonus + stigma_bonus
    return max(0.0, min(1.0, score))


def _resolve_tide_route(mode: str, profile_name: str) -> str:
    if mode == "old":
        return "old_technology"
    if mode == "new":
        return "new_technology"
    if mode == "hybrid":
        return "hybrid_technology"

    if profile_name == "lightning":
        return "new_technology"
    if profile_name == "conservative":
        return "old_technology"
    return "hybrid_technology"


async def _check_dependency(url: str) -> DependencyStatus:
    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{url}/health")
        if r.status_code == 200:
            return DependencyStatus(status="up")
        return DependencyStatus(status="error", message=f"health_status_{r.status_code}")
    except httpx.HTTPError as exc:
        return DependencyStatus(status="error", message=str(exc))


def _pack_u16_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    if len(raw) > 65535:
        raise ValueError("nodedb_field_too_long")
    return struct.pack(">H", len(raw)) + raw


def _build_nodedb_binary_payload(
    *,
    request_id: str,
    route_name: str,
    stigma_profile: str,
    tide_route: str,
    resonance_ndb: float,
    resonance_decibel: float,
    stigma_level: int,
    mirror_level: int,
) -> bytes:
    ts_ns = time.time_ns()
    payload = bytearray()
    payload.extend(
        struct.pack(
            ">BqddBB",
            1,
            ts_ns,
            float(resonance_ndb),
            float(resonance_decibel),
            int(stigma_level),
            int(mirror_level),
        )
    )
    payload.extend(_pack_u16_text(request_id))
    payload.extend(_pack_u16_text(route_name))
    payload.extend(_pack_u16_text(stigma_profile))
    payload.extend(_pack_u16_text(tide_route))
    return bytes(payload)


def _build_osclx_telemetry(
    *,
    route_name: str,
    stigma_profile: str,
    tide_route: str,
    resonance_score: float,
    stigma_level: int,
) -> dict[str, Any]:
    normalized_resonance = max(0.0, min(1.0, float(resonance_score)))
    return {
        "fabric_id": "clx-fabric",
        "trust_domain": "clisonix-production",
        "role": "bridge",
        "capabilities": ["scanner", "printer", "hybrid-routing", "nodedb-telemetry"],
        "trust_level": "trusted",
        "affinity_tags": [stigma_profile, tide_route],
        "pressure": 1.0 - normalized_resonance,
        "resonance": normalized_resonance,
        "health_score": normalized_resonance,
        "memory": 0.0,
        "momentum": 0.0,
        "error_rate": 0.0,
        "queue_depth": 0.0,
        "latency_ms": 0.0,
        "preferred_task_types": [route_name],
        "burst_allowed": stigma_level < 3,
    }


def _build_nodedb_headers(*, url: str, request_id: str, content_type: str) -> dict[str, str]:
    headers = {
        "Content-Type": content_type,
        "X-CLX-Event-Type": "clx_hybrid_ndb_event",
        "X-CLX-Request-Id": request_id,
        "X-CLX-Role": _env("NODEDB_FLUID_ROLE", NODEDB_FLUID_ROLE),
    }
    api_key = _env("NODEDB_FLUID_API_KEY", "")
    if api_key:
        headers["X-API-Key"] = api_key
    hmac_secret = _env("NODEDB_FLUID_HMAC_SECRET", "")
    if hmac_secret:
        timestamp = str(int(time.time()))
        path = urlsplit(url).path or "/"
        message = f"POST\n{path}\n{timestamp}".encode("utf-8")
        headers["X-CLX-Timestamp"] = timestamp
        headers["X-CLX-Signature"] = hmac.new(
            hmac_secret.encode("utf-8"), message, hashlib.sha256
        ).hexdigest()
    return headers


async def _write_nodedb_event(
    *,
    request_id: str,
    route_name: str,
    stigma_profile: str,
    tide_route: str,
    resonance_ndb: float,
    resonance_decibel: float,
    resonance_score: float,
    stigma_level: int,
    mirror_level: int,
) -> dict[str, Any]:
    nodedb_url = _env("NODEDB_FLUID_URL", NODEDB_FLUID_URL)
    if not nodedb_url:
        return {"status": "not_configured", "message": None}

    transport = _env("NODEDB_FLUID_TRANSPORT", NODEDB_FLUID_TRANSPORT).lower()
    if transport == "auto":
        transport = "osclx_json" if nodedb_url.rstrip("/").endswith("/telemetry") else "binary"
    if transport not in {"osclx_json", "binary"}:
        return {"status": "error", "message": "unsupported_nodedb_transport"}

    payload: bytes | None = None
    json_payload: dict[str, Any] | None = None
    if transport == "binary":
        try:
            payload = _build_nodedb_binary_payload(
                request_id=request_id,
                route_name=route_name,
                stigma_profile=stigma_profile,
                tide_route=tide_route,
                resonance_ndb=resonance_ndb,
                resonance_decibel=resonance_decibel,
                stigma_level=stigma_level,
                mirror_level=mirror_level,
            )
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}
    else:
        json_payload = _build_osclx_telemetry(
            route_name=route_name,
            stigma_profile=stigma_profile,
            tide_route=tide_route,
            resonance_score=resonance_score,
            stigma_level=stigma_level,
        )

    timeout = httpx.Timeout(REQUEST_TIMEOUT_SECONDS)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = _build_nodedb_headers(
                url=nodedb_url,
                request_id=request_id,
                content_type="application/json" if transport == "osclx_json" else "application/octet-stream",
            )
            headers["X-CLX-Stigma-Profile"] = stigma_profile
            headers["X-CLX-Tide-Route"] = tide_route
            if transport == "osclx_json":
                response = await client.post(nodedb_url, json=json_payload, headers=headers)
            else:
                response = await client.post(nodedb_url, content=payload, headers=headers)
        if 200 <= response.status_code < 300:
            return {
                "status": "persisted",
                "status_code": response.status_code,
                "transport": transport,
                "bytes": len(payload) if payload is not None else len(response.request.content),
            }
        return {
            "status": "error",
            "status_code": response.status_code,
            "message": "nodedb_rejected_event",
        }
    except httpx.HTTPError as exc:
        return {"status": "error", "message": str(exc)}


@app.get("/health")
async def health() -> dict[str, Any]:
    api_url = _env("CLX_HYBRID_API_URL", API_URL)
    ocean_url = _env("CLX_HYBRID_OCEAN_URL", OCEAN_URL)
    clx_agent_url = _env("CLX_HYBRID_CLX_AGENT_URL", CLX_AGENT_URL)
    clxi_url = _env("CLX_HYBRID_CLXI_URL", CLXI_URL)

    api_dep = await _check_dependency(api_url)
    ocean_dep = await _check_dependency(ocean_url)
    clx_agent_dep = await _check_dependency(clx_agent_url)
    clxi_dep = await _check_dependency(clxi_url)

    require_nodedb = _env_bool("CLX_HYBRID_REQUIRE_NODEDB_FLUID", REQUIRE_NODEDB_FLUID)
    nodedb_url = _env("NODEDB_FLUID_URL", NODEDB_FLUID_URL)
    if require_nodedb and not nodedb_url:
        nodedb_status = {"status": "required_not_configured", "required": True}
    else:
        nodedb_status = {
            "status": "configured" if nodedb_url else "not_configured",
            "required": require_nodedb,
        }

    deps = {
        "api": api_dep.model_dump(),
        "ocean_core": ocean_dep.model_dump(),
        "clx_agent": clx_agent_dep.model_dump(),
        "clx_i": clxi_dep.model_dump(),
        "nodedb_fluid": nodedb_status,
    }

    overall = "healthy"
    critical = [api_dep.status, ocean_dep.status, clx_agent_dep.status]
    if any(v != "up" for v in critical):
        overall = "degraded"
    if require_nodedb and not nodedb_url:
        overall = "degraded"

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": overall,
        "timestamp": _utcnow(),
        "dependencies": deps,
    }


@app.post("/api/v1/hybrid/scan-print", response_model=HybridScanResponse)
async def hybrid_scan_print(req: HybridScanRequest) -> HybridScanResponse:
    started = time.perf_counter()
    request_id = f"clxhy_{int(time.time() * 1000)}"

    require_nodedb = _env_bool("CLX_HYBRID_REQUIRE_NODEDB_FLUID", REQUIRE_NODEDB_FLUID)
    nodedb_url = _env("NODEDB_FLUID_URL", NODEDB_FLUID_URL)
    if require_nodedb and not nodedb_url:
        raise HTTPException(status_code=503, detail="nodedb_fluid_required_not_configured")

    score = req.resonance_score if req.resonance_score is not None else _derive_resonance_score(req.text, req.stigma_level)
    score = max(0.0, min(1.0, float(score)))

    resonance_db = resonance_to_decibel(score)
    resonance_ndb = resonance_to_nanodecibel(score)
    stigma_profile = get_profile_for_resonance(resonance_ndb)

    tide_route = _resolve_tide_route(req.tide_mode, stigma_profile.name)
    include_firewall = req.stigma_level >= 3 and tide_route == "old_technology"

    stream = ScannerPrinterStream(input_text=req.text, resonance_score=score)
    phases: list[dict[str, Any]] = []
    async for phase in stream.stream_phases(
        matched=True,
        route_name=req.route_name,
        model="hybrid_scanner_printer",
        include_firewall=include_firewall,
    ):
        phases.append(phase)

    nodedb_status = await _write_nodedb_event(
        request_id=request_id,
        route_name=req.route_name,
        stigma_profile=stigma_profile.name,
        tide_route=tide_route,
        resonance_ndb=resonance_ndb,
        resonance_decibel=resonance_db,
        resonance_score=score,
        stigma_level=req.stigma_level,
        mirror_level=req.mirror_level,
    )
    if nodedb_status.get("status") != "persisted":
        raise HTTPException(status_code=503, detail={"code": "nodedb_persist_failed", "nodedb": nodedb_status})

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if elapsed_ms <= 0:
        raise HTTPException(status_code=500, detail="invalid_processing_time")

    return HybridScanResponse(
        service=APP_NAME,
        version=APP_VERSION,
        request_id=request_id,
        timestamp=_utcnow(),
        resonance_score=round(score, 6),
        resonance_decibel=round(resonance_db, 3),
        resonance_ndb=round(resonance_ndb, 3),
        stigma={
            "requested_level": req.stigma_level,
            "selected_profile": stigma_profile.name,
            "profile_mode": stigma_profile.mode.value,
            "profile_config": stigma_profile.get_config(),
        },
        tide={
            "mode": req.tide_mode,
            "route": tide_route,
            "processing_time_ms": round(elapsed_ms, 3),
        },
        transport={
            "type": "scanner_printer_stream",
            "replaces_streaming": True,
            "wwwmmm": True,
            "nanodecibel": True,
            "hybrid_old_new": True,
        },
        phases=phases,
        nodedb_fluid=nodedb_status,
    )

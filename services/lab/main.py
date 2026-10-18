import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException, Query, Request

from signal_fabric import SignalEvent, SignalLevel, get_signal_fabric

LAB_ID = os.getenv("LAB_ID", "unknown-lab")
PORT = int(os.getenv("PORT", "9100"))
ANALYSIS_UPSTREAM = os.getenv("ANALYSIS_UPSTREAM", "").strip()
ANALYSIS_HEALTH_URL = os.getenv("ANALYSIS_HEALTH_URL", "http://clisonix-ocean-core:8030/health").strip()
ANALYSIS_TIMEOUT_SECONDS = float(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "45"))
ANALYSIS_HEALTH_TIMEOUT_SECONDS = float(os.getenv("ANALYSIS_HEALTH_TIMEOUT_SECONDS", "2.0"))
REGISTRY_PATH = Path(os.getenv("CITY_LABS_REGISTRY", "/app/config/city-labs.registry.json"))


def load_identity() -> Dict[str, str]:
    fallback = {
        "lab_id": LAB_ID,
        "lab_type": os.getenv("LAB_TYPE", "General"),
        "name": os.getenv("LAB_NAME", LAB_ID),
        "function": os.getenv("LAB_FUNCTION", "General research"),
        "city": os.getenv("LAB_CITY", "Unknown"),
        "country": os.getenv("LAB_COUNTRY", "Unknown"),
    }
    if not REGISTRY_PATH.exists():
        return fallback
    try:
        payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        match = next((item for item in payload.get("labs", []) if item.get("lab_id") == LAB_ID), None)
        if match:
            return {**fallback, **{key: str(value) for key, value in match.items() if key in fallback}}
    except (OSError, ValueError, TypeError):
        pass
    return fallback


IDENTITY = load_identity()
LAB_TYPE = IDENTITY["lab_type"]
LAB_NAME = IDENTITY["name"]
LAB_FUNCTION = IDENTITY["function"]
LAB_CITY = IDENTITY["city"]
LAB_COUNTRY = IDENTITY["country"]
SIGNAL_SOURCE = f"city-lab:{LAB_ID}"

CAPABILITIES: Dict[str, List[str]] = {
    "AI": ["machine_learning", "nlp", "computer_vision", "agent_orchestration"],
    "Medical": ["clinical_data", "bioscience", "sensor_analysis", "research_workflows"],
    "IoT": ["sensors", "edge_computing", "device_networks", "telemetry"],
    "Marine": ["oceanography", "marine_biology", "environmental_monitoring", "sensor_analysis"],
    "Environmental": ["climate", "pollution", "ecology", "sustainability"],
    "Agricultural": ["crop_science", "soil_analysis", "precision_farming", "environmental_monitoring"],
    "Underwater": ["underwater_observation", "marine_archaeology", "sensor_analysis", "exploration"],
    "Security": ["cybersecurity", "network_defense", "threat_analysis", "runtime_isolation"],
    "Energy": ["renewables", "power_systems", "energy_telemetry", "forecasting"],
    "Academic": ["research", "knowledge_analysis", "document_intelligence", "heritage"],
    "Architecture": ["design", "engineering", "urban_planning", "restoration"],
    "Finance": ["risk_analysis", "market_data", "blockchain", "financial_research"],
    "Industrial": ["manufacturing", "automation", "optimization", "quality"],
    "Chemistry": ["materials", "compounds", "experimental_data", "research"],
    "Biotech": ["genetics", "bioinformatics", "experimental_data", "clinical_data"],
    "Quantum": ["quantum_computing", "simulation", "cryptography", "research"],
    "Neuroscience": ["brain_data", "cognition", "signal_analysis", "research_workflows"],
    "Robotics": ["robotics", "automation", "sensor_fusion", "edge_control"],
    "Data": ["analytics", "visualization", "data_processing", "observability"],
    "Nanotechnology": ["nanomaterials", "nanoelectronics", "experimental_data", "research"],
    "Trade": ["logistics", "commerce", "supply_chain", "market_analysis"],
    "Archeology": ["preservation", "artifact_analysis", "documentation", "research"],
    "Heritage": ["restoration", "preservation", "documentation", "knowledge_analysis"],
}

app = FastAPI(
    title=f"Clisonix City Lab - {LAB_NAME}",
    version="1.3.0",
    description="Shared Clisonix City Labs runtime with context-aware Ocean analysis and traceable Signal Fabric evidence.",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def capabilities_for_lab() -> List[str]:
    return CAPABILITIES.get(LAB_TYPE, ["research", "analysis", "telemetry"])


async def analysis_readiness() -> Dict[str, Any]:
    if not ANALYSIS_UPSTREAM or not ANALYSIS_HEALTH_URL:
        return {"ready": False, "status": "not_configured", "latency_ms": None}
    started = time.perf_counter()
    try:
        timeout = httpx.Timeout(ANALYSIS_HEALTH_TIMEOUT_SECONDS, connect=ANALYSIS_HEALTH_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(ANALYSIS_HEALTH_URL)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "ready": 200 <= response.status_code < 300,
            "status": "reachable" if 200 <= response.status_code < 300 else "degraded",
            "http_status": response.status_code,
            "latency_ms": latency_ms,
        }
    except httpx.HTTPError as exc:
        return {
            "ready": False,
            "status": "unreachable",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "error": type(exc).__name__,
        }


def manifest() -> Dict[str, Any]:
    return {
        "schema": "clisonix.city-lab.manifest/v1",
        "lab_id": LAB_ID,
        "name": LAB_NAME,
        "city": LAB_CITY,
        "country": LAB_COUNTRY,
        "lab_type": LAB_TYPE,
        "function": LAB_FUNCTION,
        "status": "operational",
        "capabilities": capabilities_for_lab(),
        "runtime": {
            "port": PORT,
            "analysis_upstream_configured": bool(ANALYSIS_UPSTREAM),
            "analysis_contract": "clisonix.city-lab.analysis/v1",
            "trace_provider": "signal_fabric",
            "identity_source": "registry" if REGISTRY_PATH.exists() else "environment-fallback",
        },
        "ui": {"shell": "kameleon", "sections": ["live", "lab", "intelligence", "city", "system"]},
        "timestamp": now_iso(),
    }


def normalize_request(payload: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
    raw_message = payload.get("message") or payload.get("query") or payload.get("goal") or payload.get("prompt")
    if not isinstance(raw_message, str) or not raw_message.strip():
        raise HTTPException(status_code=422, detail="Analysis requires one of: message, query, goal, prompt")
    message = raw_message.strip()
    caller_context = payload.get("context")
    if not isinstance(caller_context, (dict, list)):
        caller_context = {} if caller_context is None else {"value": caller_context}
    lab_context = {
        "lab_id": LAB_ID,
        "name": LAB_NAME,
        "city": LAB_CITY,
        "country": LAB_COUNTRY,
        "lab_type": LAB_TYPE,
        "function": LAB_FUNCTION,
        "capabilities": capabilities_for_lab(),
    }
    context = {
        "city_lab": lab_context,
        "caller": caller_context,
        "operating_environment": {
            "orchestrator": "Ocean",
            "memory": "NodeDB",
            "runtime": "OS-CLX/Kloud",
            "trace_id": trace_id,
        },
    }
    return {
        "message": message,
        "query": message,
        "goal": payload.get("goal") or message,
        "session_id": payload.get("session_id") or f"citylab-{LAB_ID}-{trace_id[:12]}",
        "context": context,
        "lab_context": lab_context,
        "trace_id": trace_id,
    }


def extract_result(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    for key in ("ocean_response", "response", "answer", "result", "message"):
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return payload


async def publish(kind: str, trace_id: str, level: SignalLevel, message: str, payload: Dict[str, Any]) -> None:
    await get_signal_fabric().publish(
        SignalEvent(
            source=SIGNAL_SOURCE,
            kind=kind,
            level=level,
            message=message,
            payload=payload,
            trace_id=trace_id,
            tags=["city-lab", LAB_TYPE.lower(), LAB_CITY.lower().replace(" ", "-")],
        )
    )


@app.get("/")
async def root() -> Dict[str, Any]:
    return manifest()


@app.get("/health")
async def health() -> Dict[str, Any]:
    readiness = await analysis_readiness()
    return {
        "status": "healthy",
        "lab_id": LAB_ID,
        "lab": LAB_NAME,
        "type": LAB_TYPE,
        "analysis_ready": readiness["ready"],
        "analysis": readiness,
        "timestamp": now_iso(),
    }


@app.get("/readiness")
async def readiness() -> Dict[str, Any]:
    analysis = await analysis_readiness()
    return {
        "status": "ready" if analysis["ready"] else "degraded",
        "runtime_ready": True,
        "analysis_ready": analysis["ready"],
        "analysis": analysis,
        "lab_id": LAB_ID,
        "timestamp": now_iso(),
    }


@app.get("/manifest")
async def get_manifest() -> Dict[str, Any]:
    return manifest()


@app.get("/capabilities")
async def capabilities() -> Dict[str, Any]:
    caps = capabilities_for_lab()
    return {"lab_id": LAB_ID, "lab_type": LAB_TYPE, "capabilities": caps, "total": len(caps)}


@app.get("/traces")
async def traces(limit: int = Query(default=50, ge=1, le=500)) -> Dict[str, Any]:
    rows = [item for item in get_signal_fabric().all_signals(limit=max(limit * 4, 100)) if item.get("source") == SIGNAL_SOURCE]
    rows = rows[-limit:]
    return {"lab_id": LAB_ID, "total": len(rows), "events": rows, "timestamp": now_iso()}


@app.get("/traces/{trace_id}")
async def trace(trace_id: str) -> Dict[str, Any]:
    rows = [item for item in get_signal_fabric().all_signals(limit=5000) if item.get("source") == SIGNAL_SOURCE and item.get("trace_id") == trace_id]
    if not rows:
        raise HTTPException(status_code=404, detail=f"Trace not found: {trace_id}")
    return {"lab_id": LAB_ID, "trace_id": trace_id, "events": rows, "timestamp": now_iso()}


@app.post("/analyze")
async def analyze(request: Request) -> Dict[str, Any]:
    if not ANALYSIS_UPSTREAM:
        raise HTTPException(status_code=503, detail="No ANALYSIS_UPSTREAM configured; refusing to fabricate an analysis result.")
    try:
        payload = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="Analysis request must be a JSON object")

    trace_id = request.headers.get("x-trace-id") or payload.get("trace_id") or str(uuid.uuid4())
    normalized = normalize_request(payload, trace_id)
    started = time.perf_counter()
    await publish("analysis.started", trace_id, SignalLevel.INFO, "City Lab analysis started", {"lab_id": LAB_ID, "lab_type": LAB_TYPE, "goal": normalized["goal"]})
    headers = {"content-type": "application/json", "x-clisonix-lab-id": LAB_ID, "x-clisonix-lab-type": LAB_TYPE, "x-trace-id": trace_id}

    try:
        timeout = httpx.Timeout(ANALYSIS_TIMEOUT_SECONDS, connect=min(5.0, ANALYSIS_TIMEOUT_SECONDS))
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(ANALYSIS_UPSTREAM, json=normalized, headers=headers)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        if response.status_code >= 400:
            body = response.text[:500]
            await publish("analysis.failed", trace_id, SignalLevel.ERROR, "Ocean analysis returned an error", {"lab_id": LAB_ID, "http_status": response.status_code, "latency_ms": latency_ms})
            raise HTTPException(status_code=502, detail=f"Analysis upstream HTTP {response.status_code}: {body}")
    except HTTPException:
        raise
    except httpx.TimeoutException as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        await publish("analysis.failed", trace_id, SignalLevel.ERROR, "Ocean analysis timed out", {"lab_id": LAB_ID, "latency_ms": latency_ms, "reason": "timeout"})
        raise HTTPException(status_code=504, detail="Analysis upstream timed out") from exc
    except httpx.HTTPError as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        await publish("analysis.failed", trace_id, SignalLevel.ERROR, "Ocean analysis unavailable", {"lab_id": LAB_ID, "latency_ms": latency_ms, "reason": type(exc).__name__})
        raise HTTPException(status_code=502, detail=f"Analysis upstream unavailable: {exc}") from exc

    try:
        upstream_payload: Any = response.json()
    except ValueError:
        upstream_payload = {"text": response.text}
    result = extract_result(upstream_payload)
    evidence = {
        "trace_id": trace_id,
        "lab_id": LAB_ID,
        "lab_type": LAB_TYPE,
        "orchestrator": "Ocean",
        "http_status": response.status_code,
        "latency_ms": latency_ms,
        "signal_fabric": True,
        "analysis_contract": "clisonix.city-lab.analysis/v1",
    }
    await publish("analysis.completed", trace_id, SignalLevel.INFO, "City Lab analysis completed", evidence)
    return {
        "schema": "clisonix.city-lab.analysis/v1",
        "status": "completed",
        "trace_id": trace_id,
        "lab": normalized["lab_context"],
        "result": result,
        "upstream": upstream_payload,
        "evidence": evidence,
        "timestamp": now_iso(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

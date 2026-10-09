#!/usr/bin/env python3
"""ASI Realtime Engine API Server"""
from datetime import datetime
from typing import Any, Awaitable, Callable

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from asi_core import ASICore, ClisonixMeshNode, ClisonixNodeReal

create_jona_real: Callable[[], Awaitable[Any]] | None

try:
    from apps.api.services.jona_real_monitor import create_jona_real
except Exception:
    create_jona_real = None

# API Version
API_V1 = "/api/v1"

app = FastAPI(
    title="ASI Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RootResponse(BaseModel):
    service: str
    version: str
    status: str
    endpoints: dict[str, str]


class HealthResponse(BaseModel):
    status: str
    engine: str
    health_score: float | None
    timestamp: str | None


class LogsResponse(BaseModel):
    count: int
    items: list[dict[str, Any]]
    timestamp: str


class OperationResponse(BaseModel):
    status: str
    operation: str
    node_id: str
    timestamp: str


class JointStatusResponse(BaseModel):
    asi: dict[str, Any]
    jona: dict[str, Any]
    timestamp: str

asi = ASICore()
node = ClisonixNodeReal(asi)
mesh = ClisonixMeshNode(asi)

@app.get("/", response_model=RootResponse)
def root():
    return {
        "service": "ASI Realtime Engine",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "GET /health": "Health check",
            "GET /status": "Realtime status",
            "GET /api/status": "API status",
            "GET /metrics": "Engine metrics",
            "GET /nodes": "ASI nodes",
            "GET /logs": "Recent ASI logs",
            "GET /system": "Host system metrics",
            "POST /mesh/register": "Register node with mesh service",
            "POST /mesh/send": "Send node telemetry to mesh service",
            "GET /asi/joint-status": "ASI + JONA real combined status"
        }
    }

@app.get("/health", response_model=HealthResponse)
def health():
    snapshot = asi.get_health_snapshot()
    return {
        "status": "operational",
        "engine": "ASI Realtime",
        "health_score": snapshot.get("health_score"),
        "timestamp": snapshot.get("timestamp"),
    }

@app.get("/status")
@app.get("/api/status")
@app.get(API_V1 + "/status")
def status():
    try:
        rt_status = asi.get_realtime_status()
        rt_status["timestamp"] = datetime.utcnow().isoformat()
        return rt_status
    except Exception as e:
        return {
            "status": "operational",
            "service": "ASI Engine",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get(API_V1 + "/spec")
def api_spec():
    return app.openapi()

@app.get("/metrics")
def metrics():
    return asi.realtime_engine.collect_metrics()

@app.get("/nodes")
def nodes():
    return asi.nodes

@app.get("/logs", response_model=LogsResponse)
@app.get(API_V1 + "/logs", response_model=LogsResponse)
def logs():
    return {
        "count": len(asi.logs),
        "items": asi.logs[-20:],
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/system")
@app.get(API_V1 + "/system")
def system_metrics():
    try:
        return node.collect_system_metrics()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to collect system metrics: {exc}")

@app.post("/mesh/register", response_model=OperationResponse)
@app.post(API_V1 + "/mesh/register", response_model=OperationResponse)
def mesh_register():
    mesh.register_node()
    return {
        "status": "ok",
        "operation": "mesh_register",
        "node_id": mesh.node_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.post("/mesh/send", response_model=OperationResponse)
@app.post(API_V1 + "/mesh/send", response_model=OperationResponse)
def mesh_send():
    mesh.send_status()
    return {
        "status": "ok",
        "operation": "mesh_send",
        "node_id": mesh.node_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/asi/joint-status", response_model=JointStatusResponse)
@app.get(API_V1 + "/asi/joint-status", response_model=JointStatusResponse)
async def asi_joint_status():
    asi_snapshot = asi.get_health_snapshot()
    if create_jona_real is None:
        return {
            "asi": asi_snapshot,
            "jona": {
                "available": False,
                "error": "jona_real_monitor_not_importable",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    try:
        jona = await create_jona_real()
        jona_health = await jona.monitor_real_system_health()
        jona_harmony = await jona.calculate_real_harmony_score()
        jona_status = await jona.get_real_status()
        return {
            "asi": asi_snapshot,
            "jona": {
                "available": True,
                "status": jona_status,
                "health": jona_health,
                "harmony": jona_harmony,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as exc:
        return {
            "asi": asi_snapshot,
            "jona": {
                "available": False,
                "error": str(exc),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9094)

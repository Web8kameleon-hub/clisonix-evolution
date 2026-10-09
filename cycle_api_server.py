#!/usr/bin/env python3
"""Cycle Engine API Server - API v1 Compliant"""
from fastapi import FastAPI
from cycle_engine import CycleEngine, CycleDefinition
import uvicorn
import os
import time

API_V1 = os.getenv("API_V1", "/api/v1")
START_TIME = time.time()

app = FastAPI(
    title="Cycle Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
engine = CycleEngine()

@app.get("/health")
def health():
    return {"status": "operational", "engine": "Cycle Engine", "active_cycles": engine.metrics.get("active_cycles", 0)}


@app.get(API_V1 + "/status")
def api_status():
    return {
        "service": "Cycle Engine",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - START_TIME),
        "active_cycles": engine.metrics.get("active_cycles", 0),
        "total_cycles": len(engine.cycles)
    }


@app.get(API_V1 + "/spec")
def api_spec():
    return app.openapi()


@app.get("/cycles")
def list_cycles():
    return {"cycles": list(engine.cycles.keys()), "total": len(engine.cycles)}

@app.post("/cycles/create")
def create_cycle(domain: str = "general", task: str = "monitor"):
    cycle_def = engine.create_cycle(domain=domain, task=task)
    return {"created": cycle_def.cycle_id, "status": "registered"}

@app.get("/metrics")
def get_metrics():
    return engine.metrics

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9095)

"""
Copyright (c) Clisonix Cloud. All rights reserved.
Closed Source License.
"""

import logging
import time

import psutil
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from industrial_data import router as industrial_router

try:
    from apps.api.routes.model_governance_routes import (
        router as model_governance_router,
    )
except Exception:
    model_governance_router = None

app = FastAPI(title="Clisonix Industrial API", description="Industrial backend for monitoring, logging, and control.")
app.include_router(industrial_router)
if model_governance_router is not None:
    app.include_router(model_governance_router)

@app.get("/status")
def get_status():
    return {
        "uptime": time.time(),
        "cpu_percent": psutil.cpu_percent(),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
        "active_users": 1,
        "system": "Clisonix Industrial"
    }

@app.post("/log")
def log_event(request: Request):
    data = request.json()
    logging.info(f"Industrial log: {data}")
    return {"status": "logged", "data": data}

@app.post("/control")
def control_system(request: Request):
    data = request.json()
    return {"status": "control received", "data": data}

@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/dashboard")
def dashboard():
    return {
        "system": "Clisonix Industrial",
        "status": "active",
        "metrics": {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage("/").percent
        }
    }



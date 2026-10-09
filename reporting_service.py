#!/usr/bin/env python3
"""
Standalone Reporting service wrapper.

Exposes the existing reporting router from apps/api/reporting_api.py as a
dedicated service with its own health and status endpoints.
"""

import os
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

APP_ROOT = Path(__file__).resolve().parent
API_ROOT = APP_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from reporting_api import router as reporting_router  # type: ignore


app = FastAPI(
    title="Clisonix Reporting Service",
    description="Dedicated reporting service backed by the real reporting router",
    version="1.0.0",
)

app.include_router(reporting_router)


@app.get("/")
def root():
    return {
        "service": "reporting",
        "status": "operational",
        "docs": "/docs",
        "router_prefix": "/api/reporting",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "reporting",
    }


@app.get("/status")
def status():
    return {
        "service": "reporting",
        "reports_dir": str((APP_ROOT / "reports").resolve()),
        "docker_host": os.getenv("DOCKER_HOST"),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
#!/usr/bin/env python3
"""
Clisonix Health Monitor service.

Real monitoring service that probes configured microservice health endpoints and
reports live status instead of returning a static stub payload.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Optional

import httpx
import uvicorn
from fastapi import FastAPI

PORT = int(os.getenv("PORT", "8099"))

app = FastAPI(
    title="Clisonix Health Monitor",
    description="Real-time health monitoring for Clisonix microservices",
    version="1.0.0",
)

SERVICES: Dict[str, int] = {
    "postgres": 5432,
    "redis": 6379,
    "neo4j": 7474,
    "victoriametrics": 8428,
    "minio": 9000,
    "ollama": 11434,
    "ollama-multi-api": 4444,
    "ocean-core": 8030,
    "alba": 5555,
    "albi": 6680,
    "jona": 7777,
    "asi": 9094,
    "alphabet-layers": 8061,
    "liam": 8062,
    "alda": 8063,
    "alba-idle": 8031,
    "blerina": 8035,
    "cycle-engine": 8070,
    "saas-orchestrator": 9999,
    "personas": 9200,
    "agiem": 9300,
    "datasource-europe": 9301,
    "datasource-americas": 9302,
    "datasource-asia": 9303,
    "datasource-india": 9304,
    "datasource-africa": 9305,
    "datasource-oceania": 9306,
    "datasource-central-asia": 9307,
    "datasource-antarctica": 9308,
    "reporting": 8001,
    "excel": 8002,
    "behavioral": 8003,
    "analytics": 8016,
    "neurosonix": 8015,
    "aviation": 8080,
    "multi-tenant": 8007,
    "quantum": 8008,
    "curiosity": 8019,
    "api": 8000,
    "web": 3000,
    "prometheus": 9090,
    "grafana": 3001,
    "loki": 3100,
    "jaeger": 16686,
    "tempo": 3200,
    "agent-telemetry": 8009,
    "cognitive-engine": 8010,
    "adaptive-router": 8011,
}

health_cache: Dict[str, Dict] = {}
last_check: Optional[datetime] = None


async def check_service_health(name: str, port: int) -> Dict:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            for url in (f"http://{name}:{port}/health", f"http://{name}:{port}/", f"http://localhost:{port}/health"):
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        return {
                            "status": "UP",
                            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
                        }
                except Exception:
                    continue
    except Exception:
        pass
    return {"status": "DOWN", "response_time_ms": None}


async def check_all_services() -> Dict:
    global health_cache, last_check
    tasks = [check_service_health(name, port) for name, port in SERVICES.items()]
    results = await asyncio.gather(*tasks)
    health_cache = {
        name: {**result, "port": port}
        for (name, port), result in zip(SERVICES.items(), results)
    }
    last_check = datetime.utcnow()
    return health_cache


@app.get("/")
def root():
    return {
        "service": "Clisonix Health Monitor",
        "version": "1.0.0",
        "total_services": len(SERVICES),
        "status": "operational",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "health-monitor",
        "monitored_services": len(SERVICES),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/status")
async def status():
    await check_all_services()
    up_count = sum(1 for service in health_cache.values() if service["status"] == "UP")
    down_count = len(SERVICES) - up_count
    return {
        "services": health_cache,
        "summary": {
            "total": len(SERVICES),
            "up": up_count,
            "down": down_count,
            "health_percentage": round((up_count / len(SERVICES)) * 100, 1),
        },
        "last_check": last_check.isoformat() if last_check else None,
    }


@app.get("/status/{service_name}")
async def service_status(service_name: str):
    if service_name not in SERVICES:
        return {"error": f"Unknown service: {service_name}"}
    port = SERVICES[service_name]
    result = await check_service_health(service_name, port)
    return {
        "service": service_name,
        "port": port,
        **result,
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

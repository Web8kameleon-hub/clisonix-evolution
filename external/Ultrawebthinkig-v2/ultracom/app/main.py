import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ultracom.app.storage import init_db
from ultracom.app.routers import (
    ads_enterprise,
    agi_inference,
    auth_enterprise,
    chat,
    extended,
    health,
    paywall,
)

# Load ultracom/.env automatically — single source of truth
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class ManagerRequest(BaseModel):
    message: str
    clientId: str = "client-001"


class ActivityRecord(BaseModel):
    id: str
    layer: str
    process: str
    status: str
    timestamp: str
    input: str
    duration_ms: float | None = None
    upstream: str | None = None


app = FastAPI(
    title="UltraCom - AI Manager System",
    version="3.0.0",
    description="Complete Autonomous Chat System - Zero Human Intervention",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(agi_inference.router)
app.include_router(extended.router)
app.include_router(auth_enterprise.router)
app.include_router(paywall.router)
app.include_router(ads_enterprise.router)

MANAGER_TIMEOUT = float(os.getenv("MANAGER_TIMEOUT", "30"))
MANAGER_ROUTE_SENSOR = os.getenv("MANAGER_ROUTE_SENSOR", "").strip()
MANAGER_ROUTE_ANALYTICS = os.getenv("MANAGER_ROUTE_ANALYTICS", "").strip()
MANAGER_ROUTE_NEWS = os.getenv("MANAGER_ROUTE_NEWS", "").strip()

layer_activities: list[ActivityRecord] = []


def _pick_manager_upstream(client_message: str) -> str:
    lowered = client_message.lower()
    if any(word in lowered for word in ["sensor", "iot", "temperature", "alba"]):
        return MANAGER_ROUTE_SENSOR
    if any(
        word in lowered for word in ["analytics", "diagnostic", "performance", "asi"]
    ):
        return MANAGER_ROUTE_ANALYTICS
    if any(word in lowered for word in ["news", "financial", "economic"]):
        return MANAGER_ROUTE_NEWS
    return ""


def _activity_dict(record: ActivityRecord) -> dict[str, Any]:
    return record.model_dump()


# AI Manager endpoints - PURE REAL API
@app.get("/manager/health")
async def ai_manager_health():
    """AI manager health check."""
    return {
        "status": "OPERATIONAL",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
    }


@app.post("/manager/handle")
async def ai_manager_handle(request: ManagerRequest):
    """Route manager requests to configured real upstream services only."""
    client_message = request.message

    activity_id = f"ai_manager_{int(time.time() * 1000)}"
    start_time = time.time()

    activity = ActivityRecord(
        id=activity_id,
        layer="AI Manager",
        process="Request Processing",
        status="processing",
        timestamp=datetime.now().isoformat(),
        input=client_message[:100],
    )
    layer_activities.append(activity)

    upstream_url = _pick_manager_upstream(client_message)
    if not upstream_url:
        activity.status = "failed"
        activity.duration_ms = round((time.time() - start_time) * 1000, 2)
        raise HTTPException(
            status_code=422,
            detail={
                "error": "unroutable_request",
                "message": "No upstream route matched this request message",
            },
        )

    try:
        async with httpx.AsyncClient(timeout=MANAGER_TIMEOUT) as client:
            resp = await client.post(
                upstream_url,
                json={"message": client_message, "clientId": request.clientId},
            )
        if resp.status_code >= 400:
            raise HTTPException(
                status_code=resp.status_code,
                detail={
                    "error": "upstream_request_failed",
                    "status": resp.status_code,
                    "upstream": upstream_url,
                },
            )

        end_time = time.time()
        activity.status = "completed"
        activity.duration_ms = round((end_time - start_time) * 1000, 2)
        activity.upstream = upstream_url
        return {
            "success": True,
            "category": "real_api",
            "handledBy": f"Real API: {upstream_url}",
            "timestamp": datetime.now().isoformat(),
            "realApiData": resp.json(),
        }
    except HTTPException:
        end_time = time.time()
        activity.status = "failed"
        activity.duration_ms = round((end_time - start_time) * 1000, 2)
        activity.upstream = upstream_url
        raise
    except Exception as error:
        end_time = time.time()
        activity.status = "failed"
        activity.duration_ms = round((end_time - start_time) * 1000, 2)
        activity.upstream = upstream_url
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_unavailable",
                "message": str(error),
                "upstream": upstream_url,
            },
        )


@app.get("/api/system-layers")
async def system_layers():
    """Return tracked real manager activities only."""
    end_time = time.time()
    completed = [item for item in layer_activities if item.status == "completed"]
    failed = [item for item in layer_activities if item.status == "failed"]
    return {
        "activities": [_activity_dict(item) for item in layer_activities[-50:]],
        "stats": {
            "processedRequests": len(layer_activities),
            "completedRequests": len(completed),
            "failedRequests": len(failed),
            "inFlight": len(
                [item for item in layer_activities if item.status == "processing"]
            ),
            "lastUpdated": datetime.utcnow().isoformat(),
            "uptimeSeconds": int(end_time),
        },
    }

@app.on_event("startup")
async def _startup():
    await init_db()

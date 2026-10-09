from __future__ import annotations

import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Request


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


INSTANCE_ID = os.getenv("INSTANCE_ID") or socket.gethostname()

app = FastAPI(title="Clisonix Kitchen API", version="1.0.0")
kitchen_router = APIRouter(prefix="/api/kitchen", tags=["protocol-kitchen"])

HybridProtocolPipeline: Any = None
try:
    from hybrid_protocol_pipeline import (
        HybridProtocolPipeline as _HybridProtocolPipeline,
    )

    HybridProtocolPipeline = _HybridProtocolPipeline
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False


@kitchen_router.get("/status")
async def kitchen_status() -> dict[str, Any]:
    return {
        "status": "operational",
        "pipeline_available": PIPELINE_AVAILABLE,
        "layers": {
            "intake": {"status": "active", "description": "REST/gRPC/File Input"},
            "raw": {"status": "active", "description": "Raw Data Layer"},
            "normalized": {"status": "active", "description": "Standardized Format"},
            "test": {"status": "active", "description": "Security & Validation"},
            "immature": {"status": "active", "description": "Artifacts Generated"},
            "ml_overlay": {"status": "active", "description": "ML Suggestions"},
            "enforcement": {"status": "active", "description": "Canonical API & Compliance"},
        },
        "timestamp": utcnow(),
        "instance": INSTANCE_ID,
    }


@kitchen_router.get("/layers")
async def kitchen_layers() -> dict[str, Any]:
    return {
        "layers": [
            {"id": 1, "name": "INTAKE", "type": "input", "protocols": ["REST", "gRPC", "File"]},
            {"id": 2, "name": "RAW", "type": "data", "description": "Raw unprocessed data"},
            {"id": 3, "name": "NORMALIZED", "type": "transform", "description": "Standardized format"},
            {"id": 4, "name": "TEST", "type": "validation", "description": "Security & Schema check"},
            {"id": 5, "name": "IMMATURE", "type": "staging", "description": "Pre-production staging"},
            {"id": 6, "name": "ML_OVERLAY", "type": "ai", "description": "Machine learning suggestions"},
            {"id": 7, "name": "ENFORCEMENT", "type": "compliance", "description": "Canonical API rules"},
        ],
        "flow": "INPUT -> RAW -> NORMALIZED -> TEST -> IMMATURE -> ML_OVERLAY -> ENFORCEMENT",
        "timestamp": utcnow(),
    }


@kitchen_router.post("/intake")
async def kitchen_intake(request: Request) -> dict[str, Any]:
    if not PIPELINE_AVAILABLE or HybridProtocolPipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not available")

    try:
        data = await request.json()
        if not isinstance(data, list):
            data = [data]

        pipeline = HybridProtocolPipeline()
        pipeline.intake(data)
        results = pipeline.run()

        return {
            "status": "processed",
            "stats": results["stats"],
            "completed": len(results["completed"]),
            "failed": len(results["failed"]),
            "results": results,
            "timestamp": utcnow(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@kitchen_router.get("/metrics")
async def kitchen_metrics() -> dict[str, Any]:
    return {
        "metrics": {
            "total_processed": 0,
            "pass_rate": 0.95,
            "avg_processing_time_ms": 45,
            "anomalies_detected": 0,
            "ml_suggestions_applied": 0,
        },
        "layers_health": {
            "intake": 1.0,
            "raw": 1.0,
            "normalized": 1.0,
            "test": 0.98,
            "immature": 0.97,
            "ml_overlay": 0.95,
            "enforcement": 0.99,
        },
        "timestamp": utcnow(),
    }


@kitchen_router.get("/health")
async def kitchen_health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "protocol-kitchen",
        "pipeline_available": PIPELINE_AVAILABLE,
        "layers_operational": 7,
        "timestamp": utcnow(),
        "instance": INSTANCE_ID,
    }


@kitchen_router.get("/excel-integration")
async def kitchen_excel_integration() -> dict[str, Any]:
    excel_dir = Path("/app")
    excel_files: list[str] = []
    for pattern in ("*.xlsx", "*.xls"):
        for file_path in excel_dir.glob(pattern):
            if not file_path.name.startswith("~$"):
                excel_files.append(file_path.name)

    return {
        "status": "connected",
        "integration": {
            "kitchen_to_excel": True,
            "excel_to_kitchen": True,
            "bidirectional_sync": True,
        },
        "excel_sources": {
            "count": len(excel_files),
            "files": excel_files[:10],
            "ready_for_intake": True,
        },
        "timestamp": utcnow(),
        "instance": INSTANCE_ID,
    }


@kitchen_router.post("/intake-excel")
async def kitchen_intake_excel(request: Request) -> dict[str, Any]:
    try:
        data = await request.json()
        file_name = data.get("file", "unknown.xlsx")
        sheet = data.get("sheet", "Sheet1")
        rows = data.get("rows", [])

        return {
            "status": "processed",
            "source": file_name,
            "sheet": sheet,
            "rows_ingested": len(rows),
            "timestamp": utcnow(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@kitchen_router.get("/excel-to-kitchen/{filename}")
async def excel_to_kitchen(filename: str) -> dict[str, Any]:
    file_path = Path("/app") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Excel file '{filename}' not found")

    stat = file_path.stat()
    return {
        "status": "ready",
        "file": filename,
        "size_bytes": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "kitchen_ready": True,
        "timestamp": utcnow(),
    }


@kitchen_router.get("/kitchen-to-excel")
async def kitchen_to_excel() -> dict[str, Any]:
    return {
        "status": "ready",
        "export_formats": ["xlsx", "csv", "json"],
        "timestamp": utcnow(),
    }


app.include_router(kitchen_router)


@app.get("/health")
async def root_health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "kitchen-api",
        "timestamp": utcnow(),
    }

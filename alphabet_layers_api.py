#!/usr/bin/env python3
"""Alphabet Layers service: real API on top of ocean-core/alphabet_layers.py."""

from __future__ import annotations

import operator
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parent
OCEAN_CORE_DIR = APP_ROOT / "ocean-core"
if str(OCEAN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(OCEAN_CORE_DIR))

try:
    from alphabet_layers import get_alphabet_layer_system  # type: ignore
except Exception as exc:  # pragma: no cover
    get_alphabet_layer_system = None
    _IMPORT_ERROR: Optional[str] = str(exc)
else:
    _IMPORT_ERROR = None


app = FastAPI(title="Alphabet Layers Service", version="1.0.0")


class ProcessRequest(BaseModel):
    query: str = Field(..., min_length=1)


def _get_system():
    if get_alphabet_layer_system is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "ALPHABET_LAYER_IMPORT_FAILED",
                "message": "Alphabet layer system is unavailable",
                "reason": _IMPORT_ERROR,
            },
        )
    return get_alphabet_layer_system()


@app.get("/health")
def health() -> dict[str, Any]:
    if get_alphabet_layer_system is None:
        return {
            "status": "degraded",
            "service": "alphabet-layers",
            "reason": _IMPORT_ERROR,
        }

    system = get_alphabet_layer_system()
    return {
        "status": "healthy",
        "service": "alphabet-layers",
        "letters": system.alphabet["size"],
        "layers": 61,
    }


@app.get("/api/v1/alphabet/stats")
def alphabet_stats() -> dict[str, Any]:
    system = _get_system()
    return system.get_layer_stats()


@app.get("/api/v1/alphabet/consciousness")
def alphabet_consciousness(text: str = Query(..., min_length=1)) -> dict[str, Any]:
    system = _get_system()
    return system.compute_consciousness(text)


@app.post("/api/v1/alphabet/process")
def alphabet_process(payload: ProcessRequest) -> dict[str, Any]:
    system = _get_system()
    return system.process_query(payload.query)


@app.get("/api/v1/curiosity/algebra/op")
def algebra_op(
    a: int = Query(...),
    b: int = Query(...),
    op: str = Query("XOR"),
    bits: int = Query(8, ge=1, le=64),
) -> dict[str, Any]:
    operations = {
        "AND": operator.and_,
        "OR": operator.or_,
        "XOR": operator.xor,
    }

    op_upper = op.upper()
    if op_upper not in operations:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "UNSUPPORTED_OPERATION",
                "message": "Supported ops: AND, OR, XOR",
                "operation": op,
            },
        )

    mask = (1 << bits) - 1
    a_masked = a & mask
    b_masked = b & mask
    result = operations[op_upper](a_masked, b_masked) & mask

    system = _get_system()
    layer_view = system.process_query(f"{op_upper} {a_masked} {b_masked}")

    return {
        "a": a_masked,
        "b": b_masked,
        "operation": op_upper,
        "bits": bits,
        "result": result,
        "binary": {
            "a": format(a_masked, f"0{bits}b"),
            "b": format(b_masked, f"0{bits}b"),
            "result": format(result, f"0{bits}b"),
        },
        "alphabet_layers": {
            "active_layers": layer_view.get("active_layers"),
            "total_complexity": layer_view.get("total_complexity"),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

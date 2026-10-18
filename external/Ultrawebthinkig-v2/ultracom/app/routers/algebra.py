from datetime import datetime
from importlib import import_module
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field



def _get_binary_algebra():
    module = import_module("app.algebra")
    return module.get_binary_algebra()


router = APIRouter(prefix="/api/algebra", tags=["algebra"])


class BinaryAlgebraRequest(BaseModel):
    operation: str = Field("xor", description="Operation: and, or, xor, not, nand, nor, xnor, shl, shr, rol, ror, add, sub, mul, div, mod")
    operand_a: int = Field(0)
    operand_b: int = Field(0)
    bits: int = Field(64, ge=1, le=64)


class BatchAlgebraRequest(BaseModel):
    operations: List[Dict[str, Any]] = Field(default_factory=list)
    mode: str = Field("sequential", description="sequential or chain")
    chain_intermediate: bool = Field(False, description="Use previous result as operand_a in chain mode")
    stop_on_error: bool = Field(True)


@router.get("/operate")
async def algebra_operate_get(op: str, a: int, b: int = 0, bits: int = 64):
    engine = _get_binary_algebra()
    result = engine.operate(a, op, b, bits)
    return {
        "success": True,
        "operation": op.upper(),
        "operand_a": a,
        "operand_b": b,
        "result": result.value,
        "result_binary": result.binary,
        "result_hex": result.hex,
        "bits": result.bits,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/operate")
async def algebra_operate_post(request: BinaryAlgebraRequest):
    engine = _get_binary_algebra()
    result = engine.operate(request.operand_a, request.operation, request.operand_b, request.bits)
    return {
        "success": True,
        "operation": request.operation.upper(),
        "operand_a": request.operand_a,
        "operand_b": request.operand_b,
        "result": result.value,
        "result_binary": result.binary,
        "result_hex": result.hex,
        "bits": result.bits,
        "ones_count": result.binary.count("1"),
        "zeros_count": result.bits - result.binary.count("1"),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/batch")
async def algebra_batch(request: BatchAlgebraRequest):
    engine = _get_binary_algebra()
    results, errors, final_result = engine.batch(
        operations=request.operations,
        mode=request.mode,
        chain_intermediate=request.chain_intermediate,
        stop_on_error=request.stop_on_error,
    )
    return {
        "success": len(errors) == 0,
        "mode": request.mode,
        "total_operations": len(request.operations),
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors if errors else None,
        "final_result": final_result,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/stats")
async def algebra_stats():
    return _get_binary_algebra().get_stats()

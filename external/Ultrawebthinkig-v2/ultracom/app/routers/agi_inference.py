from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.ollama_client import (
    OLLAMA_MODEL,
    OLLAMA_MULTIMODAL_MODEL,
    OLLAMA_URL,
    analyze_multimodal,
    generate_text,
)

router = APIRouter(prefix="/api/agi", tags=["agi-inference"])


class AGIQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    model: Optional[str] = None


class AGIMultimodalRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    image_base64: str = Field(..., min_length=32)
    model: Optional[str] = None


@router.post("/query")
async def agi_query(request: AGIQueryRequest):
    result = await generate_text(request.query, request.model)
    return {
        "success": True,
        "provider": "ollama",
        "content": result["response"],
        "model": result["model"],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/multimodal")
async def agi_multimodal(request: AGIMultimodalRequest):
    result = await analyze_multimodal(request.prompt, request.image_base64, request.model)
    return {
        "success": True,
        "provider": "ollama",
        "content": result["response"],
        "model": result["model"],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health")
async def agi_health():
    return {
        "status": "active",
        "provider": "ollama",
        "baseUrl": OLLAMA_URL,
        "defaultModel": OLLAMA_MODEL,
        "multimodalModel": OLLAMA_MULTIMODAL_MODEL,
        "timestamp": datetime.utcnow().isoformat(),
    }

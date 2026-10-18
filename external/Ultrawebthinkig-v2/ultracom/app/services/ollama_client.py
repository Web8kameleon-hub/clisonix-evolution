import os
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_MULTIMODAL_MODEL = os.getenv("OLLAMA_MULTIMODAL_MODEL", "llava:7b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))


def _endpoint(path: str) -> str:
    return f"{OLLAMA_URL}{path}"


async def generate_text(prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
    payload = {
        "model": model or OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(_endpoint("/api/generate"), json=payload)
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={"error": "ollama_request_failed", "status": response.status_code},
            )
        data = response.json()
        return {
            "model": data.get("model", payload["model"]),
            "response": data.get("response", ""),
            "done": data.get("done", True),
            "raw": data,
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={"error": "ollama_unavailable", "message": str(error)},
        )


async def analyze_multimodal(prompt: str, image_base64: str, model: Optional[str] = None) -> Dict[str, Any]:
    payload = {
        "model": model or OLLAMA_MULTIMODAL_MODEL,
        "prompt": prompt,
        "images": [image_base64],
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(_endpoint("/api/generate"), json=payload)
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={"error": "ollama_multimodal_failed", "status": response.status_code},
            )
        data = response.json()
        return {
            "model": data.get("model", payload["model"]),
            "response": data.get("response", ""),
            "done": data.get("done", True),
            "raw": data,
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={"error": "ollama_multimodal_unavailable", "message": str(error)},
        )

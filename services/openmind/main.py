import os
import time
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="OpenMind Gateway", version="1.0.0")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
SERVICE_PORT = int(os.getenv("OPENMIND_PORT", "9999"))
DEFAULT_MODEL = os.getenv("OPENMIND_MODEL", "llama3.1:8b")


class OpenMindRequest(BaseModel):
    message: str
    provider: str = "openmind"
    model: str = DEFAULT_MODEL
    options: Dict[str, Any] = Field(default_factory=dict)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "openmind",
        "status": "ready",
        "port": SERVICE_PORT,
        "providers": ["openmind", "ollama"],
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "openmind",
        "provider_count": 2,
        "timestamp": time.time(),
    }


@app.get("/status")
async def status() -> Dict[str, Any]:
    return {
        "service": "openmind",
        "ready": True,
        "providers": ["openmind", "ollama"],
        "ollama_url": OLLAMA_URL,
        "default_model": DEFAULT_MODEL,
    }


@app.get("/api/openmind/providers")
async def providers() -> Dict[str, List[str]]:
    return {"providers": ["openmind", "ollama"]}


@app.post("/api/openmind")
async def openmind_chat(payload: OpenMindRequest) -> Dict[str, Any]:
    if payload.provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": payload.model,
                        "prompt": payload.message,
                        "stream": False,
                        **payload.options,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "service": "openmind",
                    "provider": "ollama",
                    "model": payload.model,
                    "response": data.get("response", ""),
                }
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Ollama provider error: {exc}") from exc

    return {
        "service": "openmind",
        "provider": payload.provider,
        "model": payload.model,
        "response": f"OpenMind gateway accepted message: {payload.message[:200]}",
    }
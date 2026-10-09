#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-OSS 120B Microservice - Port 8031
Heavy model microservice for complex tasks
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Optional

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger("GPT-OSS-120B")

# Config
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = "gpt-oss:120b"
PORT = int(os.getenv("GPT_PORT", "8031"))
TIMEOUT = 300  # 5 minuta për model të madh

# FastAPI App
app = FastAPI(
    title="GPT-OSS 120B Microservice",
    description="Heavy model microservice for complex AI tasks",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = -1

class ChatResponse(BaseModel):
    response: str
    model: str
    time_ms: float
    btl: Optional[dict] = None

class TaskRequest(BaseModel):
    task_id: str
    message: str
    callback_url: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

# In-memory task storage
tasks: dict[str, TaskStatus] = {}

# System Prompt for GPT-OSS
SYSTEM_PROMPT = """You are GPT-OSS, a powerful 120B parameter AI model.
You excel at:
- Complex reasoning and analysis
- Code generation and review
- Scientific and technical explanations
- Creative writing and storytelling
- Multi-step problem solving

Respond in the user's language. Be thorough but concise."""

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "model": MODEL,
        "ollama": OLLAMA_HOST,
        "timeout_seconds": TIMEOUT
    }

@app.get("/model/info")
async def model_info():
    """Get model information"""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(
                f"{OLLAMA_HOST}/api/show",
                json={"name": MODEL}
            )
            if r.status_code == 200:
                return r.json()
            return {"error": "Model not found"}
        except Exception as e:
            return {"error": str(e)}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Synchronous chat - waits for response
    WARNING: May take several minutes for complex queries
    """
    start = time.perf_counter()

    system = request.system_prompt or SYSTEM_PROMPT

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            logger.info(f"🔄 Processing: {request.message[:50]}...")

            r = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": request.message}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    }
                }
            )

            elapsed_ms = (time.perf_counter() - start) * 1000

            if r.status_code == 200:
                data = r.json()
                response_text = data.get("message", {}).get("content", "")
                logger.info(f"✅ Completed in {elapsed_ms:.0f}ms")

                return ChatResponse(
                    response=response_text,
                    model=MODEL,
                    time_ms=elapsed_ms,
                    btl={
                        "bits": len(response_text.encode("utf-8")) * 8,
                        "pixels": len(response_text),
                        "chunks": data.get("eval_count", 0),
                        "unit": "BTL",
                        "nanogrid": {
                            "protocol": "nanogridata-v1",
                            "header_bytes": 14,
                            "cell_bytes": 16,
                            "payload_bytes": len(response_text.encode("utf-8")),
                            "cells": max(1, (len(response_text.encode("utf-8")) + 15) // 16),
                            "frame_bytes": 14 + (max(1, (len(response_text.encode("utf-8")) + 15) // 16) * 16),
                        },
                    }
                )

            raise HTTPException(status_code=r.status_code, detail="Model error")

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Model timeout - query too complex")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/task/submit")
async def submit_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Asynchronous task submission - returns immediately
    Use /api/v1/task/{task_id} to check status
    """
    task = TaskStatus(
        task_id=request.task_id,
        status="pending",
        created_at=datetime.now().isoformat()
    )
    tasks[request.task_id] = task

    # Process in background
    background_tasks.add_task(process_task, request)

    return {"task_id": request.task_id, "status": "pending"}

async def process_task(request: TaskRequest):
    """Background task processor"""
    task = tasks.get(request.task_id)
    if not task:
        return

    task.status = "processing"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": request.message}
                    ],
                    "stream": False
                }
            )

            if r.status_code == 200:
                data = r.json()
                task.result = data.get("message", {}).get("content", "")
                task.status = "completed"
            else:
                task.status = "failed"
                task.error = f"Model returned {r.status_code}"

    except Exception as e:
        task.status = "failed"
        task.error = str(e)

    task.completed_at = datetime.now().isoformat()

    # Callback if provided
    if request.callback_url and task.status == "completed":
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                await client.post(request.callback_url, json=task.model_dump())
        except:
            pass

@app.get("/api/v1/task/{task_id}")
async def get_task_status(task_id: str):
    """Check task status"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/api/v1/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "total": len(tasks),
        "tasks": list(tasks.values())
    }

@app.delete("/api/v1/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    if task_id in tasks:
        del tasks[task_id]
        return {"deleted": task_id}
    raise HTTPException(status_code=404, detail="Task not found")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 GPT-OSS 120B Microservice starting on port {PORT}")
    logger.info(f"📡 Ollama: {OLLAMA_HOST}")
    logger.info(f"🤖 Model: {MODEL}")
    logger.info(f"⏱️ Timeout: {TIMEOUT}s")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

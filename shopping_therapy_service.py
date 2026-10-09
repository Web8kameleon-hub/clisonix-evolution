"""
shopping_therapy_service.py — FastAPI server for Shopping Therapy Engine (port 7300)
"""
from __future__ import annotations

import asyncio
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl

from shopping_therapy_core import ShoppingEngine

# ─────────────────────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Shopping Therapy Engine",
    version="1.0.0",
    description="Lexon çdo link me shërbime shopping dhe ia shfaq userit — port 7300",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.environ.get("SHOPPING_DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)
PERSIST_PATH = os.path.join(DATA_DIR, "shopping_therapy_catalogue.json")

engine = ShoppingEngine(persist_path=PERSIST_PATH)

# ─────────────────────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = ""
    category: Optional[str] = None
    limit: int = 20


class RegisterRequest(BaseModel):
    url: str
    name: str = ""
    category: str = "other"
    description: str = ""


class ReadRequest(BaseModel):
    url: str


class StreamRequest(BaseModel):
    query: str = ""
    category: Optional[str] = None


class OceanChatRequest(BaseModel):
    query: str
    messages: Optional[list] = None


# ─────────────────────────────────────────────────────────────
# ROUTES — INFO
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["info"])
def root():
    return {
        "service": "Shopping Therapy Engine",
        "version": "1.0.0",
        "port": 7300,
        "description": "Lexon çdo link me shërbime shopping dhe ia shfaq userit kur ai kërkon",
        "endpoints": [
            "GET  /health",
            "GET  /status",
            "GET  /api/v1/catalogue",
            "POST /api/v1/search",
            "POST /api/v1/stream",
            "POST /api/v1/register",
            "POST /api/v1/read",
            "POST /api/v1/ocean-chat  ← 🌊 Ocean Curiosity integration",
        ],
    }


@app.get("/health", tags=["info"])
def health():
    return {"status": "ok", "service": "shopping-therapy", "port": 7300}


@app.get("/status", tags=["info"])
def status():
    return engine.status()


# ─────────────────────────────────────────────────────────────
# ROUTES — CATALOGUE
# ─────────────────────────────────────────────────────────────

@app.get("/api/v1/catalogue", tags=["catalogue"])
def get_catalogue(category: Optional[str] = Query(None, description="Filter by category slug")):
    return engine.get_catalogue(category=category)


# ─────────────────────────────────────────────────────────────
# ROUTES — SEARCH
# ─────────────────────────────────────────────────────────────

@app.post("/api/v1/search", tags=["search"])
def search_services(req: SearchRequest):
    results = engine.search_services(
        query=req.query,
        category=req.category,
        limit=max(1, min(req.limit, 100)),
    )
    return {"query": req.query, "category": req.category, "count": len(results), "items": results}


@app.post("/api/v1/stream", tags=["search"])
async def stream_search(req: StreamRequest):
    """SSE stream of search results — one item at a time."""

    async def event_gen():
        async for chunk in engine.therapy_stream(query=req.query, category=req.category):
            yield chunk

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ─────────────────────────────────────────────────────────────
# ROUTES — LINK MANAGEMENT
# ─────────────────────────────────────────────────────────────

@app.post("/api/v1/register", tags=["links"])
async def register_link(req: RegisterRequest):
    """Fetch a URL, parse it, and add it to the catalogue."""
    try:
        result = await engine.read_and_register(
            url=req.url,
            name=req.name,
            category=req.category,
            description=req.description,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/api/v1/read", tags=["links"])
async def read_url(req: ReadRequest):
    """Fetch and parse a URL preview without saving to catalogue."""
    try:
        result = await engine.read_url_preview(url=req.url)
        return result
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ─────────────────────────────────────────────────────────────# ROUTES — OCEAN CURIOSITY INTEGRATION
# ────────────────────────────────────────────────────────────

@app.post("/api/v1/ocean-chat", tags=["ocean"])
async def ocean_chat(req: OceanChatRequest):
    """
    SSE stream — enriches user query with Shopping Therapy catalogue context
    and relays to Ocean Curiosity for an AI-powered shopping recommendation.
    """

    async def event_gen():
        async for chunk in engine.ocean_chat_stream(
            query=req.query,
            messages=req.messages,
        ):
            yield chunk

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ────────────────────────────────────────────────────────────# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("shopping_therapy_service:app", host="0.0.0.0", port=7300, reload=False)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLX BRAIN API - FastAPI Application
Entry point for CLX Brain cognitive engine service
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .main import CLXBrainRouter
from .ocean_integration import close_integration, get_integration

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("CLXBrain.API")


# ═════════════════════════════════════════════════════════════════════════════
# Lifespan Events
# ═════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting CLX Brain API...")
    try:
        # Initialize integration
        integration = await get_integration()
        app.state.integration = integration
        logger.info("✅ CLX Brain integration initialized")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down CLX Brain API...")
    try:
        await close_integration()
        logger.info("✅ CLX Brain shutdown complete")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# Create FastAPI Application
# ═════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="CLX BRAIN - Cognitive Engine",
    description="Unified cognitive system with Redis Unlimited integration",
    version="1.0.0",
    lifespan=lifespan,
)

# ═════════════════════════════════════════════════════════════════════════════
# Middleware
# ═════════════════════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═════════════════════════════════════════════════════════════════════════════
# Routes
# ═════════════════════════════════════════════════════════════════════════════

# Add CLX Brain router
brain_router = CLXBrainRouter()
app.include_router(brain_router.router)
app.include_router(brain_router.router, prefix="/public")


# Health and Status Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        integration = getattr(app.state, "integration", None)
        if integration:
            health = await integration.health_check()
            return health
        return {"status": "initializing"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)},
        )


@app.get("/public/health")
async def public_health_check():
    return await health_check()


@app.get("/status")
async def status():
    """Service status endpoint"""
    try:
        integration = getattr(app.state, "integration", None)
        if integration and integration.brain:
            return {
                "status": "operational",
                "service": "clx-brain",
                "brain": integration.brain.status(),
                "redis": await integration.redis.get_json("clx_brain:status"),
            }
        return {"status": "initializing"}
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": str(e)},
        )


@app.get("/public/status")
async def public_status():
    return await status()


@app.get("/metrics")
async def metrics():
    """Metrics endpoint"""
    try:
        integration = getattr(app.state, "integration", None)
        if integration and integration.brain:
            return {
                "metrikat": integration.brain.metrikat,
                "timestamp": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat(),
            }
        return JSONResponse(
            status_code=503,
            content={"error": "Brain not initialized"},
        )
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.get("/public/metrics")
async def public_metrics():
    return await metrics()


# ═════════════════════════════════════════════════════════════════════════════
# Root Endpoint
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "CLX BRAIN - Cognitive Engine",
        "version": "1.0.0",
        "description": "Unified cognitive system with Neural Network + Redis Unlimited",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "metrics": "/metrics",
            "brain": {
                "initialize": "POST /brain/initialize",
                "process": "POST /brain/process",
                "learn": "POST /brain/learn",
                "status": "GET /brain/status",
                "history": "GET /brain/history",
                "metrics": "GET /brain/metrics",
                "rules": "GET /brain/rules",
                "neurons": "GET /brain/neurons",
                "stream": "WS /brain/stream",
            },
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "features": [
            "Rrjet neuronal elastik (Elastic Neural Network)",
            "Processim etik (Ethical Processing)",
            "Redis Unlimited pa limite (No Limits)",
            "Learning loops elastike (Elastic Learning)",
            "Ocean-Core integration (Debate Streaming)",
            "Real-time WebSocket streaming",
        ],
    }


@app.get("/public")
async def public_root():
    return await root()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("SERVICE_PORT", 9999)),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )

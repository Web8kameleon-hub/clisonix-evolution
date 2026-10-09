#!/usr/bin/env python3
"""
LAGTER PUBLISH ORCHESTRATOR
Independent microservice for publish orchestration.
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("Lagter")

PORT = int(os.getenv("LAGTER_PORT", "9500"))
BLOG_PUBLISHER_URL = os.getenv("BLOG_PUBLISHER_URL", "http://clisonix-blog-publisher:8041")
MIN_ARTICLES_PER_DAY = int(os.getenv("MIN_ARTICLES_PER_DAY", "5"))
MAX_ARTICLES_PER_DAY = int(os.getenv("MAX_ARTICLES_PER_DAY", "9"))
TARGET_QUALITY = float(os.getenv("TARGET_QUALITY", "0.90"))
AUTO_TRIGGER_ENABLED = os.getenv("AUTO_TRIGGER_ENABLED", "false").lower() == "true"
AUTO_TRIGGER_INTERVAL_SECONDS = int(os.getenv("AUTO_TRIGGER_INTERVAL_SECONDS", "300"))
PUBLISH_TIMEOUT_SECONDS = float(os.getenv("LAGTER_PUBLISH_TIMEOUT_SECONDS", "25"))


app = FastAPI(
    title="Lagter Publish Orchestrator",
    description="Coordinates batch publishing through Blog Publisher.",
    version="1.0.0",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _publishing_window() -> str:
    return f"{MIN_ARTICLES_PER_DAY}-{MAX_ARTICLES_PER_DAY}"


async def trigger_publish_batch() -> Dict[str, Any]:
    endpoint = f"{BLOG_PUBLISHER_URL.rstrip('/')}/api/v1/publish/batch"
    async with httpx.AsyncClient(timeout=PUBLISH_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(endpoint)
            response.raise_for_status()
            payload = response.json() if response.content else {}
            return {
                "ok": True,
                "status_code": response.status_code,
                "result": payload,
            }
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            return {
                "ok": False,
                "status_code": exc.response.status_code if exc.response else 502,
                "error": detail,
            }
        except Exception as exc:
            return {"ok": False, "status_code": 502, "error": str(exc)}


@app.get("/")
@app.get("/health")
@app.get("/status")
async def health() -> Dict[str, Any]:
    return {
        "service": "lagter",
        "status": "healthy",
        "mode": "independent_microservice",
        "publishing_window": _publishing_window(),
        "target_quality": TARGET_QUALITY,
        "blog_publisher_url": BLOG_PUBLISHER_URL,
        "auto_trigger_enabled": AUTO_TRIGGER_ENABLED,
        "auto_trigger_interval_seconds": AUTO_TRIGGER_INTERVAL_SECONDS,
        "timestamp": _utc_now(),
    }


@app.post("/publish")
@app.post("/publish/batch")
@app.post("/api/v1/publish/batch")
async def publish_batch() -> Dict[str, Any]:
    result = await trigger_publish_batch()
    payload = {
        "service": "lagter",
        "action": "publish_batch",
        "mode": "independent_microservice",
        "publishing_window": _publishing_window(),
        "target_quality": TARGET_QUALITY,
        "timestamp": _utc_now(),
        **result,
    }
    if not result.get("ok"):
        raise HTTPException(status_code=result.get("status_code", 502), detail=payload)
    return payload


async def _auto_publish_loop() -> None:
    while True:
        await asyncio.sleep(AUTO_TRIGGER_INTERVAL_SECONDS)
        result = await trigger_publish_batch()
        if result.get("ok"):
            logger.info("✅ Auto publish trigger completed")
        else:
            logger.warning("⚠️ Auto publish trigger failed: %s", result.get("error"))


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("🚀 Lagter started on port %s", PORT)
    if AUTO_TRIGGER_ENABLED:
        logger.info(
            "⏱️ Auto trigger enabled: every %s seconds",
            AUTO_TRIGGER_INTERVAL_SECONDS,
        )
        asyncio.create_task(_auto_publish_loop())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)

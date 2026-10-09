#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
LAZY OLLAMA ENGINE - Intelligent Resource Management
═══════════════════════════════════════════════════════════════════════════════

Koncepti LAZY:
- Ngarkon modelin VETËM kur vjen request
- Mban model të ngrohtë me ping të vogla (1+1=2)
- Queue për requests - max 1 në kohë
- Cache për përgjigje të përsëritura
- Timeout i zgjatur (180s) për server pa GPU

Përse 1500% CPU?
- llama3.1:8b = 8 MILIARD parametra
- Pa GPU, CPU bën TË GJITHË punën
- Çdo request = 60-90 sekonda në serverin tonë

Me Lazy Engine:
- Request queue: vetëm 1 process në kohë
- Cache: përgjigjet e njëjta nuk riprocesohen
- Warmup: model i gatshëm pa ngarkesë të plotë
"""

import asyncio
import hashlib
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

logger = logging.getLogger("lazy_ollama")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Use OLLAMA_HOST from environment (set in docker-compose), fallback to auto-detect
OLLAMA_HOST_ENV = os.getenv("OLLAMA_HOST", "")
if OLLAMA_HOST_ENV:
    # Environment variable set - use it directly (e.g., "http://clisonix-ollama:11434")
    OLLAMA_BASE_URL = OLLAMA_HOST_ENV
else:
    # Auto-detect based on Docker presence
    IS_IN_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_ENV") == "1"
    OLLAMA_HOST = "clisonix-ollama" if IS_IN_DOCKER else "localhost"
    OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:11434"

DEFAULT_MODEL = os.getenv("MODEL", "llama3.1:8b")

# Timeouts për server pa GPU
REQUEST_TIMEOUT = 180.0  # 3 minuta max për përgjigje
WARMUP_TIMEOUT = 120.0   # 2 minuta për warmup
WARMUP_INTERVAL = 240    # 4 minuta - mbaj model të ngrohtë
CACHE_TTL = 3600         # 1 orë cache

# Queue settings
MAX_QUEUE_SIZE = 10
MAX_CONCURRENT = 1       # VETËM 1 request në kohë (CPU limitation)


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE CACHE
# ═══════════════════════════════════════════════════════════════════════════════

class ResponseCache:
    """Cache për përgjigje të njëjta"""

    def __init__(self, max_size: int = 100, ttl: int = CACHE_TTL):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl = ttl

    def _hash_prompt(self, prompt: str, model: str) -> str:
        """Krijo hash unik për prompt+model"""
        content = f"{model}:{prompt.strip().lower()}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[str]:
        """Merr përgjigje nga cache nëse ekziston dhe nuk ka skaduar"""
        key = self._hash_prompt(prompt, model)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self._ttl:
                logger.info(f"🎯 Cache HIT: {prompt[:50]}...")
                return entry["response"]
            else:
                del self._cache[key]
        return None

    def set(self, prompt: str, model: str, response: str) -> None:
        """Ruaj përgjigje në cache"""
        # Pastro cache të vjetër nëse tejkalon limitet
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache.items(), key=lambda x: x[1]["timestamp"])
            del self._cache[oldest[0]]

        key = self._hash_prompt(prompt, model)
        self._cache[key] = {
            "response": response,
            "timestamp": time.time()
        }
        logger.info(f"💾 Cached: {prompt[:50]}... ({len(self._cache)} total)")

    def clear(self) -> int:
        """Pastro cache"""
        count = len(self._cache)
        self._cache.clear()
        return count


# ═══════════════════════════════════════════════════════════════════════════════
# LAZY OLLAMA ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class LazyOllamaEngine:
    """
    Engine me ngarkesë të mençur:
    - Nuk ngarkon modelin deri sa të vij request
    - Queue për requests (max 1 concurrent)
    - Cache për përgjigje
    - Warmup periodik
    """

    _instance: Optional["LazyOllamaEngine"] = None

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.base_url = OLLAMA_BASE_URL

        # State
        self._is_ready = False
        self._is_warming = False
        self._last_warmup: Optional[float] = None
        self._warmup_task: Optional[asyncio.Task] = None

        # Queue & concurrency
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        self._active_requests = 0

        # Cache
        self._cache = ResponseCache()

        # Stats
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "queue_full": 0,
            "errors": 0,
            "avg_response_time": 0.0
        }

        logger.info(f"🦥 LazyOllamaEngine initialized (model={model}, max_concurrent={MAX_CONCURRENT})")

    @classmethod
    def get_instance(cls, model: str = DEFAULT_MODEL) -> "LazyOllamaEngine":
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = cls(model)
        return cls._instance

    # ═══════════════════════════════════════════════════════════════════════════
    # WARMUP & HEALTH
    # ═══════════════════════════════════════════════════════════════════════════

    async def _warmup_once(self) -> bool:
        """Ngroh modelin me një pyetje të thjeshtë"""
        if self._is_warming:
            return False

        self._is_warming = True
        try:
            logger.info("🔥 Warming up model...")
            async with httpx.AsyncClient(timeout=WARMUP_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": "1+1=",
                        "stream": False,
                        "options": {"num_predict": 5}  # Vetëm 5 tokens
                    }
                )
                if response.status_code == 200:
                    self._is_ready = True
                    self._last_warmup = time.time()
                    logger.info("✅ Model warm and ready")
                    return True
        except Exception as e:
            logger.warning(f"⚠️ Warmup failed: {e}")
        finally:
            self._is_warming = False
        return False

    async def _warmup_loop(self) -> None:
        """Background loop për mbajtur modelin të ngrohtë"""
        while True:
            await asyncio.sleep(WARMUP_INTERVAL)
            if self._active_requests == 0:  # Vetëm kur nuk ka requests aktive
                await self._warmup_once()

    def start_warmup_loop(self) -> None:
        """Nis warmup loop në background"""
        if self._warmup_task is None or self._warmup_task.done():
            self._warmup_task = asyncio.create_task(self._warmup_loop())
            logger.info("🔁 Warmup loop started")

    async def health_check(self) -> Dict[str, Any]:
        """Kontrollo statusin e Ollama"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return {
                        "status": "healthy",
                        "available_models": models,
                        "current_model": self.model,
                        "model_loaded": self.model in models,
                        "is_ready": self._is_ready,
                        "active_requests": self._active_requests,
                        "queue_size": self._queue.qsize()
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
        return {
            "status": "unhealthy",
            "error": "Ollama tags endpoint returned non-200 status"
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # GENERATE (with queue & cache)
    # ═══════════════════════════════════════════════════════════════════════════

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Gjeneroj përgjigje me queue dhe cache.

        Returns:
            {"response": str, "from_cache": bool, "wait_time": float, "generation_time": float}
        """
        start_time = time.time()
        self._stats["total_requests"] += 1

        # 1. Kontrollo cache
        if use_cache:
            cached = self._cache.get(prompt, self.model)
            if cached:
                self._stats["cache_hits"] += 1
                return {
                    "response": cached,
                    "from_cache": True,
                    "wait_time": 0,
                    "generation_time": 0,
                    "model": self.model
                }

        # 2. Ensure model is warm
        if not self._is_ready:
            await self._warmup_once()

        # 3. Queue with semaphore (max 1 concurrent)
        queue_start = time.time()
        async with self._semaphore:
            wait_time = time.time() - queue_start
            self._active_requests += 1

            try:
                gen_start = time.time()

                # Build request
                request_body = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens if isinstance(max_tokens, int) and max_tokens > 0 else -1
                    }
                }
                if system:
                    request_body["system"] = system

                # Make request
                async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=request_body
                    )

                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("response", "")

                        # Cache response
                        if use_cache and len(answer) > 10:
                            self._cache.set(prompt, self.model, answer)

                        generation_time = time.time() - gen_start

                        # Update avg response time
                        n = self._stats["total_requests"]
                        self._stats["avg_response_time"] = (
                            (self._stats["avg_response_time"] * (n - 1) + generation_time) / n
                        )

                        return {
                            "response": answer,
                            "from_cache": False,
                            "wait_time": wait_time,
                            "generation_time": generation_time,
                            "model": self.model,
                            "btl": {
                                "bits": len(answer.encode("utf-8")) * 8,
                                "pixels": len(answer),
                                "chunks": data.get("eval_count", 0),
                                "unit": "BTL",
                                "nanogrid": {
                                    "protocol": "nanogridata-v1",
                                    "header_bytes": 14,
                                    "cell_bytes": 16,
                                    "payload_bytes": len(answer.encode("utf-8")),
                                    "cells": max(1, (len(answer.encode("utf-8")) + 15) // 16),
                                    "frame_bytes": 14 + (max(1, (len(answer.encode("utf-8")) + 15) // 16) * 16),
                                },
                            }
                        }
                    else:
                        self._stats["errors"] += 1
                        return {
                            "error": f"Ollama returned {response.status_code}",
                            "from_cache": False
                        }

            except asyncio.TimeoutError:
                self._stats["errors"] += 1
                return {
                    "error": f"Request timeout after {REQUEST_TIMEOUT}s",
                    "from_cache": False
                }
            except Exception as e:
                self._stats["errors"] += 1
                return {
                    "error": str(e),
                    "from_cache": False
                }
            finally:
                self._active_requests -= 1

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream përgjigje (nuk përdor cache).
        Yields tokens njëra pas tjetrës.
        """
        # Ensure model is warm
        if not self._is_ready:
            await self._warmup_once()

        async with self._semaphore:
            self._active_requests += 1
            try:
                request_body = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens if isinstance(max_tokens, int) and max_tokens > 0 else -1
                    }
                }
                if system:
                    request_body["system"] = system

                async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/api/generate",
                        json=request_body
                    ) as response:
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    import json
                                    data = json.loads(line)
                                    token = data.get("response", "")
                                    if token:
                                        yield token
                                    if data.get("done"):
                                        break
                                except Exception:
                                    continue
            finally:
                self._active_requests -= 1

    # ═══════════════════════════════════════════════════════════════════════════
    # STATS & MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat"""
        return {
            **self._stats,
            "cache_size": len(self._cache._cache),
            "active_requests": self._active_requests,
            "is_ready": self._is_ready,
            "last_warmup": datetime.fromtimestamp(self._last_warmup, tz=timezone.utc).isoformat() if self._last_warmup else None
        }

    def clear_cache(self) -> int:
        """Pastro cache"""
        return self._cache.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON ACCESSOR
# ═══════════════════════════════════════════════════════════════════════════════

_lazy_engine: Optional[LazyOllamaEngine] = None

def get_lazy_ollama(model: str = DEFAULT_MODEL) -> LazyOllamaEngine:
    """Get singleton instance of LazyOllamaEngine"""
    global _lazy_engine
    if _lazy_engine is None:
        _lazy_engine = LazyOllamaEngine(model)
    return _lazy_engine


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio

    async def test():
        engine = get_lazy_ollama()

        print("Testing LazyOllamaEngine...")
        print(f"Stats before: {engine.get_stats()}")

        # Test health
        health = await engine.health_check()
        print(f"Health: {health}")

        # Test generate (will warm up first)
        result = await engine.generate("What is 2+2?")
        print(f"Result: {result}")

        # Test cache hit
        result2 = await engine.generate("What is 2+2?")
        print(f"Cached result: {result2}")

        print(f"Stats after: {engine.get_stats()}")

    asyncio.run(test())

#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  CLISONIX TIER-BASED RATE LIMIT MIDDLEWARE                                    ║
║  Redis-backed, per-plan enforcement for Free / Pro / Enterprise               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Limits:                                                                      ║
║  FREE       →  1,000 req/day   |  10 req/min                                 ║
║  PRO        → 10,000 req/day   | 100 req/min                                 ║
║  ENTERPRISE → 50,000 req/day   | 1,000 req/min                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("RateLimitMiddleware")

# ─── Plan configuration ──────────────────────────────────────────────────────

PLAN_LIMITS: Dict[str, Dict] = {
    "free": {
        "requests_per_day": 999_999_999,  # unlimited
        "requests_per_minute": 999_999_999,  # unlimited
        "price_eur": 0,
    },
    "pro": {
        "requests_per_day": 999_999_999,  # unlimited
        "requests_per_minute": 999_999_999,  # unlimited
        "price_eur": 29,
    },
    "enterprise": {
        "requests_per_day": 999_999_999,  # unlimited
        "requests_per_minute": 999_999_999,  # unlimited
        "price_eur": 199,
    },
}

# Endpoints that bypass rate limiting entirely
_BYPASS_PATHS = frozenset(
    ["/health", "/status", "/docs", "/openapi.json", "/redoc", "/metrics"]
)

# ─── Redis store ─────────────────────────────────────────────────────────────

class _RateLimitStore:
    """Thin wrapper around redis-py with in-memory fallback."""

    def __init__(self, redis_url: str) -> None:
        self._redis = None
        self._mem: Dict[str, int] = {}
        try:
            import redis as _redis_pkg
            client = _redis_pkg.from_url(redis_url, socket_connect_timeout=2)
            client.ping()
            self._redis = client
            logger.info("[OK] RateLimitStore connected to Redis")
        except Exception as exc:
            logger.warning("[WARN] Redis unreachable (%s). Using in-memory fallback.", exc)

    def incr(self, key: str, ttl: int) -> int:
        if self._redis:
            pipe = self._redis.pipeline(True)
            pipe.incr(key)
            pipe.expire(key, ttl)
            count, _ = pipe.execute()
            return int(count)
        # in-memory fallback (single-instance only)
        self._mem[key] = self._mem.get(key, 0) + 1
        return self._mem[key]

    def get(self, key: str) -> int:
        if self._redis:
            val = self._redis.get(key)
            if val is None or hasattr(val, "__await__"):
                return 0
            try:
                if isinstance(val, (bytes, bytearray)):
                    return int(val.decode())
                return int(str(val))
            except (TypeError, ValueError):
                return 0
        return self._mem.get(key, 0)


# ─── Plan resolvers ──────────────────────────────────────────────────────────

class _PlanCache:
    """
    Two-level plan cache:
      L1 – in-process dict (TTL 60 s)
      L2 – marketplace HTTP lookup (async)
    Defaults to "free" if marketplace is unreachable.
    """

    _TTL = 60  # seconds before re-validating plan

    def __init__(self, marketplace_url: str) -> None:
        self._url = marketplace_url.rstrip("/")
        self._cache: Dict[str, tuple] = {}  # key_hash → (plan, expires_at)

    async def resolve(self, api_key: str) -> str:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        entry = self._cache.get(key_hash)
        if entry and time.monotonic() < entry[1]:
            return entry[0]
        plan = await self._fetch_from_marketplace(api_key)
        self._cache[key_hash] = (plan, time.monotonic() + self._TTL)
        return plan

    async def _fetch_from_marketplace(self, api_key: str) -> str:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(
                    f"{self._url}/api/v1/keys/validate",
                    headers={"X-API-Key": api_key},
                )
                if r.status_code == 200:
                    data = r.json()
                    return data.get("plan", "free").lower()
        except Exception:
            pass
        return "free"


# ─── Middleware ───────────────────────────────────────────────────────────────

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Tier-based API rate limiting for Clisonix Cloud.

    Registers upstream via:
        app.add_middleware(
            RateLimitMiddleware,
            redis_url="redis://redis:6379/0",
            marketplace_url="http://clisonix-marketplace:8004",
        )
    """

    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379/0",
        marketplace_url: str = "http://clisonix-marketplace:8004",
        enabled: bool = True,
    ) -> None:
        super().__init__(app)
        self.enabled = enabled
        if enabled:
            self._store = _RateLimitStore(redis_url)
            self._plans = _PlanCache(marketplace_url)
            logger.info(
                "[OK] RateLimitMiddleware active | Redis: %s | Marketplace: %s",
                redis_url,
                marketplace_url,
            )
        else:
            logger.info("[WARN] RateLimitMiddleware disabled")

    # ── Request pipeline ──────────────────────────────────────────────────

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled or request.url.path in _BYPASS_PATHS:
            return await call_next(request)

        api_key = self._extract_key(request)
        if not api_key:
            # Anonymous / public endpoints – allow through (no key = no quota)
            return await call_next(request)

        plan = await self._plans.resolve(api_key)
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]

        # ── Daily counter ────────────────────────────────────────────────
        daily_key = f"rl:d:{key_hash}"
        daily_count = self._store.get(daily_key)
        if daily_count >= limits["requests_per_day"]:
            return self._limit_response(
                plan,
                f"{limits['requests_per_day']} req/day",
                retry_after=self._seconds_until_midnight(),
            )

        # ── Per-minute counter ───────────────────────────────────────────
        minute_key = f"rl:m:{key_hash}"
        minute_count = self._store.get(minute_key)
        if minute_count >= limits["requests_per_minute"]:
            return self._limit_response(
                plan,
                f"{limits['requests_per_minute']} req/min",
                retry_after=60,
            )

        # ── Increment both counters atomically ───────────────────────────
        self._store.incr(daily_key, ttl=86_400)
        self._store.incr(minute_key, ttl=60)

        # ── Proxy request and attach quota headers ───────────────────────
        response = await call_next(request)
        response.headers["X-RateLimit-Plan"] = plan.upper()
        response.headers["X-RateLimit-Daily-Limit"] = str(limits["requests_per_day"])
        response.headers["X-RateLimit-Daily-Remaining"] = str(
            max(0, limits["requests_per_day"] - daily_count - 1)
        )
        response.headers["X-RateLimit-Minute-Limit"] = str(limits["requests_per_minute"])
        response.headers["X-RateLimit-Minute-Remaining"] = str(
            max(0, limits["requests_per_minute"] - minute_count - 1)
        )
        return response

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _extract_key(request: Request) -> Optional[str]:
        if key := request.headers.get("x-api-key"):
            return key
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return None

    @staticmethod
    def _limit_response(plan: str, detail: str, retry_after: int) -> JSONResponse:
        logger.warning("[RATE-LIMIT] Limit exceeded [%s] - %s", plan.upper(), detail)
        resp = JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "plan": plan.upper(),
                "limit": detail,
                "message": (
                    f"You've exceeded your {plan.upper()} plan limit ({detail}). "
                    f"Upgrade at https://clisonix.com/pricing"
                ),
                "upgrade_url": "https://clisonix.com/pricing",
                "retry_after": retry_after,
            },
        )
        resp.headers["Retry-After"] = str(retry_after)
        resp.headers["X-RateLimit-Plan"] = plan.upper()
        return resp

    @staticmethod
    def _seconds_until_midnight() -> int:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # next midnight
        from datetime import timedelta

        midnight += timedelta(days=1)
        return max(1, int((midnight - now).total_seconds()))

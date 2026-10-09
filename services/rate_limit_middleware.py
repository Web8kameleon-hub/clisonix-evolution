#!/usr/bin/env python3
"""
Rate Limiting Middleware
------------------------
Enforces API rate limits based on subscription plan
Integrates with FastAPI apps/api service
"""

import hashlib
import logging
from typing import Dict, Optional

import redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("RateLimitMiddleware")

# ═══════════════════════════════════════════════════════════════════════════════
# PLAN LIMITS (from api_key_management.py)
# ═══════════════════════════════════════════════════════════════════════════════

PLAN_LIMITS = {
    "free": {
        "requests_per_day": 1000,
        "requests_per_minute": 10,
        "burst_capacity": 5,
        "price_eur": 0
    },
    "pro": {
        "requests_per_day": 10000,
        "requests_per_minute": 100,
        "burst_capacity": 50,
        "price_eur": 29
    },
    "enterprise": {
        "requests_per_day": 50000,
        "requests_per_minute": 1000,
        "burst_capacity": 500,
        "price_eur": 199
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# REDIS CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimitStore:
    """Redis-backed rate limit storage"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info(f"✓ Connected to Redis: {redis_url}")
            self.available = True
        except Exception as e:
            logger.warning(f"⚠ Redis unavailable: {e}. Falling back to in-memory limits.")
            self.available = False
            self.in_memory: Dict[str, Dict] = {}
    
    async def get_request_count(self, key: str, window: str) -> int:
        """Get request count for key in time window"""
        if self.available:
            count_key = f"rate:{key}:{window}"
            count = await self.redis_client.get(count_key)
            return int(count.decode()) if count else 0
        else:
            # Fallback: in-memory counting
            if key not in self.in_memory:
                self.in_memory[key] = {"daily": 0, "minute": 0, "burst": 0}
            return self.in_memory[key].get(window, 0)
    
    async def increment_count(self, key: str, window: str, ttl_seconds: int) -> int:
        """Increment request count for key in time window"""
        if self.available:
            count_key = f"rate:{key}:{window}"
            count = await self.redis_client.incr(count_key)
            # Set expiry only on first increment
            if count == 1:
                await self.redis_client.expire(count_key, ttl_seconds)
            return count
        else:
            # Fallback: in-memory incrementing
            if key not in self.in_memory:
                self.in_memory[key] = {"daily": 0, "minute": 0, "burst": 0}
            self.in_memory[key][window] += 1
            return self.in_memory[key][window]

# ═══════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for API rate limiting"""
    
    def __init__(self, app, redis_url: str = "redis://localhost:6379/0", enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.store = RateLimitStore(redis_url) if enabled else None
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through rate limiting"""
        
        # Skip health checks
        if request.url.path in ["/health", "/status", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        if not self.enabled or self.store is None:
            return await call_next(request)
        
        # Extract API key from header or Authorization
        api_key = self._extract_api_key(request)
        if not api_key:
            # No API key = public endpoint, allow through
            return await call_next(request)
        
        # Hash key for storage (don't log actual keys)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:12]
        
        # Get plan from API key (would fetch from db in production)
        plan = await self._get_plan_for_key(api_key)
        if not plan:
            plan = "free"
        
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        
        # Check daily limit
        daily_count = await self.store.get_request_count(f"key:{key_hash}", "daily")
        if daily_count >= limits["requests_per_day"]:
            logger.warning(f"Daily limit exceeded for {plan} key")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"{plan.upper()} plan limit: {limits['requests_per_day']} requests/day",
                    "retry_after": 86400
                }
            )
        
        # Check per-minute limit
        minute_count = await self.store.get_request_count(f"key:{key_hash}", "minute")
        if minute_count >= limits["requests_per_minute"]:
            logger.warning(f"Per-minute limit exceeded for {plan} key")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"{plan.upper()} plan limit: {limits['requests_per_minute']} requests/minute",
                    "retry_after": 60
                }
            )
        
        # Increment counters
        await self.store.increment_count(f"key:{key_hash}", "daily", 86400)
        await self.store.increment_count(f"key:{key_hash}", "minute", 60)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Plan"] = plan
        response.headers["X-RateLimit-Daily-Limit"] = str(limits["requests_per_day"])
        response.headers["X-RateLimit-Daily-Remaining"] = str(limits["requests_per_day"] - daily_count - 1)
        response.headers["X-RateLimit-Minute-Limit"] = str(limits["requests_per_minute"])
        response.headers["X-RateLimit-Minute-Remaining"] = str(limits["requests_per_minute"] - minute_count - 1)
        
        return response
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request headers"""
        # Check X-API-Key header
        if "x-api-key" in request.headers:
            return request.headers["x-api-key"]
        
        # Check Authorization bearer token (for browser-based testing)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")
        
        return None
    
    async def _get_plan_for_key(self, api_key: str) -> Optional[str]:
        """
        Get plan tier for API key
        In production, would query database or cache
        """
        # This is a stub - integrate with your API key database
        # Example: query api_key_management.py or marketplace service
        return "free"  # Default to free tier

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZATION HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def add_rate_limit_middleware(app, redis_url: str = "redis://localhost:6379/0", enabled: bool = True):
    """
    Add rate limiting middleware to FastAPI app
    
    Usage in apps/api/main.py:
    ```python
    from rate_limit_middleware import add_rate_limit_middleware
    
    app = FastAPI()
    add_rate_limit_middleware(app, redis_url="redis://redis:6379/0", enabled=True)
    ```
    """
    app.add_middleware(RateLimitMiddleware, redis_url=redis_url, enabled=enabled)
    logger.info("✓ Rate limit middleware added to app")

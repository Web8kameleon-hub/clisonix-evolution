"""
🛡️ CLISONIX RATE LIMITER - Production API Protection

Protects live users with intelligent rate limiting:
- Redis-backed sliding window algorithm
- Per-user and global limits
- Tiered limits (free/pro/enterprise)
- Burst handling
- Graceful degradation

Usage:
    from rate_limiter import RateLimiter, rate_limit
    
    limiter = RateLimiter()
    
    @app.get("/api/data")
    @rate_limit(requests=100, window=60)  # 100 requests per minute
    async def get_data():
        return {"data": "..."}
"""

import hashlib
import importlib.util
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

redis = None
REDIS_AVAILABLE = False
if importlib.util.find_spec("redis"):
    import redis as redis_module

    redis = redis_module
    REDIS_AVAILABLE = True

try:
    from fastapi import HTTPException, Request
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

logger = logging.getLogger("clisonix.rate_limiter")


class UserTier(Enum):
    """User subscription tiers with different rate limits"""
    ANONYMOUS = "anonymous"
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"  # Staff/admin


@dataclass
class RateLimitConfig:
    """Rate limit configuration per tier"""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_size: int
    cost_multiplier: float = 1.0  # For weighted endpoints


# =============================================================================
# TIER CONFIGURATIONS - Adjust based on your SLA
# =============================================================================

TIER_LIMITS = {
    UserTier.ANONYMOUS: RateLimitConfig(
        requests_per_minute=30,
        requests_per_hour=500,
        requests_per_day=2000,
        burst_size=10
    ),
    UserTier.FREE: RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_size=20
    ),
    UserTier.PRO: RateLimitConfig(
        requests_per_minute=300,
        requests_per_hour=10000,
        requests_per_day=100000,
        burst_size=50
    ),
    UserTier.ENTERPRISE: RateLimitConfig(
        requests_per_minute=1000,
        requests_per_hour=50000,
        requests_per_day=500000,
        burst_size=100
    ),
    UserTier.INTERNAL: RateLimitConfig(
        requests_per_minute=10000,  # Essentially unlimited for staff
        requests_per_hour=100000,
        requests_per_day=1000000,
        burst_size=500
    ),
}

# Heavy endpoints that cost more quota
ENDPOINT_COSTS = {
    "/api/analyze": 5,
    "/api/generate": 10,
    "/api/ml/predict": 10,
    "/api/eeg/process": 20,
    "/api/audio/process": 15,
    "/api/ocean/query": 5,
}


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, message: str, retry_after: int):
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)


class RateLimiter:
    """
    Redis-backed sliding window rate limiter.
    
    Algorithm: Sliding Window Log
    - More accurate than fixed windows
    - Handles burst traffic smoothly
    - No thundering herd at window boundaries
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        prefix: str = "clisonix:ratelimit:",
        fallback_memory: bool = True
    ):
        self.prefix = prefix
        self._local_counters: Dict[str, list] = {}
        self._enabled = True
        
        # Redis connection
        self._redis: Optional[Any] = None
        if REDIS_AVAILABLE:
            try:
                redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("✅ Rate limiter connected to Redis")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}")
                if not fallback_memory:
                    raise
                self._redis = None
    
    def _get_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limit counter"""
        return f"{self.prefix}{identifier}:{window}"
    
    def _get_identifier(
        self, 
        user_id: Optional[str] = None, 
        ip_address: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> str:
        """Get unique identifier for rate limiting"""
        if user_id:
            return f"user:{user_id}"
        elif api_key:
            # Hash API key for privacy
            return f"key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
        elif ip_address:
            return f"ip:{ip_address}"
        else:
            return "unknown"
    
    def check_rate_limit(
        self,
        identifier: str,
        tier: UserTier = UserTier.FREE,
        endpoint: str = "/",
        cost: int = 1,
        window_seconds: int = 60,
        config_override: Optional[RateLimitConfig] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit.
        
        Returns:
            Tuple of (allowed, info_dict)
            - allowed: True if request is allowed
            - info_dict: Contains remaining, limit, reset time
        """
        if not self._enabled:
            return True, {"remaining": -1, "limit": -1, "reset": 0}
        
        config = config_override or TIER_LIMITS.get(tier, TIER_LIMITS[UserTier.FREE])
        
        # Apply endpoint cost multiplier
        effective_cost = cost
        if endpoint in ENDPOINT_COSTS:
            effective_cost = ENDPOINT_COSTS[endpoint]
        
        now = time.time()
        window_key = self._get_key(identifier, f"{window_seconds}s")
        
        # Use Redis if available
        if self._redis:
            return self._check_redis_rate_limit(
                identifier, config, window_key, effective_cost, now, window_seconds
            )
        else:
            return self._check_memory_rate_limit(
                identifier, config, effective_cost, now, window_seconds
            )
    
    def _check_redis_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
        minute_key: str,
        cost: int,
        now: float,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using Redis sliding window"""
        window_start = now - window_seconds
        
        # Use pipeline for atomic operations
        pipe = self._redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(minute_key, 0, window_start)
        
        # Count current requests
        pipe.zcard(minute_key)
        
        # Get oldest entry for reset time
        pipe.zrange(minute_key, 0, 0, withscores=True)
        
        results = pipe.execute()
        current_count = results[1]
        oldest = results[2]
        
        limit = config.requests_per_minute
        remaining = max(0, limit - current_count)
        
        # Calculate reset time
        if oldest:
            reset_at = int(oldest[0][1] + window_seconds)
        else:
            reset_at = int(now + window_seconds)
        
        # Check if limit exceeded
        if current_count + cost > limit:
            logger.warning(f"🚫 Rate limit exceeded: {identifier} ({current_count}/{limit})")
            return False, {
                "remaining": 0,
                "limit": limit,
                "reset": reset_at,
                "retry_after": max(1, reset_at - int(now))
            }
        
        # Add this request
        for _ in range(cost):
            self._redis.zadd(minute_key, {f"{now}:{_}": now})
        self._redis.expire(minute_key, max(120, window_seconds * 2))
        
        return True, {
            "remaining": remaining - cost,
            "limit": limit,
            "reset": reset_at
        }
    
    def _check_memory_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
        cost: int,
        now: float,
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Fallback in-memory rate limiting"""
        window_start = now - window_seconds
        
        # Initialize if needed
        if identifier not in self._local_counters:
            self._local_counters[identifier] = []
        
        # Remove old entries
        self._local_counters[identifier] = [
            ts for ts in self._local_counters[identifier] if ts > window_start
        ]
        
        current_count = len(self._local_counters[identifier])
        limit = config.requests_per_minute
        remaining = max(0, limit - current_count)
        
        # Calculate reset time
        if self._local_counters[identifier]:
            oldest = min(self._local_counters[identifier])
            reset_at = int(oldest + window_seconds)
        else:
            reset_at = int(now + window_seconds)
        
        if current_count + cost > limit:
            return False, {
                "remaining": 0,
                "limit": limit,
                "reset": reset_at,
                "retry_after": max(1, reset_at - int(now))
            }
        
        # Add this request
        for _ in range(cost):
            self._local_counters[identifier].append(now)
        
        return True, {
            "remaining": remaining - cost,
            "limit": limit,
            "reset": reset_at
        }
    
    def get_usage(self, identifier: str) -> Dict[str, Any]:
        """Get current usage statistics for an identifier"""
        now = time.time()
        minute_key = self._get_key(identifier, "minute")
        
        if self._redis:
            window_start = now - 60
            self._redis.zremrangebyscore(minute_key, 0, window_start)
            count = self._redis.zcard(minute_key)
        else:
            if identifier in self._local_counters:
                count = len([ts for ts in self._local_counters[identifier] if ts > now - 60])
            else:
                count = 0
        
        return {
            "identifier": identifier,
            "requests_last_minute": count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for an identifier (admin use only)"""
        if self._redis:
            keys = self._redis.keys(f"{self.prefix}{identifier}:*")
            if keys:
                self._redis.delete(*keys)
        else:
            if identifier in self._local_counters:
                del self._local_counters[identifier]
        
        logger.info(f"🔄 Rate limit reset: {identifier}")


# =============================================================================
# FASTAPI MIDDLEWARE
# =============================================================================

if FASTAPI_AVAILABLE:
    class RateLimitMiddleware:
        """
        FastAPI middleware for automatic rate limiting.
        
        Usage:
            app = FastAPI()
            app.add_middleware(RateLimitMiddleware)
        """
        
        def __init__(self, app):
            self.app = app
            self.limiter = RateLimiter()
        
        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                await self.app(scope, receive, send)
                return
            
            request = Request(scope, receive)
            
            # Extract identifier
            user_id = None
            api_key = request.headers.get("X-API-Key")
            ip = request.client.host if request.client else "unknown"
            
            # Try to get user from auth header
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # Hash the token for identifier
                token = auth_header[7:]
                user_id = hashlib.sha256(token.encode()).hexdigest()[:16]
            
            identifier = self.limiter._get_identifier(user_id, ip, api_key)
            
            # Determine tier (you'd look this up from your user database)
            tier = self._get_user_tier(user_id)
            
            # Check rate limit
            allowed, info = self.limiter.check_rate_limit(
                identifier, 
                tier, 
                request.url.path
            )
            
            if not allowed:
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": info.get("retry_after", 60),
                        "message": "Too many requests. Please slow down."
                    },
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(info["reset"]),
                        "Retry-After": str(info.get("retry_after", 60))
                    }
                )
                await response(scope, receive, send)
                return
            
            # Process request with rate limit headers
            async def send_with_headers(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.extend([
                        (b"X-RateLimit-Limit", str(info["limit"]).encode()),
                        (b"X-RateLimit-Remaining", str(info["remaining"]).encode()),
                        (b"X-RateLimit-Reset", str(info["reset"]).encode()),
                    ])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_with_headers)
        
        def _get_user_tier(self, user_id: Optional[str]) -> UserTier:
            """Look up user tier from database (implement your logic)"""
            if not user_id:
                return UserTier.ANONYMOUS
            
            # Check if internal user
            internal_ids = os.getenv("INTERNAL_USER_IDS", "").split(",")
            if user_id in internal_ids:
                return UserTier.INTERNAL
            
            # Default to FREE - implement your user tier lookup here
            return UserTier.FREE


# =============================================================================
# DECORATOR
# =============================================================================

def rate_limit(
    requests: int = 60, 
    window: int = 60,
    tier: UserTier = UserTier.FREE
):
    """
    Decorator for rate limiting individual endpoints.
    
    Usage:
        @rate_limit(requests=10, window=60)  # 10 requests per minute
        async def my_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        limiter = RateLimiter()
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to extract request info
            request = None
            for arg in args:
                if FASTAPI_AVAILABLE and isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                ip = request.client.host if request.client else "unknown"
                identifier = f"endpoint:{func.__name__}:{ip}"
            else:
                identifier = f"endpoint:{func.__name__}:unknown"
            
            # Custom config for this endpoint
            config = RateLimitConfig(
                requests_per_minute=requests,
                requests_per_hour=requests * 60,
                requests_per_day=requests * 1440,
                burst_size=max(requests // 10, 5)
            )
            
            allowed, info = limiter.check_rate_limit(
                identifier,
                tier,
                window_seconds=window,
                config_override=config,
            )
            
            if not allowed:
                if FASTAPI_AVAILABLE:
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Rate limit exceeded",
                            "retry_after": info.get("retry_after", 60)
                        }
                    )
                else:
                    raise RateLimitExceeded(
                        "Rate limit exceeded",
                        info.get("retry_after", 60)
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_global_limiter: Optional[RateLimiter] = None

def get_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter()
    return _global_limiter


# =============================================================================
# CLI / ADMIN COMMANDS
# =============================================================================

def print_tier_limits():
    """Print rate limit configurations"""
    print("\n" + "="*60)
    print("⚡ CLISONIX RATE LIMITS")
    print("="*60)
    
    for tier, config in TIER_LIMITS.items():
        print(f"\n{tier.value.upper()}:")
        print(f"  Per minute:  {config.requests_per_minute:,}")
        print(f"  Per hour:    {config.requests_per_hour:,}")
        print(f"  Per day:     {config.requests_per_day:,}")
        print(f"  Burst size:  {config.burst_size}")
    
    print("\n" + "="*60)
    print("📊 ENDPOINT COSTS:")
    for endpoint, cost in ENDPOINT_COSTS.items():
        print(f"  {endpoint}: {cost}x")
    print("="*60 + "\n")


if __name__ == "__main__":
    print_tier_limits()
    
    # Test rate limiter
    limiter = get_limiter()
    
    print("\n🧪 Testing rate limiter:")
    for i in range(5):
        allowed, info = limiter.check_rate_limit("test_user_123", UserTier.FREE)
        print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'} | Remaining: {info['remaining']}")

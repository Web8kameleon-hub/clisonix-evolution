#!/usr/bin/env python3
"""
Usage Analytics Service
-----------------------
Real-time API request tracking and usage metrics
Runs on port 8006
"""

import hashlib
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import redis
from fastapi import APIRouter, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UsageAnalytics")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PORT = int(os.getenv("ANALYTICS_PORT", "8006"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Clisonix Usage Analytics",
    description="Real-time API usage tracking",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# REDIS CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()
    logger.info(f"✓ Connected to Redis: {REDIS_URL}")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠ Redis unavailable: {e}")
    REDIS_AVAILABLE = False
    redis_client = None

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class RequestEvent(BaseModel):
    """Individual request event"""
    timestamp: str
    key_hash: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    ip_address: str

class UsageMetrics(BaseModel):
    """User's usage metrics"""
    requests_today: int
    requests_limit: int
    requests_remaining: int
    requests_this_month: int
    reset_time: str
    top_endpoints: Dict[str, int]
    avg_response_time_ms: float

class EndpointStats(BaseModel):
    """Endpoint-level statistics"""
    endpoint: str
    requests: int
    errors: int
    avg_response_time_ms: float
    most_common_status: int

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "usage-analytics",
        "port": PORT,
        "redis": "connected" if REDIS_AVAILABLE else "unavailable",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/status")
async def status():
    """Service status"""
    if not REDIS_AVAILABLE:
        return {
            "status": "degraded",
            "message": "Redis connection unavailable",
            "fallback": "in-memory"
        }
    
    # Get stats from Redis
    try:
        dbsize = redis_client.dbsize()
        return {
            "status": "healthy",
            "redis_keys": dbsize,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# ═══════════════════════════════════════════════════════════════════════════════
# METRICS TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

def track_request(
    api_key: str,
    endpoint: str,
    method: str,
    status_code: int,
    response_time_ms: float,
    ip_address: str
):
    """
    Track API request in analytics
    Called by middleware after each successful request
    """
    if not REDIS_AVAILABLE or redis_client is None:
        return
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:12]
    timestamp = datetime.now(timezone.utc)
    
    # Daily bucket
    daily_key = f"analytics:{key_hash}:daily:{timestamp.date()}"
    redis_client.hincrby(daily_key, "requests", 1)
    redis_client.expire(daily_key, 2592000)  # 30 days retention
    
    # Monthly bucket
    month_key = f"analytics:{key_hash}:month:{timestamp.year}-{timestamp.month:02d}"
    redis_client.hincrby(month_key, "requests", 1)
    redis_client.expire(month_key, 2592000)
    
    # Endpoint statistics
    endpoint_key = f"analytics:{key_hash}:endpoint:{endpoint}"
    redis_client.hincrby(endpoint_key, "requests", 1)
    redis_client.hincrby(endpoint_key, f"status:{status_code}", 1)
    redis_client.hincrbyfloat(endpoint_key, "total_response_time", response_time_ms)
    redis_client.expire(endpoint_key, 2592000)
    
    # Per-minute for trending
    minute_key = f"analytics:{key_hash}:minute:{timestamp.isoformat()}[:5]"
    redis_client.incr(minute_key)
    redis_client.expire(minute_key, 3600)
    
    logger.debug(f"Tracked {method} {endpoint} -> {status_code } ({response_time_ms}ms)")

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/usage")
async def get_usage_metrics(
    authorization: str = Header(None),
    days: int = Query(1, ge=1, le=30)
) -> UsageMetrics:
    """Get usage metrics for authenticated user"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    api_key = authorization.replace("Bearer ", "")
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:12]
    
    if not REDIS_AVAILABLE:
        # Return placeholder
        return UsageMetrics(
            requests_today=0,
            requests_limit=1000,
            requests_remaining=1000,
            requests_this_month=0,
            reset_time=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            top_endpoints={},
            avg_response_time_ms=0
        )
    
    try:
        # Today's requests
        today_key = f"analytics:{key_hash}:daily:{datetime.now(timezone.utc).date()}"
        today_requests = int(redis_client.hget(today_key, "requests") or 0)
        
        # This month's requests
        now = datetime.now(timezone.utc)
        month_key = f"analytics:{key_hash}:month:{now.year}-{now.month:02d}"
        month_requests = int(redis_client.hget(month_key, "requests") or 0)
        
        # Top endpoints
        pattern = f"analytics:{key_hash}:endpoint:*"
        top_endpoints = {}
        for key in redis_client.scan_iter(match=pattern):
            endpoint = key.decode().split(":")[-1]
            requests = int(redis_client.hget(key, "requests") or 0)
            top_endpoints[endpoint] = requests
        
        # Sort by requests
        top_endpoints = dict(sorted(top_endpoints.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Average response time
        total_time = 0
        endpoint_count = 0
        for key in redis_client.scan_iter(match=pattern):
            resp_time = float(redis_client.hget(key, "total_response_time") or 0)
            total_time += resp_time
            endpoint_count += 1
        
        avg_response_time = total_time / endpoint_count if endpoint_count > 0 else 0
        
        return UsageMetrics(
            requests_today=today_requests,
            requests_limit=1000,  # Default Free plan
            requests_remaining=max(0, 1000 - today_requests),
            requests_this_month=month_requests,
            reset_time=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            top_endpoints=top_endpoints,
            avg_response_time_ms=round(avg_response_time, 2)
        )
    
    except Exception as e:
        logger.error(f"Error fetching usage metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@app.get("/api/v1/endpoints")
async def get_endpoint_stats(
    authorization: str = Header(None)
) -> List[EndpointStats]:
    """Get statistics by endpoint"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    api_key = authorization.replace("Bearer ", "")
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:12]
    
    if not REDIS_AVAILABLE:
        return []
    
    try:
        stats_list = []
        pattern = f"analytics:{key_hash}:endpoint:*"
        
        for key in redis_client.scan_iter(match=pattern):
            endpoint = key.decode().split(":")[-1]
            data = redis_client.hgetall(key)
            
            requests = int(data.get(b"requests", 0))
            total_response_time = float(data.get(b"total_response_time", 0))
            
            # Count errors (status >= 400)
            errors = 0
            most_common_status = 200
            max_status_count = 0
            
            for field, value in data.items():
                if field.startswith(b"status:"):
                    status_code = int(field.split(b":")[1])
                    count = int(value)
                    if status_code >= 400:
                        errors += count
                    if count > max_status_count:
                        max_status_count = count
                        most_common_status = status_code
            
            avg_response_time = total_response_time / requests if requests > 0 else 0
            
            stats_list.append(EndpointStats(
                endpoint=endpoint,
                requests=requests,
                errors=errors,
                avg_response_time_ms=round(avg_response_time, 2),
                most_common_status=most_common_status
            ))
        
        return sorted(stats_list, key=lambda x: x.requests, reverse=True)
    
    except Exception as e:
        logger.error(f"Error fetching endpoint stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

@app.post("/api/v1/track")
async def track_request_event(event: RequestEvent):
    """
    Track request event
    Called by rate_limit_middleware or API gateway
    """
    try:
        # Parse timestamp
        timestamp = datetime.fromisoformat(event.timestamp)
        
        # Store event
        if REDIS_AVAILABLE:
            # Store raw events for audit trail
            logger.info(f"Tracked: {event.method} {event.endpoint} -> {event.status_code}")
        
        return {"status": "tracked", "timestamp": datetime.now(timezone.utc).isoformat()}
    
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid event: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Usage Analytics starting on port {PORT}")
    logger.info(f"Redis: {'✓ Connected' if REDIS_AVAILABLE else '⚠ Unavailable (in-memory mode)'}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

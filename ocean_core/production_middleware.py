"""
🛡️ CLISONIX PRODUCTION MIDDLEWARE

Central integration of all production safety features:
- Rate Limiting
- Circuit Breakers  
- Feature Flags
- Health Checks
- Error Handling

Usage in any service:
    from ocean_core.production_middleware import setup_production_safety
    
    app = FastAPI()
    setup_production_safety(app, service_name="your-service")
"""

import logging
import os
from functools import wraps
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from .circuit_breaker import CircuitBreakerRegistry, CircuitState
from .feature_flags import FeatureFlagManager

# Import our safety modules
from .rate_limiter import RateLimiter, RateLimitMiddleware

logger = logging.getLogger("clisonix.production")


def setup_production_safety(
    app: FastAPI,
    service_name: str,
    enable_rate_limiting: bool = True,
    enable_circuit_breakers: bool = True,
    enable_feature_flags: bool = True,
    redis_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Set up production safety features for a FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service (for logging/metrics)
        enable_rate_limiting: Enable rate limiting middleware
        enable_circuit_breakers: Enable circuit breaker patterns
        enable_feature_flags: Enable feature flag system
        redis_url: Redis connection URL (auto-detected if None)
    
    Returns:
        Dictionary containing initialized components
    """
    
    logger.info(f"🛡️ Setting up production safety for {service_name}...")
    
    components: Dict[str, Any] = {
        "service_name": service_name,
        "rate_limiter": None,
        "circuit_breakers": None,
        "feature_flags": None,
    }
    
    # Auto-detect Redis URL
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    
    if enable_rate_limiting:
        rate_limiter = RateLimiter(redis_url=redis_url)
        app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)
        components["rate_limiter"] = rate_limiter
        logger.info("  ✅ Rate limiting enabled")
    
    # =========================================================================
    # CIRCUIT BREAKERS
    # =========================================================================
    
    if enable_circuit_breakers:
        circuit_registry = CircuitBreakerRegistry()
        components["circuit_breakers"] = circuit_registry
        
        # Store in app state for access in routes
        app.state.circuit_breakers = circuit_registry
        logger.info("  ✅ Circuit breakers enabled")
    
    # =========================================================================
    # FEATURE FLAGS
    # =========================================================================
    
    if enable_feature_flags:
        feature_flags = FeatureFlagManager(redis_url=redis_url)
        components["feature_flags"] = feature_flags
        
        # Store in app state
        app.state.feature_flags = feature_flags
        logger.info("  ✅ Feature flags enabled")
    
    # =========================================================================
    # HEALTH CHECK ENDPOINTS
    # =========================================================================
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check"""
        return {
            "status": "healthy",
            "service": service_name,
        }
    
    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check():
        """Detailed health check including dependencies"""
        health = {
            "status": "healthy",
            "service": service_name,
            "components": {}
        }
        
        # Check rate limiter
        if components["rate_limiter"]:
            try:
                # Simple Redis ping
                health["components"]["rate_limiter"] = "healthy"
            except Exception as e:
                logger.warning(f"Rate limiter health check failed: {e}")
                health["components"]["rate_limiter"] = "degraded"
                health["status"] = "degraded"
        
        # Check circuit breakers
        if components["circuit_breakers"]:
            circuits = {}
            for name, cb in components["circuit_breakers"]._registry.items():
                circuits[name] = {
                    "state": cb.state.name,
                    "failures": cb._failure_count,
                }
            health["components"]["circuit_breakers"] = circuits
        
        return health
    
    @app.get("/status", tags=["Health"])
    async def status():
        """Service status for load balancer"""
        return {"status": "ok"}
    
    # =========================================================================
    # ERROR HANDLERS
    # =========================================================================
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Custom HTTP exception handler with logging"""
        if exc.status_code >= 500:
            logger.error(f"Server error: {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "service": service_name,
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Catch-all exception handler"""
        logger.exception(f"Unhandled exception: {exc}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "service": service_name,
            }
        )
    
    # =========================================================================
    # REQUEST/RESPONSE MIDDLEWARE
    # =========================================================================
    
    @app.middleware("http")
    async def add_service_headers(request: Request, call_next):
        """Add service identification headers"""
        response: Response = await call_next(request)
        response.headers["X-Service"] = service_name
        response.headers["X-Clisonix-Version"] = os.getenv("VERSION", "1.0.0")
        return response
    
    logger.info(f"🛡️ Production safety setup complete for {service_name}")
    
    return components


# =============================================================================
# DECORATORS
# =============================================================================

def with_circuit_breaker(circuit_name: str):
    """
    Decorator to wrap a route with circuit breaker protection.
    
    Usage:
        @app.get("/external-api")
        @with_circuit_breaker("external_api")
        async def call_external():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args else None)
            
            if request and hasattr(request.app.state, "circuit_breakers"):
                registry: CircuitBreakerRegistry = request.app.state.circuit_breakers
                circuit = registry.get(circuit_name)
                
                if circuit.state == CircuitState.OPEN:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Service temporarily unavailable ({circuit_name})"
                    )
                
                try:
                    result = await func(*args, **kwargs)
                    circuit.record_success()
                    return result
                except Exception:
                    circuit.record_failure()
                    raise
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_feature(flag_name: str, default: bool = False):
    """
    Decorator to require a feature flag for a route.
    
    Usage:
        @app.get("/new-feature")
        @require_feature("new_dashboard")
        async def new_feature():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args else None)
            
            if request and hasattr(request.app.state, "feature_flags"):
                flags: FeatureFlagManager = request.app.state.feature_flags
                
                # Get user ID from request if available
                user_id = None
                if hasattr(request.state, "user_id"):
                    user_id = request.state.user_id
                
                if not flags.is_enabled(flag_name, user_id=user_id, default=default):
                    raise HTTPException(
                        status_code=404,
                        detail="Not found"  # Don't reveal feature exists
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Demo setup
    from fastapi import FastAPI
    
    app = FastAPI(title="Clisonix Service")
    
    # Set up all production safety features
    components = setup_production_safety(
        app,
        service_name="demo-service",
        enable_rate_limiting=True,
        enable_circuit_breakers=True,
        enable_feature_flags=True,
    )
    
    # Example route with circuit breaker
    @app.get("/external")
    @with_circuit_breaker("external_api")
    async def call_external(request: Request):
        # Call external API
        return {"status": "ok"}
    
    # Example route with feature flag
    @app.get("/beta-feature")
    @require_feature("beta_dashboard")
    async def beta_feature(request: Request):
        return {"message": "Welcome to beta!"}
    
    print("✅ Demo app configured with production safety")

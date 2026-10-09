"""
🔌 CLISONIX CIRCUIT BREAKER - Resilience Pattern Implementation

Prevents cascade failures and protects system stability:
- Automatic failure detection
- Fast fail when service is unhealthy
- Automatic recovery testing
- Per-service circuit configuration

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Failing, all requests immediately rejected  
- HALF_OPEN: Testing if service recovered

Usage:
    from circuit_breaker import CircuitBreaker, circuit_protected
    
    breaker = CircuitBreaker("external_api", failure_threshold=5)
    
    @circuit_protected("external_api")
    async def call_external_api():
        return await external_api.fetch()
"""

import asyncio
import json
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger("clisonix.circuit_breaker")


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class CircuitConfig:
    """Configuration for a circuit breaker"""
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 3          # Successes to close from half-open
    timeout: float = 30.0              # Seconds to wait before half-open
    failure_window: float = 60.0       # Window for counting failures
    half_open_max_calls: int = 3       # Max calls in half-open state
    excluded_exceptions: List[type] = field(default_factory=list)


@dataclass 
class CircuitStats:
    """Statistics for a circuit"""
    total_requests: int = 0
    total_failures: int = 0
    total_successes: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: int = 0


# =============================================================================
# DEFAULT CIRCUIT CONFIGURATIONS
# =============================================================================

DEFAULT_CONFIGS = {
    # External APIs - more lenient
    "external_api": CircuitConfig(
        failure_threshold=5,
        success_threshold=2,
        timeout=30.0
    ),
    
    # Database - critical, be careful
    "database": CircuitConfig(
        failure_threshold=3,
        success_threshold=5,
        timeout=10.0
    ),
    
    # ASI Trinity engines
    "alba": CircuitConfig(
        failure_threshold=5,
        success_threshold=3,
        timeout=15.0
    ),
    "albi": CircuitConfig(
        failure_threshold=5,
        success_threshold=3,
        timeout=15.0
    ),
    "jona": CircuitConfig(
        failure_threshold=5,
        success_threshold=3,
        timeout=15.0
    ),
    
    # Redis cache - can fail, system works without
    "redis": CircuitConfig(
        failure_threshold=10,
        success_threshold=2,
        timeout=5.0
    ),
    
    # Payment services - critical
    "stripe": CircuitConfig(
        failure_threshold=3,
        success_threshold=5,
        timeout=60.0  # Longer wait before retry
    ),
    
    # ML models
    "ml_model": CircuitConfig(
        failure_threshold=5,
        success_threshold=3,
        timeout=20.0
    ),
}


class CircuitBreakerOpen(Exception):
    """Raised when circuit is open"""
    def __init__(self, circuit_name: str, retry_after: float):
        self.circuit_name = circuit_name
        self.retry_after = retry_after
        super().__init__(f"Circuit '{circuit_name}' is open. Retry after {retry_after:.1f}s")


class CircuitBreaker:
    """
    Production-ready circuit breaker implementation.
    
    Pattern: Circuit Breaker (from Release It!)
    - Fail fast when dependent service is down
    - Prevent cascade failures
    - Automatic recovery testing
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitConfig] = None,
        redis_url: Optional[str] = None
    ):
        self.name = name
        self.config = config or DEFAULT_CONFIGS.get(name, CircuitConfig())
        
        # State
        self._state = CircuitState.CLOSED
        self._failure_times: deque = deque(maxlen=100)
        self._stats = CircuitStats()
        self._half_open_calls = 0
        self._last_state_change = time.time()
        
        # Redis for distributed circuit breaker
        self._redis: Optional[redis.Redis] = None
        self._prefix = f"clisonix:circuit:{name}:"
        
        if REDIS_AVAILABLE:
            try:
                redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                self._load_state()
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable for circuit breaker: {e}")
                self._redis = None
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for timeout transition"""
        if self._state == CircuitState.OPEN:
            time_in_open = time.time() - self._last_state_change
            if time_in_open >= self.config.timeout:
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state
    
    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        return self.state == CircuitState.HALF_OPEN
    
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state"""
        old_state = self._state
        self._state = new_state
        self._last_state_change = time.time()
        self._stats.state_changes += 1
        
        if new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        
        logger.warning(
            f"🔌 Circuit '{self.name}': {old_state.value} → {new_state.value} "
            f"(failures: {self._stats.consecutive_failures})"
        )
        
        self._save_state()
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        state = self.state
        
        if state == CircuitState.CLOSED:
            return True
            
        if state == CircuitState.OPEN:
            return False
            
        if state == CircuitState.HALF_OPEN:
            # Allow limited calls in half-open
            if self._half_open_calls < self.config.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False
        
        return False
    
    def record_success(self) -> None:
        """Record a successful call"""
        self._stats.total_requests += 1
        self._stats.total_successes += 1
        self._stats.consecutive_successes += 1
        self._stats.consecutive_failures = 0
        self._stats.last_success_time = time.time()
        
        state = self.state
        
        if state == CircuitState.HALF_OPEN:
            if self._stats.consecutive_successes >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
        
        self._save_state()
    
    def record_failure(self, exception: Optional[Exception] = None) -> None:
        """Record a failed call"""
        # Check if exception should be excluded
        if exception and type(exception) in self.config.excluded_exceptions:
            return
        
        now = time.time()
        self._stats.total_requests += 1
        self._stats.total_failures += 1
        self._stats.consecutive_failures += 1
        self._stats.consecutive_successes = 0
        self._stats.last_failure_time = now
        
        # Add to failure window
        self._failure_times.append(now)
        
        # Remove old failures outside window
        window_start = now - self.config.failure_window
        while self._failure_times and self._failure_times[0] < window_start:
            self._failure_times.popleft()
        
        state = self.state
        
        if state == CircuitState.HALF_OPEN:
            # Any failure in half-open goes back to open
            self._transition_to(CircuitState.OPEN)
            
        elif state == CircuitState.CLOSED:
            # Check if we should open
            failures_in_window = len(self._failure_times)
            if failures_in_window >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
        
        self._save_state()
    
    def get_retry_after(self) -> float:
        """Get seconds until circuit might be ready to retry"""
        if self._state != CircuitState.OPEN:
            return 0
        
        time_in_open = time.time() - self._last_state_change
        return max(0, self.config.timeout - time_in_open)
    
    def reset(self) -> None:
        """Manually reset the circuit (admin use)"""
        self._state = CircuitState.CLOSED
        self._failure_times.clear()
        self._stats = CircuitStats()
        self._half_open_calls = 0
        self._last_state_change = time.time()
        self._save_state()
        logger.info(f"🔄 Circuit '{self.name}' manually reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit status for monitoring"""
        return {
            "name": self.name,
            "state": self.state.value,
            "stats": {
                "total_requests": self._stats.total_requests,
                "total_failures": self._stats.total_failures,
                "total_successes": self._stats.total_successes,
                "consecutive_failures": self._stats.consecutive_failures,
                "failure_rate": (
                    self._stats.total_failures / self._stats.total_requests 
                    if self._stats.total_requests > 0 else 0
                ),
                "state_changes": self._stats.state_changes,
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
            },
            "retry_after": self.get_retry_after(),
            "last_state_change": self._last_state_change,
        }
    
    def _save_state(self) -> None:
        """Save state to Redis for distributed coordination"""
        if not self._redis:
            return
            
        try:
            state_data = {
                "state": self._state.value,
                "last_state_change": self._last_state_change,
                "consecutive_failures": self._stats.consecutive_failures,
                "consecutive_successes": self._stats.consecutive_successes,
            }
            self._redis.set(f"{self._prefix}state", json.dumps(state_data))
            self._redis.expire(f"{self._prefix}state", 3600)  # 1 hour TTL
        except Exception as e:
            logger.warning(f"Failed to save circuit state: {e}")
    
    def _load_state(self) -> None:
        """Load state from Redis"""
        if not self._redis:
            return
            
        try:
            data = self._redis.get(f"{self._prefix}state")
            if data:
                state_data = json.loads(data)
                self._state = CircuitState(state_data.get("state", "closed"))
                self._last_state_change = state_data.get("last_state_change", time.time())
                self._stats.consecutive_failures = state_data.get("consecutive_failures", 0)
                self._stats.consecutive_successes = state_data.get("consecutive_successes", 0)
        except Exception as e:
            logger.warning(f"Failed to load circuit state: {e}")
    
    def __call__(self, func: Callable) -> Callable:
        """Use circuit breaker as decorator"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not self.can_execute():
                raise CircuitBreakerOpen(self.name, self.get_retry_after())
            
            try:
                result = await func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure(e)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not self.can_execute():
                raise CircuitBreakerOpen(self.name, self.get_retry_after())
            
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure(e)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper


# =============================================================================
# CIRCUIT BREAKER REGISTRY
# =============================================================================

class CircuitBreakerRegistry:
    """Central registry for all circuit breakers"""
    
    _instance: Optional['CircuitBreakerRegistry'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._circuits = {}
        return cls._instance
    
    def get(self, name: str, config: Optional[CircuitConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self._circuits:
            self._circuits[name] = CircuitBreaker(name, config)
        return self._circuits[name]
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuits"""
        return {name: cb.get_status() for name, cb in self._circuits.items()}
    
    def reset_all(self) -> None:
        """Reset all circuits (admin use)"""
        for cb in self._circuits.values():
            cb.reset()


def get_circuit(name: str) -> CircuitBreaker:
    """Get circuit breaker from registry"""
    return CircuitBreakerRegistry().get(name)


# =============================================================================
# DECORATOR
# =============================================================================

def circuit_protected(
    circuit_name: str,
    fallback: Optional[Callable] = None,
    config: Optional[CircuitConfig] = None
):
    """
    Decorator to protect a function with a circuit breaker.
    
    Usage:
        @circuit_protected("external_api")
        async def call_api():
            return await external_service.fetch()
        
        # With fallback:
        @circuit_protected("external_api", fallback=lambda: {"cached": True})
        async def call_api():
            return await external_service.fetch()
    """
    def decorator(func: Callable) -> Callable:
        circuit = CircuitBreakerRegistry().get(circuit_name, config)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not circuit.can_execute():
                if fallback:
                    logger.info(f"⚡ Circuit '{circuit_name}' open, using fallback")
                    result = fallback(*args, **kwargs)
                    if asyncio.iscoroutine(result):
                        return await result
                    return result
                raise CircuitBreakerOpen(circuit_name, circuit.get_retry_after())
            
            try:
                result = await func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as e:
                circuit.record_failure(e)
                if fallback:
                    logger.info(f"⚡ Circuit '{circuit_name}' failure, using fallback")
                    result = fallback(*args, **kwargs)
                    if asyncio.iscoroutine(result):
                        return await result
                    return result
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not circuit.can_execute():
                if fallback:
                    return fallback(*args, **kwargs)
                raise CircuitBreakerOpen(circuit_name, circuit.get_retry_after())
            
            try:
                result = func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as e:
                circuit.record_failure(e)
                if fallback:
                    return fallback(*args, **kwargs)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# =============================================================================
# HEALTH CHECK ENDPOINT DATA
# =============================================================================

def get_circuits_health() -> Dict[str, Any]:
    """Get health status of all circuits for /health endpoint"""
    registry = CircuitBreakerRegistry()
    statuses = registry.get_all_status()
    
    open_circuits = [name for name, status in statuses.items() if status["state"] == "open"]
    
    return {
        "circuits": statuses,
        "healthy": len(open_circuits) == 0,
        "open_circuits": open_circuits,
        "total_circuits": len(statuses)
    }


# =============================================================================
# CLI / MONITORING
# =============================================================================

def print_circuit_status():
    """Print status of all circuits"""
    registry = CircuitBreakerRegistry()
    statuses = registry.get_all_status()
    
    print("\n" + "="*60)
    print("🔌 CLISONIX CIRCUIT BREAKERS")
    print("="*60)
    
    if not statuses:
        print("  No circuits registered yet.")
    else:
        for name, status in statuses.items():
            state = status["state"]
            state_emoji = {"closed": "🟢", "open": "🔴", "half_open": "🟡"}.get(state, "⚪")
            
            print(f"\n  {state_emoji} {name}")
            print(f"     State: {state}")
            print(f"     Requests: {status['stats']['total_requests']}")
            print(f"     Failure rate: {status['stats']['failure_rate']:.1%}")
            
            if state == "open":
                print(f"     Retry after: {status['retry_after']:.1f}s")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Demo
    print_circuit_status()
    
    # Create some test circuits
    alba = get_circuit("alba")
    albi = get_circuit("albi")
    database = get_circuit("database")
    
    print("\n🧪 Testing circuit breakers:")
    
    # Simulate some calls
    print("\nSimulating ALBA calls (5 failures):")
    for i in range(5):
        alba.record_failure()
        print(f"  Failure {i+1}: state = {alba.state.value}")
    
    print(f"\n  ALBA circuit is now: {alba.state.value}")
    print(f"  Retry after: {alba.get_retry_after():.1f}s")
    
    # Print final status
    print_circuit_status()

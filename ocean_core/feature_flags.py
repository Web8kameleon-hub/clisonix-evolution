"""
🚀 CLISONIX FEATURE FLAGS - Production Safe Deployment System

This module provides a centralized feature flag system for safe production deployments.
Features:
- Redis-backed for real-time updates
- Percentage-based rollouts
- User group targeting
- Automatic fallback
- Audit logging

Usage:
    from feature_flags import FeatureFlagManager
    
    flags = FeatureFlagManager()
    
    if flags.is_enabled("new_dashboard", user_id="user_123"):
        return new_dashboard()
    else:
        return old_dashboard()
"""

import hashlib
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional

# Try to import Redis, fallback to memory storage if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger("clisonix.feature_flags")


class RolloutStrategy(Enum):
    """Feature flag rollout strategies"""
    OFF = "off"                      # Completely disabled
    ON = "on"                        # Completely enabled
    PERCENTAGE = "percentage"        # % of users
    USER_IDS = "user_ids"           # Specific users only
    STAFF_ONLY = "staff_only"       # Internal team only
    BETA_USERS = "beta_users"       # Beta program users


@dataclass
class FeatureFlag:
    """Feature flag configuration"""
    name: str
    description: str = ""
    enabled: bool = False
    strategy: RolloutStrategy = RolloutStrategy.OFF
    percentage: int = 0  # For percentage rollout (0-100)
    user_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    

# =============================================================================
# DEFAULT FLAGS - Safe defaults for production
# =============================================================================

DEFAULT_FLAGS = {
    # Core Features (Already stable - always ON)
    "core_api": FeatureFlag(
        name="core_api",
        description="Core API endpoints",
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    "auth_system": FeatureFlag(
        name="auth_system", 
        description="Authentication system",
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    
    # ASI Trinity (Stable - always ON)
    "alba_engine": FeatureFlag(
        name="alba_engine",
        description="ALBA Analytical Intelligence Engine",
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    "albi_engine": FeatureFlag(
        name="albi_engine",
        description="ALBI Creative Intelligence Engine", 
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    "jona_engine": FeatureFlag(
        name="jona_engine",
        description="JONA Emotional Intelligence Engine",
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    
    # New Features (Safe defaults - OFF until validated)
    "new_dashboard_v2": FeatureFlag(
        name="new_dashboard_v2",
        description="Redesigned dashboard UI",
        enabled=False,
        strategy=RolloutStrategy.PERCENTAGE,
        percentage=0
    ),
    "real_time_streaming": FeatureFlag(
        name="real_time_streaming",
        description="Real-time data streaming via WebSocket",
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    "advanced_analytics": FeatureFlag(
        name="advanced_analytics",
        description="Advanced analytics module",
        enabled=True, 
        strategy=RolloutStrategy.ON
    ),
    "ocean_core_v2": FeatureFlag(
        name="ocean_core_v2",
        description="Ocean Core v2 with enhanced AI",
        enabled=False,
        strategy=RolloutStrategy.STAFF_ONLY
    ),
    "payment_stripe_v2": FeatureFlag(
        name="payment_stripe_v2",
        description="New Stripe payment integration",
        enabled=False,
        strategy=RolloutStrategy.BETA_USERS
    ),
    "eeg_analysis": FeatureFlag(
        name="eeg_analysis",
        description="EEG brain signal analysis",
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    "audio_processing": FeatureFlag(
        name="audio_processing",
        description="Audio signal processing",
        enabled=True,
        strategy=RolloutStrategy.ON
    ),
    
    # Experimental (Always OFF by default)
    "experimental_ml_model": FeatureFlag(
        name="experimental_ml_model",
        description="Experimental machine learning model",
        enabled=False,
        strategy=RolloutStrategy.OFF
    ),
    "beta_chat_interface": FeatureFlag(
        name="beta_chat_interface",
        description="Beta chat interface",
        enabled=False,
        strategy=RolloutStrategy.BETA_USERS
    ),
}


class FeatureFlagManager:
    """
    Centralized feature flag manager with Redis backing.
    
    Features:
    - Real-time flag updates via Redis
    - Percentage-based rollouts using consistent hashing
    - User targeting for beta features
    - Audit logging for compliance
    - Graceful fallback if Redis unavailable
    """
    
    def __init__(
        self, 
        redis_url: Optional[str] = None,
        prefix: str = "clisonix:flags:",
        default_enabled: bool = False
    ):
        self.prefix = prefix
        self.default_enabled = default_enabled
        self._local_cache: Dict[str, FeatureFlag] = {}
        self._cache_ttl = 60  # seconds
        self._last_cache_refresh = 0
        
        # Staff user IDs (can be loaded from config)
        self._staff_user_ids = set(os.getenv("STAFF_USER_IDS", "").split(","))
        self._beta_user_ids = set(os.getenv("BETA_USER_IDS", "").split(","))
        
        # Redis connection
        self._redis: Optional[redis.Redis] = None
        if REDIS_AVAILABLE:
            try:
                redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("✅ Feature flags connected to Redis")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed, using local cache: {e}")
                self._redis = None
        
        # Initialize default flags
        self._init_default_flags()
    
    def _init_default_flags(self) -> None:
        """Initialize default flags if not present"""
        for name, flag in DEFAULT_FLAGS.items():
            if not self._flag_exists(name):
                self._save_flag(flag)
            self._local_cache[name] = flag
    
    def _flag_exists(self, name: str) -> bool:
        """Check if flag exists in storage"""
        if self._redis:
            return self._redis.exists(f"{self.prefix}{name}") > 0
        return name in self._local_cache
    
    def _save_flag(self, flag: FeatureFlag) -> None:
        """Save flag to storage"""
        flag.updated_at = datetime.now(timezone.utc).isoformat()
        
        if self._redis:
            self._redis.set(
                f"{self.prefix}{flag.name}",
                json.dumps(asdict(flag), default=str)
            )
        
        self._local_cache[flag.name] = flag
        logger.info(f"📌 Flag saved: {flag.name} = {flag.enabled}")
    
    def _load_flag(self, name: str) -> Optional[FeatureFlag]:
        """Load flag from storage"""
        # Check local cache first
        if time.time() - self._last_cache_refresh < self._cache_ttl:
            if name in self._local_cache:
                return self._local_cache[name]
        
        if self._redis:
            data = self._redis.get(f"{self.prefix}{name}")
            if data:
                flag_data = json.loads(data)
                flag_data['strategy'] = RolloutStrategy(flag_data['strategy'])
                flag = FeatureFlag(**flag_data)
                self._local_cache[name] = flag
                return flag
        
        return self._local_cache.get(name)
    
    def is_enabled(
        self, 
        flag_name: str, 
        user_id: Optional[str] = None,
        default: Optional[bool] = None
    ) -> bool:
        """
        Check if a feature flag is enabled for a user.
        
        Args:
            flag_name: Name of the feature flag
            user_id: Optional user ID for percentage/targeting rollouts
            default: Default value if flag doesn't exist
            
        Returns:
            True if feature is enabled, False otherwise
        """
        flag = self._load_flag(flag_name)
        
        if flag is None:
            logger.warning(f"⚠️ Unknown flag: {flag_name}, using default: {default or self.default_enabled}")
            return default if default is not None else self.default_enabled
        
        # Flag is completely disabled
        if not flag.enabled:
            return False
        
        # Check strategy
        if flag.strategy == RolloutStrategy.OFF:
            return False
            
        elif flag.strategy == RolloutStrategy.ON:
            return True
            
        elif flag.strategy == RolloutStrategy.PERCENTAGE:
            if not user_id:
                return False
            return self._in_percentage_bucket(flag_name, user_id, flag.percentage)
            
        elif flag.strategy == RolloutStrategy.USER_IDS:
            return user_id in flag.user_ids
            
        elif flag.strategy == RolloutStrategy.STAFF_ONLY:
            return user_id in self._staff_user_ids
            
        elif flag.strategy == RolloutStrategy.BETA_USERS:
            return user_id in self._beta_user_ids
        
        return flag.enabled
    
    def _in_percentage_bucket(self, flag_name: str, user_id: str, percentage: int) -> bool:
        """
        Determine if a user is in the percentage bucket using consistent hashing.
        Same user always gets same result for same flag.
        """
        if percentage <= 0:
            return False
        if percentage >= 100:
            return True
            
        # Consistent hash based on flag name + user ID
        hash_input = f"{flag_name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        bucket = hash_value % 100
        
        return bucket < percentage
    
    def set_flag(
        self, 
        name: str, 
        enabled: bool, 
        strategy: RolloutStrategy = RolloutStrategy.ON,
        percentage: int = 100,
        user_ids: Optional[List[str]] = None,
        description: str = ""
    ) -> FeatureFlag:
        """
        Create or update a feature flag.
        
        Args:
            name: Flag name
            enabled: Whether flag is enabled
            strategy: Rollout strategy
            percentage: Percentage for percentage rollout
            user_ids: List of user IDs for user targeting
            description: Human-readable description
            
        Returns:
            The created/updated flag
        """
        existing = self._load_flag(name)
        
        flag = FeatureFlag(
            name=name,
            description=description or (existing.description if existing else ""),
            enabled=enabled,
            strategy=strategy,
            percentage=percentage,
            user_ids=user_ids or [],
            created_at=existing.created_at if existing else datetime.now(timezone.utc).isoformat()
        )
        
        self._save_flag(flag)
        self._log_flag_change(name, enabled, strategy, percentage)
        
        return flag
    
    def enable(self, name: str, percentage: int = 100) -> None:
        """Enable a flag (optionally with percentage)"""
        existing = self._load_flag(name) or FeatureFlag(name=name)
        if percentage < 100:
            self.set_flag(name, True, RolloutStrategy.PERCENTAGE, percentage)
        else:
            self.set_flag(name, True, RolloutStrategy.ON)
    
    def disable(self, name: str) -> None:
        """Disable a flag completely"""
        self.set_flag(name, False, RolloutStrategy.OFF)
    
    def gradual_rollout(self, name: str, target_percentage: int, step: int = 10) -> int:
        """
        Increase rollout percentage gradually.
        Returns the new percentage.
        """
        flag = self._load_flag(name)
        if not flag:
            logger.error(f"❌ Flag not found: {name}")
            return 0
            
        current = flag.percentage if flag.strategy == RolloutStrategy.PERCENTAGE else 0
        new_percentage = min(current + step, target_percentage, 100)
        
        self.set_flag(
            name, 
            True, 
            RolloutStrategy.PERCENTAGE, 
            new_percentage,
            description=flag.description
        )
        
        logger.info(f"🚀 Gradual rollout: {name} {current}% → {new_percentage}%")
        return new_percentage
    
    def get_all_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags"""
        if self._redis:
            keys = self._redis.keys(f"{self.prefix}*")
            for key in keys:
                name = key.replace(self.prefix, "")
                self._load_flag(name)
        return self._local_cache.copy()
    
    def get_flag_status(self, name: str) -> Dict[str, Any]:
        """Get detailed flag status"""
        flag = self._load_flag(name)
        if not flag:
            return {"error": f"Flag not found: {name}"}
            
        return {
            "name": flag.name,
            "enabled": flag.enabled,
            "strategy": flag.strategy.value,
            "percentage": flag.percentage,
            "description": flag.description,
            "updated_at": flag.updated_at
        }
    
    def _log_flag_change(
        self, 
        name: str, 
        enabled: bool, 
        strategy: RolloutStrategy, 
        percentage: int
    ) -> None:
        """Log flag changes for audit"""
        logger.info(
            f"🏴 FLAG CHANGE: {name} | "
            f"enabled={enabled} | "
            f"strategy={strategy.value} | "
            f"percentage={percentage}%"
        )
        
        # Store audit log in Redis if available
        if self._redis:
            audit_entry = {
                "flag": name,
                "enabled": enabled,
                "strategy": strategy.value,
                "percentage": percentage,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._redis.lpush(f"{self.prefix}audit", json.dumps(audit_entry))
            self._redis.ltrim(f"{self.prefix}audit", 0, 999)  # Keep last 1000 entries


def feature_flag(flag_name: str, default_value: Any = None):
    """
    Decorator for feature-flagged functions.
    
    Usage:
        @feature_flag("new_feature")
        def new_feature_handler():
            return "New feature!"
            
        # With fallback:
        @feature_flag("new_feature", default_value=legacy_handler)
        def new_feature_handler():
            return "New feature!"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _flags = FeatureFlagManager()
            user_id = kwargs.get('user_id') or kwargs.get('current_user_id')
            
            if _flags.is_enabled(flag_name, user_id):
                return func(*args, **kwargs)
            elif callable(default_value):
                return default_value(*args, **kwargs)
            else:
                return default_value
        return wrapper
    return decorator


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_global_flags: Optional[FeatureFlagManager] = None

def get_flags() -> FeatureFlagManager:
    """Get global feature flag manager instance"""
    global _global_flags
    if _global_flags is None:
        _global_flags = FeatureFlagManager()
    return _global_flags


# =============================================================================
# CLI / QUICK COMMANDS
# =============================================================================

def print_all_flags():
    """Print all feature flags status"""
    flags = get_flags()
    all_flags = flags.get_all_flags()
    
    print("\n" + "="*60)
    print("🏴 CLISONIX FEATURE FLAGS")
    print("="*60)
    
    for name, flag in sorted(all_flags.items()):
        status = "✅ ON" if flag.enabled else "❌ OFF"
        strategy = f"[{flag.strategy.value}]"
        pct = f" {flag.percentage}%" if flag.strategy == RolloutStrategy.PERCENTAGE else ""
        print(f"  {status} {name:30} {strategy:15} {pct}")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # Demo / test
    print_all_flags()
    
    # Example usage
    flags = get_flags()
    
    # Check flag for a user
    user = "user_123"
    print(f"\n🧪 Testing flags for user: {user}")
    print(f"  alba_engine: {flags.is_enabled('alba_engine', user)}")
    print(f"  ocean_core_v2: {flags.is_enabled('ocean_core_v2', user)}")
    print(f"  new_dashboard_v2: {flags.is_enabled('new_dashboard_v2', user)}")
    
    # Gradual rollout example
    print("\n📈 Gradual rollout demo:")
    flags.set_flag("new_dashboard_v2", True, RolloutStrategy.PERCENTAGE, 5)
    print(f"  new_dashboard_v2 @ 5%: {flags.is_enabled('new_dashboard_v2', 'user_001')}")
    print(f"  new_dashboard_v2 @ 5%: {flags.is_enabled('new_dashboard_v2', 'user_050')}")

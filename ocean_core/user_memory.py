"""
OCEAN USER MEMORY - Persistent, Redis-backed per-client memory
================================================================

Why IP-keyed, not user_id/clerk_user_id-keyed:
Request bodies are not authenticated here (see `_memory_key` history in
ocean_core_full.py) — `user_id`/`clerk_user_id` are client-supplied fields
nobody verifies server-side, so keying long-lived memory by them would let
any caller read or pollute another person's memory. The server-derived
client IP (from X-Forwarded-For / socket peer) is the strongest identity
signal honestly available end-to-end today without a real auth layer.

Persistence: best-effort Redis (already a dependency, already used
elsewhere in ocean-core with the same try/except-fallback convention).
If Redis is unavailable, memory simply doesn't survive a restart — it
never fabricates history and never breaks the chat response.
"""
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ocean_user_memory")

try:
    import redis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False

_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_REDIS_SOCKET_TIMEOUT_S = float(os.getenv("OCEAN_MEMORY_REDIS_TIMEOUT_S", "0.3"))
_KEY_PREFIX = "ocean:user_memory:"

_redis_client = None
_redis_init_attempted = False


def _get_redis_client():
    global _redis_client, _redis_init_attempted
    if not _REDIS_AVAILABLE:
        return None
    if _redis_client is not None or _redis_init_attempted:
        return _redis_client
    _redis_init_attempted = True
    try:
        _redis_client = redis.Redis.from_url(
            _REDIS_URL,
            socket_timeout=_REDIS_SOCKET_TIMEOUT_S,
            socket_connect_timeout=_REDIS_SOCKET_TIMEOUT_S,
            decode_responses=True,
        )
        _redis_client.ping()
        logger.info("Ocean user memory: Redis persistence active")
    except Exception as exc:
        logger.info(f"Ocean user memory: Redis unavailable, falling back to in-process only: {exc}")
        _redis_client = None
    return _redis_client


def memory_key_from_ip(ip: str) -> str:
    """Build the persistence key for a given client IP. Empty IP => no key,
    matching the existing deliberate "no identity, no memory" behavior."""
    clean = (ip or "").strip()
    if not clean or clean.lower() == "unknown":
        return ""
    return f"{_KEY_PREFIX}{clean}"


def load_turns(key: str, max_turns: int) -> Optional[List[Dict[str, Any]]]:
    """Load persisted turns from Redis. Returns None (not []) when Redis is
    unavailable or has no data, so callers can distinguish "no backing store"
    from "backing store confirms empty history"."""
    if not key:
        return None
    client = _get_redis_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, list):
            return data[-max_turns:]
        return []
    except Exception as exc:
        logger.info(f"Ocean user memory: load failed for key={key}: {exc}")
        return None


def save_turns(key: str, turns: List[Dict[str, Any]], ttl_seconds: int) -> None:
    """Persist the current turn bucket. Never raises — a persistence failure
    must never break the in-flight chat response."""
    if not key:
        return
    client = _get_redis_client()
    if client is None:
        return
    try:
        client.set(key, json.dumps(turns, ensure_ascii=False), ex=max(60, int(ttl_seconds)))
    except Exception as exc:
        logger.info(f"Ocean user memory: save failed for key={key}: {exc}")


def delete_turns(key: str) -> bool:
    """Delete persisted turns.

    Returns False when Redis cannot confirm the deletion so callers do not
    report a successful reset while persistent history may still exist.
    """
    if not key:
        return False
    client = _get_redis_client()
    if client is None:
        return False
    try:
        client.delete(key)
        return True
    except Exception as exc:
        logger.warning(f"Ocean user memory: delete failed for key={key}: {exc}")
        return False


def now_ts() -> float:
    return time.time()

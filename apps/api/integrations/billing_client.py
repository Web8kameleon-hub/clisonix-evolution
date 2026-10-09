# -*- coding: utf-8 -*-
"""
Fail-soft client for independent billing-core service.
This module is intentionally standalone so app runtime does not crash
if billing-core is unavailable.
"""

import os
import time
from typing import Any, Dict, Optional

import httpx

BILLING_CORE_URL = os.getenv("BILLING_CORE_URL", "").strip()
BILLING_TIMEOUT_SECONDS = float(os.getenv("BILLING_TIMEOUT_SECONDS", "0.45"))
CACHE_TTL_SECONDS = int(os.getenv("BILLING_CACHE_TTL_SECONDS", "120"))

_local_cache: Dict[str, Dict[str, Any]] = {}


def _fallback_entitlement(reason: str = "fallback") -> Dict[str, Any]:
    return {
        "ok": False,
        "source": "billing-core-unavailable",
        "plan": None,
        "requests_per_day": None,
        "features": [],
        "api_key_status": reason,
    }


def _get_cached(api_key: str) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None
    entry = _local_cache.get(api_key)
    if not entry:
        return None
    if (time.time() - entry["ts"]) > CACHE_TTL_SECONDS:
        _local_cache.pop(api_key, None)
        return None
    return entry["value"]


def _set_cached(api_key: str, value: Dict[str, Any]) -> None:
    if api_key:
        _local_cache[api_key] = {"ts": time.time(), "value": value}


async def resolve_entitlement(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return _fallback_entitlement("missing")

    if not BILLING_CORE_URL:
        return _fallback_entitlement("billing_core_url_missing")

    cached = _get_cached(api_key)
    if cached:
        return {**cached, "cache": "hit"}

    try:
        async with httpx.AsyncClient(timeout=BILLING_TIMEOUT_SECONDS) as client:
            resp = await client.get(
                f"{BILLING_CORE_URL}/api/v1/entitlements/resolve",
                headers={"X-API-Key": api_key},
            )
            if resp.status_code == 200:
                value = resp.json()
                _set_cached(api_key, value)
                return {**value, "cache": "miss"}
    except Exception:
        return _fallback_entitlement("billing_unreachable")

    return _fallback_entitlement("billing_unavailable")

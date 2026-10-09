# -*- coding: utf-8 -*-
"""
Monetization Bridge Router
Keeps monetization dependency isolated and fail-soft.
"""

from fastapi import APIRouter, Request
from integrations.billing_client import resolve_entitlement

router = APIRouter(prefix="/api/v1/monetization", tags=["monetization"])


@router.get("/health")
async def monetization_health() -> dict:
    return {
        "ok": True,
        "mode": "independent",
        "fail_soft": True,
    }


@router.get("/entitlement")
async def monetization_entitlement(request: Request) -> dict:
    raw = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
    entitlement = await resolve_entitlement(raw)
    return entitlement

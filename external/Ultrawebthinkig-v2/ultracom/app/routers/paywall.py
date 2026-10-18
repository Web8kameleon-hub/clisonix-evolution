import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/paywall", tags=["paywall"])

PAYWALL_UPSTREAM_URL = os.getenv("PAYWALL_UPSTREAM_URL", "").strip().rstrip("/")
PAYWALL_UPSTREAM_TOKEN = os.getenv("PAYWALL_UPSTREAM_TOKEN", "").strip()
PAYWALL_TIMEOUT = float(os.getenv("PAYWALL_TIMEOUT", "20"))


def _assert_paywall_config() -> None:
    if not PAYWALL_UPSTREAM_URL:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "configuration_error",
                "message": "PAYWALL_UPSTREAM_URL is required",
            },
        )


def _headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if PAYWALL_UPSTREAM_TOKEN:
        headers["Authorization"] = f"Bearer {PAYWALL_UPSTREAM_TOKEN}"
    return headers


async def _proxy(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    _assert_paywall_config()
    try:
        async with httpx.AsyncClient(timeout=PAYWALL_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=f"{PAYWALL_UPSTREAM_URL}{path}",
                headers=_headers(),
                json=body,
                params=params,
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "error": "upstream_request_failed",
                    "status": response.status_code,
                    "path": path,
                },
            )
        return response.json()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={"error": "upstream_unavailable", "path": path, "message": str(error)},
        )


@router.post("/access-check")
async def access_check(request: Request):
    return await _proxy("POST", "/access-check", body=await request.json())


@router.get("/plans")
async def plans():
    return await _proxy("GET", "/plans")


@router.get("/subscription")
async def subscription(request: Request):
    customer_id = request.query_params.get("customerId")
    params = {"customerId": customer_id} if customer_id else None
    return await _proxy("GET", "/subscription", params=params)

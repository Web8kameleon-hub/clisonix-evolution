import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/ads", tags=["ads-enterprise"])

ADS_UPSTREAM_URL = os.getenv("ADS_UPSTREAM_URL", "").strip().rstrip("/")
ADS_UPSTREAM_TOKEN = os.getenv("ADS_UPSTREAM_TOKEN", "").strip()
ADS_TIMEOUT = float(os.getenv("ADS_TIMEOUT", "20"))


def _assert_ads_config() -> None:
    if not ADS_UPSTREAM_URL:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "configuration_error",
                "message": "ADS_UPSTREAM_URL is required",
            },
        )


def _headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if ADS_UPSTREAM_TOKEN:
        headers["Authorization"] = f"Bearer {ADS_UPSTREAM_TOKEN}"
    return headers


async def _proxy(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    _assert_ads_config()
    try:
        async with httpx.AsyncClient(timeout=ADS_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=f"{ADS_UPSTREAM_URL}{path}",
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


@router.get("/health")
async def ads_health():
    return await _proxy("GET", "/health")


@router.get("/campaigns")
async def campaigns(request: Request):
    account_id = request.query_params.get("accountId")
    params = {"accountId": account_id} if account_id else None
    return await _proxy("GET", "/campaigns", params=params)


@router.post("/serve")
async def serve_ad(request: Request):
    return await _proxy("POST", "/serve", body=await request.json())


@router.get("/revenue")
async def revenue(request: Request):
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    params: dict[str, str] = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    return await _proxy("GET", "/revenue", params=params or None)

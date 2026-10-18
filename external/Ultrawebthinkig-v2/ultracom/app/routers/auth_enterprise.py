import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/auth", tags=["enterprise-auth"])

AUTH_UPSTREAM_URL = os.getenv("AUTH_UPSTREAM_URL", "").strip().rstrip("/")
AUTH_UPSTREAM_TOKEN = os.getenv("AUTH_UPSTREAM_TOKEN", "").strip()
AUTH_TIMEOUT = float(os.getenv("AUTH_TIMEOUT", "20"))


def _assert_auth_config() -> None:
    if not AUTH_UPSTREAM_URL:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "configuration_error",
                "message": "AUTH_UPSTREAM_URL is required",
            },
        )


def _headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if AUTH_UPSTREAM_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_UPSTREAM_TOKEN}"
    return headers


async def _proxy(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    incoming_auth: str | None = None,
) -> Any:
    _assert_auth_config()
    headers = _headers()
    if incoming_auth:
        headers["X-Forwarded-Authorization"] = incoming_auth
    try:
        async with httpx.AsyncClient(timeout=AUTH_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=f"{AUTH_UPSTREAM_URL}{path}",
                headers=headers,
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


@router.post("/verify-token")
async def verify_token(request: Request):
    return await _proxy(
        method="POST",
        path="/verify-token",
        body=await request.json(),
        incoming_auth=request.headers.get("Authorization"),
    )


@router.get("/session")
async def get_session(request: Request):
    return await _proxy(
        method="GET",
        path="/session",
        incoming_auth=request.headers.get("Authorization"),
    )

from __future__ import annotations

import os
from collections.abc import AsyncIterator

from fastapi import HTTPException

try:
    from longo_client import LongoClient
except ImportError:
    from apps.api.longo_client import LongoClient


async def get_longo() -> AsyncIterator[LongoClient]:
    longo_url = os.getenv("LONGO_URL")
    if not longo_url:
        raise HTTPException(
            status_code=503,
            detail={"code": "LONGO_NOT_CONFIGURED", "message": "Longo datastore is not configured"},
        )
    client = LongoClient(longo_url)
    try:
        yield client
    finally:
        await client.close()

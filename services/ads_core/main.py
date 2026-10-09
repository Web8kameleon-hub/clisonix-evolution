# -*- coding: utf-8 -*-
"""
Clisonix Ads Core (isolated)
- Consent-gated ad serving
- No automatic script injection
- Minimal tracking for impressions/clicks
"""

import os
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header
from pydantic import BaseModel, Field

APP_NAME = "clisonix-ads-core"
PORT = int(os.getenv("PORT", "8096"))
DATA_DIR = Path(os.getenv("ADS_DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "ads.db"

ADS_PROVIDER = os.getenv("ADS_PROVIDER", "none").lower()  # propellerads | adsterra | none
ADS_ENABLED = os.getenv("ADS_ENABLED", "false").lower() == "true"
ADS_REQUIRE_CONSENT = os.getenv("ADS_REQUIRE_CONSENT", "true").lower() == "true"
ADS_ALLOWED_COUNTRIES = [c.strip().upper() for c in os.getenv("ADS_ALLOWED_COUNTRIES", "AL,XK,MK,ME,RS,GR,IT,ES,DE,CH").split(",") if c.strip()]

# Zone ids (never hardcode sensitive keys in code)
PROPELLER_ZONE_NATIVE = os.getenv("PROPELLER_ZONE_NATIVE", "")
PROPELLER_ZONE_BANNER = os.getenv("PROPELLER_ZONE_BANNER", "")
ADSTERRA_ZONE_SOCIAL = os.getenv("ADSTERRA_ZONE_SOCIAL", "")

DATA_DIR.mkdir(parents=True, exist_ok=True)
_db_lock = threading.Lock()


class AdConfigResponse(BaseModel):
    enabled: bool
    reason: str
    provider: str
    slot: str
    render_mode: str = "script"
    script_url: Optional[str] = None
    script_attrs: Dict[str, str] = Field(default_factory=dict)
    fallback_text: Optional[str] = None


class TrackEvent(BaseModel):
    event: str = Field(pattern="^(impression|click)$")
    slot: str = Field(min_length=2, max_length=64)
    provider: str = Field(min_length=2, max_length=32)
    placement_id: Optional[str] = Field(default=None, max_length=128)
    page: Optional[str] = Field(default="", max_length=256)
    country: Optional[str] = Field(default="", max_length=4)


@contextmanager
def db_conn():
    with _db_lock:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    with db_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ad_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                slot TEXT NOT NULL,
                provider TEXT NOT NULL,
                placement_id TEXT,
                page TEXT,
                country TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_ad_payload(slot: str) -> AdConfigResponse:
    if not ADS_ENABLED:
        return AdConfigResponse(enabled=False, reason="ads_disabled", provider=ADS_PROVIDER, slot=slot, fallback_text="Ads are currently disabled.")

    if ADS_PROVIDER == "propellerads":
        if slot == "native" and PROPELLER_ZONE_NATIVE:
            return AdConfigResponse(
                enabled=True,
                reason="ok",
                provider="propellerads",
                slot=slot,
                script_url="https://native.do/runner/current/native.js",
                script_attrs={"data-zone": PROPELLER_ZONE_NATIVE},
            )
        if slot == "footer" and PROPELLER_ZONE_BANNER:
            return AdConfigResponse(
                enabled=True,
                reason="ok",
                provider="propellerads",
                slot=slot,
                script_url="https://banner.do/runner/current/banner.js",
                script_attrs={"data-zone": PROPELLER_ZONE_BANNER},
            )
        return AdConfigResponse(enabled=False, reason="zone_missing", provider="propellerads", slot=slot, fallback_text="Ad slot not configured.")

    if ADS_PROVIDER == "adsterra":
        if slot == "footer" and ADSTERRA_ZONE_SOCIAL:
            return AdConfigResponse(
                enabled=True,
                reason="ok",
                provider="adsterra",
                slot=slot,
                script_url="https://www.highperformanceformat.com/invoke.js",
                script_attrs={"data-zone": ADSTERRA_ZONE_SOCIAL},
            )
        return AdConfigResponse(enabled=False, reason="zone_missing", provider="adsterra", slot=slot, fallback_text="Ad slot not configured.")

    return AdConfigResponse(enabled=False, reason="provider_not_configured", provider=ADS_PROVIDER, slot=slot, fallback_text="No ad provider configured.")


app = FastAPI(title=APP_NAME, version="1.0.0")


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": APP_NAME,
        "provider": ADS_PROVIDER,
        "ads_enabled": ADS_ENABLED,
        "require_consent": ADS_REQUIRE_CONSENT,
        "time": utc_now(),
    }


@app.get("/api/v1/ads/config", response_model=AdConfigResponse)
async def ads_config(
    slot: str = "footer",
    country: str = "",
    consent: bool = False,
) -> AdConfigResponse:
    normalized_country = (country or "").upper()

    if ADS_REQUIRE_CONSENT and not consent:
        return AdConfigResponse(enabled=False, reason="consent_required", provider=ADS_PROVIDER, slot=slot, fallback_text="Consent required")

    if normalized_country and ADS_ALLOWED_COUNTRIES and normalized_country not in ADS_ALLOWED_COUNTRIES:
        return AdConfigResponse(enabled=False, reason="country_not_allowed", provider=ADS_PROVIDER, slot=slot, fallback_text="Ads unavailable in your region")

    return build_ad_payload(slot=slot)


@app.post("/api/v1/ads/track")
async def ads_track(event: TrackEvent, x_request_id: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    event_id = str(uuid.uuid4())

    with db_conn() as conn:
        conn.execute(
            """
            INSERT INTO ad_events (id, event_type, slot, provider, placement_id, page, country, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                event.event,
                event.slot,
                event.provider,
                event.placement_id or "",
                event.page or "",
                (event.country or "").upper(),
                utc_now(),
            ),
        )

    return {"ok": True, "event_id": event_id, "request_id": x_request_id}


@app.get("/api/v1/ads/stats")
async def ads_stats() -> Dict[str, Any]:
    with db_conn() as conn:
        total = conn.execute("SELECT COUNT(1) c FROM ad_events").fetchone()["c"]
        by_event = conn.execute("SELECT event_type, COUNT(1) c FROM ad_events GROUP BY event_type").fetchall()
        by_slot = conn.execute("SELECT slot, COUNT(1) c FROM ad_events GROUP BY slot").fetchall()

    return {
        "ok": True,
        "service": APP_NAME,
        "total_events": total,
        "by_event": {row["event_type"]: row["c"] for row in by_event},
        "by_slot": {row["slot"]: row["c"] for row in by_slot},
    }

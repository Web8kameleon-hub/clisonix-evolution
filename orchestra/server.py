"""
Orchestra Division — FastAPI server (port 9700)
================================================
Endpoints
---------
  GET  /health                 liveness check
  GET  /status                 readiness — returns overall signal status
  GET  /report                 full DivisionReport (all domains)
  GET  /report/{domain}        single domain probe
  GET  /domains                list registered domains
  POST /report/refresh         trigger fresh run (same as GET /report)
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from orchestra import OrchestraDivision, __version__
from orchestra.models import SignalStatus

logging.basicConfig(
    level    = os.getenv("LOG_LEVEL", "INFO"),
    format   = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt  = "%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("orchestra.server")

app = FastAPI(
    title       = "Clisonix Orchestra Division",
    description = "Unified signal orchestrator for all Clisonix domains",
    version     = __version__,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["GET", "POST"],
    allow_headers  = ["*"],
)

_division: Optional[OrchestraDivision] = None


@app.on_event("startup")
async def _startup() -> None:
    global _division
    _division = OrchestraDivision()
    log.info("OrchestraDivision initialised  domains=%s", _division.domains)


@app.on_event("shutdown")
async def _shutdown() -> None:
    if _division:
        _division.shutdown()


# ── helpers ────────────────────────────────────────────────────────────────────

def _division_or_raise() -> OrchestraDivision:
    if _division is None:
        raise HTTPException(503, "Division not initialised yet")
    return _division


# ── routes ─────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["ops"])
async def health() -> Dict[str, Any]:
    return {
        "status":    "ok",
        "service":   "orchestra-division",
        "version":   __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status", tags=["ops"])
async def status() -> JSONResponse:
    """Quick readiness check — runs all probes and returns overall status."""
    division = _division_or_raise()
    report   = await division.run()
    overall  = report.compute_overall()
    http_status = 200 if overall != SignalStatus.ERROR else 503
    return JSONResponse(
        status_code = http_status,
        content = {
            "overall":      overall.value,
            "ok_count":     report.ok_count,
            "warning_count": report.warning_count,
            "error_count":  report.error_count,
            "generated_at": report.generated_at,
        },
    )


@app.get("/domains", tags=["orchestra"])
async def list_domains() -> Dict[str, Any]:
    division = _division_or_raise()
    return {
        "domains": division.domains,
        "total":   len(division.domains),
    }


@app.get("/report", tags=["orchestra"])
async def full_report(
    domains: Optional[str] = Query(
        None,
        description="Comma-separated subset, e.g. 'repo,hetzner,cache'",
    )
) -> JSONResponse:
    """Run all (or selected) domain probes and return the full report."""
    division = _division_or_raise()

    if domains:
        domain_list = [d.strip() for d in domains.split(",") if d.strip()]
        probe_division = OrchestraDivision(
            timeout_s = division.timeout_s,
            domains   = domain_list,
        )
        report = await probe_division.run()
        probe_division.shutdown()
    else:
        report = await division.run()

    data         = report.to_dict()
    http_status  = 200 if report.compute_overall() != SignalStatus.ERROR else 207
    return JSONResponse(status_code=http_status, content=data)


@app.get("/report/{domain}", tags=["orchestra"])
async def domain_report(domain: str) -> JSONResponse:
    """Run a single domain probe."""
    division = _division_or_raise()
    result   = await division.run_domain(domain)
    http_status = 200 if result.status != SignalStatus.ERROR else 503
    return JSONResponse(status_code=http_status, content=result.to_dict())


@app.post("/report/refresh", tags=["orchestra"])
async def refresh_report() -> JSONResponse:
    """Alias for GET /report — useful for webhook triggers."""
    return await full_report(domains=None)

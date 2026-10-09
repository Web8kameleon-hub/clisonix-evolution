"""
Orchestra Division Framework
=============================
Unified signal orchestrator for the entire Clisonix stack.

Signals covered
---------------
  repo          — GitHub repository (CI runs, PRs, vuln count, last push)
  hetzner       — Hetzner server services health battery
  cloudflare    — Cloudflare edge worker / zone status
  git_profile   — Local git identity (author, email, remotes)
  gitignore     — .gitignore hygiene gate
  cache         — Redis cache health (PING, memory, hit-rate)
  clients       — Active API-key clients telemetry

Entry points
------------
  division.OrchestraDivision   async orchestrator class
  server.app                   FastAPI ASGI application (port 9700)
"""

from .division import OrchestraDivision  # noqa: F401
from .models import DivisionReport, ProbeResult, SignalStatus  # noqa: F401

__version__ = "1.0.0"
__all__ = ["OrchestraDivision", "DivisionReport", "ProbeResult", "SignalStatus"]

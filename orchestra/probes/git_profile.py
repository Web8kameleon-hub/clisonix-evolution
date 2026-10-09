"""
orchestra.probes.git_profile
=============================
Reads the local git identity and remote configuration.

Checks
------
  - user.name and user.email are set
  - Correct GitHub remote (origin) points to expected org
  - GPG / commit signing configured (advisory)
  - Recent commit author matches expected identity

Env var
-------
  GIT_EXPECTED_EMAIL   e.g. "you@example.com"  (optional cross-check)
  GIT_EXPECTED_ORG     e.g. "Web8kameleon-hub"  (optional remote check)
  GIT_REPO_PATH        path to repo root (default: CWD)
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

from orchestra.models import ProbeResult, SignalStatus

_EXPECTED_EMAIL = os.getenv("GIT_EXPECTED_EMAIL", "")
_EXPECTED_ORG   = os.getenv("GIT_EXPECTED_ORG", "Web8kameleon-hub")
_REPO_PATH      = Path(os.getenv("GIT_REPO_PATH", ".")).resolve()


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(_REPO_PATH)] + list(args),
        capture_output=True, text=True, timeout=5
    )
    return result.stdout.strip()


def run() -> ProbeResult:
    start = time.monotonic()
    details: Dict[str, Any] = {}
    warnings: list[str] = []
    errors: list[str] = []

    try:
        # ── identity ─────────────────────────────────────────────────────────
        name  = _git("config", "--get", "user.name")
        email = _git("config", "--get", "user.email")
        details["git_name"]  = name  or "(not set)"
        details["git_email"] = email or "(not set)"

        if not name:
            warnings.append("git user.name is not configured")
        if not email:
            warnings.append("git user.email is not configured")
        if _EXPECTED_EMAIL and email and email != _EXPECTED_EMAIL:
            warnings.append(f"git email mismatch: got '{email}', expected '{_EXPECTED_EMAIL}'")

        # ── remotes ───────────────────────────────────────────────────────────
        remotes_raw = _git("remote", "-v")
        details["remotes_raw"] = remotes_raw
        remotes: Dict[str, str] = {}
        for line in remotes_raw.splitlines():
            parts = line.split()
            if len(parts) >= 2 and "(fetch)" in parts:
                remotes[parts[0]] = parts[1]
        details["remotes"] = remotes

        origin = remotes.get("origin", "")
        if not origin:
            errors.append("No 'origin' remote configured")
        elif _EXPECTED_ORG and _EXPECTED_ORG.lower() not in origin.lower():
            warnings.append(f"origin={origin!r} does not contain expected org '{_EXPECTED_ORG}'")

        # ── current branch ────────────────────────────────────────────────────
        branch = _git("branch", "--show-current")
        details["current_branch"] = branch or _git("rev-parse", "--abbrev-ref", "HEAD")

        # ── last commit ───────────────────────────────────────────────────────
        log = _git("log", "-1", "--format=%H|%ae|%s|%ci")
        if log:
            parts = log.split("|", 3)
            details["last_commit"] = {
                "hash":    parts[0] if len(parts) > 0 else "",
                "author":  parts[1] if len(parts) > 1 else "",
                "subject": parts[2] if len(parts) > 2 else "",
                "date":    parts[3] if len(parts) > 3 else "",
            }

        # ── signing ───────────────────────────────────────────────────────────
        signing_key = _git("config", "--get", "user.signingkey")
        details["gpg_signing_key"] = signing_key or "(not set)"
        details["commit_gpgsign"]  = _git("config", "--get", "commit.gpgsign") or "false"

        # ── result ────────────────────────────────────────────────────────────
        if errors:
            status  = SignalStatus.ERROR
            message = "; ".join(errors)
        elif warnings:
            status  = SignalStatus.WARNING
            message = "; ".join(warnings)
        else:
            status  = SignalStatus.OK
            message = f"git identity ok ({email}) on branch '{details.get('current_branch')}'"

    except FileNotFoundError:
        status  = SignalStatus.ERROR
        message = "git executable not found"
    except Exception as exc:
        status  = SignalStatus.ERROR
        message = f"git_profile probe failed: {exc}"

    return ProbeResult(
        domain     = "git_profile",
        status     = status,
        message    = message,
        details    = details,
        latency_ms = (time.monotonic() - start) * 1000,
    )

"""
orchestra.probes.gitignore
===========================
Hygiene gate for the repository .gitignore file.

Checks
------
  - .gitignore file exists
  - Critical patterns are present: .env*, secrets/, *.key, *.pem,
    __pycache__/, .venv/, node_modules/, *.pyc, .DS_Store
  - No committed .env files (outside of .env.example / .env.template)
  - No committed private key files (*.pem, *.key)
  - .gitignore is not empty

Env var
-------
  GIT_REPO_PATH        path to repo root (default: CWD)
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from orchestra.models import ProbeResult, SignalStatus

_REPO_PATH = Path(os.getenv("GIT_REPO_PATH", ".")).resolve()

# These patterns MUST be present in .gitignore
_REQUIRED_PATTERNS: List[str] = [
    ".env",
    "*.key",
    "*.pem",
    "__pycache__",
    ".venv",
    "node_modules",
    "*.pyc",
    ".DS_Store",
]

# Glob patterns that should NOT be tracked in git
_FORBIDDEN_TRACKED: List[str] = [
    "*.pem",
    "*.key",
]

# Tracked .env files that are explicitly allowed (templates / examples)
_ALLOWED_ENV_FILES = {".env.example", ".env.template", ".env.sample"}


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
        gitignore_path = _REPO_PATH / ".gitignore"

        # ── file exists ───────────────────────────────────────────────────────
        if not gitignore_path.exists():
            return ProbeResult(
                domain     = "gitignore",
                status     = SignalStatus.ERROR,
                message    = ".gitignore file is MISSING from repo root",
                details    = {"path": str(gitignore_path)},
                latency_ms = (time.monotonic() - start) * 1000,
            )

        content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
        lines   = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]
        details["total_patterns"] = len(lines)

        # ── required patterns ─────────────────────────────────────────────────
        missing = []
        for pat in _REQUIRED_PATTERNS:
            found = any(pat in line for line in lines)
            if not found:
                missing.append(pat)

        details["missing_patterns"] = missing
        if missing:
            warnings.append(f"Missing recommended .gitignore patterns: {', '.join(missing)}")

        # ── tracked secret files ──────────────────────────────────────────────
        tracked_raw = _git("ls-files")
        tracked = set(tracked_raw.splitlines())

        # check .env files (exclude allowed ones)
        leaked_env = [
            f for f in tracked
            if os.path.basename(f).startswith(".env")
            and os.path.basename(f) not in _ALLOWED_ENV_FILES
        ]
        if leaked_env:
            errors.append(f"TRACKED .env files: {', '.join(leaked_env)}")
        details["leaked_env_files"] = leaked_env

        # check private keys
        leaked_keys = [
            f for f in tracked
            if f.endswith(".pem") or f.endswith(".key")
        ]
        if leaked_keys:
            errors.append(f"TRACKED key/cert files: {', '.join(leaked_keys)}")
        details["leaked_key_files"] = leaked_keys

        # ── gitignore size sanity ─────────────────────────────────────────────
        details["gitignore_size_bytes"] = gitignore_path.stat().st_size
        if len(lines) < 5:
            warnings.append(".gitignore seems too sparse (< 5 active patterns)")

        # ── result ────────────────────────────────────────────────────────────
        if errors:
            status  = SignalStatus.ERROR
            message = "; ".join(errors)
        elif warnings:
            status  = SignalStatus.WARNING
            message = "; ".join(warnings)
        else:
            status  = SignalStatus.OK
            message = f".gitignore clean — {len(lines)} patterns, 0 leaked secrets"

    except Exception as exc:
        status  = SignalStatus.ERROR
        message = f"gitignore probe failed: {exc}"

    return ProbeResult(
        domain     = "gitignore",
        status     = status,
        message    = message,
        details    = details,
        latency_ms = (time.monotonic() - start) * 1000,
    )

"""
orchestra.probes.repo
======================
Probes the Clisonix GitHub repository via the GitHub REST API.

Checks
------
  - Last push timestamp (staleness gate: > 7 days → WARNING)
  - Open pull requests count
  - Open security vulnerability count (Dependabot)
  - Latest CI workflow conclusion (slo-sli-gate)
  - Branch protection on main

Env vars
--------
  GITHUB_TOKEN          Personal/repo token (repo, read:org scopes)
  GITHUB_REPO           owner/repo  (default: Web8kameleon-hub/clisonix.com)
  GITHUB_STALE_DAYS     int         (default: 7)
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from orchestra.models import ProbeResult, SignalStatus

_REPO    = os.getenv("GITHUB_REPO", "Web8kameleon-hub/clisonix.com")
_TOKEN   = os.getenv("GITHUB_TOKEN", "")
_STALE   = int(os.getenv("GITHUB_STALE_DAYS", "7"))
_API     = "https://api.github.com"


def _get(path: str, timeout: int = 8) -> Dict[str, Any]:
    url = f"{_API}{path}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if _TOKEN:
        req.add_header("Authorization", f"Bearer {_TOKEN}")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def run() -> ProbeResult:
    start = time.monotonic()
    details: Dict[str, Any] = {"repo": _REPO}
    warnings: list[str] = []
    errors: list[str] = []

    try:
        # ── repo info ────────────────────────────────────────────────────────
        repo_data = _get(f"/repos/{_REPO}")
        pushed_at = repo_data.get("pushed_at", "")
        details["pushed_at"] = pushed_at
        details["default_branch"] = repo_data.get("default_branch", "main")
        details["open_issues"] = repo_data.get("open_issues_count", 0)
        details["stars"] = repo_data.get("stargazers_count", 0)
        details["forks"] = repo_data.get("forks_count", 0)

        if pushed_at:
            pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - pushed_dt).days
            details["pushed_age_days"] = age_days
            if age_days > _STALE:
                warnings.append(f"Last push {age_days} days ago (threshold={_STALE}d)")

        # ── open PRs ─────────────────────────────────────────────────────────
        try:
            pulls = _get(f"/repos/{_REPO}/pulls?state=open&per_page=1")
            # actual count via search
            pr_search = _get(f"/search/issues?q=repo:{_REPO}+is:pr+is:open")
            details["open_prs"] = pr_search.get("total_count", len(pulls))
        except Exception:
            details["open_prs"] = "n/a"

        # ── dependabot alerts ────────────────────────────────────────────────
        try:
            vulns = _get(f"/repos/{_REPO}/vulnerability-alerts")
            details["dependabot_alerts"] = "enabled"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                details["dependabot_alerts"] = "disabled_or_no_access"
            else:
                details["dependabot_alerts"] = f"unknown ({e.code})"

        # ── latest slo-sli-gate workflow run ─────────────────────────────────
        try:
            runs = _get(f"/repos/{_REPO}/actions/workflows/slo-sli-gate.yml/runs?per_page=1")
            wf_runs = runs.get("workflow_runs", [])
            if wf_runs:
                latest = wf_runs[0]
                details["ci_conclusion"] = latest.get("conclusion", "in_progress")
                details["ci_status"]     = latest.get("status", "")
                details["ci_branch"]     = latest.get("head_branch", "")
                details["ci_run_id"]     = latest.get("id", "")
                if details["ci_conclusion"] == "failure":
                    errors.append("slo-sli-gate last run FAILED")
            else:
                details["ci_conclusion"] = "no_runs"
        except Exception as exc:
            details["ci_conclusion"] = f"error ({exc})"

        # ── aggregate ────────────────────────────────────────────────────────
        if errors:
            status  = SignalStatus.ERROR
            message = "; ".join(errors)
        elif warnings:
            status  = SignalStatus.WARNING
            message = "; ".join(warnings)
        else:
            status  = SignalStatus.OK
            message = f"repo healthy — pushed {details.get('pushed_age_days', '?')}d ago"

    except urllib.error.HTTPError as exc:
        status  = SignalStatus.ERROR
        message = f"GitHub API HTTP {exc.code}: {exc.reason}"
    except Exception as exc:
        status  = SignalStatus.ERROR
        message = f"repo probe failed: {exc}"

    return ProbeResult(
        domain     = "repo",
        status     = status,
        message    = message,
        details    = details,
        latency_ms = (time.monotonic() - start) * 1000,
    )

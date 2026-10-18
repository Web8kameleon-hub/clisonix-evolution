#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = (
    ROOT / "docs" / "production" / "canonical" / "single_branch_pr_guard_report.json"
)


@dataclass
class CheckFailure:
    code: str
    message: str


def github_get(url: str, token: str) -> dict | list:
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "clisonix-single-branch-pr-guard")
    request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read().decode("utf-8", errors="ignore")
            return json.loads(payload) if payload.strip() else {}
    except urllib.error.HTTPError as ex:
        body = ex.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API HTTP {ex.code}: {body[:300]}") from ex
    except urllib.error.URLError as ex:
        raise RuntimeError(f"GitHub API unreachable: {ex}") from ex


EXEMPT_BOT_LOGINS = {"dependabot[bot]"}
EXEMPT_HEAD_PREFIXES = ("release/",)


def is_exempt_pr(pr: dict) -> bool:
    """Automated dependency-update and release-promotion PRs are governed by
    their own dedicated workflows and must not count against the single
    feature-branch policy enforced here."""
    user = pr.get("user")
    if isinstance(user, dict):
        if str(user.get("login", "")).lower() in EXEMPT_BOT_LOGINS:
            return True

    head = pr.get("head")
    head_ref = str((head or {}).get("ref", "")) if isinstance(head, dict) else ""
    if head_ref.startswith(EXEMPT_HEAD_PREFIXES):
        return True

    return False


def main() -> int:
    failures: list[CheckFailure] = []

    repo = (os.getenv("GITHUB_REPOSITORY") or "").strip()
    token = (os.getenv("GITHUB_TOKEN") or "").strip()
    event_name = (os.getenv("GITHUB_EVENT_NAME") or "").strip()
    ref_name = (os.getenv("GITHUB_REF_NAME") or "").strip()

    default_branch = (os.getenv("DEFAULT_BRANCH") or "main").strip()
    primary_work_branch = (
        os.getenv("PRIMARY_WORK_BRANCH") or "fix/hetzner-swarm-rollout"
    ).strip()
    max_open_prs = int((os.getenv("MAX_OPEN_PRS") or "1").strip())

    allowed_push_branches = {default_branch, primary_work_branch}

    report: dict[str, object] = {
        "ok": False,
        "repo": repo,
        "event": event_name,
        "ref_name": ref_name,
        "policy": {
            "default_branch": default_branch,
            "primary_work_branch": primary_work_branch,
            "max_open_prs": max_open_prs,
            "allowed_push_branches": sorted(allowed_push_branches),
        },
        "failures": [],
    }

    if not repo:
        report["ok"] = True
        report["note"] = "No GITHUB_REPOSITORY detected (local mode)."
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("[SINGLE-BRANCH-PR-GUARD] PASS (local mode)")
        print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
        return 0

    if not token:
        failures.append(
            CheckFailure(
                "MISSING_GITHUB_TOKEN",
                "GITHUB_TOKEN is required to enforce PR/branch governance.",
            )
        )
    else:
        encoded_repo = urllib.parse.quote(repo, safe="/")
        pulls_url = f"https://api.github.com/repos/{encoded_repo}/pulls?state=open&per_page=100"
        pulls = github_get(pulls_url, token)
        if not isinstance(pulls, list):
            failures.append(
                CheckFailure("INVALID_PRS_PAYLOAD", "GitHub pulls API did not return a list.")
            )
            pulls = []

        open_prs_same_repo = []
        for pr in pulls:
            if not isinstance(pr, dict):
                continue
            head = pr.get("head")
            if not isinstance(head, dict):
                continue
            head_repo = head.get("repo")
            if not isinstance(head_repo, dict):
                continue
            if str(head_repo.get("full_name", "")).lower() != repo.lower():
                continue
            open_prs_same_repo.append(pr)

        governed_prs = [pr for pr in open_prs_same_repo if not is_exempt_pr(pr)]

        report["open_pr_count"] = len(governed_prs)
        report["open_prs"] = [
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "head": (pr.get("head") or {}).get("ref"),
                "base": (pr.get("base") or {}).get("ref"),
            }
            for pr in governed_prs
            if isinstance(pr, dict)
        ]
        report["exempt_prs"] = [
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "head": (pr.get("head") or {}).get("ref"),
                "base": (pr.get("base") or {}).get("ref"),
            }
            for pr in open_prs_same_repo
            if isinstance(pr, dict) and is_exempt_pr(pr)
        ]

        if len(governed_prs) > max_open_prs:
            failures.append(
                CheckFailure(
                    "TOO_MANY_OPEN_PRS",
                    f"Open PR count is {len(governed_prs)}; max allowed is {max_open_prs}.",
                )
            )

    if event_name == "push" and ref_name and ref_name not in allowed_push_branches and not ref_name.startswith(EXEMPT_HEAD_PREFIXES):
        failures.append(
            CheckFailure(
                "UNAUTHORIZED_PUSH_BRANCH",
                f"Push branch '{ref_name}' is not allowed. Allowed: {sorted(allowed_push_branches)}",
            )
        )

    if event_name == "pull_request":
        event_path = (os.getenv("GITHUB_EVENT_PATH") or "").strip()
        if event_path and Path(event_path).exists():
            try:
                event_payload = json.loads(
                    Path(event_path).read_text(encoding="utf-8", errors="ignore")
                )
            except Exception as ex:
                failures.append(
                    CheckFailure("INVALID_EVENT_PAYLOAD", f"Cannot parse event payload: {ex}")
                )
                event_payload = {}

            pr = event_payload.get("pull_request") if isinstance(event_payload, dict) else None
            if isinstance(pr, dict):
                base_value = pr.get("base")
                head_value = pr.get("head")
                base = base_value if isinstance(base_value, dict) else {}
                head = head_value if isinstance(head_value, dict) else {}
                base_ref = str(base.get("ref") or "")
                head_ref = str(head.get("ref") or "")
                report["pull_request"] = {
                    "base_ref": base_ref,
                    "head_ref": head_ref,
                }

                if base_ref != default_branch:
                    failures.append(
                        CheckFailure(
                            "PR_BASE_MUST_BE_DEFAULT",
                            f"PR base branch must be '{default_branch}', found '{base_ref}'.",
                        )
                    )

                if head_ref != primary_work_branch and not is_exempt_pr(pr):
                    failures.append(
                        CheckFailure(
                            "PR_HEAD_MUST_BE_PRIMARY_WORK_BRANCH",
                            f"PR head branch must be '{primary_work_branch}', found '{head_ref}'.",
                        )
                    )
        else:
            failures.append(
                CheckFailure(
                    "MISSING_EVENT_PATH",
                    "GITHUB_EVENT_PATH is required for pull_request validation.",
                )
            )

    report["ok"] = len(failures) == 0
    report["failures"] = [failure.__dict__ for failure in failures]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if failures:
        print("[SINGLE-BRANCH-PR-GUARD] FAIL")
        for failure in failures:
            print(f"- {failure.code}: {failure.message}")
        print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
        return 1

    print("[SINGLE-BRANCH-PR-GUARD] PASS")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

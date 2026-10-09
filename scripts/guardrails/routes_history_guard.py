#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Conservative minimums for current branch history.
# Avoid false negatives caused by environment-specific ref availability.
MIN_EXPECTED_TOTAL_ROUTES = 460
MIN_EXPECTED_NEXTJS_ROUTES = 220
MIN_EXPECTED_PYTHON_ROUTE_FILES = 230

IGNORED_SEGMENTS = (
    "/node_modules/",
    "/.next/",
    "/archive/",
    "/.venv/",
)


@dataclass
class CheckFailure:
    code: str
    message: str


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def should_keep(path: str) -> bool:
    p = f"/{path.lstrip('/')}"
    for segment in IGNORED_SEGMENTS:
        if segment in p:
            return False
    return True


def collect_nextjs_routes() -> list[str]:
    output = run_git(
        [
            "log",
            "--name-only",
            "--pretty=format:",
            "--",
            "**/route.ts",
            "**/route.tsx",
            "**/route.js",
            "**/route.jsx",
        ]
    )
    rows = [normalize(line) for line in output.splitlines() if line.strip()]
    rows = [r for r in rows if should_keep(r)]
    return sorted(set(rows))


def collect_python_route_files() -> list[str]:
    regexes = [
        r"app\.get\(",
        r"app\.post\(",
        r"app\.put\(",
        r"app\.delete\(",
        r"app\.patch\(",
        r"app\.options\(",
        r"app\.head\(",
        r"router\.get\(",
        r"router\.post\(",
        r"router\.put\(",
        r"router\.delete\(",
        r"router\.patch\(",
        r"router\.options\(",
        r"router\.head\(",
    ]

    rows: list[str] = []
    for regex in regexes:
        output = run_git(["log", "-G", regex, "--name-only", "--pretty=format:", "--", "*.py"])
        rows.extend(normalize(line) for line in output.splitlines() if line.strip())

    rows = [r for r in rows if should_keep(r)]
    return sorted(set(rows))


def main() -> int:
    failures: list[CheckFailure] = []

    try:
        nextjs_routes = collect_nextjs_routes()
        python_route_files = collect_python_route_files()
    except Exception as ex:
        failures.append(CheckFailure("GIT_HISTORY_SCAN_FAILED", str(ex)))
        nextjs_routes = []
        python_route_files = []

    combined = sorted(set(nextjs_routes) | set(python_route_files))

    if len(nextjs_routes) < MIN_EXPECTED_NEXTJS_ROUTES:
        failures.append(
            CheckFailure(
                "NEXTJS_ROUTE_HISTORY_TOO_SMALL",
                f"Expected at least {MIN_EXPECTED_NEXTJS_ROUTES} Next.js route files, found {len(nextjs_routes)}",
            )
        )

    if len(python_route_files) < MIN_EXPECTED_PYTHON_ROUTE_FILES:
        failures.append(
            CheckFailure(
                "PYTHON_ROUTE_HISTORY_TOO_SMALL",
                f"Expected at least {MIN_EXPECTED_PYTHON_ROUTE_FILES} Python route files, found {len(python_route_files)}",
            )
        )

    if len(combined) < MIN_EXPECTED_TOTAL_ROUTES:
        failures.append(
            CheckFailure(
                "ROUTE_HISTORY_TOO_SMALL",
                f"Expected at least {MIN_EXPECTED_TOTAL_ROUTES} combined route files, found {len(combined)}",
            )
        )

    report = {
        "ok": len(failures) == 0,
        "minimums": {
            "nextjs": MIN_EXPECTED_NEXTJS_ROUTES,
            "python": MIN_EXPECTED_PYTHON_ROUTE_FILES,
            "combined": MIN_EXPECTED_TOTAL_ROUTES,
        },
        "counts": {
            "nextjs": len(nextjs_routes),
            "python": len(python_route_files),
            "combined": len(combined),
        },
        "failures": [f.__dict__ for f in failures],
        "samples": {
            "nextjs_first_50": nextjs_routes[:50],
            "python_first_50": python_route_files[:50],
            "combined_first_50": combined[:50],
        },
    }

    out = ROOT / "docs" / "production" / "canonical" / "routes_history_guard_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if failures:
        print("[ROUTES-HISTORY-GUARD] FAIL")
        for failure in failures:
            print(f"- {failure.code}: {failure.message}")
        print(f"Report: {out.relative_to(ROOT)}")
        return 1

    print("[ROUTES-HISTORY-GUARD] PASS")
    print(
        f"Counts => nextjs={len(nextjs_routes)}, python={len(python_route_files)}, combined={len(combined)}"
    )
    print(f"Report: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

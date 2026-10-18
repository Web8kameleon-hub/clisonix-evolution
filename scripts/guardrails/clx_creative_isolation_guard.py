#!/usr/bin/env python3
"""Guardrail to keep clx.creative isolated from NO_FAKE_DATA critical runtime paths."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CRITICAL_FILES = [
    "apps/api/main.py",
    "apps/api/master.py",
    "alba_service_5555.py",
    "albi_service_6680.py",
    "jona_neural_api.py",
    "ocean-core/ocean_core_full.py",
    "services/blerina/main.py",
    "apps/web/app/api/_lib/upstream.ts",
]

FORBIDDEN_IMPORTS = [
    re.compile(r"\\bfrom\\s+clx\\.creative\\b"),
    re.compile(r"\\bimport\\s+clx\\.creative\\b"),
    re.compile(r"\\bfrom\\s+sdk\\.python\\.clx\\.creative\\b"),
    re.compile(r"\\bimport\\s+sdk\\.python\\.clx\\.creative\\b"),
]


def _scan_file(path: Path) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        issues.append(f"Missing critical file: {path.as_posix()}")
        return issues

    text = path.read_text(encoding="utf-8", errors="ignore")
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        for pattern in FORBIDDEN_IMPORTS:
            if pattern.search(line):
                issues.append(
                    f"{path.as_posix()}:{idx} imports clx.creative into critical runtime"
                )
    return issues


def main() -> int:
    all_issues: list[str] = []
    for rel in CRITICAL_FILES:
        all_issues.extend(_scan_file(REPO_ROOT / rel))

    if all_issues:
        print("[CLX-CREATIVE-ISOLATION] FAIL")
        for issue in all_issues:
            print(f" - {issue}")
        return 1

    print("[CLX-CREATIVE-ISOLATION] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

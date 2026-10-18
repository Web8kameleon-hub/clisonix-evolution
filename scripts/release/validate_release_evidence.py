#!/usr/bin/env python3
"""Fail CI when a code release lacks its required evidence document."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

REQUIRED = ("Issue", "Documentation", "Tests", "Edge cases", "Benchmark", "Rollback")


def output(*args: str) -> list[str]:
    value = subprocess.check_output(["git", *args], text=True)
    return [line.strip() for line in value.splitlines() if line.strip()]


def main() -> None:
    head_ref = os.getenv("GITHUB_HEAD_REF", "")
    if head_ref and not head_ref.startswith("release/"):
        raise SystemExit(f"Changes targeting main must use a release/* branch, got {head_ref!r}")

    before = os.getenv("BEFORE_SHA", "")
    base = os.getenv("BASE_SHA", "")
    if before and set(before) != {"0"}:
        diff_base = before
    elif base:
        diff_base = base
    else:
        diff_base = "HEAD^"

    changed = output("diff", "--name-only", f"{diff_base}...HEAD")
    code_changed = any(not path.startswith("docs/") for path in changed)
    if not code_changed:
        print("Documentation-only change; release evidence gate satisfied.")
        return

    release_notes = [Path(path) for path in changed if path.startswith("docs/releases/") and path.endswith(".md")]
    if not release_notes:
        raise SystemExit("Code changes require a changed docs/releases/*.md evidence file")
    for note in release_notes:
        content = note.read_text(encoding="utf-8")
        missing = [heading for heading in REQUIRED if f"## {heading}" not in content]
        if missing:
            raise SystemExit(f"{note} is missing sections: {', '.join(missing)}")
    print(f"Release evidence validated: {', '.join(map(str, release_notes))}")


if __name__ == "__main__":
    main()

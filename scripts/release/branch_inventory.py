#!/usr/bin/env python3
"""Read-only inventory of remote branches relative to origin/main."""

from __future__ import annotations

import subprocess


def git(*args: str) -> list[str]:
    output = subprocess.check_output(["git", *args], text=True)
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> None:
    git("fetch", "--all", "--prune")
    branches = [
        branch
        for branch in git("for-each-ref", "--format=%(refname:short)", "refs/remotes")
        if branch not in {"origin/HEAD", "origin/main"} and not branch.endswith("/HEAD")
    ]
    merged = set(git("branch", "-r", "--merged", "origin/main"))
    print("MERGED (review before deletion)")
    for branch in sorted(set(branches) & merged):
        print(f"  {branch}")
    print("\nUNMERGED (preserve until reconciled)")
    for branch in sorted(set(branches) - merged):
        print(f"  {branch}")


if __name__ == "__main__":
    main()

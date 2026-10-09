#!/usr/bin/env python3
"""Validate ALB runtime env values against canonical record.

Checks:
- SOLANA_ALB_MINT
- SOLANA_ALB_AUTHORITY
- UTT_AUTHORITY
- NEXT_PUBLIC_UTT_AUTHORITY

Exit code:
- 0: all checks passed
- 1: one or more checks failed
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

CANONICAL_FILE = Path("ALB_CANONICAL_RECORD.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ALB runtime configuration")
    parser.add_argument(
        "--env-file",
        default=None,
        help="Optional path to .env file to load before validation",
    )
    return parser.parse_args()


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")

    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def parse_canonical_values(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Canonical file not found: {path}")

    content = path.read_text(encoding="utf-8")

    mint_match = re.search(r"^- Canonical mint:\s*(\S+)\s*$", content, flags=re.MULTILINE)
    authority_match = re.search(r"^- Authority:\s*(\S+)\s*$", content, flags=re.MULTILINE)

    if not mint_match:
        raise ValueError("Could not parse canonical mint from ALB_CANONICAL_RECORD.md")
    if not authority_match:
        raise ValueError("Could not parse authority from ALB_CANONICAL_RECORD.md")

    return {
        "mint": mint_match.group(1),
        "authority": authority_match.group(1),
    }


def check(name: str, actual: str | None, expected: str) -> tuple[bool, str]:
    if not actual:
        return False, f"{name}: missing (expected {expected})"
    if actual != expected:
        return False, f"{name}: mismatch (actual {actual}, expected {expected})"
    return True, f"{name}: ok"


def main() -> int:
    args = parse_args()

    if args.env_file:
        load_env_file(Path(args.env_file))

    canonical = parse_canonical_values(CANONICAL_FILE)

    checks = [
        check("SOLANA_ALB_MINT", os.getenv("SOLANA_ALB_MINT"), canonical["mint"]),
        check("SOLANA_ALB_AUTHORITY", os.getenv("SOLANA_ALB_AUTHORITY"), canonical["authority"]),
        check("UTT_AUTHORITY", os.getenv("UTT_AUTHORITY"), canonical["authority"]),
        check(
            "NEXT_PUBLIC_UTT_AUTHORITY",
            os.getenv("NEXT_PUBLIC_UTT_AUTHORITY"),
            canonical["authority"],
        ),
    ]

    has_error = False
    for ok, message in checks:
        prefix = "PASS" if ok else "FAIL"
        print(f"[{prefix}] {message}")
        if not ok:
            has_error = True

    if has_error:
        print("\nValidation failed. Runtime config is not aligned with ALB canonical record.")
        return 1

    print("\nValidation passed. Runtime config is aligned with ALB canonical record.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1)

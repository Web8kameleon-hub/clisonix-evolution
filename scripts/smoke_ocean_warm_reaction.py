#!/usr/bin/env python3
"""Smoke tests for Ocean warm and reaction proxy endpoints.

Usage:
  python scripts/smoke_ocean_warm_reaction.py --base http://localhost:3000
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def post_json(url: str, payload: dict) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        try:
            return err.code, json.loads(body)
        except json.JSONDecodeError:
            return err.code, body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:3000", help="Base web URL")
    args = parser.parse_args()

    base = args.base.rstrip("/")
    warm_url = f"{base}/api/ocean/stream/warm"
    reaction_url = f"{base}/api/ocean/message/reaction"

    tests = [
        (
            "warm_proxy",
            warm_url,
            {"message": "kjo eshte nje mesazh testimi per warm proxy debounce"},
            {"status"},
        ),
        (
            "reaction_proxy",
            reaction_url,
            {"message_id": "smoke-msg-001", "emoji": "ok", "user_id": "smoke-test"},
            {"status"},
        ),
    ]

    failed = 0
    for name, url, payload, required_keys in tests:
        status, body = post_json(url, payload)
        print(f"[{name}] status={status} body={body}")

        if not (200 <= status < 300):
            failed += 1
            print(f"[FAIL] {name}: non-2xx status")
            continue

        if isinstance(body, dict):
            missing = [key for key in required_keys if key not in body]
            if missing:
                failed += 1
                print(f"[FAIL] {name}: missing keys {missing}")
        else:
            failed += 1
            print(f"[FAIL] {name}: response is not JSON object")

    if failed:
        print(f"Smoke tests failed: {failed}")
        return 1

    print("Smoke tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.request


def fetch_json(url: str, timeout: float):
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Clisonix City Labs 23/23 live smoke test")
    parser.add_argument("--registry", default="http://127.0.0.1:9130", help="City Labs registry base URL")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--require-analysis", action="store_true", help="Also require analysis_upstream_configured for every lab")
    args = parser.parse_args()

    try:
        snapshot = fetch_json(f"{args.registry.rstrip('/')}/api/v1/snapshot", args.timeout)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"FAIL registry unavailable: {exc}")
        return 2

    labs = snapshot.get("laboratories", [])
    print(f"City Labs: total={snapshot.get('total')} healthy={snapshot.get('healthy')} degraded={snapshot.get('degraded')} unavailable={snapshot.get('unavailable')}")

    failures = []
    if snapshot.get("total") != 23 or len(labs) != 23:
        failures.append(f"expected 23 labs, got total={snapshot.get('total')} list={len(labs)}")

    for lab in labs:
        lab_id = lab.get("lab_id", "unknown")
        status = lab.get("status")
        latency = lab.get("latency_ms")
        print(f"{lab_id:28} {status:12} {str(latency):>8} ms")
        if status != "healthy":
            failures.append(f"{lab_id}: status={status}")

        if args.require_analysis:
            try:
                detail = fetch_json(f"{args.registry.rstrip('/')}/api/v1/labs/{lab_id}?live=true", args.timeout)
                configured = bool((detail.get("manifest") or {}).get("runtime", {}).get("analysis_upstream_configured"))
            except Exception as exc:  # smoke script should report all failures
                configured = False
                failures.append(f"{lab_id}: manifest probe failed: {exc}")
            if not configured:
                failures.append(f"{lab_id}: analysis upstream not configured")

    if failures:
        print("\nFAIL")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("\nPASS 23/23 City Labs healthy" + (" and analysis-capable" if args.require_analysis else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

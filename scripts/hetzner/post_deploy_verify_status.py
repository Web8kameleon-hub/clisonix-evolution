#!/usr/bin/env python3
"""Verify fresh HTTP observations against actual Redis records and aggregates.

Run inside the API container, where REDIS_URL is configured. No backfill or
status fallback is permitted. Two uncached observations must reach storage.
"""
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from urllib.request import urlopen

NAMES = {"api", "web", "core", "excel", "marketplace", "balancer"}
PREFIX = "clisonix:system:health"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fresh(value):
    timestamp = datetime.fromisoformat(value)
    require(timestamp.tzinfo is not None, "Observation has no timezone")
    age = (datetime.now(timezone.utc) - timestamp).total_seconds()
    require(-5 <= age <= 120, "Observation is stale or from the future")


def verify_snapshot(snapshot, client):
    fresh(snapshot["timestamp"])
    rows = snapshot["services"]
    require(len(rows) == len(NAMES) and {row["name"] for row in rows} == NAMES, "Service registry differs from the six monitored services")
    require(snapshot["status"] == "operational", "System is not Operational")
    for row in rows:
        latency = row.get("latency_ms")
        require(row["healthy"] is True, f"{row['name']} probe is unhealthy")
        require(isinstance(latency, (int, float)) and not isinstance(latency, bool) and math.isfinite(latency) and latency >= 0,
                f"{row['name']} latency is not a measured number")
        fresh(row["observed_at"])
    telemetry = snapshot["telemetry"]
    require(telemetry["status"] == "recorded", "Telemetry storage is unavailable")
    require(telemetry["last_sample_at"] == snapshot["timestamp"], "Telemetry timestamp differs from the probes")
    history = telemetry["uptime_history"]
    require(bool(history), "No received uptime history")
    observed_month = datetime.fromisoformat(snapshot["timestamp"]).strftime("%Y-%m")
    require(any(month["month"] == observed_month and month["last_sample_at"] >= snapshot["timestamp"] for month in history),
            "History does not include this observation")
    records = client.xrevrange(PREFIX + ":samples", count=100)
    matching = [record for _, record in records if record["observed_at"] == snapshot["timestamp"]]
    require(bool(matching), "HTTP observation is absent from Redis raw storage")
    require(any(json.loads(record["services"]) == rows for record in matching), "Redis probes differ from HTTP observations")
    for month in history:
        stored = client.hgetall(PREFIX + ":month:" + month["month"])
        total = int(stored["samples"])
        require(0 < month["samples"] <= total, "Monthly count is not supported by stored observations")
        # Another worker may add observations between HTTP and verification.
        if total == month["samples"]:
            require(month["uptime"] == round(100 * int(stored["operational"]) / total, 2), "History availability differs from storage")
            for name in NAMES:
                service = month["services"][name]
                require(service["samples"] == int(stored[name + ":samples"]), "Service count differs from storage")
                require(service["uptime"] == round(100 * int(stored[name + ":operational"]) / service["samples"], 2), "Service history differs from storage")
    return snapshot["timestamp"]


def main():
    from redis import Redis
    redis_url = os.environ.get("REDIS_URL")
    require(bool(redis_url), "REDIS_URL is required to verify actual persistence")
    url = os.environ.get("STATUS_VERIFY_URL", "http://127.0.0.1:8000/api/system/health")
    client = Redis.from_url(redis_url, decode_responses=True, socket_timeout=5, socket_connect_timeout=5)
    previous = None
    try:
        for index in range(2):
            if index:
                time.sleep(11)  # Actual cache expiry; never manufacture timestamps.
            with urlopen(url, timeout=20) as response:
                snapshot = json.load(response)
            observed = verify_snapshot(snapshot, client)
            require(observed != previous, "Second poll did not produce a new persisted observation")
            previous = observed
            balancer = next(row for row in snapshot["services"] if row["name"] == "balancer")
            print(json.dumps({"observed_at": observed, "balancer_latency_ms": balancer["latency_ms"],
                              "services_operational": len(snapshot["services"]), "storage": "verified_redis",
                              "history_months": len(snapshot["telemetry"]["uptime_history"])}))
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Never expose connection URLs, passwords, or response bodies.
        detail = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(f"POST_DEPLOY_STATUS_FAILED: {detail}", file=sys.stderr)
        raise SystemExit(1)

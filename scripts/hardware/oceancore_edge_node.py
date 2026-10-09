#!/usr/bin/env python3
"""Local OceanCore edge-node runner for the Kloud bridge hardware contract.

This script keeps the hardware direction practical and testable:
- loads a node profile
- registers the node with `kloud-bridge`
- emits one-shot or repeated heartbeat updates
- optionally publishes a real proof-of-life signal through the bridge

Example:
    python scripts/hardware/oceancore_edge_node.py \
        --bridge http://127.0.0.1:8889 \
        --profile scripts/hardware/profiles/oceancore_lab_01.json \
        --count 3 --interval 5
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import error, request

DEFAULT_PROFILE = Path(__file__).resolve().parent / "profiles" / "oceancore_lab_01.json"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _post_json(base_url: str, endpoint: str, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["x-node-token"] = token
    req = request.Request(
        f"{base_url.rstrip('/')}{endpoint}",
        data=data,
        headers=headers,
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(base_url: str, endpoint: str, token: Optional[str] = None) -> Dict[str, Any]:
    headers = {"x-node-token": token} if token else {}
    req = request.Request(f"{base_url.rstrip('/')}{endpoint}", headers=headers, method="GET")
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _build_heartbeat(profile: Dict[str, Any], sequence: int, forward_to_ocean: bool) -> Dict[str, Any]:
    base_temp = float(profile.get("telemetry_defaults", {}).get("temperature_c", 41.0))
    base_power = float(profile.get("telemetry_defaults", {}).get("power_watts", 6.0))
    base_latency = float(profile.get("telemetry_defaults", {}).get("latency_ms", 8.0))

    return {
        "node_id": profile["node_id"],
        "status": "online",
        "uptime_seconds": sequence * 15,
        "temperature_c": round(base_temp + random.uniform(-0.4, 0.6), 2),
        "power_watts": round(base_power + random.uniform(-0.2, 0.3), 2),
        "latency_ms": round(base_latency + random.uniform(-1.0, 1.0), 2),
        "telemetry": {
            "mode": "edge-active",
            "queue_depth": sequence % 4,
            "lab_id": profile.get("metadata", {}).get("lab_id", "lab-unknown"),
            "deployment_target": profile.get("metadata", {}).get("deployment_target", "prototype"),
        },
        "forward_to_ocean": forward_to_ocean,
    }


def _build_signal(profile: Dict[str, Any], sequence: int, heartbeat: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ops": ["S"],
        "source": profile["node_id"],
        "payload": {
            "signal_type": "hardware.proof-of-life",
            "node_id": profile["node_id"],
            "sequence": sequence,
            "lab_id": profile.get("metadata", {}).get("lab_id", "lab-unknown"),
            "deployment_target": profile.get("metadata", {}).get("deployment_target", "prototype"),
            "metrics": {
                "temperature_c": heartbeat["temperature_c"],
                "power_watts": heartbeat["power_watts"],
                "latency_ms": heartbeat["latency_ms"],
            },
            "timestamp": int(time.time()),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="OceanCore local edge-node heartbeat runner")
    parser.add_argument("--bridge", default="http://127.0.0.1:8889", help="Kloud bridge base URL")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Path to JSON node profile")
    parser.add_argument("--count", type=int, default=1, help="Number of heartbeats to send")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between heartbeats")
    parser.add_argument("--forward-to-ocean", action="store_true", help="Forward heartbeats to Ocean Core routing")
    parser.add_argument("--emit-signal", action="store_true", help="Publish one real proof-of-life signal through the bridge")
    parser.add_argument("--forever", action="store_true", help="Keep sending heartbeats until interrupted")
    parser.add_argument("--node-token", default="", help="Optional node token for protected bridge endpoints")
    parser.add_argument("--register-only", action="store_true", help="Register the node and stop")
    args = parser.parse_args()

    profile_path = Path(args.profile).resolve()
    if not profile_path.exists():
        print(f"Profile not found: {profile_path}", file=sys.stderr)
        return 1

    profile = _load_json(profile_path)

    try:
        contract = _get_json(args.bridge, "/api/v1/hardware/contracts/firmware-v0.1", args.node_token or None)
        print("== Firmware Contract ==")
        print(json.dumps(contract, indent=2))

        registration = {
            "node_id": profile["node_id"],
            "node_class": profile.get("node_class", "oceancore-edge"),
            "architecture": profile.get("architecture", "riscv"),
            "runtime": profile.get("runtime", "rust"),
            "transport": profile.get("transport", "http"),
            "firmware_version": profile.get("firmware_version", "0.1.0"),
            "capabilities": profile.get("capabilities", ["heartbeat", "telemetry"]),
            "metadata": profile.get("metadata", {}),
        }

        result = _post_json(args.bridge, "/api/v1/hardware/nodes/register", registration, args.node_token or None)
        print("== Registration ==")
        print(json.dumps(result, indent=2))

        if args.register_only:
            return 0

        sequence = 1
        while True:
            heartbeat = _build_heartbeat(profile, sequence, args.forward_to_ocean)
            result = _post_json(args.bridge, "/api/v1/hardware/nodes/heartbeat", heartbeat, args.node_token or None)
            print(f"== Heartbeat {sequence}{'' if args.forever else f'/{args.count}'} ==")
            print(json.dumps(result, indent=2))

            if args.emit_signal and sequence == 1:
                signal = _build_signal(profile, sequence, heartbeat)
                signal_result = _post_json(args.bridge, "/api/v1/signals/publish", signal, args.node_token or None)
                print("== Proof-of-Life Signal ==")
                print(json.dumps(signal_result, indent=2))

            if not args.forever and sequence >= args.count:
                break

            sequence += 1
            time.sleep(args.interval)

        return 0
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error {exc.code}: {body}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - emergency CLI reporting
        print(f"Runner failed: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from typing import Any, Dict, Tuple


REQUIRED_TOP_LEVEL = {
    "event_id",
    "event_type",
    "timestamp",
    "trace",
    "delivery",
    "payload_version",
    "payload_schema",
    "payload",
    "metadata",
}


def validate_clx_event(payload: Dict[str, Any]) -> Tuple[bool, str]:
    missing = [key for key in REQUIRED_TOP_LEVEL if key not in payload]
    if missing:
        return False, f"missing fields: {', '.join(sorted(missing))}"

    trace = payload.get("trace")
    if not isinstance(trace, dict):
        return False, "trace must be object"
    for key in ("trace_id", "span_id", "correlation_id"):
        if not trace.get(key):
            return False, f"trace.{key} is required"

    delivery = payload.get("delivery")
    if not isinstance(delivery, dict):
        return False, "delivery must be object"
    for key in ("retry_count", "max_retries", "ttl_ms", "delivery_mode"):
        if key not in delivery:
            return False, f"delivery.{key} is required"

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return False, "metadata must be object"
    for key in ("source_service", "target_service", "priority", "auth_context"):
        if key not in metadata:
            return False, f"metadata.{key} is required"

    return True, "ok"

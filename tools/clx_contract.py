#!/usr/bin/env python3
"""Clisonix contract checker.

Read-only validator for service contracts, endpoint drift, and telemetry schema.
This tool never mutates project files and never deploys.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = ROOT / "contracts" / "clisonix-contract.json"
DEFAULT_SCHEMA_PATH = ROOT / "contracts" / "clisonix-contract.schema.json"
AGENT_TELEMETRY_PATH = ROOT / "agent_telemetry.py"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _check_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)


def _join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def _http_get(url: str, timeout_s: float) -> Dict[str, Any]:
    req = urllib.request.Request(url=url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return {
                "ok": True,
                "status_code": int(resp.getcode()),
                "url": url,
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status_code": int(exc.code),
            "url": url,
            "error": f"http_error:{exc.code}",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "status_code": None,
            "url": url,
            "error": str(exc),
        }


def _make_check(
    service: str,
    check: str,
    status: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "service": service,
        "check": check,
        "status": status,
    }
    payload.update(kwargs)
    return payload


def _validate_with_jsonschema(schema: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import jsonschema
        from jsonschema import Draft202012Validator
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "blocked",
            "error": "jsonschema package is not installed",
            "detail": str(exc),
        }

    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(contract), key=lambda item: list(item.path))
        if errors:
            return {
                "status": "failed",
                "errors": [
                    {
                        "message": err.message,
                        "path": "/" + "/".join(str(p) for p in err.path),
                    }
                    for err in errors
                ],
            }
        return {"status": "passed"}
    except jsonschema.SchemaError as exc:
        return {
            "status": "failed",
            "error": "schema_definition_invalid",
            "detail": str(exc),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "failed",
            "error": "schema_validation_error",
            "detail": str(exc),
        }


def _extract_telemetry_defaults(path: Path) -> Dict[str, Optional[int]]:
    result: Dict[str, Optional[int]] = {
        "alba_port": None,
        "albi_port": None,
        "jona_port": None,
        "asi_port": None,
    }
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    def read_defaults(node: ast.FunctionDef) -> Dict[str, Optional[int]]:
        values: Dict[str, Optional[int]] = {}
        arg_names = [arg.arg for arg in node.args.args]
        defaults = node.args.defaults
        first_default_idx = len(arg_names) - len(defaults)
        for idx, default_expr in enumerate(defaults):
            arg_name = arg_names[first_default_idx + idx]
            if arg_name in values or arg_name not in result:
                continue
            if isinstance(default_expr, ast.Constant) and isinstance(default_expr.value, int):
                values[arg_name] = default_expr.value
        return values

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "TelemetryRouter":
            for class_item in node.body:
                if isinstance(class_item, ast.FunctionDef) and class_item.name == "__init__":
                    result.update(read_defaults(class_item))
        if isinstance(node, ast.FunctionDef) and node.name == "init_telemetry":
            defaults = read_defaults(node)
            for key, val in defaults.items():
                if result.get(key) is None:
                    result[key] = val
    return result


def _collect_contract_routes(contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    routes: List[Dict[str, Any]] = []
    services = contract.get("services", {})
    endpoint_keys = ["telemetry_ingest", "analytics", "coordination", "execute"]
    for service_name, cfg in services.items():
        if not isinstance(cfg, dict):
            continue
        base_url = str(cfg.get("base_url", ""))
        if cfg.get("health"):
            routes.append(
                {
                    "service": service_name,
                    "name": "health",
                    "method": "GET",
                    "path": str(cfg.get("health")),
                    "url": _join_url(base_url, str(cfg.get("health"))),
                }
            )
        if cfg.get("status"):
            routes.append(
                {
                    "service": service_name,
                    "name": "status",
                    "method": "GET",
                    "path": str(cfg.get("status")),
                    "url": _join_url(base_url, str(cfg.get("status"))),
                }
            )
        for endpoint_key in endpoint_keys:
            endpoint = cfg.get(endpoint_key)
            if not isinstance(endpoint, dict):
                continue
            path = str(endpoint.get("path", ""))
            method = str(endpoint.get("method", "POST")).upper()
            routes.append(
                {
                    "service": service_name,
                    "name": endpoint_key,
                    "method": method,
                    "path": path,
                    "url": _join_url(base_url, path),
                }
            )
    return routes


def _load_openapi_paths(contract: Dict[str, Any]) -> Dict[str, List[str]]:
    paths: Dict[str, List[str]] = {}
    for item in contract.get("openapi_sources", []):
        rel_path = str(item)
        source_path = ROOT / rel_path
        if not source_path.exists():
            continue

        if source_path.suffix.lower() == ".json":
            try:
                payload = _load_json(source_path)
                for route_path in payload.get("paths", {}).keys():
                    paths.setdefault(route_path, []).append(rel_path)
            except Exception:
                continue

        if source_path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except Exception:
                continue
            try:
                with source_path.open("r", encoding="utf-8") as handle:
                    payload = yaml.safe_load(handle)
                for route_path in (payload or {}).get("paths", {}).keys():
                    paths.setdefault(route_path, []).append(rel_path)
            except Exception:
                continue
    return paths


def run_check(contract_path: Path, schema_path: Path, timeout_s: float) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    if not contract_path.exists():
        return {
            "contract_version": "unknown",
            "status": "blocked",
            "checks": [
                _make_check(
                    "contract",
                    "file_exists",
                    "failed",
                    expected=str(contract_path),
                    error="contract file missing",
                )
            ],
            "blocking_failures": 1,
        }

    if not schema_path.exists():
        return {
            "contract_version": "unknown",
            "status": "blocked",
            "checks": [
                _make_check(
                    "contract",
                    "schema_exists",
                    "failed",
                    expected=str(schema_path),
                    error="schema file missing",
                )
            ],
            "blocking_failures": 1,
        }

    contract = _load_json(contract_path)
    schema = _load_json(schema_path)
    contract_version = str(contract.get("contract_version", "unknown"))

    schema_check = _validate_with_jsonschema(schema, contract)
    if schema_check["status"] == "passed":
        checks.append(_make_check("contract", "json_schema", "passed", draft="2020-12"))
    elif schema_check["status"] == "blocked":
        checks.append(
            _make_check(
                "contract",
                "json_schema",
                "failed",
                error=schema_check.get("error"),
                detail=schema_check.get("detail"),
            )
        )
    else:
        checks.append(
            _make_check(
                "contract",
                "json_schema",
                "failed",
                error=schema_check.get("error", "validation_failed"),
                details=schema_check.get("errors", []),
            )
        )

    required_services = {"alba", "albi", "jona", "asi"}
    services = contract.get("services", {})
    for required in sorted(required_services):
        if required in services:
            checks.append(_make_check(required, "service_declared", "passed"))
        else:
            checks.append(_make_check(required, "service_declared", "failed", error="missing_service"))

    for service_name, cfg in services.items():
        if not isinstance(cfg, dict):
            checks.append(_make_check(service_name, "service_shape", "failed", error="service config must be object"))
            continue
        base_url = str(cfg.get("base_url", ""))
        if _check_url(base_url):
            checks.append(_make_check(service_name, "base_url", "passed", url=base_url))
        else:
            checks.append(_make_check(service_name, "base_url", "failed", configured=base_url, error="invalid_url"))
            continue

        for simple_route in ["health", "status"]:
            path_value = cfg.get(simple_route)
            if not path_value:
                continue
            url = _join_url(base_url, str(path_value))
            response = _http_get(url, timeout_s=timeout_s)
            if response["ok"] and 200 <= int(response["status_code"]) < 400:
                checks.append(_make_check(service_name, simple_route, "passed", url=url, status_code=response["status_code"]))
            else:
                checks.append(
                    _make_check(
                        service_name,
                        simple_route,
                        "failed",
                        url=url,
                        status_code=response.get("status_code"),
                        error=response.get("error", "unreachable"),
                    )
                )

    # Payload contract checks for event envelope + telemetry schema
    event_required = contract.get("event_envelope", {}).get("required", [])
    if isinstance(event_required, list) and all(isinstance(item, str) for item in event_required):
        checks.append(_make_check("event_envelope", "required_fields", "passed", fields=event_required))
    else:
        checks.append(_make_check("event_envelope", "required_fields", "failed", error="invalid_required_fields"))

    statuses = contract.get("event_envelope", {}).get("status_values", [])
    if isinstance(statuses, list) and all(isinstance(item, str) for item in statuses):
        checks.append(_make_check("event_envelope", "status_values", "passed", values=statuses))
    else:
        checks.append(_make_check("event_envelope", "status_values", "failed", error="invalid_status_values"))

    telemetry_required = contract.get("telemetry_schema", {}).get("required", [])
    expected_telemetry_required = ["agent_name", "timestamp", "status", "success"]
    if isinstance(telemetry_required, list) and all(field in telemetry_required for field in expected_telemetry_required):
        checks.append(
            _make_check(
                "agent_telemetry",
                "telemetry_required_fields",
                "passed",
                required=telemetry_required,
            )
        )
    else:
        checks.append(
            _make_check(
                "agent_telemetry",
                "telemetry_required_fields",
                "failed",
                expected=expected_telemetry_required,
                configured=telemetry_required,
            )
        )

    # Drift: compare contract ports vs agent_telemetry defaults.
    defaults = _extract_telemetry_defaults(AGENT_TELEMETRY_PATH)
    service_port_key = {
        "alba": "alba_port",
        "albi": "albi_port",
        "jona": "jona_port",
        "asi": "asi_port",
    }
    for service, port_key in service_port_key.items():
        service_cfg = services.get(service, {})
        base_url = str(service_cfg.get("base_url", "")) if isinstance(service_cfg, dict) else ""
        parsed = urllib.parse.urlparse(base_url)
        expected_port = parsed.port
        configured_port = defaults.get(port_key)
        if expected_port is None or configured_port is None:
            checks.append(
                _make_check(
                    "agent_telemetry",
                    f"{port_key}",
                    "failed",
                    expected=expected_port,
                    configured=configured_port,
                    error="missing_port_data",
                )
            )
            continue

        if expected_port == configured_port:
            checks.append(
                _make_check(
                    "agent_telemetry",
                    f"{port_key}",
                    "passed",
                    expected=expected_port,
                    configured=configured_port,
                )
            )
        else:
            checks.append(
                _make_check(
                    "agent_telemetry",
                    f"{port_key}",
                    "failed",
                    expected=expected_port,
                    configured=configured_port,
                    error="endpoint drift",
                )
            )

    # OpenAPI route drift checks
    openapi_paths = _load_openapi_paths(contract)
    for route in _collect_contract_routes(contract):
        if route["path"] in openapi_paths:
            checks.append(
                _make_check(
                    route["service"],
                    f"openapi:{route['name']}",
                    "passed",
                    path=route["path"],
                    sources=openapi_paths[route["path"]],
                )
            )
        else:
            checks.append(
                _make_check(
                    route["service"],
                    f"openapi:{route['name']}",
                    "failed",
                    path=route["path"],
                    error="route missing in configured openapi sources",
                )
            )

    failed = [item for item in checks if item.get("status") == "failed"]

    status = "passed"
    if failed:
        status = "failed"
    if any(item.get("check") == "json_schema" and item.get("error") == "jsonschema package is not installed" for item in failed):
        status = "blocked"

    return {
        "contract_version": contract_version,
        "status": status,
        "checks": checks,
        "blocking_failures": len(failed),
    }


def run_routes(contract_path: Path) -> Dict[str, Any]:
    contract = _load_json(contract_path)
    routes = _collect_contract_routes(contract)
    return {
        "contract_version": contract.get("contract_version", "unknown"),
        "count": len(routes),
        "routes": routes,
    }


def run_drift(contract_path: Path) -> Dict[str, Any]:
    contract = _load_json(contract_path)
    services = contract.get("services", {})
    defaults = _extract_telemetry_defaults(AGENT_TELEMETRY_PATH)

    checks: List[Dict[str, Any]] = []
    for service, key in {
        "alba": "alba_port",
        "albi": "albi_port",
        "jona": "jona_port",
        "asi": "asi_port",
    }.items():
        base_url = str(services.get(service, {}).get("base_url", ""))
        expected = urllib.parse.urlparse(base_url).port
        configured = defaults.get(key)
        state = "passed" if expected == configured and expected is not None else "failed"
        check = _make_check("agent_telemetry", key, state, expected=expected, configured=configured)
        if state == "failed":
            check["error"] = "endpoint drift"
        checks.append(check)

    return {
        "contract_version": contract.get("contract_version", "unknown"),
        "status": "passed" if all(item["status"] == "passed" for item in checks) else "failed",
        "checks": checks,
        "blocking_failures": sum(1 for item in checks if item["status"] == "failed"),
    }


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Clisonix contract checker")
    parser.add_argument(
        "command",
        choices=["check", "report", "routes", "drift"],
        help="Operation mode",
    )
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Path to contract JSON file",
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Path to contract schema JSON file",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.5,
        help="HTTP timeout in seconds for health/status checks",
    )

    args = parser.parse_args(argv)
    contract_path = Path(args.contract)
    schema_path = Path(args.schema)

    if args.command in {"check", "report"}:
        payload = run_check(contract_path=contract_path, schema_path=schema_path, timeout_s=args.timeout)
        _print_json(payload)
        return 0 if payload.get("status") == "passed" else 1

    if args.command == "routes":
        payload = run_routes(contract_path=contract_path)
        _print_json(payload)
        return 0

    if args.command == "drift":
        payload = run_drift(contract_path=contract_path)
        _print_json(payload)
        return 0 if payload.get("status") == "passed" else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

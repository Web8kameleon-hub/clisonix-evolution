from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SERVICE_DIR = ROOT / "services" / "curiosity_ocean"
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

from capability_registry import (
    get_ocean_capability_registry,  # type: ignore  # noqa: E402
)
from execution_gate import evaluate_execution  # type: ignore  # noqa: E402
from manifest_validator import validate_claims  # type: ignore  # noqa: E402


def _manifest(module_id: str = "nanogrid-zeiss") -> dict:
    registry = get_ocean_capability_registry()
    manifest = registry.get(module_id)
    assert manifest is not None
    return manifest.to_dict()


def test_manifest_validator_rejects_unsupported_capability_claim() -> None:
    manifest = _manifest()
    response = {
        "language": "en",
        "declared_capabilities": ["inspect_status", "prepare_workflow", "execute_workflow"],
        "execution_status": "not_executed",
        "correlation_id": "req_123",
    }

    result = validate_claims(manifest=manifest, response=response, expected_language="en")
    assert result["valid"] is False
    assert any(err["error"] == "unsupported_capability_claim" for err in result["errors"])


def test_manifest_validator_rejects_execution_without_job_id() -> None:
    manifest = _manifest()
    response = {
        "language": "en",
        "declared_capabilities": ["inspect_status"],
        "execution_status": "executed",
        "correlation_id": "req_123",
    }

    result = validate_claims(manifest=manifest, response=response, expected_language="en")
    assert result["valid"] is False
    assert any(err["error"] == "missing_job_id" for err in result["errors"])


def test_manifest_validator_rejects_language_mismatch_and_missing_correlation_id() -> None:
    manifest = _manifest()
    response = {
        "language": "de",
        "declared_capabilities": ["inspect_status"],
        "execution_status": "not_executed",
    }

    result = validate_claims(manifest=manifest, response=response, expected_language="en")
    assert result["valid"] is False
    assert any(err["error"] == "language_mismatch" for err in result["errors"])
    assert any(err["error"] == "missing_correlation_id" for err in result["errors"])


def test_execution_gate_blocks_when_live_execution_not_supported() -> None:
    manifest = _manifest("nanogrid-zeiss")
    decision = evaluate_execution(
        manifest=manifest,
        action="prepare_workflow",
        runtime_state="online",
        provided_requirements={"zeiss_connector", "authenticated_operator"},
        authenticated_operator="operator_1",
    )

    assert decision["decision"] == "blocked"
    assert decision["execution_status"] == "blocked"
    assert "supports_live_execution=false" in decision["reasons"]


def test_execution_gate_requires_approval_for_destructive_actions() -> None:
    manifest = {
        "module_id": "live-module",
        "declared_capabilities": ["execute_workflow"],
        "supports_live_execution": True,
        "requires": ["authenticated_operator"],
        "runtime_state": "online",
    }

    decision = evaluate_execution(
        manifest=manifest,
        action="execute_workflow",
        runtime_state="online",
        provided_requirements={"authenticated_operator"},
        authenticated_operator="operator_1",
        approval_granted=False,
    )

    assert decision["decision"] == "requires_approval"
    assert decision["execution_status"] == "not_executed"


def test_execution_gate_allows_started_execution_with_job_id() -> None:
    manifest = {
        "module_id": "live-module",
        "declared_capabilities": ["prepare_workflow"],
        "supports_live_execution": True,
        "requires": ["zeiss_connector", "authenticated_operator"],
        "runtime_state": "online",
    }

    decision = evaluate_execution(
        manifest=manifest,
        action="prepare_workflow",
        runtime_state="online",
        provided_requirements={"zeiss_connector", "authenticated_operator"},
        authenticated_operator="operator_1",
        approval_granted=True,
    )

    assert decision["decision"] == "allowed"
    assert decision["execution_status"] == "started"
    assert str(decision.get("job_id", "")).startswith("job_")


def test_manifest_validator_rejects_simulation_reported_as_executed() -> None:
    manifest = _manifest()
    response = {
        "language": "en",
        "declared_capabilities": ["inspect_status"],
        "simulation_supported": True,
        "execution_status": "executed",
        "job_id": "job_123",
        "correlation_id": "req_123",
    }

    result = validate_claims(manifest=manifest, response=response, expected_language="en")
    assert result["valid"] is False
    assert any(err["error"] == "simulation_marked_as_execution" for err in result["errors"])


@pytest.mark.parametrize(
    "payload",
    [
        {"declared_capabilities": ["inspect_status"]},
        {"declared_capabilities": ["inspect_status"], "live_execution_supported": False},
    ],
)
def test_manifest_validator_accepts_valid_payload(payload: dict) -> None:
    manifest = _manifest()
    response = {
        "language": "en",
        "execution_status": "not_executed",
        "correlation_id": "req_ok",
        **payload,
    }

    result = validate_claims(manifest=manifest, response=response, expected_language="en")
    assert result["valid"] is True
    assert result["errors"] == []

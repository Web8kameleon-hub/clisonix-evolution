from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class ManifestValidationResult:
    valid: bool
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        if self.valid:
            return {"valid": True, "errors": []}
        return {"valid": False, "errors": self.errors}


class ManifestValidator:
    """Validates model claims against capability manifest and execution semantics."""

    def validate_claims(
        self,
        manifest: Dict[str, Any],
        response: Dict[str, Any],
        expected_language: Optional[str] = None,
        require_correlation_id: bool = True,
    ) -> ManifestValidationResult:
        errors: List[Dict[str, Any]] = []

        declared: Set[str] = set(manifest.get("declared_capabilities", []))
        mentioned: Set[str] = set(response.get("declared_capabilities", []))
        unsupported = sorted(mentioned - declared)
        if unsupported:
            errors.append(
                {
                    "error": "unsupported_capability_claim",
                    "items": unsupported,
                }
            )

        if response.get("live_execution_supported") and not manifest.get("supports_live_execution", False):
            errors.append(
                {
                    "error": "live_execution_conflict",
                    "message": "live_execution_supported cannot be true for this module",
                }
            )

        execution_status = str(response.get("execution_status") or "not_executed")
        if execution_status in {"started", "executed", "completed"}:
            job_id = str(response.get("job_id") or "").strip()
            if not job_id:
                errors.append(
                    {
                        "error": "missing_job_id",
                        "message": "job_id is required when execution status is started/executed/completed",
                    }
                )

        if response.get("simulation_supported") and execution_status in {"executed", "completed"}:
            errors.append(
                {
                    "error": "simulation_marked_as_execution",
                    "message": "simulation cannot be reported as executed/completed",
                }
            )

        connector_claim = str(response.get("active_connector") or "").strip()
        if connector_claim:
            known_connector = str(manifest.get("active_connector") or "").strip()
            required = set(manifest.get("requires", []))
            connector_allowed = bool(known_connector and connector_claim == known_connector)
            connector_required = connector_claim in required
            if not connector_allowed and not connector_required:
                errors.append(
                    {
                        "error": "connector_claim_not_declared",
                        "connector": connector_claim,
                    }
                )

        requirements_mentioned = set(response.get("missing_requirements", []))
        known_requirements = set(manifest.get("requires", []))
        unknown_requirements = sorted(requirements_mentioned - known_requirements)
        if unknown_requirements:
            errors.append(
                {
                    "error": "unknown_requirements",
                    "items": unknown_requirements,
                }
            )

        if expected_language is not None:
            actual_language = str(response.get("language") or "").strip().lower()
            if actual_language != expected_language.lower():
                errors.append(
                    {
                        "error": "language_mismatch",
                        "expected": expected_language.lower(),
                        "actual": actual_language,
                    }
                )

        if require_correlation_id:
            correlation_id = str(response.get("correlation_id") or "").strip()
            if not correlation_id:
                errors.append(
                    {
                        "error": "missing_correlation_id",
                        "message": "correlation_id is required",
                    }
                )

        return ManifestValidationResult(valid=not errors, errors=errors)


def validate_claims(
    manifest: Dict[str, Any],
    response: Dict[str, Any],
    expected_language: Optional[str] = None,
    require_correlation_id: bool = True,
) -> Dict[str, Any]:
    validator = ManifestValidator()
    result = validator.validate_claims(
        manifest=manifest,
        response=response,
        expected_language=expected_language,
        require_correlation_id=require_correlation_id,
    )
    return result.to_dict()

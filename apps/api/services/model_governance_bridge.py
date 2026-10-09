"""
Model Governance Bridge
=======================

Thin bridge so `apps/api` can adopt the shared root governance policy without
duplicating lifecycle rules.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.services.model_governance_store import (  # noqa: E402
    add_governance_approval,
    append_governance_event,
    create_governance_audit_log,
    persist_approval,
    persist_registration,
    persist_stage_transition,
    upsert_governance_record,
)
from model_governance import (  # noqa: E402
    ApprovalRecord,
    ApprovalStage,
    DeploymentTarget,
    GovernanceDecision,
    GovernanceEnforcementResult,
    GovernanceEvidence,
    GovernanceRiskLevel,
    ReviewerRequirement,
    ReviewerRole,
    classify_governance_risk,
    decision_from_model_snapshot,
    default_governance_decision,
    evaluate_stage_gate,
    governance_summary,
    minimum_evidence_required,
    required_reviewers,
    requires_sensitive_controls,
    validate_transition,
)

__all__ = [
    "ApprovalStage",
    "ApprovalRecord",
    "DeploymentTarget",
    "GovernanceDecision",
    "GovernanceEnforcementResult",
    "GovernanceEvidence",
    "GovernanceRiskLevel",
    "ReviewerRequirement",
    "ReviewerRole",
    "classify_governance_risk",
    "decision_from_model_snapshot",
    "default_governance_decision",
    "evaluate_stage_gate",
    "governance_summary",
    "minimum_evidence_required",
    "required_reviewers",
    "requires_sensitive_controls",
    "validate_transition",
    "add_governance_approval",
    "append_governance_event",
    "create_governance_audit_log",
    "persist_approval",
    "persist_registration",
    "persist_stage_transition",
    "upsert_governance_record",
]

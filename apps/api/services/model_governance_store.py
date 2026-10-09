"""
Model Governance Persistence Store
=================================

Database-side skeleton for governance records, approvals, and audit events.
This does not replace the file-based registry yet; it mirrors critical state so
the workflow can become audit-ready in the next phase.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from apps.api.database.models import (
    AuditLog,
    GovernanceApprovalDecision,
    ModelGovernanceApproval,
    ModelGovernanceEvent,
    ModelGovernanceRecord,
)

logger = logging.getLogger(__name__)


def _normalize_snapshot(model_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "model_id": model_snapshot.get("model_id"),
        "model_version": model_snapshot.get("version"),
        "risk_level": model_snapshot.get("ai_risk_assessment", "low"),
        "approval_stage": model_snapshot.get("approval_stage", "draft"),
        "deployment_target": model_snapshot.get("deployment_target", "development"),
        "intended_use": model_snapshot.get("intended_use", "general"),
        "domain_tags": model_snapshot.get("domain_tags") or [],
        "requires_specialized_reviewer": bool(model_snapshot.get("requires_specialized_reviewer", False)),
        "requires_licensed_approver": bool(model_snapshot.get("requires_licensed_approver", False)),
        "evidence_bundle": model_snapshot.get("governance_evidence") or {},
        "registry_snapshot": model_snapshot,
    }


def upsert_governance_record(session: Session, model_snapshot: Dict[str, Any]) -> ModelGovernanceRecord:
    """Create or update the DB mirror for a model governance record."""
    payload = _normalize_snapshot(model_snapshot)
    record = (
        session.query(ModelGovernanceRecord)
        .filter(
            ModelGovernanceRecord.model_id == payload["model_id"],
            ModelGovernanceRecord.model_version == payload["model_version"],
        )
        .one_or_none()
    )

    if record is None:
        record = ModelGovernanceRecord(**payload)
        session.add(record)
    else:
        for key, value in payload.items():
            setattr(record, key, value)

    session.flush()
    return record


def create_governance_audit_log(
    session: Session,
    *,
    action: str,
    entity_id: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Write a generic audit log entry tied to governance actions."""
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type="model_governance",
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        old_values=old_values,
        new_values=new_values,
        success=success,
        error_message=error_message,
    )
    session.add(audit_entry)
    session.flush()
    return audit_entry


def append_governance_event(
    session: Session,
    *,
    record: ModelGovernanceRecord,
    action: str,
    from_stage: Optional[str] = None,
    to_stage: Optional[str] = None,
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None,
    audit_log: Optional[AuditLog] = None,
) -> ModelGovernanceEvent:
    event = ModelGovernanceEvent(
        record_id=record.id,
        audit_log_id=audit_log.id if audit_log else None,
        action=action,
        actor_id=actor_id,
        actor_role=actor_role,
        from_stage=from_stage,
        to_stage=to_stage,
        success=success,
        details=details or {},
    )
    session.add(event)
    session.flush()
    return event


def add_governance_approval(
    session: Session,
    *,
    record: ModelGovernanceRecord,
    reviewer_id: str,
    reviewer_role: str,
    decision: str,
    reviewer_name: Optional[str] = None,
    reviewer_license_id: Optional[str] = None,
    reviewer_user_id: Optional[str] = None,
    notes: str = "",
    evidence_refs: Optional[Dict[str, Any]] = None,
) -> ModelGovernanceApproval:
    approval = ModelGovernanceApproval(
        record_id=record.id,
        reviewer_user_id=reviewer_user_id,
        reviewer_id=reviewer_id,
        reviewer_role=reviewer_role,
        reviewer_name=reviewer_name,
        reviewer_license_id=reviewer_license_id,
        decision=GovernanceApprovalDecision(decision),
        notes=notes,
        evidence_refs=evidence_refs or {},
    )
    session.add(approval)
    session.flush()
    return approval


def persist_registration(
    session: Session,
    *,
    model_snapshot: Dict[str, Any],
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist model registration into governance mirror + audit trail."""
    record = upsert_governance_record(session, model_snapshot)
    audit_entry = create_governance_audit_log(
        session,
        action="model_governance.register",
        entity_id=f"{record.model_id}:{record.model_version}",
        new_values=record.registry_snapshot,
        request_id=request_id,
    )
    event = append_governance_event(
        session,
        record=record,
        action="registered",
        to_stage=record.approval_stage,
        actor_id=actor_id,
        actor_role=actor_role,
        audit_log=audit_entry,
        details={
            "risk_level": record.risk_level,
            "deployment_target": record.deployment_target,
        },
    )
    logger.info("Governance registration persisted for %s@%s", record.model_id, record.model_version)
    return {
        "record_id": str(record.id),
        "audit_log_id": str(audit_entry.id),
        "event_id": str(event.id),
    }


def persist_approval(
    session: Session,
    *,
    model_snapshot: Dict[str, Any],
    approval_payload: Dict[str, Any],
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    record = upsert_governance_record(session, model_snapshot)
    approval = add_governance_approval(
        session,
        record=record,
        reviewer_id=approval_payload["reviewer_id"],
        reviewer_role=approval_payload["reviewer_role"],
        decision="approved" if approval_payload.get("approved", False) else "rejected",
        reviewer_name=approval_payload.get("reviewer_name"),
        reviewer_license_id=approval_payload.get("reviewer_license_id"),
        reviewer_user_id=approval_payload.get("reviewer_user_id"),
        notes=approval_payload.get("notes", ""),
        evidence_refs=approval_payload.get("evidence_refs") or {},
    )
    audit_entry = create_governance_audit_log(
        session,
        action="model_governance.approval",
        entity_id=f"{record.model_id}:{record.model_version}",
        new_values=approval_payload,
        request_id=request_id,
    )
    event = append_governance_event(
        session,
        record=record,
        action="approval_recorded",
        actor_id=approval_payload.get("reviewer_id"),
        actor_role=approval_payload.get("reviewer_role"),
        audit_log=audit_entry,
        details={
            "approval_id": str(approval.id),
            "approved": approval_payload.get("approved", False),
            "reviewer_verified": approval_payload.get("reviewer_verified", False),
            "verification_reasons": approval_payload.get("verification_reasons") or [],
        },
    )
    return {
        "record_id": str(record.id),
        "approval_id": str(approval.id),
        "audit_log_id": str(audit_entry.id),
        "event_id": str(event.id),
    }


def persist_stage_transition(
    session: Session,
    *,
    model_snapshot: Dict[str, Any],
    from_stage: str,
    to_stage: str,
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    record = upsert_governance_record(session, model_snapshot)
    audit_entry = create_governance_audit_log(
        session,
        action="model_governance.transition",
        entity_id=f"{record.model_id}:{record.model_version}",
        new_values={"from": from_stage, "to": to_stage, "details": details or {}},
        request_id=request_id,
    )
    event = append_governance_event(
        session,
        record=record,
        action="stage_transition",
        from_stage=from_stage,
        to_stage=to_stage,
        actor_id=actor_id,
        actor_role=actor_role,
        audit_log=audit_entry,
        details=details or {},
    )
    return {
        "record_id": str(record.id),
        "audit_log_id": str(audit_entry.id),
        "event_id": str(event.id),
    }


def persist_evidence_update(
    session: Session,
    *,
    model_snapshot: Dict[str, Any],
    previous_evidence: Dict[str, Any],
    updated_evidence: Dict[str, Any],
    actor_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist evidence bundle changes into DB mirror and audit trail."""
    record = upsert_governance_record(session, model_snapshot)
    audit_entry = create_governance_audit_log(
        session,
        action="model_governance.evidence_update",
        entity_id=f"{record.model_id}:{record.model_version}",
        old_values=previous_evidence,
        new_values=updated_evidence,
        request_id=request_id,
    )
    event = append_governance_event(
        session,
        record=record,
        action="evidence_updated",
        actor_id=actor_id,
        actor_role=actor_role,
        audit_log=audit_entry,
        details={
            "updated_keys": sorted(updated_evidence.keys()),
            "evidence_completeness": record.evidence_bundle,
        },
    )
    return {
        "record_id": str(record.id),
        "audit_log_id": str(audit_entry.id),
        "event_id": str(event.id),
    }

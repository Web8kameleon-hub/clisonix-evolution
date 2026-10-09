"""
Model Governance Policy Skeleton
================================

Enterprise-oriented governance primitives for model lifecycle control.

Goals:
- Add risk-based approval requirements
- Enforce human approval for production promotions
- Require specialized and licensed reviewers for sensitive workloads
- Keep implementation lightweight so existing registry code can adopt it incrementally
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class GovernanceRiskLevel(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStage(str, Enum):
    DRAFT = "draft"
    RISK_REVIEW = "risk_review"
    COMPLIANCE_REVIEW = "compliance_review"
    APPROVED = "approved"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


class DeploymentTarget(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ReviewerRole(str, Enum):
    MODEL_OWNER = "model_owner"
    RISK_OWNER = "risk_owner"
    COMPLIANCE_OWNER = "compliance_owner"
    SPECIALIZED_REVIEWER = "specialized_reviewer"
    LICENSED_APPROVER = "licensed_approver"


@dataclass
class ReviewerRequirement:
    role: ReviewerRole
    required: bool = True
    reason: str = ""


@dataclass
class GovernanceEvidence:
    explainability_report: Optional[str] = None
    bias_assessment_report: Optional[str] = None
    validation_report: Optional[str] = None
    adversarial_test_report: Optional[str] = None
    approval_notes: List[str] = field(default_factory=list)
    attached_artifacts: List[str] = field(default_factory=list)

    def completeness(self) -> float:
        checks = [
            self.explainability_report,
            self.bias_assessment_report,
            self.validation_report,
            self.adversarial_test_report,
        ]
        present = sum(1 for item in checks if item)
        return present / len(checks)


@dataclass
class ApprovalRecord:
    reviewer_id: str
    reviewer_role: ReviewerRole
    approved: bool
    reviewer_user_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    reviewer_license_id: Optional[str] = None
    reviewer_verified: bool = False
    verification_reasons: List[str] = field(default_factory=list)
    notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class GovernanceDecision:
    risk_level: GovernanceRiskLevel
    current_stage: ApprovalStage = ApprovalStage.DRAFT
    deployment_target: DeploymentTarget = DeploymentTarget.DEVELOPMENT
    intended_use: str = "general"
    domain_tags: List[str] = field(default_factory=list)
    requires_specialized_reviewer: bool = False
    requires_licensed_approver: bool = False
    approvals: List[ApprovalRecord] = field(default_factory=list)
    evidence: GovernanceEvidence = field(default_factory=GovernanceEvidence)


@dataclass
class GovernanceEnforcementResult:
    allowed: bool
    next_stage: ApprovalStage
    missing_roles: List[str] = field(default_factory=list)
    missing_license_roles: List[str] = field(default_factory=list)
    evidence_completeness: float = 0.0
    minimum_evidence_required: float = 0.0
    reasons: List[str] = field(default_factory=list)


SENSITIVE_DOMAIN_TAGS = {
    "health",
    "healthtech",
    "telehealth",
    "medical",
    "clinical",
    "biosignal",
    "eeg",
    "patient-facing",
}


STAGE_ORDER = {
    ApprovalStage.DRAFT: 0,
    ApprovalStage.RISK_REVIEW: 1,
    ApprovalStage.COMPLIANCE_REVIEW: 2,
    ApprovalStage.APPROVED: 3,
    ApprovalStage.PRODUCTION: 4,
    ApprovalStage.DEPRECATED: 5,
}


def normalize_domain_tags(tags: Optional[List[str]]) -> List[str]:
    return sorted({tag.strip().lower() for tag in (tags or []) if tag and tag.strip()})


def requires_sensitive_controls(domain_tags: Optional[List[str]], intended_use: str = "") -> bool:
    normalized = set(normalize_domain_tags(domain_tags))
    if normalized.intersection(SENSITIVE_DOMAIN_TAGS):
        return True
    return any(token in intended_use.lower() for token in ["health", "clinical", "patient", "biosignal", "eeg"])


def classify_governance_risk(
    *,
    model_type: str,
    trained_on_samples: int,
    accuracy: float,
    high_stakes: bool = False,
    domain_tags: Optional[List[str]] = None,
    intended_use: str = "",
) -> GovernanceRiskLevel:
    sensitive = requires_sensitive_controls(domain_tags, intended_use)
    if high_stakes or sensitive:
        if accuracy < 0.90 or trained_on_samples < 5000:
            return GovernanceRiskLevel.HIGH
        return GovernanceRiskLevel.MEDIUM

    if accuracy < 0.80:
        return GovernanceRiskLevel.MEDIUM
    if trained_on_samples < 1000:
        return GovernanceRiskLevel.LOW
    if model_type.lower() in {"llm", "neural_network", "time_series"}:
        return GovernanceRiskLevel.LOW
    return GovernanceRiskLevel.MINIMAL


def required_reviewers(decision: GovernanceDecision, next_stage: ApprovalStage) -> List[ReviewerRequirement]:
    requirements: List[ReviewerRequirement] = []

    if next_stage == ApprovalStage.RISK_REVIEW:
        requirements.append(ReviewerRequirement(ReviewerRole.RISK_OWNER, reason="Risk triage required"))

    if next_stage == ApprovalStage.COMPLIANCE_REVIEW:
        requirements.append(ReviewerRequirement(ReviewerRole.COMPLIANCE_OWNER, reason="Compliance review required"))
        if decision.requires_specialized_reviewer:
            requirements.append(
                ReviewerRequirement(
                    ReviewerRole.SPECIALIZED_REVIEWER,
                    reason="Sensitive domain requires subject-matter review",
                )
            )
        if decision.requires_licensed_approver:
            requirements.append(
                ReviewerRequirement(
                    ReviewerRole.LICENSED_APPROVER,
                    reason="Sensitive production path requires licensed approver",
                )
            )

    if next_stage == ApprovalStage.PRODUCTION:
        requirements.append(ReviewerRequirement(ReviewerRole.RISK_OWNER, reason="Production promotion requires risk sign-off"))
        requirements.append(ReviewerRequirement(ReviewerRole.COMPLIANCE_OWNER, reason="Production promotion requires compliance sign-off"))
        if decision.requires_specialized_reviewer:
            requirements.append(
                ReviewerRequirement(
                    ReviewerRole.SPECIALIZED_REVIEWER,
                    reason="Production-sensitive deployment requires specialist confirmation",
                )
            )
        if decision.requires_licensed_approver:
            requirements.append(
                ReviewerRequirement(
                    ReviewerRole.LICENSED_APPROVER,
                    reason="Production-sensitive deployment requires licensed approval",
                )
            )

    return requirements


def validate_transition(current_stage: ApprovalStage, next_stage: ApprovalStage) -> Tuple[bool, str]:
    if next_stage == current_stage:
        return True, "No-op transition"
    if next_stage == ApprovalStage.DEPRECATED:
        return True, "Deprecation allowed from any stage"
    if STAGE_ORDER[next_stage] != STAGE_ORDER[current_stage] + 1:
        return False, f"Invalid stage transition: {current_stage.value} -> {next_stage.value}"
    return True, "Transition allowed"


def default_governance_decision(
    *,
    risk_level: GovernanceRiskLevel,
    deployment_target: DeploymentTarget,
    intended_use: str,
    domain_tags: Optional[List[str]] = None,
) -> GovernanceDecision:
    sensitive = requires_sensitive_controls(domain_tags, intended_use)
    return GovernanceDecision(
        risk_level=risk_level,
        current_stage=ApprovalStage.DRAFT,
        deployment_target=deployment_target,
        intended_use=intended_use,
        domain_tags=normalize_domain_tags(domain_tags),
        requires_specialized_reviewer=sensitive,
        requires_licensed_approver=sensitive and deployment_target == DeploymentTarget.PRODUCTION,
    )


def governance_summary(decision: GovernanceDecision) -> Dict[str, Any]:
    return {
        "risk_level": decision.risk_level.value,
        "current_stage": decision.current_stage.value,
        "deployment_target": decision.deployment_target.value,
        "intended_use": decision.intended_use,
        "domain_tags": decision.domain_tags,
        "requires_specialized_reviewer": decision.requires_specialized_reviewer,
        "requires_licensed_approver": decision.requires_licensed_approver,
        "required_evidence_completeness": round(decision.evidence.completeness(), 2),
        "approval_count": len(decision.approvals),
    }


def approval_records_from_snapshot(raw_approvals: Optional[List[Dict[str, Any]]]) -> List[ApprovalRecord]:
    approvals: List[ApprovalRecord] = []
    for item in raw_approvals or []:
        try:
            approvals.append(
                ApprovalRecord(
                    reviewer_user_id=item.get("reviewer_user_id"),
                    reviewer_id=item["reviewer_id"],
                    reviewer_role=ReviewerRole(item["reviewer_role"]),
                    approved=bool(item.get("approved", False)),
                    reviewer_name=item.get("reviewer_name"),
                    reviewer_license_id=item.get("reviewer_license_id"),
                    reviewer_verified=bool(item.get("reviewer_verified", False)),
                    verification_reasons=list(item.get("verification_reasons") or []),
                    notes=item.get("notes", ""),
                    timestamp=item.get("timestamp", datetime.now(timezone.utc).isoformat()),
                )
            )
        except Exception:
            continue
    return approvals


def decision_from_model_snapshot(model_snapshot: Dict[str, Any]) -> GovernanceDecision:
    decision = default_governance_decision(
        risk_level=GovernanceRiskLevel(model_snapshot.get("ai_risk_assessment", GovernanceRiskLevel.LOW.value)),
        deployment_target=DeploymentTarget(model_snapshot.get("deployment_target", DeploymentTarget.DEVELOPMENT.value)),
        intended_use=model_snapshot.get("intended_use", "general"),
        domain_tags=model_snapshot.get("domain_tags", []),
    )
    decision.current_stage = ApprovalStage(model_snapshot.get("approval_stage", ApprovalStage.DRAFT.value))
    decision.requires_specialized_reviewer = bool(model_snapshot.get("requires_specialized_reviewer", False))
    decision.requires_licensed_approver = bool(model_snapshot.get("requires_licensed_approver", False))
    decision.approvals = approval_records_from_snapshot(model_snapshot.get("governance_approvals"))
    decision.evidence = GovernanceEvidence(**(model_snapshot.get("governance_evidence") or {}))
    return decision


def minimum_evidence_required(next_stage: ApprovalStage) -> float:
    if next_stage == ApprovalStage.COMPLIANCE_REVIEW:
        return 0.25
    if next_stage == ApprovalStage.APPROVED:
        return 0.50
    if next_stage == ApprovalStage.PRODUCTION:
        return 1.0
    return 0.0


def approved_roles(decision: GovernanceDecision) -> Dict[ReviewerRole, List[ApprovalRecord]]:
    grouped: Dict[ReviewerRole, List[ApprovalRecord]] = {}
    for approval in decision.approvals:
        if not approval.approved or not approval.reviewer_verified:
            continue
        grouped.setdefault(approval.reviewer_role, []).append(approval)
    return grouped


def evaluate_stage_gate(decision: GovernanceDecision, next_stage: ApprovalStage) -> GovernanceEnforcementResult:
    requirements = required_reviewers(decision, next_stage)
    grouped = approved_roles(decision)
    completeness = decision.evidence.completeness()
    min_required = minimum_evidence_required(next_stage)

    result = GovernanceEnforcementResult(
        allowed=True,
        next_stage=next_stage,
        evidence_completeness=round(completeness, 2),
        minimum_evidence_required=min_required,
    )

    for requirement in requirements:
        matching = grouped.get(requirement.role, [])
        if not matching:
            result.missing_roles.append(requirement.role.value)
            result.reasons.append(f"Missing required approval role: {requirement.role.value}")
            continue

        if requirement.role == ReviewerRole.LICENSED_APPROVER:
            has_license = any(record.reviewer_license_id for record in matching)
            if not has_license:
                result.missing_license_roles.append(requirement.role.value)
                result.reasons.append("Licensed approver must include reviewer_license_id")

    if completeness < min_required:
        result.reasons.append(
            f"Evidence completeness {completeness:.2f} below required {min_required:.2f} for {next_stage.value}"
        )

    if result.missing_roles or result.missing_license_roles or completeness < min_required:
        result.allowed = False

    return result

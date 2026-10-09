"""
AI Model Versioning & Registry - AI Act Compliance
Tracks all ML models, versions, performance, and compliance status
"""

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from model_governance import (
    ApprovalRecord,
    ApprovalStage,
    DeploymentTarget,
    GovernanceEvidence,
    GovernanceRiskLevel,
    ReviewerRole,
    classify_governance_risk,
    decision_from_model_snapshot,
    default_governance_decision,
    evaluate_stage_gate,
    governance_summary,
    required_reviewers,
    validate_transition,
)
from reviewer_identity_registry import ReviewerIdentityRegistry, ReviewerProfile

get_db_session_fn: Optional[Callable[..., Any]] = None
persist_registration_fn: Optional[Callable[..., Dict[str, Any]]] = None
persist_approval_fn: Optional[Callable[..., Dict[str, Any]]] = None
persist_stage_transition_fn: Optional[Callable[..., Dict[str, Any]]] = None
persist_evidence_update_fn: Optional[Callable[..., Dict[str, Any]]] = None

try:
    from apps.api.database.connection import get_db_session as get_db_session_fn
    from apps.api.services.model_governance_store import (
        persist_approval as persist_approval_fn,
    )
    from apps.api.services.model_governance_store import (
        persist_evidence_update as persist_evidence_update_fn,
    )
    from apps.api.services.model_governance_store import (
        persist_registration as persist_registration_fn,
    )
    from apps.api.services.model_governance_store import (
        persist_stage_transition as persist_stage_transition_fn,
    )
    GOVERNANCE_DB_AVAILABLE = True
except Exception:
    GOVERNANCE_DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class ModelStatus(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"

class ModelType(str, Enum):
    LLM = "llm"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    NEURAL_NETWORK = "neural_network"
    TIME_SERIES = "time_series"

@dataclass
class ModelVersion:
    """Model version metadata"""
    model_id: str
    version: str
    status: str
    model_type: str
    framework: str
    created_date: str
    trained_on_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_data_hash: str
    model_hash: str
    parameters: Dict[str, Any]
    compliance_checked: bool
    ai_risk_assessment: str  # "minimal", "low", "medium", "high"
    documentation: str
    owner: str
    approval_stage: str = ApprovalStage.DRAFT.value
    deployment_target: str = DeploymentTarget.DEVELOPMENT.value
    intended_use: str = "general"
    domain_tags: Optional[List[str]] = None
    requires_specialized_reviewer: bool = False
    requires_licensed_approver: bool = False
    governance_evidence: Optional[Dict[str, Any]] = None

class AIModelRegistry:
    """Centralized AI Model Registry"""

    MODEL_REGISTRY_FILE = os.getenv("MODEL_REGISTRY_PATH", "model_registry.json")

    def __init__(self) -> None:
        self.models: Dict[str, List[Dict[str, Any]]] = self._load_registry()

    def _load_registry(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load model registry from disk"""
        try:
            if os.path.exists(self.MODEL_REGISTRY_FILE):
                with open(self.MODEL_REGISTRY_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load model registry: {e}")
        return {}

    def _save_registry(self):
        """Save model registry to disk"""
        try:
            with open(self.MODEL_REGISTRY_FILE, 'w') as f:
                json.dump(self.models, f, indent=2)
            logger.info(f"✅ Model registry saved to {self.MODEL_REGISTRY_FILE}")
        except Exception as e:
            logger.error(f"Failed to save model registry: {e}")

    def register_model(self, model_version: ModelVersion) -> bool:
        """Register a new model version"""
        try:
            if model_version.model_id not in self.models:
                self.models[model_version.model_id] = []

            self.models[model_version.model_id].append(asdict(model_version))
            self._save_registry()
            logger.info(f"✅ Model registered: {model_version.model_id}@{model_version.version}")
            return True
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return False

    def get_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a model"""
        return self.models.get(model_id, [])

    def get_latest_production_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get latest production version of a model"""
        versions = self.get_model_versions(model_id)
        production_versions = [v for v in versions if v['status'] == ModelStatus.PRODUCTION.value]
        if production_versions:
            return production_versions[-1]
        return None

    def promote_model(self, model_id: str, version: str, new_status: str) -> bool:
        """Promote model to new status (e.g., staging -> production)"""
        versions: List[Dict[str, Any]] = self.models.get(model_id, [])
        for v in versions:
            if v['version'] == version:
                old_status = v['status']
                v['status'] = new_status
                v['last_promoted'] = datetime.utcnow().isoformat()
                self._save_registry()
                logger.info(f"🔄 Model promoted: {model_id}@{version} ({old_status} -> {new_status})")
                return True
        return False

    def deprecate_model(self, model_id: str, version: str, reason: str) -> bool:
        """Deprecate a model version"""
        versions: List[Dict[str, Any]] = self.models.get(model_id, [])
        for v in versions:
            if v['version'] == version:
                v['status'] = ModelStatus.DEPRECATED.value
                v['deprecation_reason'] = reason
                v['deprecated_date'] = datetime.utcnow().isoformat()
                self._save_registry()
                logger.warning(f"⚠️  Model deprecated: {model_id}@{version} - {reason}")
                return True
        return False

class AIComplianceChecker:
    """AI/ML Model Compliance Verification"""

    @staticmethod
    def calculate_model_hash(model_path: str) -> str:
        """Calculate SHA-256 hash of model file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(model_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate model hash: {e}")
            return ""

    @staticmethod
    def assess_ai_risk(model_type: str, training_samples: int,
                      accuracy: float, high_stakes: bool = False) -> str:
        """
        Assess AI model risk level per EU AI Act
        Returns: "minimal", "low", "medium", "high"
        """
        if high_stakes and accuracy < 0.90:
            return "high"
        elif accuracy < 0.80:
            return "medium"
        elif training_samples < 1000:
            return "low"
        else:
            return "minimal"

    @staticmethod
    def assess_governance_risk(
        model_type: str,
        training_samples: int,
        accuracy: float,
        high_stakes: bool = False,
        domain_tags: Optional[List[str]] = None,
        intended_use: str = "general",
    ) -> str:
        """Risk classification aligned with staged governance workflow"""
        return classify_governance_risk(
            model_type=model_type,
            trained_on_samples=training_samples,
            accuracy=accuracy,
            high_stakes=high_stakes,
            domain_tags=domain_tags,
            intended_use=intended_use,
        ).value

    @staticmethod
    def generate_model_documentation(model: ModelVersion) -> str:
        """Generate AI model documentation for compliance"""
        doc = f"""
# Model: {model.model_id} v{model.version}

## Model Information
- **Type**: {model.model_type}
- **Framework**: {model.framework}
- **Status**: {model.status}
- **Created**: {model.created_date}
- **Owner**: {model.owner}
- **Risk Level**: {model.ai_risk_assessment}

## Performance Metrics
- **Accuracy**: {model.accuracy:.2%}
- **Precision**: {model.precision:.2%}
- **Recall**: {model.recall:.2%}
- **F1 Score**: {model.f1_score:.2%}

## Training Data
- **Samples**: {model.trained_on_samples:,}
- **Data Hash**: {model.training_data_hash}

## Model Integrity
- **Model Hash**: {model.model_hash}
- **Parameters**: {json.dumps(model.parameters, indent=2)}

## Compliance Status
✅ **Compliance Checked**: {model.compliance_checked}
✅ **AI Act Risk Assessment**: {model.ai_risk_assessment}
✅ **Documentation**: Complete

## Governance Workflow
- **Approval Stage**: {model.approval_stage}
- **Deployment Target**: {model.deployment_target}
- **Intended Use**: {model.intended_use}
- **Domain Tags**: {', '.join(model.domain_tags or []) or 'n/a'}
- **Specialized Reviewer Required**: {model.requires_specialized_reviewer}
- **Licensed Approver Required**: {model.requires_licensed_approver}
- **Evidence Completeness**: {round(GovernanceEvidence(**(model.governance_evidence or {})).completeness(), 2)}

## Parameters
{json.dumps(model.parameters, indent=2)}
"""
        return doc

class ModelVersioningAPI:
    """API endpoints for model versioning"""

    def __init__(self):
        self.registry = AIModelRegistry()
        self.reviewer_registry = ReviewerIdentityRegistry()

    def upsert_reviewer_profile(
        self,
        reviewer_id: str,
        reviewer_name: str,
        allowed_roles: List[str],
        status: str = "active",
        license_id: Optional[str] = None,
        license_expires_at: Optional[str] = None,
        specialization_tags: Optional[List[str]] = None,
        organization: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        profile = ReviewerProfile(
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            status=status,
            allowed_roles=allowed_roles,
            license_id=license_id,
            license_expires_at=license_expires_at,
            specialization_tags=specialization_tags or [],
            organization=organization,
            metadata=metadata or {},
        )
        saved = self.reviewer_registry.upsert_reviewer(profile)
        return {
            "status": "saved",
            "reviewer": saved,
        }

    def get_reviewer_profile(self, reviewer_id: str) -> Dict[str, Any]:
        profile = self.reviewer_registry.get_reviewer(reviewer_id)
        if not profile:
            return {"status": "not_found", "reason": "Reviewer profile not found"}
        return {"status": "ok", "reviewer": profile}

    def reviewer_roles(self, reviewer_id: str) -> List[str]:
        profile = self.reviewer_registry.get_reviewer(reviewer_id)
        if not profile:
            return []
        if profile.get("status") != "active":
            return []
        return list(profile.get("allowed_roles") or [])

    def can_manage_reviewer_profiles(self, reviewer_id: str) -> bool:
        roles = set(self.reviewer_roles(reviewer_id))
        privileged = {
            ReviewerRole.RISK_OWNER.value,
            ReviewerRole.COMPLIANCE_OWNER.value,
        }
        return bool(roles.intersection(privileged))

    def can_transition_stage(self, reviewer_id: str, next_stage: str) -> bool:
        roles = set(self.reviewer_roles(reviewer_id))
        if next_stage == ApprovalStage.PRODUCTION.value:
            return ReviewerRole.COMPLIANCE_OWNER.value in roles
        return bool(
            roles.intersection(
                {
                    ReviewerRole.RISK_OWNER.value,
                    ReviewerRole.COMPLIANCE_OWNER.value,
                }
            )
        )

    def get_model_version_snapshot(self, model_id: str, version: str) -> Optional[Dict[str, Any]]:
        """Return a single model version snapshot from the registry."""
        versions = self.registry.get_model_versions(model_id)
        for model in versions:
            if model.get("version") == version:
                return model
        return None

    def get_governance_status(self, model_id: str, version: str) -> Dict[str, Any]:
        """Return current governance status for a model version."""
        model = self.get_model_version_snapshot(model_id, version)
        if not model:
            return {"status": "not_found", "reason": "Model version not found"}

        decision = decision_from_model_snapshot(model)
        return {
            "status": "ok",
            "model_id": model_id,
            "version": version,
            "governance": governance_summary(decision),
            "approvals": model.get("governance_approvals", []),
            "evidence": model.get("governance_evidence") or {},
            "approval_stage": model.get("approval_stage", ApprovalStage.DRAFT.value),
        }

    def create_model_version(self, model_id: str, version: str,
                            model_type: str, framework: str,
                            trained_on_samples: int, accuracy: float,
                            precision: float, recall: float, f1_score: float,
                            training_data_hash: str, model_hash: str,
                            parameters: Dict, owner: str,
                            deployment_target: str = DeploymentTarget.DEVELOPMENT.value,
                            intended_use: str = "general",
                            domain_tags: Optional[List[str]] = None,
                            high_stakes: bool = False) -> Dict[str, Any]:
        """Create and register a new model version"""

        ai_risk = AIComplianceChecker.assess_governance_risk(
            model_type,
            trained_on_samples,
            accuracy,
            high_stakes=high_stakes,
            domain_tags=domain_tags,
            intended_use=intended_use,
        )

        governance = default_governance_decision(
            risk_level=GovernanceRiskLevel(ai_risk),
            deployment_target=DeploymentTarget(deployment_target),
            intended_use=intended_use,
            domain_tags=domain_tags,
        )

        evidence_bundle = GovernanceEvidence()

        model_version = ModelVersion(
            model_id=model_id,
            version=version,
            status=ModelStatus.DEVELOPMENT.value,
            model_type=model_type,
            framework=framework,
            created_date=datetime.utcnow().isoformat(),
            trained_on_samples=trained_on_samples,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            training_data_hash=training_data_hash,
            model_hash=model_hash,
            parameters=parameters,
            compliance_checked=False,
            ai_risk_assessment=ai_risk,
            documentation=AIComplianceChecker.generate_model_documentation(
                ModelVersion(
                    model_id, version, ModelStatus.DEVELOPMENT.value, model_type,
                    framework, datetime.utcnow().isoformat(), trained_on_samples,
                    accuracy, precision, recall, f1_score, training_data_hash,
                    model_hash, parameters, False, ai_risk, "", owner,
                    approval_stage=governance.current_stage.value,
                    deployment_target=governance.deployment_target.value,
                    intended_use=governance.intended_use,
                    domain_tags=governance.domain_tags,
                    requires_specialized_reviewer=governance.requires_specialized_reviewer,
                    requires_licensed_approver=governance.requires_licensed_approver,
                    governance_evidence=asdict(evidence_bundle),
                )
            ),
            owner=owner,
            approval_stage=governance.current_stage.value,
            deployment_target=governance.deployment_target.value,
            intended_use=governance.intended_use,
            domain_tags=governance.domain_tags,
            requires_specialized_reviewer=governance.requires_specialized_reviewer,
            requires_licensed_approver=governance.requires_licensed_approver,
            governance_evidence=asdict(evidence_bundle),
        )

        success = self.registry.register_model(model_version)
        persistence = None
        if success and GOVERNANCE_DB_AVAILABLE and get_db_session_fn is not None and persist_registration_fn is not None:
            try:
                with get_db_session_fn() as session:
                    persistence = persist_registration_fn(
                        session,
                        model_snapshot=asdict(model_version),
                        actor_id=owner,
                        actor_role=ReviewerRole.MODEL_OWNER.value,
                    )
            except Exception as e:
                logger.warning(f"Governance DB persistence skipped: {e}")
        return {
            "status": "registered" if success else "failed",
            "model": asdict(model_version),
            "governance": governance_summary(governance),
            "required_reviewers_for_compliance_review": [
                requirement.role.value
                for requirement in required_reviewers(governance, ApprovalStage.COMPLIANCE_REVIEW)
            ],
            "governance_persistence": persistence,
        }

    def transition_model_stage(
        self,
        model_id: str,
        version: str,
        next_stage: str,
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Skeleton stage transition validator for governance workflow"""
        versions = self.registry.get_model_versions(model_id)
        for model in versions:
            if model.get("version") != version:
                continue

            current = ApprovalStage(model.get("approval_stage", ApprovalStage.DRAFT.value))
            target = ApprovalStage(next_stage)
            allowed, message = validate_transition(current, target)
            if not allowed:
                return {"status": "rejected", "reason": message}

            decision = decision_from_model_snapshot(model)
            enforcement = evaluate_stage_gate(decision, target)
            if not enforcement.allowed:
                return {
                    "status": "blocked",
                    "reason": "Governance requirements not satisfied",
                    "enforcement": {
                        "missing_roles": enforcement.missing_roles,
                        "missing_license_roles": enforcement.missing_license_roles,
                        "evidence_completeness": enforcement.evidence_completeness,
                        "minimum_evidence_required": enforcement.minimum_evidence_required,
                        "reasons": enforcement.reasons,
                    },
                }

            model["approval_stage"] = target.value
            self.registry._save_registry()
            persistence = None
            if GOVERNANCE_DB_AVAILABLE and get_db_session_fn is not None and persist_stage_transition_fn is not None:
                try:
                    with get_db_session_fn() as session:
                        persistence = persist_stage_transition_fn(
                            session,
                            model_snapshot=model,
                            from_stage=current.value,
                            to_stage=target.value,
                            actor_id=actor_id,
                            actor_role=actor_role,
                            details={"enforcement": enforcement.reasons},
                        )
                except Exception as e:
                    logger.warning(f"Governance transition persistence skipped: {e}")
            return {
                "status": "transitioned",
                "model_id": model_id,
                "version": version,
                "from": current.value,
                "to": target.value,
                "governance_persistence": persistence,
            }

        return {"status": "not_found", "reason": "Model version not found"}

    def required_human_review(self, model_id: str, version: str, next_stage: str) -> Dict[str, Any]:
        """Return which human roles are required for the next stage"""
        versions = self.registry.get_model_versions(model_id)
        for model in versions:
            if model.get("version") != version:
                continue

            governance = decision_from_model_snapshot(model)
            roles = required_reviewers(governance, ApprovalStage(next_stage))
            enforcement = evaluate_stage_gate(governance, ApprovalStage(next_stage))
            return {
                "model_id": model_id,
                "version": version,
                "next_stage": next_stage,
                "required_roles": [role.role.value for role in roles],
                "licensed_approver_required": any(role.role == ReviewerRole.LICENSED_APPROVER for role in roles),
                "gate_status": {
                    "allowed": enforcement.allowed,
                    "missing_roles": enforcement.missing_roles,
                    "missing_license_roles": enforcement.missing_license_roles,
                    "evidence_completeness": enforcement.evidence_completeness,
                    "minimum_evidence_required": enforcement.minimum_evidence_required,
                },
            }

        return {"status": "not_found", "reason": "Model version not found"}

    def add_model_approval(
        self,
        model_id: str,
        version: str,
        reviewer_id: str,
        reviewer_role: str,
        approved: bool,
        *,
        reviewer_name: Optional[str] = None,
        reviewer_license_id: Optional[str] = None,
        notes: str = "",
        reviewer_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record a governance approval into the file registry and DB mirror."""
        versions = self.registry.get_model_versions(model_id)
        for model in versions:
            if model.get("version") != version:
                continue

            verification = self.reviewer_registry.verify(
                reviewer_id=reviewer_id,
                reviewer_role=reviewer_role,
                reviewer_license_id=reviewer_license_id,
            )
            if not verification.verified:
                return {
                    "status": "rejected",
                    "reason": "Reviewer identity verification failed",
                    "verification": {
                        "reviewer_id": verification.reviewer_id,
                        "reviewer_role": verification.reviewer_role,
                        "profile_found": verification.profile_found,
                        "reasons": verification.reasons,
                    },
                }

            approval = ApprovalRecord(
                reviewer_user_id=reviewer_user_id,
                reviewer_id=reviewer_id,
                reviewer_role=ReviewerRole(reviewer_role),
                approved=approved,
                reviewer_name=reviewer_name,
                reviewer_license_id=reviewer_license_id,
                reviewer_verified=verification.verified,
                verification_reasons=verification.reasons,
                notes=notes,
            )
            model.setdefault("governance_approvals", []).append(asdict(approval))
            self.registry._save_registry()

            persistence = None
            if GOVERNANCE_DB_AVAILABLE and get_db_session_fn is not None and persist_approval_fn is not None:
                try:
                    with get_db_session_fn() as session:
                        persistence = persist_approval_fn(
                            session,
                            model_snapshot=model,
                            approval_payload=asdict(approval),
                        )
                except Exception as e:
                    logger.warning(f"Governance approval persistence skipped: {e}")

            return {
                "status": "recorded",
                "model_id": model_id,
                "version": version,
                "approval": asdict(approval),
                "governance_persistence": persistence,
            }

        return {"status": "not_found", "reason": "Model version not found"}

    def update_governance_evidence(
        self,
        model_id: str,
        version: str,
        evidence_updates: Dict[str, Any],
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Merge governance evidence into a model snapshot and persist it."""
        model = self.get_model_version_snapshot(model_id, version)
        if not model:
            return {"status": "not_found", "reason": "Model version not found"}

        previous_evidence = dict(model.get("governance_evidence") or {})
        merged_evidence = {**previous_evidence, **evidence_updates}
        validated_evidence = asdict(GovernanceEvidence(**merged_evidence))
        model["governance_evidence"] = validated_evidence

        # Refresh embedded documentation snapshot
        refreshed_model = ModelVersion(
            model_id=model["model_id"],
            version=model["version"],
            status=model["status"],
            model_type=model["model_type"],
            framework=model["framework"],
            created_date=model["created_date"],
            trained_on_samples=model["trained_on_samples"],
            accuracy=model["accuracy"],
            precision=model["precision"],
            recall=model["recall"],
            f1_score=model["f1_score"],
            training_data_hash=model["training_data_hash"],
            model_hash=model["model_hash"],
            parameters=model["parameters"],
            compliance_checked=model["compliance_checked"],
            ai_risk_assessment=model["ai_risk_assessment"],
            documentation=model.get("documentation", ""),
            owner=model["owner"],
            approval_stage=model.get("approval_stage", ApprovalStage.DRAFT.value),
            deployment_target=model.get("deployment_target", DeploymentTarget.DEVELOPMENT.value),
            intended_use=model.get("intended_use", "general"),
            domain_tags=model.get("domain_tags"),
            requires_specialized_reviewer=bool(model.get("requires_specialized_reviewer", False)),
            requires_licensed_approver=bool(model.get("requires_licensed_approver", False)),
            governance_evidence=validated_evidence,
        )
        refreshed_model.documentation = AIComplianceChecker.generate_model_documentation(refreshed_model)
        model["documentation"] = refreshed_model.documentation

        self.registry._save_registry()

        persistence = None
        if (
            GOVERNANCE_DB_AVAILABLE
            and get_db_session_fn is not None
            and persist_evidence_update_fn is not None
        ):
            try:
                with get_db_session_fn() as session:
                    persistence = persist_evidence_update_fn(
                        session,
                        model_snapshot=model,
                        previous_evidence=previous_evidence,
                        updated_evidence=validated_evidence,
                        actor_id=actor_id,
                        actor_role=actor_role,
                    )
            except Exception as e:
                logger.warning(f"Governance evidence persistence skipped: {e}")

        decision = decision_from_model_snapshot(model)
        return {
            "status": "updated",
            "model_id": model_id,
            "version": version,
            "evidence": validated_evidence,
            "governance": governance_summary(decision),
            "governance_persistence": persistence,
        }

# FastAPI Integration
"""
from fastapi import FastAPI, HTTPException

app = FastAPI()
versioning_api = ModelVersioningAPI()

@app.post("/api/models/register")
async def register_model(model_data: dict):
    result = versioning_api.create_model_version(**model_data)
    return result

@app.get("/api/models/{model_id}/versions")
async def get_model_versions(model_id: str):
    versions = versioning_api.registry.get_model_versions(model_id)
    return {"model_id": model_id, "versions": versions}

@app.get("/api/models/{model_id}/production")
async def get_production_model(model_id: str):
    model = versioning_api.registry.get_latest_production_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="No production model found")
    return model

@app.post("/api/models/{model_id}/{version}/promote")
async def promote_model(model_id: str, version: str, new_status: str):
    success = versioning_api.registry.promote_model(model_id, version, new_status)
    return {"status": "promoted" if success else "failed"}
"""

if __name__ == "__main__":
    print("🤖 AI Model Versioning System")
    print("   Registry: model_registry.json")
    print("   Compliance: EU AI Act, GDPR, Transparency")
    print("   Status tracking: Development → Staging → Production → Deprecated")

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ai_model_versioning import ApprovalStage, ModelVersioningAPI
from apps.api.auth.dependencies import get_current_active_user
from apps.api.auth.models import User
from model_governance import ReviewerRole

router = APIRouter(prefix="/api/models", tags=["model-governance"])
versioning_api = ModelVersioningAPI()


class ModelRegistrationRequest(BaseModel):
    model_id: str
    version: str
    model_type: str
    framework: str
    trained_on_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_data_hash: str
    model_hash: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    owner: str
    deployment_target: str = "development"
    intended_use: str = "general"
    domain_tags: List[str] = Field(default_factory=list)
    high_stakes: bool = False


class GovernanceApprovalRequest(BaseModel):
    reviewer_id: str
    reviewer_role: str
    approved: bool
    reviewer_name: Optional[str] = None
    reviewer_license_id: Optional[str] = None
    notes: str = ""


class GovernanceTransitionRequest(BaseModel):
    next_stage: str


class GovernanceEvidenceUpdateRequest(BaseModel):
    explainability_report: Optional[str] = None
    bias_assessment_report: Optional[str] = None
    validation_report: Optional[str] = None
    adversarial_test_report: Optional[str] = None
    approval_notes: Optional[List[str]] = None
    attached_artifacts: Optional[List[str]] = None
    actor_id: Optional[str] = None
    actor_role: Optional[str] = None


class ReviewerProfileUpsertRequest(BaseModel):
    reviewer_id: str
    reviewer_name: str
    allowed_roles: List[str] = Field(default_factory=list)
    status: str = "active"
    license_id: Optional[str] = None
    license_expires_at: Optional[str] = None
    specialization_tags: List[str] = Field(default_factory=list)
    organization: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.post("/register")
async def register_model(request: ModelRegistrationRequest):
    return versioning_api.create_model_version(**request.model_dump())


@router.get("/{model_id}/{version}/governance")
async def get_governance(model_id: str, version: str):
    result = versioning_api.get_governance_status(model_id, version)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result


@router.get("/{model_id}/{version}/gate-status")
async def get_gate_status(model_id: str, version: str, next_stage: str):
    try:
        ApprovalStage(next_stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid next_stage: {next_stage}") from exc

    result = versioning_api.required_human_review(model_id, version, next_stage)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result


@router.post("/{model_id}/{version}/approvals")
async def add_approval(
    model_id: str,
    version: str,
    request: GovernanceApprovalRequest,
    current_user: User = Depends(get_current_active_user),
):
    actor_reviewer_id = str(current_user.id)
    if request.reviewer_id != actor_reviewer_id:
        raise HTTPException(
            status_code=403,
            detail="reviewer_id must match authenticated user identity",
        )

    result = versioning_api.add_model_approval(
        model_id=model_id,
        version=version,
        reviewer_id=actor_reviewer_id,
        reviewer_user_id=actor_reviewer_id,
        reviewer_role=request.reviewer_role,
        approved=request.approved,
        reviewer_name=request.reviewer_name or getattr(current_user, "full_name", None) or current_user.email,
        reviewer_license_id=request.reviewer_license_id,
        notes=request.notes,
    )
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result["reason"])
    if result.get("status") == "rejected":
        raise HTTPException(status_code=409, detail=result)
    return result


@router.post("/{model_id}/{version}/transition")
async def transition_model(
    model_id: str,
    version: str,
    request: GovernanceTransitionRequest,
    current_user: User = Depends(get_current_active_user),
):
    try:
        ApprovalStage(request.next_stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid next_stage: {request.next_stage}") from exc

    actor_id = str(current_user.id)
    if not versioning_api.can_transition_stage(actor_id, request.next_stage):
        raise HTTPException(
            status_code=403,
            detail="Authenticated user is not authorized to transition this governance stage",
        )

    result = versioning_api.transition_model_stage(
        model_id,
        version,
        request.next_stage,
        actor_id=actor_id,
        actor_role="authenticated_user",
    )
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result["reason"])
    if result.get("status") in {"rejected", "blocked"}:
        raise HTTPException(status_code=409, detail=result)
    return result


@router.patch("/{model_id}/{version}/evidence")
async def update_evidence(
    model_id: str,
    version: str,
    request: GovernanceEvidenceUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    payload = request.model_dump(exclude_none=True)
    payload.pop("actor_id", None)
    payload.pop("actor_role", None)
    result = versioning_api.update_governance_evidence(
        model_id=model_id,
        version=version,
        evidence_updates=payload,
        actor_id=str(current_user.id),
        actor_role="authenticated_user",
    )
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result


@router.post("/reviewers")
async def upsert_reviewer(
    request: ReviewerProfileUpsertRequest,
    current_user: User = Depends(get_current_active_user),
):
    actor_reviewer_id = str(current_user.id)
    payload = request.model_dump()

    is_self_update = payload["reviewer_id"] == actor_reviewer_id
    is_privileged = versioning_api.can_manage_reviewer_profiles(actor_reviewer_id)

    if not is_self_update and not is_privileged:
        raise HTTPException(
            status_code=403,
            detail="Only governance reviewers can manage other reviewer profiles",
        )

    if is_self_update and not is_privileged:
        payload["reviewer_id"] = actor_reviewer_id
        payload["reviewer_name"] = getattr(current_user, "full_name", None) or current_user.email
        payload["allowed_roles"] = [ReviewerRole.MODEL_OWNER.value]
        payload["status"] = "active"
        payload["license_id"] = None
        payload["license_expires_at"] = None
        payload["specialization_tags"] = []
        payload["organization"] = payload.get("organization")
        payload["metadata"] = payload.get("metadata") or {}

    return versioning_api.upsert_reviewer_profile(**payload)


@router.get("/reviewers/{reviewer_id}")
async def get_reviewer(reviewer_id: str, current_user: User = Depends(get_current_active_user)):
    actor_reviewer_id = str(current_user.id)
    is_privileged = versioning_api.can_manage_reviewer_profiles(actor_reviewer_id)
    if reviewer_id != actor_reviewer_id and not is_privileged:
        raise HTTPException(
            status_code=403,
            detail="Can only read own reviewer profile unless governance privileged",
        )

    result = versioning_api.get_reviewer_profile(reviewer_id)
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result

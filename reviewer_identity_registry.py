from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from model_governance import ReviewerRole

logger = logging.getLogger(__name__)


class ReviewerStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


@dataclass
class ReviewerProfile:
    reviewer_id: str
    reviewer_name: str
    status: str = ReviewerStatus.ACTIVE.value
    allowed_roles: List[str] = field(default_factory=list)
    license_id: Optional[str] = None
    license_expires_at: Optional[str] = None
    specialization_tags: List[str] = field(default_factory=list)
    organization: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ReviewerVerificationResult:
    verified: bool
    reviewer_id: str
    reviewer_role: str
    reasons: List[str] = field(default_factory=list)
    profile_found: bool = False


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


class ReviewerIdentityRegistry:
    REVIEWER_REGISTRY_FILE = os.getenv("REVIEWER_REGISTRY_PATH", "reviewer_registry.json")

    def __init__(self) -> None:
        self.reviewers: Dict[str, Dict[str, Any]] = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        try:
            if os.path.exists(self.REVIEWER_REGISTRY_FILE):
                with open(self.REVIEWER_REGISTRY_FILE, "r", encoding="utf-8") as file:
                    loaded = json.load(file)
                if isinstance(loaded, dict):
                    return loaded
        except Exception as exc:
            logger.warning("Could not load reviewer registry: %s", exc)
        return {}

    def _save_registry(self) -> None:
        try:
            with open(self.REVIEWER_REGISTRY_FILE, "w", encoding="utf-8") as file:
                json.dump(self.reviewers, file, indent=2)
            logger.info("Reviewer registry saved to %s", self.REVIEWER_REGISTRY_FILE)
        except Exception as exc:
            logger.error("Failed to save reviewer registry: %s", exc)

    def upsert_reviewer(self, profile: ReviewerProfile) -> Dict[str, Any]:
        normalized = asdict(profile)
        normalized["allowed_roles"] = sorted({role.strip() for role in profile.allowed_roles if role and role.strip()})
        normalized["specialization_tags"] = sorted(
            {tag.strip().lower() for tag in profile.specialization_tags if tag and tag.strip()}
        )
        normalized["updated_at"] = datetime.now(timezone.utc).isoformat()

        self.reviewers[profile.reviewer_id] = normalized
        self._save_registry()
        return normalized

    def get_reviewer(self, reviewer_id: str) -> Optional[Dict[str, Any]]:
        return self.reviewers.get(reviewer_id)

    def verify(self, reviewer_id: str, reviewer_role: str, reviewer_license_id: Optional[str] = None) -> ReviewerVerificationResult:
        profile = self.get_reviewer(reviewer_id)
        result = ReviewerVerificationResult(
            verified=False,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            profile_found=profile is not None,
        )

        if profile is None:
            result.reasons.append("Reviewer profile not found")
            return result

        status = profile.get("status", ReviewerStatus.ACTIVE.value)
        if status != ReviewerStatus.ACTIVE.value:
            result.reasons.append(f"Reviewer status is not active: {status}")

        allowed_roles = set(profile.get("allowed_roles") or [])
        if reviewer_role not in allowed_roles:
            result.reasons.append(f"Reviewer role not authorized: {reviewer_role}")

        if reviewer_role == ReviewerRole.SPECIALIZED_REVIEWER.value:
            specialization_tags = profile.get("specialization_tags") or []
            if not specialization_tags:
                result.reasons.append("Specialized reviewer must include specialization_tags")

        if reviewer_role == ReviewerRole.LICENSED_APPROVER.value:
            profile_license_id = profile.get("license_id")
            if not profile_license_id:
                result.reasons.append("Licensed approver missing registry license_id")
            if reviewer_license_id and profile_license_id and reviewer_license_id != profile_license_id:
                result.reasons.append("Provided reviewer_license_id does not match registry")
            if not reviewer_license_id and profile_license_id:
                reviewer_license_id = profile_license_id

            expires_at = _parse_dt(profile.get("license_expires_at"))
            if expires_at and expires_at < datetime.now(timezone.utc):
                result.reasons.append("Reviewer license is expired")

        result.verified = len(result.reasons) == 0
        return result

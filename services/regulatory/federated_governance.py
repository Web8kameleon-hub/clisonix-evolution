from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class FederatedGovernanceHub:
    """Simple local-first federated governance utility with policy checks."""

    def __init__(self) -> None:
        self._local_updates: List[Dict[str, Any]] = []
        self._jurisdiction_profiles: Dict[str, Dict[str, Any]] = {}

    def register_jurisdiction_profile(
        self,
        jurisdiction: str,
        allowed_transfer_targets: List[str],
        required_regulation_tags: Optional[List[str]] = None,
    ) -> None:
        self._jurisdiction_profiles[jurisdiction] = {
            "allowed_transfer_targets": set(allowed_transfer_targets),
            "required_regulation_tags": set(required_regulation_tags or []),
        }

    def collect_local_update(
        self,
        *,
        jurisdiction: str,
        model_id: str,
        pattern_vector: List[float],
        is_clinical_data: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if is_clinical_data:
            raise ValueError("Clinical data is not allowed for federated pattern sharing")

        event = {
            "timestamp": _utc_now_iso(),
            "jurisdiction": jurisdiction,
            "model_id": model_id,
            "pattern_vector": pattern_vector,
            "is_clinical_data": is_clinical_data,
            "metadata": metadata or {},
        }
        self._local_updates.append(event)
        return event

    def can_transfer(
        self,
        *,
        source_jurisdiction: str,
        target_jurisdiction: str,
        regulation_tags: Optional[List[str]] = None,
    ) -> bool:
        profile = self._jurisdiction_profiles.get(source_jurisdiction)
        if not profile:
            return False
        if target_jurisdiction not in profile["allowed_transfer_targets"]:
            return False

        required = profile["required_regulation_tags"]
        tags = set(regulation_tags or [])
        return required.issubset(tags)

    def export_global_patterns(self, min_jurisdictions: int = 2) -> Dict[str, List[float]]:
        grouped: Dict[str, Dict[str, List[List[float]]]] = {}
        for item in self._local_updates:
            model_id = item["model_id"]
            jurisdiction = item["jurisdiction"]
            grouped.setdefault(model_id, {}).setdefault(jurisdiction, []).append(item["pattern_vector"])

        result: Dict[str, List[float]] = {}
        for model_id, by_jurisdiction in grouped.items():
            if len(by_jurisdiction) < min_jurisdictions:
                continue

            vectors = []
            for jurisdiction_vectors in by_jurisdiction.values():
                vectors.extend(jurisdiction_vectors)

            if not vectors:
                continue

            dim = len(vectors[0])
            means = []
            for i in range(dim):
                values = [vector[i] for vector in vectors if len(vector) == dim]
                means.append(sum(values) / len(values))
            result[model_id] = means

        return result

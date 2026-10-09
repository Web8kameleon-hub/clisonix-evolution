from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass
class SandboxPolicy:
    jurisdiction: str
    allowed_data_region: str
    regulation_profile: str
    allow_continuous_learning: bool = True
    require_reversible_versioning: bool = True


class SandboxedLearningEnvironment:
    """Jurisdiction-scoped learning guardrail with append-only JSONL logging."""

    def __init__(self, log_file: str = "./data/sandbox_learning_log.jsonl") -> None:
        self._policies: Dict[str, SandboxPolicy] = {}
        self._latest_version_by_model: Dict[str, str] = {}
        self._log_file = Path(log_file)
        self._log_file.parent.mkdir(parents=True, exist_ok=True)

    def register_policy(self, policy: SandboxPolicy) -> None:
        self._policies[policy.jurisdiction] = policy

    def validate_learning_scope(self, jurisdiction: str, data_region: str) -> Tuple[bool, str]:
        policy = self._policies.get(jurisdiction)
        if not policy:
            return False, f"No sandbox policy defined for jurisdiction={jurisdiction}"
        if policy.allowed_data_region != data_region:
            return (
                False,
                f"Region mismatch: jurisdiction={jurisdiction} allows={policy.allowed_data_region} got={data_region}",
            )
        if not policy.allow_continuous_learning:
            return False, f"Continuous learning disabled for jurisdiction={jurisdiction}"
        return True, "ok"

    def record_learning_iteration(
        self,
        *,
        model_id: str,
        jurisdiction: str,
        data_region: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        is_valid, reason = self.validate_learning_scope(jurisdiction, data_region)
        if not is_valid:
            raise ValueError(reason)

        previous_version = self._latest_version_by_model.get(model_id)
        version_id = f"{model_id}:{uuid4().hex[:12]}"
        self._latest_version_by_model[model_id] = version_id

        policy = self._policies[jurisdiction]
        event = {
            "event_id": uuid4().hex,
            "event_type": "learning_iteration",
            "timestamp": _utc_now_iso(),
            "model_id": model_id,
            "version_id": version_id,
            "previous_version": previous_version,
            "jurisdiction": jurisdiction,
            "data_region": data_region,
            "regulation_profile": policy.regulation_profile,
            "reversible": policy.require_reversible_versioning,
            "metadata": metadata or {},
        }
        self._append_log(event)
        return event

    def get_policy(self, jurisdiction: str) -> Optional[SandboxPolicy]:
        return self._policies.get(jurisdiction)

    def _append_log(self, event: Dict[str, Any]) -> None:
        with self._log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def export_policies(self) -> Dict[str, Dict[str, Any]]:
        return {k: asdict(v) for k, v in self._policies.items()}

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Set


@dataclass
class ExecutionDecision:
    decision: str
    reasons: List[str]
    execution_status: str
    job_id: Optional[str] = None

    def to_dict(self, module_id: str, approved_by: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "decision": self.decision,
            "reasons": list(self.reasons),
            "execution_status": self.execution_status,
            "module_id": module_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if self.job_id:
            payload["job_id"] = self.job_id
        if approved_by:
            payload["approved_by"] = approved_by
        return payload


class ExecutionGate:
    """Guards live execution from unverified or unsafe actions."""

    def __init__(self, destructive_actions: Optional[Sequence[str]] = None) -> None:
        self.destructive_actions = {
            action.lower() for action in (destructive_actions or ["delete_workflow", "execute_workflow", "shutdown"])
        }

    def evaluate(
        self,
        manifest: Dict[str, Any],
        action: str,
        runtime_state: Optional[str] = None,
        provided_requirements: Optional[Set[str]] = None,
        authenticated_operator: Optional[str] = None,
        approval_granted: bool = False,
    ) -> ExecutionDecision:
        reasons: List[str] = []
        requirements = set(manifest.get("requires", []))
        provided = set(provided_requirements or set())

        if not manifest.get("supports_live_execution", False):
            reasons.append("supports_live_execution=false")

        effective_runtime = str(runtime_state or manifest.get("runtime_state") or "offline").lower()
        if effective_runtime != "online":
            reasons.append(f"runtime_state={effective_runtime}")

        missing_requirements = sorted(requirements - provided)
        if missing_requirements:
            reasons.append(f"missing_requirements={','.join(missing_requirements)}")

        if "authenticated_operator" in requirements and not authenticated_operator:
            reasons.append("authenticated_operator=missing")

        action_key = action.lower().strip()
        if action_key in self.destructive_actions and not approval_granted:
            return ExecutionDecision(
                decision="requires_approval",
                reasons=["destructive_action_requires_approval"],
                execution_status="not_executed",
            )

        if reasons:
            return ExecutionDecision(
                decision="blocked",
                reasons=reasons,
                execution_status="blocked",
            )

        return ExecutionDecision(
            decision="allowed",
            reasons=[],
            execution_status="started",
            job_id=f"job_{uuid.uuid4().hex}",
        )


def evaluate_execution(
    manifest: Dict[str, Any],
    action: str,
    runtime_state: Optional[str] = None,
    provided_requirements: Optional[Set[str]] = None,
    authenticated_operator: Optional[str] = None,
    approval_granted: bool = False,
) -> Dict[str, Any]:
    gate = ExecutionGate()
    decision = gate.evaluate(
        manifest=manifest,
        action=action,
        runtime_state=runtime_state,
        provided_requirements=provided_requirements,
        authenticated_operator=authenticated_operator,
        approval_granted=approval_granted,
    )
    module_id = str(manifest.get("module_id") or "unknown-module")
    return decision.to_dict(module_id=module_id, approved_by=authenticated_operator)

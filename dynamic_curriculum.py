"""Persistent curriculum pipeline that commits only validated claims."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dump(model: BaseModel) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _normalise(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.casefold()))


class ValidationStatus(str, Enum):
    PASS = "pass"
    UNCERTAIN = "uncertain"
    REJECT = "reject"


class ClaimCandidate(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    source: str = Field(default="ocean", min_length=1)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    runtime_validated: Optional[bool] = None
    contradicts_claim_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GrandChallengeSubmission(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    claims: List[ClaimCandidate] = Field(default_factory=list, max_length=500)
    challenge_id: Optional[str] = None


class CurriculumEngine:
    """Evaluate challenges and persist only claims that pass validation."""

    SCHEMA_VERSION = 1

    def __init__(self, storage_path: Optional[str] = None):
        configured = storage_path or os.getenv(
            "ALBA_CURRICULUM_PATH", "data/alba_curriculum_memory.json"
        )
        self.storage_path = Path(configured)
        self._lock = asyncio.Lock()
        self.state: Dict[str, Any] = self._load()

    def _empty_state(self) -> Dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "validated_knowledge": {},
            "candidate_knowledge": {},
            "rejected_knowledge": {},
            "contradiction_memory": [],
            "durable_lessons": [],
            "followup_challenges": [],
            "challenges": {},
        }

    def _load(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return self._empty_state()
        try:
            loaded = json.loads(self.storage_path.read_text(encoding="utf-8"))
            if loaded.get("schema_version") != self.SCHEMA_VERSION:
                raise ValueError("unsupported curriculum schema")
            loaded.setdefault("followup_challenges", [])
            return loaded
        except (OSError, ValueError, json.JSONDecodeError):
            state = self._empty_state()
            state["storage_error"] = "existing curriculum memory could not be loaded"
            return state

    def _persist(self) -> None:
        if "storage_error" in self.state:
            raise RuntimeError(self.state["storage_error"])
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.state, ensure_ascii=False, indent=2, sort_keys=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self.storage_path.name}.",
            suffix=".tmp",
            dir=str(self.storage_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.storage_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    @staticmethod
    def _claim_id(text: str) -> str:
        return "claim-" + hashlib.sha256(_normalise(text).encode()).hexdigest()[:16]

    def _evaluate(self, claim: ClaimCandidate) -> Dict[str, Any]:
        claim_id = self._claim_id(claim.text)
        known = self.state["validated_knowledge"]
        duplicate = claim_id in known
        contradictions = [
            claim_id
            for claim_id in claim.contradicts_claim_ids
            if claim_id in known
        ]

        reasons: List[str] = []
        if claim.runtime_validated is False:
            status = ValidationStatus.REJECT
            reasons.append("runtime validation failed")
        elif contradictions:
            status = ValidationStatus.UNCERTAIN
            reasons.append("contradicts validated knowledge; adjudication required")
        elif duplicate:
            status = ValidationStatus.PASS
            reasons.append("matches existing validated knowledge")
        elif (
            claim.runtime_validated is True
            and claim.evidence
            and claim.confidence >= 0.75
        ):
            status = ValidationStatus.PASS
            reasons.append("evidence, runtime validation, and confidence gates passed")
        else:
            status = ValidationStatus.UNCERTAIN
            if not claim.evidence:
                reasons.append("evidence missing")
            if claim.runtime_validated is not True:
                reasons.append("runtime validation missing")
            if claim.confidence < 0.75:
                reasons.append("confidence below 0.75")

        score = round(
            0.35 * claim.confidence
            + 0.30 * float(bool(claim.evidence))
            + 0.35 * float(claim.runtime_validated is True),
            4,
        )
        return {
            "claim_id": claim_id,
            **_dump(claim),
            "status": status.value,
            "validation_score": score,
            "validation_reasons": reasons,
            "contradictions": contradictions,
            "knowledge_match": claim_id if duplicate else None,
            "evaluated_at": _now(),
        }

    async def process(self, submission: GrandChallengeSubmission) -> Dict[str, Any]:
        async with self._lock:
            challenge_id = submission.challenge_id or f"gc-{uuid.uuid4().hex[:12]}"
            if challenge_id in self.state["challenges"]:
                raise ValueError(f"challenge_id already exists: {challenge_id}")

            state_before = copy.deepcopy(self.state)
            evaluated = [self._evaluate(claim) for claim in submission.claims]
            counts = {status.value: 0 for status in ValidationStatus}
            contradiction_count = 0
            memory_updates = 0

            for record in evaluated:
                status = record["status"]
                counts[status] += 1
                contradiction_count += len(record["contradictions"])
                claim_id = record["claim_id"]
                if status == ValidationStatus.PASS.value:
                    if claim_id not in self.state["validated_knowledge"]:
                        memory_updates += 1
                        self.state["validated_knowledge"][claim_id] = record
                    else:
                        record["resolved_from_memory"] = True
                    self.state["candidate_knowledge"].pop(claim_id, None)
                elif status == ValidationStatus.REJECT.value:
                    self.state["rejected_knowledge"][claim_id] = record
                else:
                    self.state["candidate_knowledge"][claim_id] = record

                for target in record["contradictions"]:
                    self.state["contradiction_memory"].append(
                        {
                            "challenge_id": challenge_id,
                            "candidate_claim_id": claim_id,
                            "validated_claim_id": target,
                            "detected_at": record["evaluated_at"],
                        }
                    )

            followups = []
            for record in evaluated:
                if record["status"] != ValidationStatus.UNCERTAIN.value:
                    continue
                followup = {
                    "followup_id": f"fu-{uuid.uuid4().hex[:12]}",
                    "parent_challenge_id": challenge_id,
                    "topic": submission.topic,
                    "claim_id": record["claim_id"],
                    "objective": "Resolve validation gaps for the candidate claim",
                    "required_actions": list(record["validation_reasons"]),
                    "status": "open",
                    "created_at": _now(),
                }
                followups.append(followup)
                self.state["followup_challenges"].append(followup)

            lesson_ids = [
                record["claim_id"]
                for record in evaluated
                if record["status"] == ValidationStatus.PASS.value
            ]
            if lesson_ids:
                self.state["durable_lessons"].append(
                    {
                        "challenge_id": challenge_id,
                        "topic": submission.topic,
                        "claim_ids": lesson_ids,
                        "created_at": _now(),
                    }
                )

            summary = {
                "challenge_id": challenge_id,
                "topic": submission.topic,
                "difficulty": submission.difficulty,
                "claims_generated": len(evaluated),
                "claims_validated": counts["pass"],
                "claims_rejected": counts["reject"],
                "claims_unresolved": counts["uncertain"],
                "contradictions_found": contradiction_count,
                "lessons_created": 1 if lesson_ids else 0,
                "memory_updates": memory_updates,
                "followup_challenges": len(followups),
                "followups": followups,
                "created_at": _now(),
                "claims": evaluated,
            }
            self.state["challenges"][challenge_id] = summary
            try:
                self._persist()
            except Exception:
                self.state = state_before
                raise
            return summary

    def snapshot(self) -> Dict[str, Any]:
        return {
            "validated_knowledge": len(self.state["validated_knowledge"]),
            "candidate_knowledge": len(self.state["candidate_knowledge"]),
            "rejected_knowledge": len(self.state["rejected_knowledge"]),
            "contradictions": len(self.state["contradiction_memory"]),
            "durable_lessons": len(self.state["durable_lessons"]),
            "followup_challenges": len(self.state["followup_challenges"]),
            "challenges": len(self.state["challenges"]),
            "storage_path": str(self.storage_path),
            "storage_healthy": "storage_error" not in self.state,
        }

    def get_challenge(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        return self.state["challenges"].get(challenge_id)

    def get_memory(self, tier: str, limit: int = 100) -> List[Dict[str, Any]]:
        mapping = {
            "candidate": "candidate_knowledge",
            "validated": "validated_knowledge",
            "rejected": "rejected_knowledge",
            "contradictions": "contradiction_memory",
            "lessons": "durable_lessons",
            "followups": "followup_challenges",
        }
        key = mapping.get(tier)
        if key is None:
            raise ValueError(f"unknown memory tier: {tier}")
        collection = self.state[key]
        values = (
            list(collection.values())
            if isinstance(collection, dict)
            else list(collection)
        )
        return values[-limit:]

import asyncio
import json

import pytest

from dynamic_curriculum import (
    ClaimCandidate,
    CurriculumEngine,
    GrandChallengeSubmission,
)


def test_only_validated_claims_enter_durable_memory(tmp_path):
    path = tmp_path / "curriculum.json"
    engine = CurriculumEngine(str(path))
    result = asyncio.run(
        engine.process(
            GrandChallengeSubmission(
                challenge_id="gc-test",
                topic="Distributed memory",
                claims=[
                    ClaimCandidate(
                        text="Validated claim",
                        confidence=0.9,
                        evidence=["runtime:test-1"],
                        runtime_validated=True,
                    ),
                    ClaimCandidate(text="Model assertion only", confidence=0.95),
                    ClaimCandidate(
                        text="Failed experiment",
                        confidence=0.9,
                        evidence=["runtime:test-2"],
                        runtime_validated=False,
                    ),
                ],
            )
        )
    )

    assert result["claims_validated"] == 1
    assert result["claims_unresolved"] == 1
    assert result["claims_rejected"] == 1
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert len(persisted["validated_knowledge"]) == 1
    assert len(persisted["candidate_knowledge"]) == 1
    assert len(persisted["rejected_knowledge"]) == 1


def test_contradiction_is_not_committed(tmp_path):
    engine = CurriculumEngine(str(tmp_path / "curriculum.json"))
    first = asyncio.run(
        engine.process(
            GrandChallengeSubmission(
                topic="Baseline",
                claims=[
                    ClaimCandidate(
                        text="Replication is required",
                        confidence=0.9,
                        evidence=["experiment:a"],
                        runtime_validated=True,
                    )
                ],
            )
        )
    )
    known_id = first["claims"][0]["claim_id"]

    second = asyncio.run(
        engine.process(
            GrandChallengeSubmission(
                topic="Challenge baseline",
                claims=[
                    ClaimCandidate(
                        text="Replication is unnecessary",
                        confidence=0.99,
                        evidence=["experiment:b"],
                        runtime_validated=True,
                        contradicts_claim_ids=[known_id],
                    )
                ],
            )
        )
    )

    assert second["claims_unresolved"] == 1
    assert second["contradictions_found"] == 1
    assert second["memory_updates"] == 0


def test_challenge_ids_are_idempotency_keys(tmp_path):
    engine = CurriculumEngine(str(tmp_path / "curriculum.json"))
    submission = GrandChallengeSubmission(challenge_id="gc-fixed", topic="A")
    asyncio.run(engine.process(submission))
    with pytest.raises(ValueError, match="already exists"):
        asyncio.run(engine.process(submission))


def test_unvalidated_duplicate_cannot_replace_durable_evidence(tmp_path):
    engine = CurriculumEngine(str(tmp_path / "curriculum.json"))
    first = asyncio.run(
        engine.process(
            GrandChallengeSubmission(
                topic="Evidence",
                claims=[
                    ClaimCandidate(
                        text="Validated claim",
                        confidence=0.95,
                        evidence=["experiment:replicated"],
                        runtime_validated=True,
                    )
                ],
            )
        )
    )
    claim_id = first["claims"][0]["claim_id"]
    second = asyncio.run(
        engine.process(
            GrandChallengeSubmission(
                topic="Restatement",
                claims=[ClaimCandidate(text="Validated claim", confidence=0.1)],
            )
        )
    )

    durable = engine.state["validated_knowledge"][claim_id]
    assert second["memory_updates"] == 0
    assert second["claims"][0]["resolved_from_memory"] is True
    assert durable["evidence"] == ["experiment:replicated"]
    assert durable["runtime_validated"] is True


def test_uncertain_claim_creates_auditable_followup(tmp_path):
    engine = CurriculumEngine(str(tmp_path / "curriculum.json"))
    result = asyncio.run(
        engine.process(
            GrandChallengeSubmission(
                challenge_id="gc-followup",
                topic="Unknown mechanism",
                claims=[ClaimCandidate(text="A claim that still needs testing")],
            )
        )
    )

    assert result["followup_challenges"] == 1
    assert result["followups"][0]["parent_challenge_id"] == "gc-followup"
    assert result["followups"][0]["status"] == "open"
    assert engine.snapshot()["followup_challenges"] == 1

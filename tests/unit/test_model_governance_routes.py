from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routes import model_governance_routes as routes


class FakeVersioningAPI:
    def __init__(self):
        self.last_upsert_payload = None
        self.last_get_reviewer_id = None
        self.last_transition_payload = None
        self.last_evidence_payload = None
        self.last_approval_payload = None
        self.last_governance_lookup = None
        self.last_gate_lookup = None

    def get_governance_status(self, model_id: str, version: str):
        self.last_governance_lookup = {"model_id": model_id, "version": version}
        if model_id == "missing":
            return {"status": "not_found", "reason": "Model version not found"}
        return {
            "status": "ok",
            "model_id": model_id,
            "version": version,
            "governance": {"risk_level": "low"},
        }

    def required_human_review(self, model_id: str, version: str, next_stage: str):
        self.last_gate_lookup = {
            "model_id": model_id,
            "version": version,
            "next_stage": next_stage,
        }
        if model_id == "missing":
            return {"status": "not_found", "reason": "Model version not found"}
        return {
            "model_id": model_id,
            "version": version,
            "next_stage": next_stage,
            "required_roles": ["risk_owner"],
            "gate_status": {"allowed": True},
        }

    def add_model_approval(self, **kwargs):
        self.last_approval_payload = kwargs
        if kwargs.get("model_id") == "missing":
            return {"status": "not_found", "reason": "Model version not found"}
        if kwargs.get("reviewer_role") == "reject_me":
            return {"status": "rejected", "reason": "forced rejection"}
        return {"status": "recorded", "approval": kwargs}

    def can_transition_stage(self, reviewer_id: str, next_stage: str) -> bool:
        return reviewer_id == "allowed-user"

    def transition_model_stage(self, model_id: str, version: str, next_stage: str, actor_id=None, actor_role=None):
        if model_id == "missing":
            return {"status": "not_found", "reason": "Model version not found"}
        self.last_transition_payload = {
            "model_id": model_id,
            "version": version,
            "next_stage": next_stage,
            "actor_id": actor_id,
            "actor_role": actor_role,
        }
        return {
            "status": "transitioned",
            "model_id": model_id,
            "version": version,
            "to": next_stage,
            "actor_id": actor_id,
            "actor_role": actor_role,
        }

    def update_governance_evidence(self, **kwargs):
        self.last_evidence_payload = kwargs
        return {"status": "updated", "evidence": kwargs.get("evidence_updates", {})}

    def can_manage_reviewer_profiles(self, reviewer_id: str) -> bool:
        return reviewer_id == "compliance-user"

    def upsert_reviewer_profile(self, **kwargs):
        self.last_upsert_payload = kwargs
        return {"status": "saved", "reviewer": kwargs}

    def get_reviewer_profile(self, reviewer_id: str):
        self.last_get_reviewer_id = reviewer_id
        if reviewer_id == "missing":
            return {"status": "not_found", "reason": "Reviewer profile not found"}
        return {"status": "ok", "reviewer": {"reviewer_id": reviewer_id}}



def _client_for_user(user_id: str, email: str = "user@example.com") -> TestClient:
    app = FastAPI()
    app.include_router(routes.router)
    app.dependency_overrides[routes.get_current_active_user] = lambda: SimpleNamespace(
        id=user_id,
        email=email,
        full_name="Test User",
    )
    return TestClient(app)


def test_approval_reviewer_id_mismatch_returns_403(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("user-1")

    response = client.post(
        "/api/models/m1/v1/approvals",
        json={
            "reviewer_id": "someone-else",
            "reviewer_role": "risk_owner",
            "approved": True,
            "notes": "ok",
        },
    )

    assert response.status_code == 403


def test_approval_rejected_from_engine_returns_409(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("user-1")

    response = client.post(
        "/api/models/m1/v1/approvals",
        json={
            "reviewer_id": "user-1",
            "reviewer_role": "reject_me",
            "approved": True,
            "notes": "ok",
        },
    )

    assert response.status_code == 409


def test_transition_requires_authorized_role_returns_403(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("unauthorized-user")

    response = client.post(
        "/api/models/m1/v1/transition",
        json={"next_stage": "approved"},
    )

    assert response.status_code == 403


def test_reviewer_self_service_is_role_constrained(monkeypatch):
    fake = FakeVersioningAPI()
    monkeypatch.setattr(routes, "versioning_api", fake)
    client = _client_for_user("self-user", email="clisonix@pm.me")

    response = client.post(
        "/api/models/reviewers",
        json={
            "reviewer_id": "self-user",
            "reviewer_name": "Custom",
            "allowed_roles": ["compliance_owner"],
            "status": "suspended",
            "license_id": "LIC-1",
            "specialization_tags": ["health"],
            "metadata": {"x": 1},
        },
    )

    assert response.status_code == 200
    assert fake.last_upsert_payload is not None
    assert fake.last_upsert_payload["allowed_roles"] == ["model_owner"]
    assert fake.last_upsert_payload["status"] == "active"
    assert fake.last_upsert_payload["license_id"] is None


def test_get_other_reviewer_forbidden_for_non_privileged(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("plain-user")

    response = client.get("/api/models/reviewers/compliance-user")

    assert response.status_code == 403


def test_get_other_reviewer_allowed_for_privileged(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("compliance-user")

    response = client.get("/api/models/reviewers/target-user")

    assert response.status_code == 200
    assert response.json()["reviewer"]["reviewer_id"] == "target-user"


def test_approval_success_includes_authenticated_reviewer_identity(monkeypatch):
    fake = FakeVersioningAPI()
    monkeypatch.setattr(routes, "versioning_api", fake)
    client = _client_for_user("user-123", email="clisonix@pm.me")

    response = client.post(
        "/api/models/m1/v1/approvals",
        json={
            "reviewer_id": "user-123",
            "reviewer_role": "risk_owner",
            "approved": True,
            "notes": "approved",
        },
    )

    assert response.status_code == 200
    assert fake.last_approval_payload is not None
    assert fake.last_approval_payload["reviewer_id"] == "user-123"
    assert fake.last_approval_payload["reviewer_user_id"] == "user-123"


def test_transition_authorized_passes_actor_metadata(monkeypatch):
    fake = FakeVersioningAPI()
    monkeypatch.setattr(routes, "versioning_api", fake)
    client = _client_for_user("allowed-user")

    response = client.post(
        "/api/models/m1/v1/transition",
        json={"next_stage": "approved"},
    )

    assert response.status_code == 200
    assert fake.last_transition_payload is not None
    assert fake.last_transition_payload["actor_id"] == "allowed-user"
    assert fake.last_transition_payload["actor_role"] == "authenticated_user"


def test_update_evidence_uses_authenticated_actor(monkeypatch):
    fake = FakeVersioningAPI()
    monkeypatch.setattr(routes, "versioning_api", fake)
    client = _client_for_user("evidence-user")

    response = client.patch(
        "/api/models/m1/v1/evidence",
        json={
            "validation_report": "artifact://validation-v1",
            "actor_id": "spoofed",
            "actor_role": "spoofed_role",
        },
    )

    assert response.status_code == 200
    assert fake.last_evidence_payload is not None
    assert fake.last_evidence_payload["actor_id"] == "evidence-user"
    assert fake.last_evidence_payload["actor_role"] == "authenticated_user"
    assert "actor_id" not in fake.last_evidence_payload["evidence_updates"]
    assert "actor_role" not in fake.last_evidence_payload["evidence_updates"]


def test_get_reviewer_returns_404_when_profile_missing(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("compliance-user")

    response = client.get("/api/models/reviewers/missing")

    assert response.status_code == 404


def test_get_governance_success(monkeypatch):
    fake = FakeVersioningAPI()
    monkeypatch.setattr(routes, "versioning_api", fake)
    client = _client_for_user("any-user")

    response = client.get("/api/models/m1/v1/governance")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert fake.last_governance_lookup == {"model_id": "m1", "version": "v1"}


def test_get_governance_not_found_returns_404(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("any-user")

    response = client.get("/api/models/missing/v1/governance")

    assert response.status_code == 404


def test_get_gate_status_success(monkeypatch):
    fake = FakeVersioningAPI()
    monkeypatch.setattr(routes, "versioning_api", fake)
    client = _client_for_user("any-user")

    response = client.get("/api/models/m1/v1/gate-status", params={"next_stage": "approved"})

    assert response.status_code == 200
    assert response.json()["next_stage"] == "approved"
    assert fake.last_gate_lookup == {
        "model_id": "m1",
        "version": "v1",
        "next_stage": "approved",
    }


def test_get_gate_status_invalid_stage_returns_400(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("any-user")

    response = client.get("/api/models/m1/v1/gate-status", params={"next_stage": "not-a-stage"})

    assert response.status_code == 400


def test_get_gate_status_not_found_returns_404(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("any-user")

    response = client.get("/api/models/missing/v1/gate-status", params={"next_stage": "approved"})

    assert response.status_code == 404


def test_transition_invalid_stage_returns_400(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("allowed-user")

    response = client.post(
        "/api/models/m1/v1/transition",
        json={"next_stage": "invalid-stage"},
    )

    assert response.status_code == 400


def test_transition_not_found_returns_404(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("allowed-user")

    response = client.post(
        "/api/models/missing/v1/transition",
        json={"next_stage": "approved"},
    )

    assert response.status_code == 404


def test_approval_not_found_returns_404(monkeypatch):
    monkeypatch.setattr(routes, "versioning_api", FakeVersioningAPI())
    client = _client_for_user("user-1")

    response = client.post(
        "/api/models/missing/v1/approvals",
        json={
            "reviewer_id": "user-1",
            "reviewer_role": "risk_owner",
            "approved": True,
            "notes": "ok",
        },
    )

    assert response.status_code == 404


def test_reviewer_self_service_preserves_safe_profile_fields(monkeypatch):
    fake = FakeVersioningAPI()
    monkeypatch.setattr(routes, "versioning_api", fake)
    client = _client_for_user("self-user", email="clisonix@pm.me")

    response = client.post(
        "/api/models/reviewers",
        json={
            "reviewer_id": "self-user",
            "reviewer_name": "Will Be Overridden",
            "allowed_roles": ["compliance_owner"],
            "status": "suspended",
            "license_id": "LIC-2",
            "organization": "Clisonix Labs",
            "metadata": {"team": "governance", "timezone": "CET"},
        },
    )

    assert response.status_code == 200
    assert fake.last_upsert_payload is not None
    assert fake.last_upsert_payload["organization"] == "Clisonix Labs"
    assert fake.last_upsert_payload["metadata"] == {"team": "governance", "timezone": "CET"}
    assert fake.last_upsert_payload["allowed_roles"] == ["model_owner"]
    assert fake.last_upsert_payload["status"] == "active"
    assert fake.last_upsert_payload["license_id"] is None

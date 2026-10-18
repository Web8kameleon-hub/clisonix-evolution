import pytest

from clx_hybrid_service import _build_nodedb_headers, _build_osclx_telemetry


def test_osclx_telemetry_matches_canonical_shape() -> None:
    payload = _build_osclx_telemetry(
        route_name="hybrid_route",
        stigma_profile="balanced",
        tide_route="hybrid_technology",
        resonance_score=0.82,
        stigma_level=2,
    )

    assert payload["fabric_id"] == "clx-fabric"
    assert payload["role"] == "bridge"
    assert payload["pressure"] == pytest.approx(0.18)
    assert payload["resonance"] == 0.82
    assert payload["preferred_task_types"] == ["hybrid_route"]
    assert payload["burst_allowed"] is True


def test_osclx_telemetry_clamps_resonance() -> None:
    payload = _build_osclx_telemetry(
        route_name="new_route",
        stigma_profile="lightning",
        tide_route="new_technology",
        resonance_score=4.0,
        stigma_level=3,
    )

    assert payload["pressure"] == 0.0
    assert payload["resonance"] == 1.0
    assert payload["health_score"] == 1.0
    assert payload["burst_allowed"] is False


def test_osclx_write_uses_operator_role(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NODEDB_FLUID_API_KEY", raising=False)
    monkeypatch.delenv("NODEDB_FLUID_HMAC_SECRET", raising=False)
    headers = _build_nodedb_headers(
        url="https://aiagi.io/v1/ndb/nodes/clisonix-hybrid/telemetry",
        request_id="clxhy_contract",
        content_type="application/json",
    )

    assert headers["X-CLX-Role"] == "operator"
    assert headers["X-CLX-Request-Id"] == "clxhy_contract"
    assert "X-API-Key" not in headers
    assert "X-CLX-Signature" not in headers

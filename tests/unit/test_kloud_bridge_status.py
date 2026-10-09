import asyncio
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KLOUD_BRIDGE_MAIN = ROOT / "services" / "kloud_bridge" / "main.py"
SPEC = importlib.util.spec_from_file_location("kloud_bridge_main", KLOUD_BRIDGE_MAIN)
assert SPEC and SPEC.loader
kloud_bridge_main = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kloud_bridge_main)


def test_normalize_candidate_urls_includes_gateway_aliases(monkeypatch):
    monkeypatch.setattr(kloud_bridge_main, "KLOUD_UPSTREAM_URL", "http://fabric-primary:9080")
    monkeypatch.setattr(
        kloud_bridge_main,
        "KLOUD_UPSTREAM_CANDIDATES_RAW",
        "http://fabric-secondary:9080,http://host.docker.internal:9080",
    )

    urls = kloud_bridge_main._normalize_candidate_urls()

    assert urls[0] == "http://fabric-primary:9080"
    assert "http://fabric-secondary:9080" in urls
    assert "http://kloud-upstream-runtime:9080" in urls
    assert "https://aiagi.io" in urls
    assert "http://host.docker.internal:9080" in urls
    assert "http://host.containers.internal:9080" in urls
    assert "http://gateway.docker.internal:9080" in urls
    assert "http://172.17.0.1:9080" in urls
    assert "http://172.18.0.1:9080" in urls
    assert len(urls) == len(set(urls))


def test_normalize_candidate_urls_excludes_self_referential_targets(monkeypatch):
    monkeypatch.setattr(kloud_bridge_main, "PORT", 8889)
    monkeypatch.setattr(kloud_bridge_main, "KLOUD_UPSTREAM_URL", "http://clisonix-kloud-bridge:8889")
    monkeypatch.setattr(
        kloud_bridge_main,
        "KLOUD_UPSTREAM_CANDIDATES_RAW",
        "http://kloud-bridge:8889,http://localhost:8889,http://127.0.0.1:8889,http://kloud-upstream-runtime:9080",
    )

    urls = kloud_bridge_main._normalize_candidate_urls()

    assert "http://clisonix-kloud-bridge:8889" not in urls
    assert "http://kloud-bridge:8889" not in urls
    assert "http://localhost:8889" not in urls
    assert "http://127.0.0.1:8889" not in urls
    assert "http://kloud-upstream-runtime:9080" in urls


def test_status_distinguishes_sovereign_upstream_from_ocean(monkeypatch):
    async def fake_upstream():
        return {
            "configured": True,
            "reachable": False,
            "url": "http://fabric-primary:9080",
            "message": "No live Kloud upstream responded.",
        }

    async def fake_ocean():
        return {
            "configured": True,
            "reachable": True,
            "url": "http://clisonix-ocean-core:8030",
            "status": {"service": "ocean-core", "status": "ok"},
        }

    def fake_summary(upstream, ocean):
        return {
            "bridge": "live",
            "upstream_status": "configured",
            "ocean_status": "live",
            "upstream_target": upstream.get("url"),
            "ocean_target": ocean.get("url"),
            "peer_count": 0,
            "hardware_nodes": {"registered_nodes": 1, "online_nodes": 1},
            "service_truth": {
                "state": "monitoring",
                "connectivity": "limited",
                "sync_status": "waiting",
                "live_flow": "Bridge → Ocean visible → Sovereign upstream pending",
            },
            "state": "monitoring",
            "connectivity": "limited",
            "sync_status": "waiting",
            "confidence": "verified",
            "last_successful_sync": None,
            "estimated_recovery": "Point KLOUD_UPSTREAM_URL to the sovereign fabric.",
        }

    monkeypatch.setattr(kloud_bridge_main, "_probe_upstream", fake_upstream)
    monkeypatch.setattr(kloud_bridge_main, "_probe_ocean", fake_ocean)
    monkeypatch.setattr(kloud_bridge_main, "_build_bridge_summary", fake_summary)
    monkeypatch.setattr(kloud_bridge_main, "_security_summary", lambda: {})
    monkeypatch.setattr(kloud_bridge_main, "_audit_summary", lambda: {})
    monkeypatch.setattr(kloud_bridge_main, "_openapi_summary", lambda: {})

    payload = asyncio.run(kloud_bridge_main.status())

    assert payload["upstream"]["url"] == "http://fabric-primary:9080"
    assert payload["upstream"]["reachable"] is False
    assert payload["ocean_core"]["url"] == "http://clisonix-ocean-core:8030"
    assert payload["ocean_core"]["reachable"] is True
    assert payload["summary"]["upstream_target"] == "http://fabric-primary:9080"
    assert payload["summary"]["ocean_target"] == "http://clisonix-ocean-core:8030"


def test_status_exposes_user_facing_partial_outage(monkeypatch):
    async def fake_upstream():
        return {
            "configured": True,
            "reachable": False,
            "url": "http://fabric-primary:9080",
            "message": "No live Kloud upstream responded.",
        }

    async def fake_ocean():
        return {
            "configured": True,
            "reachable": True,
            "url": "http://clisonix-ocean-core:8030",
            "status": {"service": "ocean-core", "status": "ok"},
        }

    monkeypatch.setattr(kloud_bridge_main, "_probe_upstream", fake_upstream)
    monkeypatch.setattr(kloud_bridge_main, "_probe_ocean", fake_ocean)

    payload = asyncio.run(kloud_bridge_main.status())

    assert payload["user_facing_status"]["state"] == "partial-outage"
    assert payload["user_facing_status"]["severity"] == "warning"


def test_failure_modes_reports_fail_closed_blocked_when_dependency_down(monkeypatch):
    async def fake_upstream():
        return {
            "configured": True,
            "reachable": False,
            "url": "http://fabric-primary:9080",
        }

    async def fake_ocean():
        return {
            "configured": True,
            "reachable": True,
            "url": "http://clisonix-ocean-core:8030",
        }

    monkeypatch.setattr(kloud_bridge_main, "_probe_upstream", fake_upstream)
    monkeypatch.setattr(kloud_bridge_main, "_probe_ocean", fake_ocean)

    payload = asyncio.run(kloud_bridge_main.failure_modes())
    matrix = {entry["endpoint"]: entry for entry in payload["matrix"]}

    assert matrix["POST /signals/publish"]["mode"] == "fail-closed"
    assert matrix["POST /signals/publish"]["blocked"] is True
    assert matrix["GET /status"]["mode"] == "fail-open"
    assert matrix["GET /status"]["blocked"] is False

import importlib.util
import json
from pathlib import Path
import sys

import pytest

PATH = Path(__file__).resolve().parents[2] / "scripts/hetzner/deploy_changed_services.py"
spec = importlib.util.spec_from_file_location("scoped_deploy", PATH)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def test_snapshot_preserves_runtime_secrets_data_ports_and_networks():
    old = {
        "Id": "abc123", "Name": "/clisonix-web",
        "Config": {"Env": ["AUTH_SECRET=fixture-only"], "Cmd": ["npm", "start"],
                   "Labels": {"com.docker.compose.project": "old", "owner": "team"},
                   "Healthcheck": {"Test": ["CMD", "curl", "-f", "http://localhost:3000"],
                                   "Interval": 30000000000, "Retries": 3}},
        "HostConfig": {"RestartPolicy": {"Name": "unless-stopped"},
                       "PortBindings": {"3000/tcp": [{"HostIp": "127.0.0.1", "HostPort": "3003"}]}},
        "NetworkSettings": {"Networks": {"clisonix-net": {"Aliases": ["web", "abc123"]}}},
        "Mounts": [{"Type": "volume", "Name": "existing-data", "Source": "/var/lib/docker/volumes/existing-data/_data",
                    "Destination": "/app/data", "RW": True},
                   {"Type": "bind", "Source": "/opt/config", "Destination": "/app/config", "RW": False}],
    }
    networks, volumes = {}, {}
    result = deploy.runtime_service(old, "candidate:sha", networks, volumes)
    assert result["environment"] == ["AUTH_SECRET=fixture-only"]
    assert volumes == {"existing-data": "vol_0"}
    assert result["volumes"][0]["source"] == "vol_0"
    assert result["volumes"][1]["read_only"] is True
    assert result["volumes"][1]["bind"]["create_host_path"] is False
    assert result["ports"][0]["published"] == "3003"
    assert result["ports"][0]["host_ip"] == "127.0.0.1"
    assert result["networks"] == {"net_0": {"aliases": ["web"]}}
    assert result["labels"] == {"owner": "team"}
    assert result["healthcheck"]["interval"] == "30000000000ns"


def test_apply_refuses_container_changed_since_prepare(tmp_path, monkeypatch):
    state = tmp_path / ".runtime"
    state.mkdir()
    (state / "containers.json").write_text(json.dumps({"web": {"Id": "before"}}))
    monkeypatch.setattr(sys, "argv", [str(PATH), "apply", "--release", str(tmp_path), "--services", "web"])
    monkeypatch.setattr(deploy, "inspect", lambda _: {"Id": "after"})
    monkeypatch.setattr(deploy, "run", lambda *_a, **_k: pytest.fail("Must not restart changed container"))
    with pytest.raises(RuntimeError, match="changed since prepare"):
        deploy.main()


def test_source_mapping_excludes_tests_and_unrelated_services():
    changed = ["ocean-core/ocean_core_full.py", "ocean-core/tests/test_chat.py",
               "apps/api/unified_status_layer.py", "shopping_therapy_core.py"]
    assert deploy.source_files("api", changed) == ["apps/api/unified_status_layer.py"]
    assert deploy.source_files("ocean-core", changed) == ["ocean-core/ocean_core_full.py"]


def test_failed_health_rolls_back_only_attempted_services(tmp_path, monkeypatch):
    state = tmp_path / ".runtime"
    state.mkdir()
    (state / "containers.json").write_text(json.dumps({"web": {"Id": "web-before"},
                                                      "ocean-core": {"Id": "ocean-before"}}))
    monkeypatch.setattr(sys, "argv", [str(PATH), "apply", "--release", str(tmp_path),
                                     "--services", "web,ocean-core"])
    responses = iter([{"Id": "web-before"}, {"Id": "ocean-before"},
                      {"State": {"Running": True, "Health": {"Status": "unhealthy"}}}])
    monkeypatch.setattr(deploy, "inspect", lambda _: next(responses))
    commands = []
    monkeypatch.setattr(deploy, "run", lambda command: commands.append(command))
    with pytest.raises(RuntimeError, match="failed health"):
        deploy.main()
    assert len(commands) == 2
    assert all("--no-deps" in command for command in commands)
    assert commands[0][-1] == commands[1][-1] == "web"
    assert str(state / "rollback.json") in commands[1]

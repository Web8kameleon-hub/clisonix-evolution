"""Real filesystem/process/Git evidence in temporary workspaces; no tool mocks."""
import asyncio
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def mission(tmp_path_factory):
    runtime = tmp_path_factory.mktemp("mission-runtime")
    with pytest.MonkeyPatch.context() as env:
        env.setenv("MISSION_DB_PATH", str(runtime / "missions.db"))
        env.setenv("SANDBOX_LOG_PATH", str(runtime / "sandbox.jsonl"))
        env.setenv("LIABILITY_CHAIN_PATH", str(runtime / "liability.jsonl"))
        env.setenv("OCEAN_WORKSPACE_ROOT", str(runtime))
        env.setenv("REGULATORY_ENABLED", "0")
        spec = importlib.util.spec_from_file_location("ocean_mission_tools_tests", ROOT / "ocean-core/ocean_mission_service.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        yield module
        sys.modules.pop(spec.name, None)


@pytest.fixture
def registry(mission, tmp_path):
    return mission.ToolRegistry(tmp_path)


def call(registry, name, **params):
    return asyncio.run(registry.execute(name, params))


def script(root, name, content):
    path = root / name
    path.write_bytes(content.encode("utf-8"))
    return path


def test_workspace_read_and_list_are_real(registry, tmp_path):
    script(tmp_path, "content.txt", "Hello real workspace\n")
    result = call(registry, "workspace_read", path="content.txt")
    assert result["ok"] is True and result["content"] == "Hello real workspace\n"
    assert result["size"] == 21 and len(result["sha256"]) == 64
    listing = call(registry, "workspace_list")
    assert listing["ok"] and listing["entries"][0]["path"] == str(tmp_path / "content.txt")


@pytest.mark.parametrize("tool", ["workspace_read", "workspace_write", "workspace_patch", "workspace_list", "workspace_search", "file_exists", "python_script"])
@pytest.mark.parametrize("absolute", [False, True])
def test_all_file_tools_reject_outside_paths(registry, tmp_path, tool, absolute):
    outside = script(tmp_path.parent, "outside.py", "print('outside')")
    path = str(outside) if absolute else "../outside.py"
    result = call(registry, tool, path=path, script=path, content="changed", old="outside", new="changed", query="outside")
    assert result["ok"] is False and "escapes" in result["error"]
    assert outside.read_text() == "print('outside')"


@pytest.mark.parametrize("path", [".git/config", ".env", "config/.env.production", "secrets/token.txt", "id_rsa", "private.pem", ".secrets.baseline", "secrets.yaml", "credentials.json", ".npmrc"])
def test_secret_and_git_metadata_access_denied(registry, path):
    result = call(registry, "workspace_write", path=path, content="blocked")
    assert result["ok"] is False and "denied" in result["error"]


def test_symlink_escape_and_secret_alias_denied(registry, tmp_path):
    outside = script(tmp_path.parent, "external.txt", "untouched")
    secret = script(tmp_path, ".env", "private")
    try:
        (tmp_path / "escape").symlink_to(outside)
        (tmp_path / "alias").symlink_to(secret)
    except OSError as exc:
        pytest.skip(f"Symlinks not supported for this account: {exc}")
    for name in ("escape", "alias"):
        assert call(registry, "workspace_read", path=name)["ok"] is False
        assert call(registry, "workspace_write", path=name, content="wrong", overwrite=True)["ok"] is False
    assert outside.read_text() == "untouched" and secret.read_text() == "private"


def test_search_real_matches_and_secret_exclusion(registry, tmp_path):
    script(tmp_path, "real.txt", "first\nneedle actual\n")
    script(tmp_path, ".env", "needle confidential\n")
    result = call(registry, "workspace_search", query="needle")
    assert result["ok"] is True
    assert result["matches"] == [{"path": str(tmp_path / "real.txt"), "line": 2, "content": "needle actual"}]
    assert any(row["path"].endswith(".env") for row in result["excluded"])


def test_search_and_read_report_real_errors(registry, tmp_path):
    (tmp_path / "broken.txt").write_bytes(b"\xff invalid utf8")
    assert call(registry, "workspace_read", path="broken.txt")["ok"] is False
    result = call(registry, "workspace_search", query="invalid")
    assert result["ok"] is False and result["errors"]
    assert call(registry, "workspace_search", path="missing.txt", query="missing")["ok"] is False


def test_write_only_requested_file_and_require_explicit_overwrite(registry, tmp_path):
    untouched = script(tmp_path, "untouched.txt", "retain")
    result = call(registry, "workspace_write", path="new.txt", content="created")
    assert result["ok"] and result["action"] == "created"
    assert call(registry, "workspace_write", path="new.txt", content="wrong")["ok"] is False
    result = call(registry, "workspace_write", path="new.txt", content="modified", overwrite=True)
    assert result["ok"] and result["action"] == "modified"
    assert (tmp_path / "new.txt").read_text() == "modified" and untouched.read_text() == "retain"
    assert not list(tmp_path.glob(".ocean-write-*"))


def test_patch_exact_context_and_failed_context_leave_file_untouched(registry, tmp_path):
    target = script(tmp_path, "patch.txt", "before\n")
    result = call(registry, "workspace_patch", path="patch.txt", old="before", new="after")
    assert result["ok"] and result["replacements"] == 1 and target.read_text() == "after\n"
    result = call(registry, "workspace_patch", path="patch.txt", old="before", new="wrong")
    assert result["ok"] is False and result["actual_matches"] == 0 and target.read_text() == "after\n"
    target.write_text("twice twice")
    assert call(registry, "workspace_patch", path="patch.txt", old="twice", new="once")["ok"] is False
    assert target.read_text() == "twice twice"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, "init")
    git(tmp_path, "config", "user.name", "Temporary test repository")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    script(tmp_path, "tracked.txt", "original\n")
    script(tmp_path, ".env", "initial-private-value")
    git(tmp_path, "add", "tracked.txt", ".env")
    git(tmp_path, "commit", "-m", "Temporary initial record")
    (tmp_path / "tracked.txt").write_text("actual changed content\n")
    (tmp_path / ".env").write_text("different-private-value")
    return tmp_path


def test_git_status_diff_log_real_read_only_evidence(mission, repository):
    tools = mission.ToolRegistry(repository)
    before = git(repository, "rev-parse", "HEAD")
    status = call(tools, "git_status")
    diff = call(tools, "git_diff")
    log = call(tools, "git_log", limit=1)
    assert status["ok"] and " M tracked.txt" in status["stdout"]
    assert diff["ok"] and "+actual changed content" in diff["stdout"]
    assert "private-value" not in diff["stdout"]
    assert log["ok"] and before.strip() in log["stdout"]
    for result in (status, diff, log):
        assert result["returncode"] == 0 and result["command"] and result["cwd"] == str(repository)
        assert "stderr" in result
    assert git(repository, "rev-parse", "HEAD") == before
    assert call(tools, "git_diff", paths=[".env"])["ok"] is False


def test_git_rejects_parent_repository_outside_workspace(mission, repository):
    child = repository / "child"
    child.mkdir()
    assert call(mission.ToolRegistry(child), "git_status")["ok"] is False


def test_allowed_command_and_existing_python_script_real_exit_status(registry, tmp_path):
    script(tmp_path, "run.py", "from pathlib import Path\nprint(Path.cwd())\n")
    result = call(registry, "command_run", command=["python", "run.py"])
    assert result["ok"] and result["returncode"] == 0 and str(tmp_path) in result["stdout"]
    assert result["command"] == [sys.executable, str(tmp_path / "run.py")]
    legacy = call(registry, "python_script", script="run.py")
    assert legacy["ok"] and legacy["cwd"] == str(tmp_path)
    script(tmp_path, "fail.py", "import sys\nprint('actual failure')\nsys.exit(7)\n")
    failed = call(registry, "command_run", command=["python", "fail.py"])
    assert failed["ok"] is False and failed["returncode"] == 7 and "actual failure" in failed["stdout"]


def test_timeout_reports_failure(registry, tmp_path):
    script(tmp_path, "slow.py", "import time\ntime.sleep(5)\n")
    result = call(registry, "command_run", command=["python", "slow.py"], timeout=0.1)
    assert result["ok"] is False and result["timed_out"] is True and result["returncode"] is None
    assert result["timeout"] == 0.1


@pytest.mark.parametrize("command", [["git", "reset", "--hard"], ["git", "push"], ["sh", "-c", "true"],
    ["powershell", "-Command", "Remove-Item"], ["python", "-c", "print('inline')"],
    ["python", "-m", "os"], ["python", "../outside.py"], ["python", "run.py", "--output=../../escape"],
    ["python", "run.py", ".env"], ["python", "run.py", "reset"], ["python", "run.py", "x; git clean"],
    ["python", "-m", "pytest", "-p", "outside_plugin"], ["python", "-m", "pytest", "../outside.py"]])
def test_disallowed_commands_fail_before_execution(registry, tmp_path, command):
    marker = tmp_path / "executed.txt"
    script(tmp_path, "run.py", "from pathlib import Path\nPath('executed.txt').write_text('executed')\n")
    result = call(registry, "command_run", command=command)
    assert result["ok"] is False and not marker.exists()


def test_outside_command_cwd_rejected(registry):
    assert call(registry, "command_run", command=["python", "--version"], cwd="..")["ok"] is False


def test_test_run_exposes_actual_pytest_pass_and_failure(registry, tmp_path):
    script(tmp_path, "test_pass.py", "def test_pass():\n    assert 2 + 2 == 4\n")
    script(tmp_path, "test_fail.py", "def test_fail():\n    assert 2 + 2 == 5\n")
    passed = call(registry, "test_run", command=["python", "-m", "pytest", "test_pass.py", "-q"])
    failed = call(registry, "test_run", command=["python", "-m", "pytest", "test_fail.py", "-q"])
    assert passed["ok"] and passed["returncode"] == 0 and "1 passed" in passed["stdout"]
    assert failed["ok"] is False and failed["returncode"] == 1 and "1 failed" in failed["stdout"]
    assert call(registry, "test_run", command=["python", "--version"])["ok"] is False


def test_unknown_tool_remains_rejected(registry):
    with pytest.raises(ValueError, match="Unknown tool"):
        call(registry, "not_registered")


def test_existing_file_exists_and_sleep_remain_real(registry, tmp_path):
    script(tmp_path, "exists.txt", "real")
    assert call(registry, "file_exists", path="exists.txt")["exists"] is True
    assert call(registry, "file_exists", path="absent.txt")["ok"] is False
    started = time.monotonic()
    assert call(registry, "sleep", seconds=0.01)["ok"] is True
    assert time.monotonic() - started >= 0.01
    assert call(registry, "sleep", seconds=-1)["ok"] is False


@pytest.mark.parametrize("timeout", [True, -1, float("nan"), float("inf"), 181])
def test_invalid_execution_timeout_is_rejected(registry, timeout):
    result = call(registry, "command_run", command=["python", "--version"], timeout=timeout)
    assert result["ok"] is False and "Timeout" in result["error"]


def test_mission_persists_real_tool_failure_and_retries(mission, registry, tmp_path):
    store = mission.MissionStore(tmp_path / "missions.db")
    engine = mission.MissionEngine(store, registry)
    request = mission.MissionRequest(query="read missing file", max_retries=1, steps=[
        mission.MissionStepSpec(name="read", tool="workspace_read", params={"path": "missing.txt"})])
    async def execute():
        state = await engine.submit(request)
        await engine.execute_mission(state.mission_id)
        return store.get(state.mission_id)
    state = asyncio.run(execute())
    assert state.status == "failed" and state.steps[0].status == "failed"
    assert state.steps[0].output["ok"] is False and state.steps[0].retries == 1


def test_mission_rejects_missing_success_field_from_actual_file_stat(mission, registry, tmp_path):
    path = script(tmp_path, "observed.txt", "actual content")
    # A real extension performing stat, deliberately lacking the success contract.
    def incomplete_stat(params):
        return {"size": path.stat().st_size}
    registry._tools["incomplete_stat"] = incomplete_stat
    store = mission.MissionStore(tmp_path / "missions.db")
    engine = mission.MissionEngine(store, registry)
    request = mission.MissionRequest(query="stat", max_retries=0, steps=[
        mission.MissionStepSpec(name="stat", tool="incomplete_stat")])
    async def execute():
        state = await engine.submit(request)
        await engine.execute_mission(state.mission_id)
        return store.get(state.mission_id)
    result = asyncio.run(execute())
    assert result.steps[0].output == {"size": len("actual content")}
    assert result.status == "failed"


def test_implicit_planner_never_claims_work_completed(mission, registry, tmp_path):
    engine = mission.MissionEngine(mission.MissionStore(tmp_path / "missions.db"), registry)
    with pytest.raises(mission.HTTPException) as exc:
        engine.build_steps(mission.MissionRequest(query="write code and publish"))
    assert exc.value.status_code == 422 and "request.steps" in exc.value.detail


def test_existing_api_calls_explicit_tool_steps(mission):
    target = mission.tools.workspace_root / "api-proof.txt"
    target.write_text("actual API content", encoding="utf-8")
    with TestClient(mission.app) as client:
        assert "workspace_read" in client.get("/missions/tools").json()["tools"]
        response = client.post("/missions/submit", json={"query": "read", "max_retries": 0,
            "steps": [{"name": "read", "tool": "workspace_read", "params": {"path": "api-proof.txt"}}]})
        assert response.status_code == 200
        mission_id = response.json()["mission_id"]
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            state = client.get(f"/missions/{mission_id}").json()
            if state["status"] in {"completed", "failed"}:
                break
            time.sleep(0.02)
        assert state["status"] == "completed" and state["steps"][0]["output"]["content"] == "actual API content"
        rejected = client.post("/missions/submit", json={"query": "write everything"})
        assert rejected.status_code == 422

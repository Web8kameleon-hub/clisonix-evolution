import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_evaluator():
    path = ROOT / "scripts" / "mali_module_evaluator.py"
    spec = importlib.util.spec_from_file_location("mali_module_evaluator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_control_plane():
    path = ROOT / "services" / "intelligence-lab" / "control_plane.py"
    spec = importlib.util.spec_from_file_location("mali_control_plane", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_project_map_is_generated_only_from_evaluation_evidence():
    evidence = json.loads((ROOT / "artifacts/mali/module-evaluation.json").read_text())
    project_map = json.loads(
        (ROOT / "services/intelligence-lab/generated/project-map.v1.json").read_text()
    )
    assert project_map["generated_from"] == evidence["spec_version"]
    assert project_map["generated_at"] == evidence["generated_at"]
    assert project_map["modules"] == evidence["modules"]
    assert project_map["central_orchestrator"] == "intelligence-lab"
    assert evidence["module_count"] == len(evidence["modules"])


def test_every_compose_module_has_evidence_and_honest_grade():
    evaluator = load_evaluator()
    compose = evaluator.load_compose(ROOT / "docker-compose.yml")
    evidence = json.loads((ROOT / "artifacts/mali/module-evaluation.json").read_text())
    assert set(evidence["modules"]) == set(compose["services"])
    for result in evidence["modules"].values():
        assert result["grade"] in {"A", "B", "F", "UNVERIFIED"}
        if not result["runtime"]["tested"]:
            assert result["grade"] == "UNVERIFIED"


def test_mali_rejects_unknown_sources_and_targets(tmp_path):
    control = load_control_plane()
    source_map = ROOT / "services/intelligence-lab/generated/project-map.v1.json"
    plane = control.MaliControlPlane(source_map)
    envelope = control.SignalEnvelope(type="test.signal", source_module="does-not-exist", payload={})

    class RedisRecorder:
        async def xadd(self, *_args, **_kwargs):
            pytest.fail("invalid envelope must not reach Redis")

    plane.redis = RedisRecorder()
    with pytest.raises(ValueError, match="unknown source module"):
        import asyncio
        asyncio.run(plane.publish(envelope))


def test_ocean_runtime_profile_preserves_gpu_unlimited_and_stigmafilm():
    project_map = json.loads(
        (ROOT / "services/intelligence-lab/generated/project-map.v1.json").read_text()
    )
    ocean = project_map["modules"]["ocean-core"]
    # Runtime truth is graded separately; these invariants must remain visible in Compose.
    compose_text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "NVIDIA_VISIBLE_DEVICES" in compose_text or "gpus: all" in compose_text
    assert 'OCEAN_STREAM_FIRST_TOKEN_TIMEOUT_S: "0"' in compose_text
    assert 'CHAT_MAX_TOKENS_HARD: "0"' in compose_text
    assert 'OCEAN_STIGMAFILM_ENABLED: "true"' in compose_text
    assert ocean["grade"] in {"A", "B", "F", "UNVERIFIED"}


def test_canonical_gram_engine_grows_searches_and_handles_edges():
    from packages.gram.core import GRAMEngine

    engine = GRAMEngine({"auto_grow": True, "max_nodes": 100})
    first = engine.add_node("musica cervello ritmo", language="it", tags=["music"])
    engine.add_node("ritmo e memoria uditiva", language="it", tags=["music"])
    assert engine.get_node(first.id) is first
    assert engine.search("musica ritmo", language="it")
    assert engine.search("", min_score=1.0) == []
    assert engine.delete_node("missing-node") is False

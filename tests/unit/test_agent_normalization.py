from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_agents_module():
    module_path = ROOT / "agents.py"
    spec = importlib.util.spec_from_file_location("clisonix_agents_file", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_top_level_registry_normalizes_unicode_agent_name() -> None:
    agents_module = _load_agents_module()
    registry = agents_module.AgentRegistry()
    registry.register(agents_module.ALBAAgent)
    assert registry.get_pool("ＡＬＢＡ") is not None
    assert registry.get_pool("al-ba") is not None


def test_top_level_orchestrator_normalizes_scale_lookup() -> None:
    agents_module = _load_agents_module()
    orchestrator = agents_module.AgentOrchestrator(auto_register_core=False)
    orchestrator.register(agents_module.ALBAAgent)
    pool = orchestrator._registry.get_pool("álbà")
    assert pool is not None


def test_package_create_core_agent_normalizes_fullwidth_name() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    core_module = importlib.import_module("agents.core")
    agent = core_module.create_core_agent("ＪＯＮＡ")
    assert agent.config.name == "jona"


def test_asi_core_normalizes_node_identifier() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    asi_module = importlib.import_module("asi_core")
    core = asi_module.ASICore()
    core.update_node_status("álbì", "paused")
    assert core.nodes["ALBI"]["status"] == "paused"

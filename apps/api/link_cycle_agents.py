#!/usr/bin/env python3
"""Cycle Engine - ASI Agent Linker.

Links selected agents to a cycle, executes real agent tasks for information
gathering, and transfers synthesized context to Ocean Core.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import importlib.util
import inspect
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OCEAN_CORE_URL = os.getenv("OCEAN_CORE_URL", "http://localhost:8030")

DEFAULT_AGENT_ACTIONS: Dict[str, Dict[str, Any]] = {
    "alba": {"action": "collect"},
    "albi": {"action": "analyze", "data": []},
    "jona": {"action": "synthesize", "sources": ["alba", "albi"]},
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_agent_name(name: str) -> str:
    clean = (name or "").strip().lower()
    aliases = {
        "asitrinity": "asi-trinity",
        "trinity": "asi-trinity",
        "dralba": "albana",
        "videocreator": "video-creator",
        "newspublisher": "news-publisher",
    }
    return aliases.get(clean.replace("_", "").replace("-", ""), clean)


def _resolve_agents_module():
    module_path = PROJECT_ROOT / "agents.py"
    if not module_path.exists():
        return importlib.import_module("agents")

    spec = importlib.util.spec_from_file_location("clisonix_agents_file", module_path)
    if spec is None or spec.loader is None:
        return importlib.import_module("agents")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _build_agent_payload(agent_name: str, query: str) -> Dict[str, Any]:
    normalized = _normalize_agent_name(agent_name)
    base = dict(DEFAULT_AGENT_ACTIONS.get(normalized, {"action": "analyze"}))
    base["query"] = query
    return base


async def _run_agents(agents: List[str], query: str) -> Dict[str, Any]:
    agents_module = _resolve_agents_module()
    orchestrator: Any = agents_module.AgentOrchestrator()

    init_fn = getattr(orchestrator, "initialize", None)
    submit_fn = getattr(orchestrator, "submit", None)
    shutdown_fn = getattr(orchestrator, "shutdown", None)

    if not callable(init_fn) or not callable(submit_fn) or not callable(shutdown_fn):
        return {
            "ok": False,
            "error": "agents_orchestrator_interface_mismatch",
            "outputs": [],
        }

    await _maybe_await(init_fn())
    try:
        outputs: List[Dict[str, Any]] = []
        for agent_name in agents:
            payload = _build_agent_payload(agent_name, query)
            result = await _maybe_await(submit_fn(agent_name, payload))
            outputs.append(
                {
                    "agent": _normalize_agent_name(agent_name),
                    "success": bool(result.success),
                    "error": result.error,
                    "duration_ms": result.duration_ms,
                    "result": result.result,
                }
            )
        return {"ok": True, "outputs": outputs}
    finally:
        await _maybe_await(shutdown_fn())


def _transfer_to_ocean(cycle_id: str, query: str, agent_outputs: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
    transfer_payload = {
        "message": query,
        "query": query,
        "language": language,
        "response_language": language,
        "cycle_id": cycle_id,
        "agent_context": agent_outputs,
    }
    response = requests.post(
        f"{DEFAULT_OCEAN_CORE_URL.rstrip('/')}/api/v1/query",
        json=transfer_payload,
        timeout=60,
    )
    if response.status_code >= 400:
        return {
            "ok": False,
            "status": response.status_code,
            "error": response.text,
        }
    return {"ok": True, "status": response.status_code, "data": response.json()}


def link_agents(cycle_id: str, agents: List[str], query: str, language: str = "sq") -> Dict[str, Any]:
    """Link agents to cycle, gather info, and transfer to Ocean Core."""
    started_at = _utc_now_iso()
    normalized_agents = [_normalize_agent_name(name) for name in agents]

    run_result = asyncio.run(_run_agents(normalized_agents, query))
    agent_outputs = run_result.get("outputs", [])

    successful_outputs = [item for item in agent_outputs if item.get("success")]
    if not successful_outputs:
        return {
            "cycle_id": cycle_id,
            "agents": normalized_agents,
            "timestamp": started_at,
            "status": "failed",
            "error": "no_agent_data",
            "agent_outputs": agent_outputs,
            "ocean_transfer": None,
        }

    ocean_transfer = _transfer_to_ocean(cycle_id, query, successful_outputs, language)
    status = "linked" if ocean_transfer.get("ok") else "transfer_failed"

    return {
        "cycle_id": cycle_id,
        "agents": normalized_agents,
        "timestamp": started_at,
        "status": status,
        "query": query,
        "agent_outputs": agent_outputs,
        "ocean_transfer": ocean_transfer,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Link agents to cycle and transfer findings to Ocean Core")
    parser.add_argument("cycle_id", nargs="?", default="cycle_prod_001")
    parser.add_argument("agents", nargs="*", default=["ALBA", "ALBI", "JONA"])
    parser.add_argument("--query", default="Përmblidh gjendjen aktuale të sistemit.")
    parser.add_argument("--language", default="sq")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    result = link_agents(args.cycle_id, args.agents, args.query, args.language)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("status") == "linked":
        print(f"\n✓ {len(args.agents)} agents linked to {args.cycle_id} and transferred to Ocean")
    else:
        print(f"\n✗ Agent cycle transfer failed for {args.cycle_id}")

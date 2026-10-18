"""The existing orchestrator performs bounded reads, never implicit writes."""
import asyncio
import importlib.util
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import httpx


def load_orchestrator():
    name = "existing_ocean_orchestrator_test"
    path = Path(__file__).resolve().parents[2] / "ocean-core/ocean_orchestrator.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_excel_uses_both_existing_services():
    module = load_orchestrator()
    caller = module.ServiceCaller(module.SERVICES)
    caller.call = AsyncMock(return_value={"templates": []})
    results = asyncio.run(caller.collect_context("Which Excel templates are available?"))
    assert {row["service"] for row in results} == {"excel", "excel_core"}
    assert all(call.kwargs["method"] == "GET" for call in caller.call.await_args_list)
    assert module.SERVICES["excel"].port == 8002
    assert module.SERVICES["excel_core"].port == 8010


def test_overview_keeps_failures_and_does_not_expose_raw_health_fields():
    module = load_orchestrator()
    caller = module.ServiceCaller(module.SERVICES)

    async def call(service, operation, **kwargs):
        assert kwargs["method"] == "GET"
        if service == "hybrid":
            raise httpx.ConnectError("unreachable")
        return {"status": "healthy", "private_field": "exclude", "total": 23, "analysis_ready": 1}

    caller.call = call
    results = asyncio.run(caller.collect_context("sa i avancuar eshte clisonix?"))
    by_name = {row["service"]: row for row in results}
    assert by_name["hybrid"]["status"] == "unavailable"
    assert "private_field" not in by_name["clx"]["data"]
    assert by_name["city_labs"]["data"]["analysis_ready"] == 1


def test_general_question_does_not_fan_out_to_services():
    module = load_orchestrator()
    caller = module.ServiceCaller(module.SERVICES)
    caller.call = AsyncMock()
    assert asyncio.run(caller.collect_context("Explain photosynthesis")) == []
    caller.call.assert_not_awaited()

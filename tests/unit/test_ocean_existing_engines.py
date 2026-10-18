"""Regression coverage for restoring existing Ocean engines."""
import ast
import importlib.util
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

import pytest

ROOT = Path(__file__).resolve().parents[2] / "ocean-core"


def load_function(filename, name, **namespace):
    tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
    nodes = list(tree.body)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            nodes.extend(node.body)
    function = next(node for node in nodes if isinstance(node, ast.FunctionDef) and node.name == name)
    namespace.update(Dict=Dict, Any=Any)
    exec(compile(ast.Module(body=[function], type_ignores=[]), filename, "exec"), namespace)
    return namespace[name]


def test_megalayer_preserves_computation():
    results = {"binary_transformation": 0.125, "multi_script": {"algebraic_signature": "abc"}}
    activation = SimpleNamespace(meta_level=SimpleNamespace(value=3), unique_signature="signature")
    process = load_function(
        "ocean_core_full.py", "process_with_mega_layers",
        MEGA_LAYERS_AVAILABLE=True,
        mega_engine=SimpleNamespace(process_query=lambda query: (activation, results)),
        logger=logging.getLogger(__name__),
    )
    output = process("test")
    assert output["results"] == results
    assert output["consciousness_depth"] == 3
    assert output["measurement_kind"] == "algorithmic_features_not_accuracy_benchmark"


@pytest.mark.parametrize("query,operation,result", [
    ("255 NAND 170", "NAND", 85),
    ("255 AND 170", "AND", 170),
    ("170 NOR 0", "NOR", 85),
    ("255 XOR 0", "XOR", 255),
    ("word 15 OR 0", "OR", 15),
])
def test_existing_binary_operator_dispatch(query, operation, result):
    process = load_function("layer_algebra_integration.py", "process_binary_operation")
    instance = SimpleNamespace(
        _number_to_layers=lambda number: [],
        _calculate_layer_transform=lambda *args: {},
        _format_binary_response=lambda *args: "computed",
    )
    output = process(instance, query, {}, {})
    assert output["operation"] == operation
    assert output["result"] == result
    if output["b"] == 0:
        assert output["binary_b"] == "0b0"


def test_existing_knowledge_router_can_parse_and_route():
    spec = importlib.util.spec_from_file_location("ocean_knowledge_router_test", ROOT / "knowledge_router.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    router = module.KnowledgeRouter()
    parsed = router.parse_query("compare statistics Albania Germany")
    assert parsed.intent_type == module.QueryIntentType.COMPARE
    assert parsed.to_dict()["intent_type"] == "compare"
    assert router.route("compare statistics Albania Germany").strategy == "parallel"
    assert "alba" in router.route("real-time sensor stream").modules

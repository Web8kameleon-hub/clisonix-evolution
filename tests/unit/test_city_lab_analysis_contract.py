import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.lab.main import extract_result, manifest, normalize_request


def test_manifest_exposes_analysis_contract_and_trace_provider():
    payload = manifest()
    assert payload["runtime"]["analysis_contract"] == "clisonix.city-lab.analysis/v1"
    assert payload["runtime"]["trace_provider"] == "signal_fabric"
    assert payload["ui"]["shell"] == "kameleon"


def test_normalize_request_preserves_trace_and_injects_lab_context():
    trace_id = "trace-test-123"
    payload = normalize_request({"goal": "Inspect the current lab state", "context": {"source": "test"}}, trace_id)
    assert payload["trace_id"] == trace_id
    assert payload["message"] == "Inspect the current lab state"
    assert payload["query"] == payload["message"]
    assert payload["context"]["operating_environment"]["trace_id"] == trace_id
    assert payload["context"]["city_lab"]["lab_id"]
    assert payload["context"]["caller"]["source"] == "test"


def test_extract_result_prefers_known_ocean_response_fields():
    assert extract_result({"ocean_response": "ocean"}) == "ocean"
    assert extract_result({"response": "response"}) == "response"
    assert extract_result({"answer": "answer"}) == "answer"
    assert extract_result({"result": {"ok": True}}) == {"ok": True}

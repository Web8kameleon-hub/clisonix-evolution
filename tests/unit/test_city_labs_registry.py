import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config" / "city-labs.registry.json"


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_schema_and_count():
    payload = load_registry()
    assert payload["schema"] == "clisonix.city-labs.registry/v1"
    assert payload["internal_port"] == 9100
    assert len(payload["labs"]) == 23


def test_registry_ids_and_services_are_unique():
    labs = load_registry()["labs"]
    ids = [lab["lab_id"] for lab in labs]
    services = [lab["service"] for lab in labs]
    assert len(ids) == len(set(ids)) == 23
    assert len(services) == len(set(services)) == 23


def test_every_lab_has_required_kameleon_identity():
    required = {"lab_id", "service", "name", "city", "country", "lab_type", "function"}
    for lab in load_registry()["labs"]:
        assert required.issubset(lab)
        for key in required:
            assert isinstance(lab[key], str)
            assert lab[key].strip()
        assert lab["service"].startswith("lab-")


def test_expected_albanian_labs_are_present():
    ids = {lab["lab_id"] for lab in load_registry()["labs"]}
    assert {
        "Elbasan_AI",
        "Tirana_Medical",
        "Durres_IoT",
        "Vlore_Environmental",
        "Shkoder_Marine",
        "Korce_Agricultural",
        "Sarrande_Underwater",
    }.issubset(ids)

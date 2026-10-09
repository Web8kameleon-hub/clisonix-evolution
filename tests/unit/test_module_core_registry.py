from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OCEAN_CORE_DIR = ROOT / "ocean-core"
if str(OCEAN_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(OCEAN_CORE_DIR))

from module_core_registry import (  # type: ignore
    build_module_core_brief,
    get_module_core_catalog,
    resolve_module_core,
)


def test_registry_exposes_20_plus_module_cores() -> None:
    catalog = get_module_core_catalog()
    assert len(catalog) >= 20


def test_resolve_module_core_matches_common_queries() -> None:
    weather = resolve_module_core("show weather forecast and climate dashboard")
    docs = resolve_module_core("help me analyze an excel spreadsheet document")
    iot = resolve_module_core("iot sensor gateway and lora telemetry status")

    assert weather is not None
    assert weather["id"] == "weather-dashboard"

    assert docs is not None
    assert docs["id"] in {"document-tools", "excel-dashboard"}

    assert iot is not None
    assert iot["id"] == "iot-network"


def test_build_module_core_brief_is_user_facing() -> None:
    brief = build_module_core_brief("crypto-dashboard", language="en")
    assert "Crypto Dashboard" in brief
    assert "/modules/crypto-dashboard" in brief
    assert "portfolio" in brief.lower()

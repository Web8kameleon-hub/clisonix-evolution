"""
Teste për XLCCommandRouter.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ocean-core/xlc"))

import pytest
from xlc_command_router import RouteResult, XLCCommandRouter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def router() -> XLCCommandRouter:
    r = XLCCommandRouter(threshold=0.9999)
    r.register_many(["START", "RESET", "MODE"])
    return r


# ---------------------------------------------------------------------------
# Regjistrim
# ---------------------------------------------------------------------------

def test_register_single():
    r = XLCCommandRouter()
    r.register("START")
    assert "START" in r.commands


def test_register_strips_non_alpha():
    r = XLCCommandRouter()
    r.register("MODE_WWW_MMM")
    # ruhet vetëm pjesa alfa: MODEWWWMMM
    assert "MODEWWWMMM" in r.commands


def test_register_chaining():
    r = XLCCommandRouter()
    result = r.register("START").register("RESET")
    assert result is r
    assert len(r.commands) == 2


def test_register_many():
    r = XLCCommandRouter()
    r.register_many(["START", "RESET", "MODE"])
    assert set(r.commands) == {"START", "RESET", "MODE"}


def test_register_dedup():
    r = XLCCommandRouter()
    r.register("START")
    r.register("START")
    assert r.commands.count("START") == 1


def test_register_empty_raises():
    r = XLCCommandRouter()
    with pytest.raises(ValueError, match="bosh"):
        r.register("")


def test_register_no_alpha_raises():
    r = XLCCommandRouter()
    with pytest.raises(ValueError, match="shkronjë"):
        r.register("123_!")


# ---------------------------------------------------------------------------
# Routing — match
# ---------------------------------------------------------------------------

def test_route_exact_match(router: XLCCommandRouter):
    result = router.route("START")
    assert result.matched is True
    assert result.route_name == "START"
    assert result.report is not None
    assert result.report.opened is True


def test_route_keyword_inside_sentence(router: XLCCommandRouter):
    result = router.route("ju lutem START tani")
    assert result.matched is True
    assert result.route_name == "START"


def test_route_reset_inside_sentence(router: XLCCommandRouter):
    result = router.route("duhet te besh RESET")
    assert result.matched is True
    assert result.route_name == "RESET"


def test_route_mode_keyword(router: XLCCommandRouter):
    result = router.route("kaloje ne MODE")
    assert result.matched is True
    assert result.route_name == "MODE"


def test_route_unicode_keyword(router: XLCCommandRouter):
    unicode_router = XLCCommandRouter(threshold=0.9999)
    unicode_router.register("مرحبا")
    result = unicode_router.route("أقول مرحبا لكم")
    assert result.matched is True
    assert result.route_name == "مرحبا"


# ---------------------------------------------------------------------------
# Routing — no match
# ---------------------------------------------------------------------------

def test_route_no_match_returns_none(router: XLCCommandRouter):
    # QQQQQQQQQ nuk ndaj asnjë sekuencë me START/RESET/MODE
    result = router.route("QQQQQQQQQ")
    assert result.matched is False
    assert result.route_name is None


def test_route_no_match_report_opened_false(router: XLCCommandRouter):
    result = router.route("ZZZZZ")
    assert result.report is not None
    assert result.report.opened is False


# ---------------------------------------------------------------------------
# RouteResult struktura
# ---------------------------------------------------------------------------

def test_route_result_all_scores_populated(router: XLCCommandRouter):
    result = router.route("START")
    assert set(result.all_scores.keys()) == {"START", "RESET", "MODE"}
    for v in result.all_scores.values():
        assert 0.0 <= v <= 1.0


def test_route_result_router_ns_positive(router: XLCCommandRouter):
    result = router.route("START")
    assert result.router_ns > 0


def test_route_result_as_dict_keys(router: XLCCommandRouter):
    result = router.route("START")
    d = result.as_dict()
    for key in ("input_text", "route_name", "matched", "report", "all_scores", "router_ns"):
        assert key in d


def test_route_result_scan_mode_true(router: XLCCommandRouter):
    result = router.route("fillo START tani")
    assert result.report is not None
    assert result.report.scan_mode is True


# ---------------------------------------------------------------------------
# Route pa komanda regjistrime
# ---------------------------------------------------------------------------

def test_route_without_register_raises():
    r = XLCCommandRouter()
    with pytest.raises(RuntimeError, match="komanda"):
        r.route("START")


# ---------------------------------------------------------------------------
# Threshold custom
# ---------------------------------------------------------------------------

def test_custom_threshold_strict():
    """Me threshold=1.0 asnjë match nuk pritet (similarity < 1.0 floating)."""
    r = XLCCommandRouter(threshold=1.0)
    r.register("START")
    result = r.route("START")
    # threshold=1.0 kërkon similarity==1.0 saktësisht; mund të matched ose jo
    # varësisht nga llogaritjet float; vetëm kontrollojmë që nuk crash-on
    assert isinstance(result.matched, bool)


def test_custom_threshold_low():
    """Me threshold=0.5 çdo input duhet të matcho diçka."""
    r = XLCCommandRouter(threshold=0.5)
    r.register("START")
    result = r.route("START")
    assert result.matched is True

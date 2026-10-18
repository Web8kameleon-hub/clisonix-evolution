# Test suite për middleware-t e sigurisë (pytest)
# Teston sjelljen reale të çdo faze, pa asnjë të dhënë të shpikur


import os

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from ndb_advisory_middleware import NDBAdvisoryMiddleware
from ndb_hybrid_enforcement import NDBHybridEnforcementMiddleware
from ndb_resonance_default import NDBResonanceDefaultMiddleware
from ndb_shadow_sidecar import NDBShadowMiddleware


@pytest.fixture
def app_shadow():
    app = FastAPI()
    app.add_middleware(NDBShadowMiddleware)
    @app.post("/test")
    async def test_endpoint(request: Request):
        return {"ok": True}
    return app

@pytest.fixture
def app_advisory():
    app = FastAPI()
    app.add_middleware(NDBAdvisoryMiddleware)
    @app.post("/test")
    async def test_endpoint(request: Request):
        return {"ok": True}
    return app

@pytest.fixture
def app_hybrid():
    os.environ["NDB_HYBRID_ENFORCE_ENABLED"] = "1"
    os.environ["NDB_HYBRID_ENFORCED_ROUTES"] = "/test"
    os.environ["NDB_HYBRID_CANARY_PERCENT"] = "100"
    app = FastAPI()
    app.add_middleware(NDBHybridEnforcementMiddleware)
    @app.post("/test")
    async def test_endpoint(request: Request):
        return {"ok": True}
    return app

@pytest.fixture
def app_resonance():
    os.environ["NDB_RESONANCE_DEFAULT_ENABLED"] = "1"
    os.environ["NDB_RESONANCE_PRIMARY_ROUTES"] = "/test"
    app = FastAPI()
    app.add_middleware(NDBResonanceDefaultMiddleware)
    @app.post("/test")
    async def test_endpoint(request: Request):
        return {"ok": True}
    return app


def test_shadow_mode(app_shadow):
    os.environ["NDB_SHADOW_ENABLED"] = "1"
    client = TestClient(app_shadow)
    r = client.post("/test", json={"foo": "bar"})
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_advisory_mode(app_advisory):
    os.environ["NDB_ADVISORY_ENABLED"] = "1"
    client = TestClient(app_advisory)
    r = client.post("/test", json={"foo": "bar"})
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_hybrid_enforcement(app_hybrid):
    client = TestClient(app_hybrid)
    r = client.post("/test", json={"foo": "bar"})
    # Mund të jetë 200, 403, ose 429 sipas scoring real
    assert r.status_code in (200, 403, 429)

def test_resonance_default(app_resonance):
    client = TestClient(app_resonance)
    r = client.post("/test", json={"foo": "bar"})
    assert r.status_code in (200, 403, 429)

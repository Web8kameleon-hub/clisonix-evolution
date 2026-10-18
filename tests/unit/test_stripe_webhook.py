import asyncio
import hashlib
import hmac
import json
import os
from pathlib import Path
import sys
import time

import httpx
import pytest
import stripe
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

ROOT = next((parent for parent in Path(__file__).resolve().parents if (parent / "apps" / "api").is_dir()), Path("/app"))
sys.path.insert(0, str(ROOT / "apps" / "api" if (ROOT / "apps" / "api").is_dir() else ROOT))
from billing.stripe_events import handle_webhook, subscription_data, require_internal_key, persist_event

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    return await handle_webhook(request, stripe)


def signed(event):
    payload = json.dumps(event).encode()
    now = str(int(time.time()))
    digest = hmac.new(b"whsec_test_only", now.encode() + b"." + payload, hashlib.sha256).hexdigest()
    return payload, {"stripe-signature": f"t={now},v1={digest}"}


def test_signature_is_required_even_with_unconfigured_persistence(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_only")
    with TestClient(app) as client:
        assert client.post("/webhook", json={}).status_code == 400
        assert client.post("/webhook", content=b"{}", headers={"stripe-signature": "bad"}).status_code == 400
        monkeypatch.delenv("STRIPE_WEBHOOK_SECRET")
        assert client.post("/webhook", json={}).status_code == 503


def test_paid_checkout_does_not_acknowledge_failed_persistence(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_only")
    monkeypatch.delenv("AUTH_INTERNAL_URL", raising=False)
    event = {"id": "evt_paid", "type": "checkout.session.completed", "created": 1,
             "data": {"object": {"id": "cs_paid", "mode": "payment", "payment_status": "paid"}}}
    payload, headers = signed(event)
    with TestClient(app) as client:
        assert client.post("/webhook", content=payload, headers=headers).status_code == 503


def test_unpaid_checkout_never_grants_access(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_only")
    payload, headers = signed({"id": "evt_unpaid", "type": "checkout.session.completed", "created": 1,
                              "data": {"object": {"id": "cs_unpaid", "mode": "payment", "payment_status": "unpaid"}}})
    with TestClient(app) as client:
        result = client.post("/webhook", content=payload, headers=headers)
    assert result.status_code == 200 and result.json().get("ignored")


def test_new_stripe_item_period_is_used_and_unknown_prices_fail_closed(monkeypatch):
    from types import SimpleNamespace
    sub = {"id": "sub_one", "customer": "cus_one", "status": "active", "metadata": {"user_id": "usr_one"},
           "items": {"data": [{"price": {"id": "price_pro"}, "current_period_end": 1900000000}]}}
    sdk = SimpleNamespace(Subscription=SimpleNamespace(retrieve=lambda _: sub))
    monkeypatch.setenv("STRIPE_PRICE_PROFESSIONAL_MONTHLY", "price_pro")
    data = asyncio.run(subscription_data(sdk, "sub_one", {}))
    assert data["plan"] == "professional" and data["current_period_end"].startswith("2030-")
    monkeypatch.delenv("STRIPE_PRICE_PROFESSIONAL_MONTHLY")
    with pytest.raises(HTTPException):
        asyncio.run(subscription_data(sdk, "sub_one", {}))


def test_persistence_http_failure_and_false_success_both_trigger_retry(monkeypatch):
    monkeypatch.setenv("AUTH_INTERNAL_URL", "http://users.test")
    monkeypatch.setenv("INTERNAL_API_KEY", "test-only")
    original = httpx.AsyncClient
    for response in [httpx.Response(503), httpx.Response(200, json={"success": False})]:
        monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(
            transport=httpx.MockTransport(lambda _: response), **kwargs))
        with pytest.raises(HTTPException) as error:
            asyncio.run(persist_event({"event_id": "evt_test"}))
        assert error.value.status_code == 503

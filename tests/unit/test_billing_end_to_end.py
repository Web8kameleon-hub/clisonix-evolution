"""Real HTTP/SQLite integration; Stripe payloads are signed local test events."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import httpx
import stripe
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "services" / "user-management").is_dir())
sys.path.insert(0, str(ROOT / "apps" / "api"))
from billing import stripe_routes


def test_signed_webhook_updates_existing_login_and_survives_user_service_restart(tmp_path, monkeypatch):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    env = {**os.environ, "CLISONIX_USER_DB": str(tmp_path / "users.db"),
           "INTERNAL_API_KEY": "integration-test-only", "CLISONIX_BOOTSTRAP_ADMIN_EMAIL": "",
           "PYTHONPATH": str(ROOT / "services" / "user-management")}

    def start():
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
            cwd=ROOT / "services" / "user-management", env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(100):
            try:
                if httpx.get(base + "/health", timeout=1).status_code == 200:
                    return process
            except httpx.HTTPError:
                pass
            if process.poll() is not None:
                raise AssertionError("User service could not start")
            time.sleep(0.05)
        process.terminate()
        process.wait(timeout=5)
        raise AssertionError("User service startup timed out")

    monkeypatch.setenv("AUTH_INTERNAL_URL", base)
    monkeypatch.setenv("INTERNAL_API_KEY", "integration-test-only")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_local_integration")
    monkeypatch.setenv("STRIPE_PRICE_PROFESSIONAL_MONTHLY", "price_local_pro")
    monkeypatch.setattr(stripe_routes, "STRIPE_CONFIGURED", True)
    monkeypatch.setattr(stripe_routes, "stripe", stripe)
    app = FastAPI()
    app.include_router(stripe_routes.router)
    process = start()
    try:
        registered = httpx.post(base + "/api/users/register", json={
            "email": "integration@example.com", "username": "integration", "password": "StrongPass123",
        }).json()
        assert registered["success"]
        uid = registered["user_id"]
        login = httpx.post(base + "/api/users/login", json={
            "email_or_username": "integration@example.com", "password": "StrongPass123",
        }).json()
        headers = {"Authorization": "Bearer " + login["access_token"]}
        assert httpx.post(base + "/api/users/validate-token", headers=headers).json()["user"]["plan"] == "free"
        sub = {"id": "sub_integration", "customer": "cus_integration", "status": "active",
               "metadata": {"user_id": uid}, "items": {"data": [{
                   "price": {"id": "price_local_pro"}, "current_period_end": int(time.time()) + 86400,
               }]}}
        monkeypatch.setattr(stripe.Subscription, "retrieve", lambda _: sub)
        payload = json.dumps({"id": "evt_integration", "type": "customer.subscription.updated",
                              "created": int(time.time()), "data": {"object": {"id": sub["id"]}}}).encode()
        timestamp = str(int(time.time()))
        signature = hmac.new(b"whsec_local_integration", timestamp.encode() + b"." + payload, hashlib.sha256).hexdigest()
        with TestClient(app) as client:
            for _ in range(2):
                result = client.post("/api/v1/billing/webhook", content=payload,
                                     headers={"stripe-signature": f"t={timestamp},v1={signature}"})
                assert result.status_code == 200, result.text
            assert result.json()["idempotent"] is True
        process.terminate()
        process.wait(timeout=5)
        process = start()
        state = httpx.post(base + "/api/users/validate-token", headers=headers).json()
        assert state["valid"] and state["user"]["plan"] == "professional"
        assert state["user"]["user_id"] == uid
    finally:
        process.terminate()
        process.wait(timeout=5)

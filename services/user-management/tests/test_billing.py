import concurrent.futures
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db
from billing import BillingEvent, apply_event
from user_core import UserRegistry


@pytest.fixture
def account(tmp_path, monkeypatch):
    monkeypatch.setenv("CLISONIX_USER_DB", str(tmp_path / "users.db"))
    monkeypatch.setenv("INTERNAL_API_KEY", "test-only-internal-key")
    monkeypatch.delenv("CLISONIX_BOOTSTRAP_ADMIN_EMAIL", raising=False)
    registry = UserRegistry()
    result = registry.register_user("buyer@example.com", "buyer", "StrongPass123")
    assert result["success"]
    return registry, result["user_id"]


def subscription(user_id, event_id="evt_active", created=100, status="active", sub_id="sub_one"):
    return BillingEvent(event_id=event_id, created=created, kind="subscription", data={
        "user_id": user_id, "customer_id": "cus_one", "subscription_id": sub_id,
        "plan": "professional", "status": status,
        "current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    })


def test_plan_survives_restart_and_session_reads_current_plan(account):
    registry, uid = account
    login = registry.login("buyer@example.com", "StrongPass123")
    credits = registry.get_usage(uid)["credits_balance"]
    apply_event(subscription(uid))
    restarted = UserRegistry()
    assert restarted.validate_token(login["access_token"])["plan"] == "professional"
    assert restarted.get_account(uid)["plan"] == "professional"
    assert restarted.get_usage(uid)["credits_balance"] == credits


def test_duplicates_are_atomic_and_do_not_reward_credits(account):
    registry, uid = account
    credits = registry.get_usage(uid)["credits_balance"]
    event = subscription(uid)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda _: apply_event(event), range(12)))
    assert sum(not result.get("idempotent", False) for result in results) == 1
    with db.get_connection() as conn:
        assert conn.execute("SELECT count(*) FROM billing_events").fetchone()[0] == 1
    assert registry.get_usage(uid)["credits_balance"] == credits


def test_late_event_cannot_reactivate_canceled_subscription(account):
    registry, uid = account
    apply_event(subscription(uid))
    apply_event(subscription(uid, "evt_cancel", 200, "canceled"))
    assert apply_event(subscription(uid, "evt_delayed", 101))["stale"]
    assert registry.get_account(uid)["plan"] == "free"


def test_canceling_other_subscription_preserves_active_access(account):
    registry, uid = account
    apply_event(subscription(uid))
    apply_event(subscription(uid, "evt_other_cancel", 200, "canceled", "sub_old"))
    assert registry.get_account(uid)["plan"] == "professional"


def test_unregistered_account_is_retried_not_acknowledged(account):
    with pytest.raises(HTTPException) as error:
        apply_event(subscription("usr_missing"))
    assert error.value.status_code == 409
    with db.get_connection() as conn:
        assert conn.execute("SELECT count(*) FROM billing_events").fetchone()[0] == 0


def test_paid_purchase_is_unique_per_checkout_and_refundable(account):
    _, uid = account
    event = BillingEvent(event_id="evt_payment", created=100, kind="purchase", data={
        "user_id": uid, "session_id": "cs_one", "payment_intent_id": "pi_one",
        "payment_status": "paid", "amount_total": 2500, "currency": "eur",
    })
    apply_event(event)
    apply_event(event.model_copy(update={"event_id": "evt_second_notification"}))
    apply_event(BillingEvent(event_id="evt_refund", created=200, kind="payment_adjustment",
                            data={"payment_intent_id": "pi_one", "payment_status": "refunded"}))
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM billing_purchases").fetchall()
    assert len(rows) == 1 and rows[0]["status"] == "refunded"


def test_unpaid_purchase_rolls_back(account):
    _, uid = account
    with pytest.raises(HTTPException):
        apply_event(BillingEvent(event_id="evt_unpaid", created=1, kind="purchase", data={
            "user_id": uid, "session_id": "cs_unpaid", "payment_status": "unpaid",
        }))
    with db.get_connection() as conn:
        assert conn.execute("SELECT count(*) FROM billing_events").fetchone()[0] == 0


def test_billing_requires_internal_key_and_public_signup_cannot_grant_paid_plan(account, monkeypatch):
    from main import app
    with TestClient(app) as client:
        response = client.post("/api/internal/billing/events", json=subscription(account[1]).model_dump())
        assert response.status_code == 401
        monkeypatch.delenv("INTERNAL_API_KEY")
        response = client.post("/api/internal/billing/events", json=subscription(account[1]).model_dump())
        assert response.status_code == 503
        response = client.post("/api/users/register", json={
            "email": "bypass@example.com", "username": "bypass", "password": "StrongPass123", "plan": "enterprise",
        })
        assert response.status_code == 400


def test_revoked_password_session_and_suspended_account_cannot_authenticate(account):
    registry, uid = account
    login = registry.login("buyer@example.com", "StrongPass123")
    assert registry.change_password(uid, "StrongPass123", "NewStrongPass456")["success"]
    assert registry.validate_token(login["access_token"]) is None
    login = registry.login("buyer@example.com", "NewStrongPass456")
    with db.get_connection() as conn:
        conn.execute("UPDATE accounts SET status='suspended' WHERE user_id=?", (uid,))
    assert registry.validate_token(login["access_token"]) is None

#!/usr/bin/env python3
"""
Ocean Warm + Reaction smoke/integration suite
=============================================

Covers:
1) Ocean direct warm endpoint      -> POST /api/v1/chat/stream/warm
2) Web proxy warm endpoint         -> POST /api/ocean/stream/warm
3) Ocean reaction add/toggle/read  -> POST/GET /api/v1/message/*
4) Web proxy reaction endpoint     -> POST /api/ocean/message/reaction

Tests are resilient:
- If a service is not reachable locally, test is skipped (not failed).
"""

from __future__ import annotations

import time
import uuid

import httpx
import pytest

OCEAN_URL = "http://localhost:8030"
WEB_URL = "http://localhost:3000"
TIMEOUT = 20.0


def _post(url: str, payload: dict) -> httpx.Response:
    return httpx.post(url, json=payload, timeout=TIMEOUT)


def _get(url: str) -> httpx.Response:
    return httpx.get(url, timeout=TIMEOUT)


class TestWarmEndpoints:
    def test_ocean_warm_direct(self):
        payload = {
            "message": "kjo eshte nje test i gjate per warm endpoint qe te shmanget too_short"
        }
        try:
            r = _post(f"{OCEAN_URL}/api/v1/chat/stream/warm", payload)
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable on localhost:8030")

        assert r.status_code == 200, f"Unexpected status: {r.status_code} body={r.text[:300]}"
        data = r.json()
        assert "status" in data
        assert data["status"] in {"warming", "already_warmed", "skipped"}

    def test_web_warm_proxy(self):
        payload = {
            "message": "kjo eshte nje test i gjate per web warm proxy endpoint"
        }
        try:
            r = _post(f"{WEB_URL}/api/ocean/stream/warm", payload)
        except httpx.ConnectError:
            pytest.skip("Web service not reachable on localhost:3000")

        assert r.status_code == 200, f"Unexpected status: {r.status_code} body={r.text[:300]}"
        data = r.json()
        assert "status" in data
        assert data["status"] in {"warming", "skipped", "error"}


class TestReactionEndpoints:
    def test_ocean_reaction_post_and_get(self):
        message_id = f"test-msg-{uuid.uuid4().hex[:10]}"
        payload = {
            "message_id": message_id,
            "emoji": "ok",
            "user_id": "pytest-user",
        }

        try:
            post_r = _post(f"{OCEAN_URL}/api/v1/message/reaction", payload)
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable on localhost:8030")

        assert post_r.status_code == 200, f"Unexpected status: {post_r.status_code} body={post_r.text[:300]}"
        post_data = post_r.json()
        assert post_data.get("status") == "success"

        get_r = _get(f"{OCEAN_URL}/api/v1/message/{message_id}/reactions")
        assert get_r.status_code == 200, f"Unexpected status: {get_r.status_code} body={get_r.text[:300]}"
        get_data = get_r.json()

        assert get_data.get("message_id") == message_id
        assert isinstance(get_data.get("reactions"), dict)
        assert "ok" in get_data["reactions"], f"Missing reaction in payload: {get_data}"
        assert get_data["reactions"]["ok"]["count"] >= 1

    def test_web_reaction_proxy(self):
        message_id = f"proxy-msg-{int(time.time())}"
        payload = {
            "message_id": message_id,
            "emoji": "ok",
            "user_id": "pytest-web-user",
        }

        try:
            r = _post(f"{WEB_URL}/api/ocean/message/reaction", payload)
        except httpx.ConnectError:
            pytest.skip("Web service not reachable on localhost:3000")

        assert r.status_code == 200, f"Unexpected status: {r.status_code} body={r.text[:300]}"
        data = r.json()
        assert "status" in data
        assert data["status"] in {"success", "error"}

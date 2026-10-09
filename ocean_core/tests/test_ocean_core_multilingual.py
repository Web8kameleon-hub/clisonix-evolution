#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN CORE FULL - Multilingual & Multi-Service Tests
=====================================================
Tests në shumë gjuhë për të gjitha shërbimet kryesore.
"""

import time

import httpx
import pytest

# ─────────────────────────────────────────────
# BASE URLS (from docker-compose service names)
# ─────────────────────────────────────────────
OCEAN_CORE_URL       = "http://localhost:8030"
TRANSLATION_NODE_URL = "http://localhost:8036"
CENTRAL_API_URL      = "http://localhost:8000"
ASI_LITE_URL         = "http://localhost:9094"
OPENMIND_URL         = "http://localhost:9999"
EXCEL_CORE_URL       = "http://localhost:8002"

TIMEOUT = 30.0

# ─────────────────────────────────────────────
# MULTILINGUAL TEST PROMPTS
# ─────────────────────────────────────────────
MULTILINGUAL_PROMPTS = [
    {"lang": "sq", "label": "Albanian",   "text": "Përshëndetje! Si mund të më ndihmosh sot?"},
    {"lang": "en", "label": "English",    "text": "Hello! What services does Clisonix offer?"},
    {"lang": "de", "label": "German",     "text": "Hallo! Was kannst du für mich tun?"},
    {"lang": "fr", "label": "French",     "text": "Bonjour! Quels services proposez-vous?"},
    {"lang": "it", "label": "Italian",    "text": "Ciao! Come posso usare questa piattaforma?"},
    {"lang": "es", "label": "Spanish",    "text": "¡Hola! ¿Qué puedes hacer por mí?"},
    {"lang": "pt", "label": "Portuguese", "text": "Olá! Quais são os seus serviços?"},
    {"lang": "tr", "label": "Turkish",    "text": "Merhaba! Bana nasıl yardımcı olabilirsin?"},
    {"lang": "ar", "label": "Arabic",     "text": "مرحباً! كيف يمكنك مساعدتي؟"},
    {"lang": "zh", "label": "Chinese",    "text": "你好！你能为我提供哪些服务？"},
    {"lang": "ja", "label": "Japanese",   "text": "こんにちは！どのようなことができますか？"},
    {"lang": "ru", "label": "Russian",    "text": "Привет! Чем ты можешь мне помочь?"},
    {"lang": "el", "label": "Greek",      "text": "Γεια σας! Τι υπηρεσίες προσφέρετε;"},
    {"lang": "pl", "label": "Polish",     "text": "Cześć! Jakie usługi oferujesz?"},
    {"lang": "nl", "label": "Dutch",      "text": "Hallo! Wat kun jij voor mij doen?"},
]


def _chat_payload(text: str, lang: str, session_id: str = "test-session") -> dict:
    return {
        "message": text,
        "language": lang,
        "session_id": session_id,
        "stream": False,
    }


# ═══════════════════════════════════════════════════════════════════
# 1. HEALTH CHECKS — All Services
# ═══════════════════════════════════════════════════════════════════
class TestHealthEndpoints:

    SERVICES = [
        ("Ocean Core",       OCEAN_CORE_URL),
        ("Translation Node", TRANSLATION_NODE_URL),
        ("Central API",      CENTRAL_API_URL),
        ("ASI Lite",         ASI_LITE_URL),
        ("OpenMind",         OPENMIND_URL),
        ("Excel Core",       EXCEL_CORE_URL),
    ]

    @pytest.mark.parametrize("name,base_url", SERVICES)
    def test_health(self, name, base_url):
        try:
            r = httpx.get(f"{base_url}/health", timeout=TIMEOUT)
            assert r.status_code == 200, f"{name} health check failed: {r.status_code}"
            print(f"  OK {name} /health")
        except httpx.ConnectError:
            pytest.skip(f"{name} not reachable at {base_url}")

    @pytest.mark.parametrize("name,base_url", SERVICES)
    def test_status(self, name, base_url):
        try:
            r = httpx.get(f"{base_url}/status", timeout=TIMEOUT)
            assert r.status_code in (200, 404), f"{name} /status unexpected: {r.status_code}"
            print(f"  OK {name} /status ({r.status_code})")
        except httpx.ConnectError:
            pytest.skip(f"{name} not reachable")


# ═══════════════════════════════════════════════════════════════════
# 2. OCEAN CORE — Chat in 15 Languages
# ═══════════════════════════════════════════════════════════════════
class TestOceanCoreMultilingual:

    @pytest.mark.parametrize("entry", MULTILINGUAL_PROMPTS, ids=[p["label"] for p in MULTILINGUAL_PROMPTS])
    def test_chat_language(self, entry):
        try:
            r = httpx.post(f"{OCEAN_CORE_URL}/chat", json=_chat_payload(entry["text"], entry["lang"]), timeout=TIMEOUT)
            assert r.status_code == 200, f"{entry['label']} chat failed: {r.status_code} — {r.text[:200]}"
            data = r.json()
            response_text = data.get("response") or data.get("message") or data.get("text", "")
            assert len(response_text) > 5, f"{entry['label']}: response too short: '{response_text}'"
            print(f"  OK {entry['label']}: '{response_text[:80]}'")
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable")

    def test_chat_session_memory(self):
        try:
            session = "memory-test-001"
            turn1 = httpx.post(f"{OCEAN_CORE_URL}/chat",
                json=_chat_payload("My name is TestUser and I love space exploration.", "en", session),
                timeout=TIMEOUT)
            assert turn1.status_code == 200

            turn2 = httpx.post(f"{OCEAN_CORE_URL}/chat",
                json=_chat_payload("What did I just tell you about myself?", "en", session),
                timeout=TIMEOUT)
            assert turn2.status_code == 200
            reply = (turn2.json().get("response") or "").lower()
            assert "testuser" in reply or "space" in reply, f"Memory not retained. Got: '{reply[:200]}'"
            print(f"  OK Session memory: '{reply[:80]}'")
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable")

    def test_chat_rate_limit_not_triggered_on_first(self):
        try:
            r = httpx.post(f"{OCEAN_CORE_URL}/chat", json=_chat_payload("Rate limit test", "en"), timeout=TIMEOUT)
            assert r.status_code != 429, "Rate limit hit on first request — unexpected"
            print("  OK Rate limit not triggered on first request")
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable")

    def test_chat_empty_prompt_rejected(self):
        try:
            r = httpx.post(f"{OCEAN_CORE_URL}/chat", json={"message": "", "language": "en"}, timeout=TIMEOUT)
            assert r.status_code in (400, 422), f"Expected 400/422 for empty prompt, got {r.status_code}"
            print("  OK Empty prompt correctly rejected")
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable")


# ═══════════════════════════════════════════════════════════════════
# 3. TRANSLATION NODE — 15 Languages
# ═══════════════════════════════════════════════════════════════════
class TestTranslationNode:

    SOURCE_TEXT = "Hello, this is a test of the Clisonix translation system."

    @pytest.mark.parametrize("entry", MULTILINGUAL_PROMPTS, ids=[p["label"] for p in MULTILINGUAL_PROMPTS])
    def test_translate_to_language(self, entry):
        try:
            r = httpx.post(f"{TRANSLATION_NODE_URL}/translate",
                json={"text": self.SOURCE_TEXT, "target_language": entry["lang"]},
                timeout=TIMEOUT)
            assert r.status_code == 200, f"Translation to {entry['label']} failed: {r.status_code}"
            data = r.json()
            translated = data.get("translated") or data.get("result") or data.get("text", "")
            assert len(translated) > 3, f"Translation too short for {entry['label']}: '{translated}'"
            print(f"  OK {entry['label']}: '{translated[:80]}'")
        except httpx.ConnectError:
            pytest.skip("Translation Node not reachable")

    def test_detect_english(self):
        try:
            r = httpx.post(f"{TRANSLATION_NODE_URL}/detect",
                json={"text": "The quick brown fox jumps over the lazy dog."},
                timeout=TIMEOUT)
            assert r.status_code == 200
            lang = r.json().get("language") or r.json().get("detected") or r.json().get("lang", "")
            assert "en" in str(lang).lower(), f"Expected English, got: {lang}"
            print(f"  OK Detected English: {lang}")
        except httpx.ConnectError:
            pytest.skip("Translation Node not reachable")

    def test_detect_albanian(self):
        try:
            r = httpx.post(f"{TRANSLATION_NODE_URL}/detect",
                json={"text": "Mirëmëngjes, si jeni sot?"},
                timeout=TIMEOUT)
            assert r.status_code == 200
            lang = r.json().get("language") or r.json().get("detected") or r.json().get("lang", "")
            assert "sq" in str(lang).lower() or "al" in str(lang).lower(), \
                f"Expected Albanian (sq), got: {lang}"
            print(f"  OK Detected Albanian: {lang}")
        except httpx.ConnectError:
            pytest.skip("Translation Node not reachable")


# ═══════════════════════════════════════════════════════════════════
# 4. CENTRAL API
# ═══════════════════════════════════════════════════════════════════
class TestCentralAPI:

    def test_health(self):
        try:
            r = httpx.get(f"{CENTRAL_API_URL}/health", timeout=TIMEOUT)
            assert r.status_code == 200
            print("  OK Central API /health")
        except httpx.ConnectError:
            pytest.skip("Central API not reachable")

    def test_agents_list(self):
        try:
            r = httpx.get(f"{CENTRAL_API_URL}/agents", timeout=TIMEOUT)
            assert r.status_code in (200, 401, 403), f"Unexpected: {r.status_code}"
            print(f"  OK /agents responded: {r.status_code}")
        except httpx.ConnectError:
            pytest.skip("Central API not reachable")


# ═══════════════════════════════════════════════════════════════════
# 5. ASI LITE
# ═══════════════════════════════════════════════════════════════════
class TestASILite:

    def test_health(self):
        try:
            r = httpx.get(f"{ASI_LITE_URL}/health", timeout=TIMEOUT)
            assert r.status_code == 200
            print("  OK ASI Lite /health")
        except httpx.ConnectError:
            pytest.skip("ASI Lite not reachable")

    def test_learn_endpoint(self):
        try:
            r = httpx.post(f"{ASI_LITE_URL}/learn",
                json={"prompt": "What is 2+2?", "response": "4", "language": "en"},
                timeout=TIMEOUT)
            assert r.status_code in (200, 201, 202), f"Unexpected /learn status: {r.status_code}"
            print(f"  OK ASI Lite /learn: {r.status_code}")
        except httpx.ConnectError:
            pytest.skip("ASI Lite not reachable")


# ═══════════════════════════════════════════════════════════════════
# 6. EXCEL CORE
# ═══════════════════════════════════════════════════════════════════
class TestExcelCore:

    def test_health(self):
        try:
            r = httpx.get(f"{EXCEL_CORE_URL}/health", timeout=TIMEOUT)
            assert r.status_code == 200
            print("  OK Excel Core /health")
        except httpx.ConnectError:
            pytest.skip("Excel Core not reachable")

    def test_generate_excel(self):
        try:
            r = httpx.post(f"{EXCEL_CORE_URL}/generate",
                json={"title": "Test Report", "data": [["Name", "Score"], ["Alice", 95], ["Bob", 87]], "language": "en"},
                timeout=TIMEOUT)
            assert r.status_code in (200, 201), f"Unexpected: {r.status_code}"
            assert len(r.content) > 100, "Response too small to be a valid xlsx"
            print(f"  OK Excel Core /generate — {len(r.content)} bytes")
        except httpx.ConnectError:
            pytest.skip("Excel Core not reachable")


# ═══════════════════════════════════════════════════════════════════
# 7. OPENMIND
# ═══════════════════════════════════════════════════════════════════
class TestOpenMind:

    def test_health(self):
        try:
            r = httpx.get(f"{OPENMIND_URL}/health", timeout=TIMEOUT)
            assert r.status_code == 200
            print("  OK OpenMind /health")
        except httpx.ConnectError:
            pytest.skip("OpenMind not reachable")

    @pytest.mark.parametrize("entry", MULTILINGUAL_PROMPTS[:5], ids=[p["label"] for p in MULTILINGUAL_PROMPTS[:5]])
    def test_query_multilingual(self, entry):
        try:
            r = httpx.post(f"{OPENMIND_URL}/query",
                json={"query": entry["text"], "language": entry["lang"]},
                timeout=TIMEOUT)
            assert r.status_code in (200, 404), f"{entry['label']} query failed: {r.status_code}"
            print(f"  OK OpenMind {entry['label']}: {r.status_code}")
        except httpx.ConnectError:
            pytest.skip("OpenMind not reachable")


# ═══════════════════════════════════════════════════════════════════
# 8. PERFORMANCE BASELINE
# ═══════════════════════════════════════════════════════════════════
class TestPerformanceBaseline:

    MAX_HEALTH_MS = 500
    MAX_CHAT_MS   = 15_000

    def test_ocean_health_latency(self):
        try:
            start = time.monotonic()
            r = httpx.get(f"{OCEAN_CORE_URL}/health", timeout=TIMEOUT)
            elapsed_ms = (time.monotonic() - start) * 1000
            assert r.status_code == 200
            assert elapsed_ms < self.MAX_HEALTH_MS, f"Health too slow: {elapsed_ms:.0f}ms"
            print(f"  OK /health latency: {elapsed_ms:.0f}ms")
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable")

    def test_ocean_chat_latency_english(self):
        try:
            start = time.monotonic()
            r = httpx.post(f"{OCEAN_CORE_URL}/chat",
                json=_chat_payload("Say hello in one word.", "en"),
                timeout=TIMEOUT)
            elapsed_ms = (time.monotonic() - start) * 1000
            assert r.status_code == 200
            assert elapsed_ms < self.MAX_CHAT_MS, f"Chat too slow: {elapsed_ms:.0f}ms"
            print(f"  OK Chat latency (EN): {elapsed_ms:.0f}ms")
        except httpx.ConnectError:
            pytest.skip("Ocean Core not reachable")

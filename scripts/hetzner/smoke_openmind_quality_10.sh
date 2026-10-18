#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:9999}"
CHAT_URL="${BASE_URL}/api/v1/chat"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[SMOKE] python3 is required"
  exit 1
fi

echo "[SMOKE] OpenMind 10-question quality check"
echo "[SMOKE] Target: ${CHAT_URL}"

python3 - "${CHAT_URL}" <<'PY'
import json
import re
import sys
from urllib import request

chat_url = sys.argv[1]

questions = [
    "Mund te me japesh nje plan 3 hapash per fokus ne pune sot?",
    "Si ta ndaj diten ne blloqe 90-minuteshe pa u lodhur?",
    "Kam ankth para nje prezantimi. Cfare bej ne 15 minutat e fundit?",
    "Mund te me shpjegosh shkurt diferencen midis strategjise dhe taktikes?",
    "Jep nje shembull te thjeshte per buxhet mujor personal.",
    "Si te shkruaj nje email profesional per kerkese bashkepunimi?",
    "What is a practical way to learn faster without burnout?",
    "Give me a 5-step plan to improve sleep quality this week.",
    "Wie kann ich meinen Tag besser priorisieren, wenn alles dringend wirkt?",
    "Je veux un mini plan de 3 etapes pour rester regulier dans mes objectifs.",
]

low_quality_markers = [
    "i don't have knowledge about this yet",
    "help me learn",
    "model returned empty output",
    "x, shko",
]

def call_chat(prompt: str) -> str:
    payload = json.dumps({"message": prompt}).encode("utf-8")
    req = request.Request(
        chat_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=70) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    data = json.loads(body)
    return str(data.get("response", "")).strip()

def is_low_quality(text: str) -> bool:
    t = text.strip().lower()
    if not t:
        return True
    if any(m in t for m in low_quality_markers):
        return True
    if len(text.strip()) < 80:
        return True
    words = [w for w in re.split(r"\s+", text.strip()) if w]
    if len(words) < 16:
        return True
    return False

passed = 0
rows = []
for i, q in enumerate(questions, start=1):
    try:
        answer = call_chat(q)
        ok = not is_low_quality(answer)
        if ok:
            passed += 1
        preview = answer.replace("\n", " ")[:140]
        rows.append((i, ok, preview))
    except Exception as exc:
        rows.append((i, False, f"ERROR: {exc}"))

score = round((passed / len(questions)) * 10, 2)
print(f"[SMOKE] Passed: {passed}/{len(questions)}")
print(f"[SMOKE] Quality score: {score}/10")
for i, ok, preview in rows:
    status = "PASS" if ok else "FAIL"
    print(f"  - Q{i:02d} {status}: {preview}")

if passed < 8:
    sys.exit(2)
PY

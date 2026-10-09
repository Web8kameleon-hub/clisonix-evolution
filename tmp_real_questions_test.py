import json
import subprocess

questions = [
    "Shpjego shkurt si funksionon Curiosity Ocean ne 5 fjali.",
    "Me jep nje plan 7-ditor per uljen e stresit me hapa konkrete.",
    "Cili eshte ndryshimi praktik midis matched_rate dhe avg_confidence?",
    "Si do e monitoroje nje API FastAPI ne production me alerta minimale?",
    "Jep nje shembull architecture per webhook callback async pa fake data.",
]

url = "https://www.clisonix.com/api/ocean/stream"

for i, question in enumerate(questions, 1):
    payload = json.dumps({"message": question}, ensure_ascii=False)
    cmd = [
        "curl",
        "-sN",
        "--max-time",
        "30",
        url,
        "-H",
        "Content-Type: application/json",
        "-d",
        payload,
        "-w",
        "\\n__METRIC__%{time_starttransfer}|%{http_code}\\n",
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    metric_line = next((ln for ln in lines if ln.startswith("__METRIC__")), None)
    sample_lines = [ln for ln in lines if not ln.startswith("__METRIC__")][:12]

    ttfb = "unknown"
    http_code = "unknown"
    if metric_line:
        payload_metric = metric_line.replace("__METRIC__", "", 1)
        if "|" in payload_metric:
            ttfb, http_code = payload_metric.split("|", 1)

    print("=" * 80)
    print(f"Q{i}: {question}")
    print(f"time_starttransfer_s: {ttfb}")
    print(f"http_code: {http_code}")
    if result.stderr.strip():
        print("stderr:")
        print(result.stderr.strip()[:500])
    print("sample:")
    if sample_lines:
        for line in sample_lines:
            print(line[:500])
    else:
        print("(no non-empty stream lines)")

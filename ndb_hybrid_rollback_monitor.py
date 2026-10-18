
# Hybrid Enforcement SLO & Rollback Monitor
# Analizon eventet reale të enforcement-it, monitoron SLO (latency, 5xx), dhe trigger rollback nëse tejkalohen pragjet
# Pa asnjë të dhënë të shpikur, vetëm evidencë reale
#
# Ky skript ruan log të detajuar për çdo incident rollback (me timestamp, shkaqe, veprime),
# prodhon output JSON për audit të jashtëm dhe rekomandon ruajtjen e log-eve për inspektim compliance.


import json
import os
from datetime import datetime

import pandas as pd

HYBRID_FILE = os.environ.get("NDB_HYBRID_EVENTS_FILE", "ndb_hybrid_events.jsonl")
ROLLBACK_LOG = "ndb_hybrid_rollback_log.md"
ROLLBACK_INCIDENTS_JSON = "ndb_hybrid_rollback_incidents.jsonl"
P95_LATENCY_THRESHOLD = float(os.environ.get("NDB_HYBRID_P95_LATENCY_MS", "300"))  # ms
ERROR_RATE_THRESHOLD = float(os.environ.get("NDB_HYBRID_5XX_RATE", "0.01"))  # 1%

if not os.path.exists(HYBRID_FILE):
    print(f"No hybrid events file found: {HYBRID_FILE}")
    exit(1)

# Load events
events = []
with open(HYBRID_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            events.append(json.loads(line))
        except Exception as e:
            print(f"Error parsing line: {e}")

if not events:
    print("No hybrid events found.")
    exit(0)

df = pd.DataFrame(events)

# If latency is not logged, skip latency SLO (add in enforcement for real prod)
latency_col = 'latency_ms' if 'latency_ms' in df.columns else None

# Calculate 5xx error rate
error_rate = (df['outcome'] >= 500).sum() / len(df)


# Calculate p95 latency if available and not empty
p95_latency = None
if latency_col:
    latency_series = df[latency_col].dropna()
    if not latency_series.empty:
        p95_latency = latency_series.quantile(0.95)

rollback_triggered = False
rollback_reasons = []

with open(ROLLBACK_LOG, "a", encoding="utf-8") as f:
    f.write("# Hybrid Enforcement SLO & Rollback Log\n\n")
    f.write(f"Total events: {len(df)}\n")
    f.write(f"5xx error rate: {error_rate:.2%} (threshold: {ERROR_RATE_THRESHOLD:.2%})\n")

    if latency_col and p95_latency is not None:
        f.write(f"p95 latency: {p95_latency:.1f} ms (threshold: {P95_LATENCY_THRESHOLD} ms)\n")
    if error_rate > ERROR_RATE_THRESHOLD:
        f.write("\n**ROLLBACK TRIGGERED: 5xx error rate above threshold!**\n")
        rollback_triggered = True
        rollback_reasons.append("5xx error rate above threshold")
    if latency_col and p95_latency is not None and p95_latency > P95_LATENCY_THRESHOLD:
        f.write("\n**ROLLBACK TRIGGERED: p95 latency above threshold!**\n")
        rollback_triggered = True
        rollback_reasons.append("p95 latency above threshold")
    if not rollback_triggered:
        f.write("\nSLOs respected, no rollback needed.\n")

# Log incident as JSON for audit/compliance
if rollback_triggered:
    incident = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_events": len(df),
        "error_rate": error_rate,
        "error_rate_threshold": ERROR_RATE_THRESHOLD,
        "p95_latency": p95_latency,
        "p95_latency_threshold": P95_LATENCY_THRESHOLD,
        "reasons": rollback_reasons,
        "action": "ROLLBACK_TRIGGERED"
    }
    with open(ROLLBACK_INCIDENTS_JSON, "a", encoding="utf-8") as jf:
        jf.write(json.dumps(incident, ensure_ascii=False) + "\n")

print(f"Hybrid enforcement SLO/rollback log updated: {ROLLBACK_LOG}")
if rollback_triggered:
    print("ROLLBACK TRIGGERED: Please deactivate NDB_HYBRID_ENFORCE_ENABLED immediately!")
    print(f"Incident log (JSON) appended to: {ROLLBACK_INCIDENTS_JSON}")
    print("\n// Ruaj log-et dhe JSON për inspektim të jashtëm ose audit ISO/GDPR! //")

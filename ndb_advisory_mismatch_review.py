# Advisory Mismatch Review & Tuning Script
# Analizon eventet reale të advisory mode, nxjerr mismatch classes, trend, dhe ndihmon për tuning threshold-esh
# Pa asnjë të dhënë të shpikur, vetëm evidencë reale

import json
import os

import pandas as pd

ADVISORY_FILE = os.environ.get("NDB_ADVISORY_EVENTS_FILE", "ndb_advisory_events.jsonl")
REVIEW_FILE = "ndb_advisory_mismatch_review.md"

if not os.path.exists(ADVISORY_FILE):
    print(f"No advisory events file found: {ADVISORY_FILE}")
    exit(1)

# Load events
events = []
with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            events.append(json.loads(line))
        except Exception as e:
            print(f"Error parsing line: {e}")

if not events:
    print("No advisory events found.")
    exit(0)

df = pd.DataFrame(events)

# Mismatch analysis
mismatches = df[df['mismatch'] == True]
match_rate = 1 - (len(mismatches) / len(df)) if len(df) > 0 else 0

# Mismatch classes (by recommendation/legacy_decision)
mismatch_classes = mismatches.groupby(['recommendation', 'legacy_decision']).size().reset_index(name='count')

# Trend over time
df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
trend = df.groupby('date')['mismatch'].mean()

with open(REVIEW_FILE, "w", encoding="utf-8") as f:
    f.write("# NDB Advisory Mismatch Review\n\n")
    f.write(f"Total events: {len(df)}\n")
    f.write(f"Total mismatches: {len(mismatches)}\n")
    f.write(f"Recommendation agreement rate: {match_rate:.2%}\n\n")
    f.write("## Mismatch Classes\n")
    if not mismatch_classes.empty:
        f.write(mismatch_classes.to_markdown(index=False) + "\n\n")
    else:
        f.write("No mismatches found.\n\n")
    f.write("## Mismatch Trend (per day)\n")
    f.write(trend.to_markdown() + "\n\n")
    f.write("## Tuning Notes\n")
    f.write("- Review mismatch classes for threshold adjustment.\n")
    f.write("- Use real evidence for every change.\n")
    f.write("- No auto-enforcement; all changes require approval and changelog.\n")

print(f"Advisory mismatch review generated: {REVIEW_FILE}")

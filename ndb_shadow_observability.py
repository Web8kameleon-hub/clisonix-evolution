# Real Observability Script for NDB Shadow Events
# This script parses the ndb_shadow_events.jsonl file and outputs real metrics for dashboarding (no fake data)
# Can be used as a data source for Grafana/Prometheus or for generating CSV/JSON for BI tools

import json
import os
import sys

import pandas as pd

EVENTS_FILE = os.environ.get("NDB_SHADOW_EVENTS_FILE", "ndb_shadow_events.jsonl")

if not os.path.exists(EVENTS_FILE):
    print(f"No events file found: {EVENTS_FILE}")
    sys.exit(1)

# Load events
events = []
with open(EVENTS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            events.append(json.loads(line))
        except Exception as e:
            print(f"Error parsing line: {e}")

if not events:
    print("No events found.")
    sys.exit(0)

df = pd.DataFrame(events)

# Example metrics: false-positive potential, drift trend, score distribution
print("==== NDB Shadow Observability Metrics ====")
print(f"Total events: {len(df)}")
print(f"Endpoints observed: {df['endpoint'].nunique()}")
print(f"Unique IPs: {df['ip'].nunique()}")

# Score distribution
print("\nScore distribution:")
print(df['ndb_score'].describe())

# Stigma level counts
print("\nStigma level counts:")
print(df['stigma_level'].value_counts())

# Drift trend (mean score per day)
df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
print("\nDrift trend (mean ndb_score per day):")
print(df.groupby('date')['ndb_score'].mean())

# False-positive potential: count of high score but 2xx outcome
fp = df[(df['ndb_score'] > 70) & (df['outcome'] < 300)]
print(f"\nPotential false-positives (high score, allowed): {len(fp)}")

# Save summary as CSV for dashboarding
df.to_csv("ndb_shadow_events_summary.csv", index=False)
print("\nSummary saved to ndb_shadow_events_summary.csv")

# For Grafana/Prometheus: can expose metrics via HTTP or pushgateway (not included here, only real file output)

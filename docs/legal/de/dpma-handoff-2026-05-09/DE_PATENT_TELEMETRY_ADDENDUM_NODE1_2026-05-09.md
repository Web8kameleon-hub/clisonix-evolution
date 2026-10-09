# Germany Patent Telemetry Addendum (Node 1)

Document type: Technical evidence addendum for attorney packet
Date: 2026-05-09
Jurisdiction target: Germany (DPMA)

## Legal Note
This addendum is a technical interpretation of runtime telemetry and not legal advice.

## 1. Source Telemetry Snapshot

### 1.1 Security Status
```
{"metrics":{"active_peers":2,"avg_latency_ms":50,"bandwidth_kbps":10000,"load":0.0},"ndb_delta":-0.5350000262260437,"ndb_score":0.11500000208616257,"ndb_threshold":0.6499999761581421,"state":"Active","tide":"Low"}
```

### 1.2 Event Trace
```
[{"timestamp_ms":1778306233042,"node_id":1,"endpoint":"/status","action":"read-status","stigma_level":2,"ndb_score":0.115,"outcome":"ok"},{"timestamp_ms":1778306269461,"node_id":1,"endpoint":"/submit","action":"submit-op","stigma_level":2,"ndb_score":0.115,"outcome":"accepted"},{"timestamp_ms":1778306818507,"node_id":1,"endpoint":"/status","action":"read-status","stigma_level":2,"ndb_score":0.115,"outcome":"ok"},{"timestamp_ms":1778307123644,"node_id":1,"endpoint":"/status","action":"read-status","stigma_level":2,"ndb_score":0.115,"outcome":"ok"},{"timestamp_ms":1778307137124,"node_id":1,"endpoint":"/status","action":"read-status","stigma_level":2,"ndb_score":0.115,"outcome":"ok"}]
```

### 1.3 Runtime Summary
```
{"node_id":1,"tide":"Low","ndb_score":0.115,"ndb_delta":-0.535,"ndb_threshold":0.65,"high_risk":false,"event_count":5}
```

## 2. Technical Interpretation
1. Node state is operationally stable (`state=Active`, `tide=Low`, `high_risk=false`).
2. Deviation score is materially below threshold (`ndb_score=0.115` vs `ndb_threshold=0.65`).
3. Negative delta (`ndb_delta=-0.535`) indicates movement away from risk boundary.
4. Event outcomes show consistent acceptance behavior with no escalation (`ok` or `accepted`).
5. Stigma level remains fixed at level 2 during the captured window, supporting a controlled middle policy regime.

## 3. Claim-Relevance Mapping

### 3.1 NDB Deviation Control
Evidence supports method claims where node behavior is classified from a measured ndB score, an ndB delta, and a threshold comparator.

### 3.2 Tide-Conditioned Operations
Evidence supports system claims where an operational tide state influences risk posture and policy strictness.

### 3.3 Stigma-Governed Policy Regime
Evidence supports dependent claims where stigma level gates or modulates accepted endpoint operations.

### 3.4 Event-Driven Behavioral Auditability
Evidence supports computer program product claims where endpoint actions and outcomes are recorded and replayable for post-hoc compliance.

## 4. Proposed Claim Language Snippets (Working)
1. A method wherein node risk state is determined from `ndb_score`, `ndb_delta`, and `ndb_threshold` and mapped to an execution policy.
2. The method of claim 1, wherein a low tide state suppresses escalation when the ndB score remains below threshold.
3. The method of claim 1, wherein a stigma level parameter controls route acceptance for submit and status operations.
4. A system configured to emit a structured event trail containing endpoint, action, stigma level, ndB score, and outcome for each request.

## 5. Attorney Handoff Notes
1. Preserve this telemetry snapshot with timestamp and source endpoint in the filing annex.
2. Pair this addendum with source references in the DE evidence index.
3. Use this snapshot to demonstrate concrete runtime behavior, not only conceptual architecture.

# Germany Patent Draft Package

Document type: Draft invention disclosure for DPMA filing preparation
Jurisdiction target: Germany (DPMA)
Technology family: WWWMMM-NDB-STIGMA / CLX adaptive security runtime
Date: 2026-05-09

## Legal Note
This is a technical drafting pack, not legal advice. Final claims and filing strategy must be approved by a German patent attorney (Patentanwalt).

## 1. Proposed Invention Title
Method and system for endpoint-adaptive nanodecibel resonance security classification with staged policy enforcement in AI service pipelines.

## 2. Technical Field
Cybersecurity and AI runtime governance, specifically anomaly detection and policy actions using endpoint-specific resonance baselines and nanodecibel deviation metrics.

## 3. Problem Statement
Conventional request screening in AI APIs usually relies on static signatures, global thresholds, or single-pass heuristics. These approaches are weak against endpoint-specific drift and cannot reliably distinguish normal route variation from attack behavior in near-real-time.

## 4. Core Technical Solution
The invention combines:
1. Endpoint-local resonance profile histories.
2. Baseline arming by minimum samples.
3. Nanodecibel deviation thresholds with multi-level severity.
4. Policy output mapped to actionable runtime controls (allow/monitor/throttle/block).
5. Integration in a continuous learning and query-processing core.

## 5. Distinctive Technical Features (Evidence Anchors)
1. Integrated security monitor in core processing pipeline:
- sdist/clx-ai/clx/core.py line 47
- sdist/clx-ai/clx/core.py line 61
- sdist/clx-ai/clx/core.py line 108

2. Endpoint-local baseline and threshold logic:
- sdist/clx-ai/clx/security/monitor.py line 15
- sdist/clx-ai/clx/security/monitor.py line 22
- sdist/clx-ai/clx/security/monitor.py line 23
- sdist/clx-ai/clx/security/monitor.py line 92
- sdist/clx-ai/clx/security/monitor.py line 117
- sdist/clx-ai/clx/security/monitor.py line 143
- sdist/clx-ai/clx/security/monitor.py line 147
- sdist/clx-ai/clx/security/monitor.py line 162

3. Stigma-level dependent resonance scoring and ndb conversion in service mode:
- clx_i_service.py line 38
- clx_i_service.py line 83
- clx_i_service.py line 122
- clx_i_service.py line 139
- clx_i_service.py line 244
- clx_i_service.py line 270
- clx_i_service.py line 272
- clx_i_service.py line 306

4. Deterministic high-ops learning with no-fake-data and atomic persistence:
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 8
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 68
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 83
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 130
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 247

## 6. Draft Claim Set (Working)

### Claim 1 (Independent Method)
A computer-implemented method for request security classification, comprising:
1. receiving a request associated with an endpoint identifier;
2. obtaining a resonance value expressed in nanodecibel units;
3. maintaining endpoint-specific historical resonance samples;
4. computing a baseline from the historical samples when a minimum baseline sample condition is satisfied;
5. calculating a deviation between the received resonance value and the baseline;
6. assigning a severity level based on at least two nanodecibel deviation thresholds; and
7. selecting and returning a runtime policy action selected from allow, monitor, throttle, or block according to the severity level.

### Claim 2 (Dependent)
The method of claim 1, wherein the baseline includes mean, median, and standard deviation over a sliding window of endpoint-specific samples.

### Claim 3 (Dependent)
The method of claim 1, wherein a route-match indicator is combined with nanodecibel deviation to increase severity for unmatched-route requests after baseline arming.

### Claim 4 (Dependent)
The method of claim 1, wherein throttle policy includes a configurable traffic reduction coefficient.

### Claim 5 (Independent System)
A system comprising:
1. an API runtime service;
2. a security monitor configured to execute claims 1-4;
3. a learning engine and persistent knowledge store;
4. a policy gate in the request pipeline that blocks execution when the security monitor returns block.

### Claim 6 (Independent Computer Program Product)
A non-transitory computer-readable medium storing instructions that, when executed by one or more processors, perform the method of any of claims 1-4.

## 7. DPMA Filing Strategy (Recommended)
1. Immediate German national filing (DPMA) with broad independent claims plus fallback dependent claims.
2. Within 12 months, evaluate PCT extension.
3. Keep algorithm constants and tuning internals as trade secrets if not required for enablement.

## 8. Required Inputs Before Attorney Finalization
1. Inventor legal names and addresses.
2. Applicant legal entity data.
3. First disclosure dates (if any).
4. Preferred filing route: direct DPMA only vs DPMA + PCT plan.
5. Commercial embodiments to prioritize in claims.

## 9. What Else Appears Potentially Unique (Second Patent Family Candidates)
1. Stigma-level controlled output constraints tied to resonance scoring in multimodal icon analysis.
2. Combined mirror-level telemetry plus selflearning event pipeline linked to request-level resonance metrics.
3. Deterministic confidence scoring for multi-source learning ingestion with atomic checkpoint persistence.

## 10. Next Action Checklist
1. Freeze evidence snapshot (commit hashes + signed archive).
2. Convert this draft to attorney template (DE patent specification format).
3. Run prior-art search and novelty risk scoring.
4. Finalize claims and file with DPMA.

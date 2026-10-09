# Germany Novelty Matrix

Document type: Internal novelty and inventive-step working matrix
Jurisdiction: Germany / EPC-style reasoning support
Date: 2026-05-09

## Scoring Key
- Novelty confidence: Low / Medium / High
- Inventive step confidence: Low / Medium / High
- Risk: likelihood that prior art could read on claim elements

## Candidate A: Endpoint-specific nanodecibel baseline firewall

### Core Elements
1. Endpoint-local historical resonance profiles.
2. Baseline arming threshold.
3. Multi-threshold ndb deviation logic.
4. Action mapping to allow/monitor/throttle/block.
5. Runtime inline block gate in AI query path.

### Evidence
- sdist/clx-ai/clx/core.py line 47
- sdist/clx-ai/clx/core.py line 61
- sdist/clx-ai/clx/core.py line 108
- sdist/clx-ai/clx/security/monitor.py line 15
- sdist/clx-ai/clx/security/monitor.py line 92
- sdist/clx-ai/clx/security/monitor.py line 117
- sdist/clx-ai/clx/security/monitor.py line 143
- sdist/clx-ai/clx/security/monitor.py line 162

### Prior-Art Overlap (General Classes)
1. Generic anomaly detection systems: overlap medium.
2. API gateway rate limiting and WAF rules: overlap medium.
3. Endpoint-specific resonance ndb policy coupling: overlap low.

### Assessment
- Novelty confidence: Medium-High
- Inventive step confidence: Medium
- Main risk: prior art in adaptive API anomaly throttling if claims are too broad.
- Mitigation: claim ndb-specific endpoint baseline plus staged policy mapping and integration points.

## Candidate B: Stigma-level multimodal resonance scoring and response control

### Core Elements
1. Stigma levels as constrained response policy selector.
2. Resonance score computed from prompt-output features.
3. Conversion to decibel and nanodecibel metrics.
4. Mirror/selflearning event persistence with request-level metadata.

### Evidence
- clx_i_service.py line 83
- clx_i_service.py line 122
- clx_i_service.py line 129
- clx_i_service.py line 139
- clx_i_service.py line 153
- clx_i_service.py line 170
- clx_i_service.py line 244
- clx_i_service.py line 270
- clx_i_service.py line 272

### Prior-Art Overlap (General Classes)
1. Prompt safety levels: overlap medium.
2. Generic quality scoring: overlap medium.
3. Explicit stigma-level + ndb telemetry coupling: overlap low-medium.

### Assessment
- Novelty confidence: Medium
- Inventive step confidence: Medium
- Main risk: framing looks like policy parameterization unless tied to technical system effects.
- Mitigation: emphasize measurable runtime control, telemetry semantics, and endpoint security integration.

## Candidate C: No-fake-data high-ops learning with deterministic confidence + atomic checkpoints

### Core Elements
1. Learning only from successful real payloads.
2. Deterministic dynamic confidence scoring.
3. Multi-source probe catalog (local/git/live API).
4. Atomic report and snapshot persistence.

### Evidence
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 8
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 68
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 83
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 130
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 247
- sdist/clx-ai/examples/ecosystem_ops_10min.py line 499

### Assessment
- Novelty confidence: Medium
- Inventive step confidence: Low-Medium
- Main risk: many elements may be seen as engineering best practice.
- Mitigation: protect mostly as trade secret or narrow claims tied to specific pipeline coupling.

## Provisional Filing Recommendation
1. File Candidate A as primary patent family.
2. Keep Candidate B as continuation/divisional option if claim budget allows.
3. Keep Candidate C as documentation and trade-secret support unless attorney finds strong claim angle.

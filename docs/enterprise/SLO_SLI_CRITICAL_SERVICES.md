# SLO/SLI for 6 Critical Services

## Critical Services
1. Ocean Core (`8030`)
2. Backend API (`8000`)
3. OpenMind (`9999`)
4. Excel Core (`8002`)
5. Ollama (`11434`)
6. Translation Node (`8036`)

## SLI Definitions
- Availability SLI: successful health checks / total checks
- Latency SLI (p95): request latency p95 for primary endpoints
- Error SLI: 5xx ratio on service endpoints
- Dependency SLI: upstream dependency health ratio

## SLO Targets (Monthly)
- Availability:
  - Ocean/API/OpenMind/Excel: 99.95%
  - Ollama/Translation: 99.9%
- Latency p95:
  - Ocean chat: < 1200ms (excluding model generation)
  - API gateway routes: < 300ms
  - OpenMind health/control endpoints: < 200ms
- Error rate:
  - 5xx < 0.5%
- Dependency health:
  - central_api/openmind/excel in Ocean integrations: > 99%

## Error Budget
- 99.95% => 21m 54s/month downtime budget
- 99.90% => 43m 49s/month downtime budget

## Alerting Thresholds
- SEV-1: availability drop below SLO burn-rate 14x (fast burn)
- SEV-2: error rate > 2% për 5 min
- SEV-3: latency p95 > 2x target për 10 min

## Weekly Review
- Burn-rate review
- Top 3 incidents and MTTR
- Proposed reliability tasks for next sprint

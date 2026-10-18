# OS-CLX Evidence

## Summary

- Latest benchmark: YYYY-MM-DD (run ID)
- Availability: X.XX%
- p95 latency: XXX ms across N endpoints
- Production gates: N/M passed
- Replication: N/N packs completed

## Benchmark

[Table with p50/p95/p99 per endpoint]

## Production Gates

[Table with gate, target, actual, status]

## Reliability

[SLO/SLI summary]

## Scale

[Node matrix 1,5,10,25,50 results]

## Formalization

[Formula validation summary]

## How to reproduce

```powershell
pwsh ./scripts/proof/run_replication_pack.ps1 -RuntimeUrl http://127.0.0.1:56000

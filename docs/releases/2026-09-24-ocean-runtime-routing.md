# Ocean request isolation and canonical runtime routing

## Issue
Real curl requests returned HTTP 200 with incorrect Albanian arithmetic answers.
The web service targeted the legacy Ocean container instead of the service updated
by CI. Anonymous requests also shared backend memory. HTTP success alone does not
prove answer correctness or NDB inference.

## Documentation
Web deployment now explicitly targets the deployed Ocean Swarm service. Direct
CLX-agent bypass requires use_clx_agent=true. No external model is selected by
this patch. Missing streaming models fail rather than silently substituting one.
Server-side memory from caller-asserted identities is disabled; explicit messages
in the request still provide conversation continuity. SSE token whitespace is
preserved. The Ocean deployment smoke container receives its Python stdin.

## Tests
Run ocean-core/tests/test_stream_request_isolation.py, the existing HumanThinking
matrix, XLC routing tests, syntax checks, and live curl against the deployed SHA.
Live answer quality must be recorded separately from transport success.

## Edge cases
Anonymous and forged body identities cannot read or write shared memory. Missing
models remain errors. Whitespace-only stream chunks retain their formatting.
The Rust NanoGrid source still contains simulated peer/load metrics; this release
does not enable it or claim a verified NanoGrid -> GRAM inference chain.

## Benchmark
Before change: public Albanian 17-times-23 requests completed with HTTP 200 in
10.74s and 6.31s but gave irrelevant answers. A direct diagnostic call to the
existing llama3.1:8b also failed in Albanian while answering 391 in English.
These observations are not a general model benchmark.

## Rollback
Revert this commit on main and rerun the scoped Web/Ocean deployment. For an
immediate failed rollout use docker service rollback on the affected service.
Validate public streaming and request isolation before accepting recovery.

# CLX Portfolio Release Architecture

## Objective

Build a coherent release architecture for `CLX`, `XCL`, and `CLX.I`
without merging three different product surfaces into one
ambiguous package.

## Product Map

### 1. CLX

Role:
- Lightweight Python distribution.
- Streaming primitives.
- Nanodecibel metrics.
- Stigma profiles.
- No-fake-data validation.

Release vehicle:
- Standalone PyPI package `clx`.

Current source of truth:
- `sdk/python/clx/`

### 2. XCL

Role:
- Domain reasoning layer for WWWMMM and XLC semantics.
- Local authoritative retrieval.
- Prompt enrichment for high-context CLX answers.

Release vehicle:
- Near term: internal capability layer documented in portfolio docs.
- Mid term: potential `clx-xcl` or `clx[xcl]` optional capability.

Current source of truth:
- `clx_local_domain_wrapper.py`
- `tests/unit/test_clx_local_domain_wrapper.py`
- `docs/architecture/XLC_RESONANT_READING_MODEL.md`

### 3. CLX.I

Role:
- Image and icon intelligence.
- Domain enrichment and selflearning.
- Observable FastAPI service with health and metrics.

Release vehicle:
- Near term: service release artifact.
- Mid term: package a client or embedded integration layer
  rather than shipping the service file blindly.

Current source of truth:
- `clx_i_service.py`
- `tests/unit/test_clx_i_service.py`
- `Dockerfile.clx-i`

## Phase Model

### 10%
- Inventory current modules.
- Identify public APIs.
- Mark service code versus package code.

### 20%
- Freeze product boundaries.
- Decide names, ownership, and publication targets.
- Avoid naming collisions between `CLX` and `XCL`.

### 30%
- Create packaging and docs scaffold.
- Define release metadata.
- Define SEO landing page structure.

### 50%
- Refine code boundaries.
- Add examples and developer guides.
- Improve tests around public APIs.

### 80%
- Build artifacts.
- Validate metadata.
- Run product-specific tests and smoke checks.

### 100%
- Release `CLX`.
- Publish docs and package pages.
- Advance `CLX.I` to service release.
- Keep `XCL` documented as a capability layer until its API becomes stable.

## Quality Gates

A release must not proceed if any of the following are false:
- Tests pass.
- No-fake-data guarantees remain intact.
- Build artifacts pass metadata validation.
- Public API is documented.
- Product naming is consistent across docs and SEO pages.

## Architecture Rule

`CLX` is the public package.
`XCL` is the reasoning and protocol layer.
`CLX.I` is the image-intelligence service track.

They are related, but not interchangeable.

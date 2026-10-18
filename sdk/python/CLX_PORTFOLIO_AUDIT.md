# CLX Portfolio Audit

## Scope

This audit covers the three related release tracks that should not be mixed blindly:

- `CLX`: lightweight Python package for hotguard,
  nanodecibel metrics, and no-fake-data validation.
- `XCL`: domain protocol and contextual reasoning layer
  around WWWMMM, XLC, resonance, and authoritative local retrieval.
- `CLX.I`: image and icon intelligence service with
  selflearning, domain enrichment, and observable FastAPI endpoints.

## Current State

### CLX

Status: release scaffold exists and validates.

Evidence:
- Standalone package metadata exists in `sdk/python/clx/pyproject.toml`.
- Public API is exported via `sdk/python/clx/__init__.py`.
- Hotguard modules live under `sdk/python/clx/hotguard/`.
- Packaging validation passed through `python -m build` and `twine check`.
- Unit tests for hotguard passed.

Release posture:
- Ready for TestPyPI trial.
- Needs richer examples and product positioning for a stronger public release.

### XCL

Status: technical capability exists, but not yet a standalone distribution.

Evidence:
- `clx_local_domain_wrapper.py` implements local retrieval and domain mapping.
- `tests/unit/test_clx_local_domain_wrapper.py` validates mapping,
  retrieval, and answer metadata.
- The wrapper references authoritative CLX/XLC sources including
  `sdk/python/clx/hotguard/scanner_printer.py` and
  `docs/architecture/XLC_RESONANT_READING_MODEL.md`.
- Validation now passes after retrieval ranking was improved to
  prefer authoritative code sources for technical queries.

Release posture:
- Suitable as a capability layer or subpackage.
- Not yet ready as a separate PyPI distribution because its
  boundaries, naming, and public API are still service-adjacent.

### CLX.I

Status: real service exists, validated as a service, not yet
packaged as a standalone Python distribution.

Evidence:
- `clx_i_service.py` implements a FastAPI service for image and icon analysis.
- `tests/unit/test_clx_i_service.py` validates health,
  selflearning writes, and domain enrichment behavior.
- Imports and smoke checks pass in the current workspace.

Release posture:
- Service release is viable.
- Library release is not yet productized because the current
  surface is an application service, not a clean client or
  embedded SDK package.

## Real Gaps

### Packaging gaps

- `CLX` is now package-shaped.
- `XCL` lacks a standalone public package contract.
- `CLX.I` lacks a dedicated package folder, metadata,
  and release-safe application boundary.

### Product gaps

- Public naming between `CLX`, `XCL`, and `CLX.I`
  can confuse developers and search engines if left undocumented.
- `CLX.I` needs product positioning as image intelligence, not just a service file.
- `XCL` needs a precise role definition:
  protocol, reasoning layer, or developer toolkit.

### Documentation gaps

- The root SDK docs mention `CLX`, but the portfolio relationship
  is not yet documented in one place.
- There is no single release matrix for `CLX`, `XCL`, and `CLX.I`.
- SEO guidance for package pages and developer docs is not yet tied to the portfolio.

## Validation Evidence

Validated in this workspace:
- `sdk/python/clx/hotguard/test_scanner_printer.py`
- `tests/unit/test_clx_i_service.py`
- `tests/unit/test_clx_local_domain_wrapper.py`
- `clx` import surface
- `clx` package build and `twine check`

## Recommended Product Boundaries

- `CLX`: publish as the compact developer-facing Python package.
- `XCL`: keep as the knowledge and protocol layer that can later
  become a dedicated subpackage.
- `CLX.I`: publish first as a service release track, then decide
  whether a client or embedded library package is warranted.

## Decision

Do not publish empty or fake `XCL` or `CLX.I` packages just to complete naming symmetry.
Publish `CLX` now, formalize `XCL` as a capability layer,
and productize `CLX.I` through a service-first release path.

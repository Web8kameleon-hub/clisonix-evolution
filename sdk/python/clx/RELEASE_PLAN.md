# CLX Release Plan

## Phase 10% - Inventory
- Confirm current public API surface.
- Map existing modules and imports.
- Identify missing packaging metadata.
- Verify no-fake-data constraints.

## Phase 20% - Architecture
- Keep CLX as a focused hotguard package.
- Separate CLX release concerns from the broader Clisonix SDK.
- Preserve deterministic streaming and resonance calculations.
- Keep hospital or urgent-context responses direct and action-first.

## Phase 30% - Packaging Split
- Maintain standalone `clx` distribution metadata.
- Ensure `pyproject.toml` builds only the `clx` package.
- Keep README, license, and classifiers PyPI-ready.
- Define the public API explicitly.

## Phase 50% - Implementation
- Refine module boundaries.
- Add release-grade examples.
- Expand tests for stream phases, thresholds, and validator behavior.
- Stabilize import paths and package exports.

## Phase 80% - Validation
- Build wheel and sdist.
- Run unit tests and import checks.
- Verify no fake data is emitted.
- Confirm version and metadata consistency.

## Phase 100% - Release
- Tag the release.
- Publish to TestPyPI first.
- Promote to PyPI after validation.
- Keep rollback notes and patch release guidance.

## Release Goal
CLX should ship as a modern, world-class Python package with a small, sharp API, real metrics, no fake data, and a clean path to PyPI installation.

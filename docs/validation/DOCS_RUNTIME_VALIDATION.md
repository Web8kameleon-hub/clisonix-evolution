# Docs Runtime Validation

## Purpose

Prevent drift between documentation and running system behavior.

## Validation Scope

- service endpoints and ports
- health/status routes
- API contract references
- deployment command paths
- environment variable names

## Validation Strategy

1. Static check: docs references exist in repo.
2. Runtime check: listed endpoints respond as documented.
3. Contract check: OpenAPI vs documented examples.
4. CI gate: fail if critical mismatches detected.

## Proposed Automation

Create scripts:

- scripts/validate_docs_paths.ps1
- scripts/validate_runtime_endpoints.ps1
- scripts/validate_openapi_refs.ps1

Each script should output:

- pass/fail
- mismatch list
- suggested fix location

## CI Integration

Run on:

- pull requests touching docs, compose, routing, or API files
- scheduled weekly drift check

Fail conditions:

- missing referenced file
- critical endpoint documented but unavailable
- route mismatch between docs and OpenAPI for critical services

## Manual Verification Template

- date:
- validator:
- environment:
- docs checked:
- runtime checked:
- mismatches:
- resolution:

## Acceptance Criteria

- critical docs have zero unresolved critical mismatches
- mismatches are tracked as issues with owner and due date

# Release Policy

## Purpose

Define release gates, approval flow, and rollback expectations.

## Release Types

- patch: fixes and safe doc/ops updates
- minor: backward-compatible feature additions
- major: breaking changes or architecture shifts

## Required Gates

Before release:

- CI green for required checks
- security review for sensitive changes
- docs updated for behavior changes
- rollback plan documented

## Branching

- main: release-ready baseline
- feature/*: development branches
- hotfix/*: urgent production fixes

## Release Checklist

- [ ] version bump/changelog update
- [ ] migration notes (if needed)
- [ ] deployment notes updated
- [ ] post-release validation plan

## Rollback Policy

Every release must define:

- rollback trigger conditions
- rollback command or workflow
- responsible owner
- verification after rollback

## Post-Release Validation

- health endpoints
- key user flows
- error rate and latency sanity checks
- alerting baseline unchanged or explained

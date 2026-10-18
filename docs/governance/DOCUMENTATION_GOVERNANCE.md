# Documentation Governance

## Purpose

Define how documentation is owned, reviewed, and retired so docs remain trustworthy.

## Principles

- One source of truth for each topic.
- Every critical doc has an owner.
- Every critical doc has a review cadence.
- Contradictions must be resolved, not duplicated.

## Document States

Use one state per document:

- draft
- active
- deprecated
- archived

## Required Header for Critical Docs

Add this block at top of critical docs:

- owner: <team or person>
- status: draft|active|deprecated|archived
- last_reviewed: YYYY-MM-DD
- review_due: YYYY-MM-DD
- source_of_truth: true|false

## Review Cadence

- security and deployment docs: every 30 days
- architecture and API contracts: every 45 days
- process and governance docs: every 60 days

## Contradiction Handling

When two docs disagree:

1. Open issue with both references.
2. Mark one as temporary non-authoritative.
3. Resolve in a single source-of-truth doc.
4. Link all secondary docs to the resolved source.

## Archive Policy

Move outdated docs to archive folder or mark as deprecated with migration note.
Do not silently keep conflicting active docs.

## Quality Gate for PRs

For PRs touching behavior:

- update affected source-of-truth docs
- update changelog
- include runtime verification evidence if applicable

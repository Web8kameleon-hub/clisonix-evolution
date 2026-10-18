# Contributing to Clisonix Cloud

Thank you for contributing.

## Scope

This repository contains multiple services and experiments. Keep changes focused and reversible.

## Ground Rules

- Do not commit secrets, tokens, or credentials.
- Follow NO_FAKE_DATA_POLICY.md: no mock/fake fallback data in production paths.
- Keep service boundaries clear (do not mix unrelated dependencies).
- Prefer small pull requests with clear rollback paths.

## Development Workflow

1. Create a branch from `main`.
2. Explain the problem and expected behavior in the PR.
3. Add or update documentation with every behavior change.
4. Run local validation relevant to changed services.
5. Open PR with test evidence and risk notes.

## Commit Style

Use concise, imperative commit messages.

Examples:

- fix(eeg): validate sampling rate before stream start
- docs(ops): add incident triage checklist
- ci: disable auto deploy trigger for manual approval

## Pull Request Checklist

- [ ] Problem statement is clear.
- [ ] Behavior change is documented.
- [ ] Security impact reviewed.
- [ ] Operational impact reviewed.
- [ ] Rollback plan included.
- [ ] No secrets introduced.

## Documentation Requirement

If you change runtime behavior, update at least one of:

- architecture wiring/index docs
- deployment/runbook docs
- API docs/openapi
- changelog

## Review Criteria

PRs are reviewed for:

- correctness
- security and privacy
- operational safety
- observability and diagnostics
- backward compatibility

## Merge Policy

- Do not merge red CI.
- Do not merge without at least one review on critical paths.
- Use squash merge unless preserving history is required.

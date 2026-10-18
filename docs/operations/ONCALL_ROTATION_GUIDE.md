# On-Call Rotation Guide

## Purpose

Define responsibilities and handoff standards for on-call operations.

## Roles

- primary on-call: first responder
- secondary on-call: backup escalation
- incident commander: assigned during Sev0/Sev1 incidents

## Core Responsibilities

- monitor alerts and dashboards
- acknowledge incidents within SLO target
- execute runbooks
- escalate when blocked
- write concise incident notes

## Handoff Rules

At shift handoff include:

- open incidents and current state
- temporary mitigations in place
- pending risks for next shift
- blocked actions and required approvers

## Escalation Matrix

1. Primary handles initial triage.
2. Secondary joins for Sev1+ or blocked triage.
3. Commander assigned for Sev0/Sev1.
4. Security/legal notified for data/security incidents.

## Alert Hygiene

- remove noisy alerts that do not lead to action
- keep threshold changes documented
- ensure each critical alert has a runbook link

## Shift Checklist

Start of shift:

- verify access to logs/metrics/deploy tools
- review ongoing incidents
- verify latest release notes

End of shift:

- publish handoff summary
- confirm ownership transfer
- ensure unresolved risks are explicit

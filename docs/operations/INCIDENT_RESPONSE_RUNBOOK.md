# Incident Response Runbook

## Purpose

Provide a standard process for detecting, triaging, mitigating, and closing incidents.

## Severity Levels

- Sev0: full outage or critical data/security risk
- Sev1: major degradation, high customer impact
- Sev2: partial degradation, workaround exists
- Sev3: minor issue, low immediate impact

## Response Targets

- Sev0 acknowledgement: <= 5 min
- Sev1 acknowledgement: <= 10 min
- Sev2 acknowledgement: <= 30 min
- Sev3 acknowledgement: <= 4 hours

## Incident Flow

1. Detect
2. Triage
3. Assign commander
4. Stabilize service
5. Communicate status
6. Resolve root cause
7. Verify recovery
8. Publish postmortem

## Triage Checklist

- What changed recently (deploy/config/dependency)?
- Is this localized or system-wide?
- Are health endpoints failing?
- Are alerts/metrics/logs aligned with symptom?
- Is rollback safer than forward fix?

## Mitigation Options

- rollback to last known good
- disable non-critical feature flags
- isolate failing service
- increase limits/capacity where safe
- switch to safe degraded mode if defined

## Communication Template

- start time
- affected services
- user impact
- current mitigation
- next update ETA

## Closure Checklist

- service recovered and verified
- alerts normalized
- customer impact summary captured
- root cause documented
- action items with owners and deadlines

## Postmortem Minimum Fields

- timeline
- root cause
- contributing factors
- what worked
- what failed
- preventive actions

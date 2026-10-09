# Clisonis-Clisonix Protocol

## Purpose

Implements a Blerina-style intelligence cycle for governance documentation:

1. detect gaps in current documents,
2. produce objective FAIL/PASS signals,
3. optionally rewrite missing sections using controlled templates.

## Execution modes

### 1) Scan-only mode

```bash
python scripts/audit_medical_gen_layers.py --error-rate 0.004 --scan-doc-gaps
```

### 2) Scan + rewrite mode

```bash
python scripts/audit_medical_gen_layers.py --error-rate 0.004 --scan-doc-gaps --rewrite-doc-gaps
```

## What it checks

- Required package documents in `docs/medical-governance-packages/`
- Required headings per package (Purpose, Required documents, controls/assets)

## Rewrite strategy

- Appends missing sections with a strict template.
- Never deletes existing content.
- Re-scans after rewrite to verify closure.

## PASS/FAIL policy

- Any missing package heading after rewrite (or scan-only) => `FAIL`
- Governance gate failure => `FAIL`
- Only combined success => `PASS`

## Alignment with Blerina concept

Like Blerina quality intelligence, this protocol is deterministic, measurable, and recommendation-driven, with hard PASS/FAIL outputs and no subjective review dependency.

# Clisonix Medical Governance Standard (GEN6-GEN9)

This policy defines strict publication gates for scientific-medical documents generated through Clisonix.

## Core rule

Ocean is orchestration/editor only. A document is publishable only when all required medical layers (GEN6-GEN9) are covered and validated.

## Strict gates

- Maximum end-to-end error rate: `<0.5%` (`<= 0.005`)
- Missing required GEN layer: automatic `FAIL`
- Missing reference metadata in core citations: automatic `FAIL`

## Layered QC protocol (0.10-0.50)

This protocol defines strict laboratory quality layers. Lower layer code means stricter tolerance.

| Layer | Max Error Rate | Objective | Technical Profile |
| --- | --- | --- | --- |
| `0.10` | `0.10%` (`<=0.001`) | Ultra-precise control | Biomarkers, hormones, stem-cell workflows, sequencing |
| `0.20` | `0.20%` (`<=0.002`) | High-level clinical control | ELISA, PCR, spectrometry, standard clinical assays |
| `0.30` | `0.30%` (`<=0.003`) | Reinforced routine control | Routine hematology, baseline biochemistry |
| `0.40` | `0.40%` (`<=0.004`) | Operational high-volume control | High-throughput lab operations |
| `0.50` | `0.50%` (`<=0.005`) | Minimum allowed non-critical control | Screening and training workflows |

### Full strict continuum (0.001-0.50)

In addition to the 5 operational layers above, Clisonix enforces a full continuous precision range:

- Minimum: `0.001%` (`0.00001` ratio)
- Maximum: `0.50%` (`0.00500` ratio)
- Resolution: `0.001%` (`0.00001` ratio)

Each audit run maps measured error rate to the nearest checkpoint in this range.

### QC control architecture

- **Core QC layer**: device calibration, storage/temperature checks, reagent validation, deviation logging
- **Reproducibility layer**: duplicate measurements, cross-operator checks, cross-instrument comparison
- **Data integrity layer**: metadata checks, versioned results, audit traceability
- **Biosafety layer**: PPE compliance, biosafety-level rules, mandatory staff training

### SOP execution model

1. **Preparation**: validate devices/reagents and load internal controls for selected layer
2. **Execution**: run protocol and register all deviations; duplicate measurement mandatory for 0.10-0.20
3. **Verification**: compute total error and compare against selected layer threshold
4. **Certification**: certify if error is in-threshold, otherwise rerun + root-cause analysis

## Required reference fields

Each critical reference must include:

- `title`
- `journal`
- `year`
- `doi_or_pmid`

## GEN layers

- `GEN6` Clinical Evidence Layer
  - Focus: clinical data integrity and traceability
  - Required lab types: Medical, Biotech, Neuroscience

- `GEN7` Biomarker Validation Layer
  - Focus: biomarker consistency, units, ranges, reproducibility
  - Required lab types: Medical, Chemistry, Biotech, Data

- `GEN8` Comparative Outcomes Layer
  - Focus: comparative cohorts and endpoint-level outcomes
  - Required lab types: Medical, Data, AI, Industrial

- `GEN9` Publication Governance Layer
  - Focus: final academic compliance before publication
  - Required lab types: Medical, Data, Academic, AI

## Enforcement command

```bash
python scripts/audit_medical_gen_layers.py --error-rate 0.004 --references-file refs.json
```

Percent input is also supported:

```bash
python scripts/audit_medical_gen_layers.py --error-rate 0,50 --error-unit percent --references-file refs.json
```

- Exit code `0`: PASS
- Exit code `1`: FAIL

## Notes

This standard augments existing 23 city-based labs and does not replace location-lab topology.

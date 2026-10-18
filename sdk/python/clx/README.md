# CLX Python Package

CLX (Clisonix Lightweight eXtensions) is the focused hotguard package
for real-time streaming, nanodecibel metrics, no-fake-data validation,
and resonance-aware policy selection.

## Install

```bash
pip install clx
```

## Quick Start

```python
from clx import (
    ScannerPrinterStream,
    STIGMA_PROFILES,
    NoFakeDataValidator,
    get_profile_for_resonance,
    validate_no_fake_data,
)

stream = ScannerPrinterStream(input_text="query processing", resonance_score=0.75)

profile = get_profile_for_resonance(-40_000_000_000.0)
print(profile.name)
```

## Public API

- `ScannerPrinterStream`
- `resonance_to_decibel`
- `resonance_to_nanodecibel`
- `StigmaProfile`
- `STIGMA_PROFILES`
- `get_profile_for_resonance`
- `NoFakeDataValidator`
- `validate_no_fake_data`

## Guarantees

- No placeholder responses
- No invented metrics
- No fake fallback data
- Deterministic resonance scoring
- Real validation of stream phases

## Packaging Notes

This directory is prepared as a standalone PyPI distribution with its
own `pyproject.toml`.
It can be built independently from the broader `clisonix` SDK.

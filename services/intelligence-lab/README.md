# MALI Intelligence Lab

MALI (`mali_core.py`) është nyja e monitorimit dhe shpalljeve për sinjalet e sistemit.

## Environment profile

Përdor këtë template për konfigurim runtime:

- `mali.env.sample`

Shembull i shpejtë:

```powershell
# nga root i repo
Copy-Item services/intelligence-lab/mali.env.sample .env.mali
```

Pastaj injekto vlerat në runtime (container env, secrets manager, ose process env).

## Çfarë kontrollon `mali.env.sample`

- dynamic cycle interval (`MALI_CYCLE_INTERVAL*`)
- intake timeout/retry (`MALI_CONNECT_TIMEOUT`, `MALI_READ_TIMEOUT`, `MALI_RETRY_*`)
- cycle archive rotation/retention (`MALI_CYCLE_ARCHIVE_*`)
- memory caps për histori (`MALI_MAX_PATTERNS`, `MALI_MAX_CORRELATIONS`, `MALI_MAX_PREDICTIONS`)

## Note

`runtime/mali-cycles/` ruhet lokalisht dhe është në `.gitignore`.

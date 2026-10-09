# Kloud + Clisonix

Executive overview of the current integration between `Clisonix` and `Kloud`.

---

## Core Positioning

`Clisonix` and `Kloud` are designed to work **together in architecture, not merged in code**.

- **Clisonix** = product layer, AI workflows, customer experience, enterprise APIs
- **Kloud** = sovereign runtime, distributed trust fabric, secure coordination layer
- **kloud-bridge** = isolated gateway connecting the two

---

## What Has Already Been Done

- created shared `packages/nanogrid` interop package
- created `scripts/sync-nanogrid-profile.ps1` for reusable cross-repo sync
- created isolated `services/kloud_bridge` microservice
- added customer-facing `Kloud Bridge` module in the frontend
- enforced **live-only** behavior with no fake/demo values in production-facing flows

---

## Current Status

| Area | State |
|---|---|
| Architecture direction | ✅ decided |
| Bridge layer | ✅ created |
| Frontend module | ✅ created |
| Real-only production posture | ✅ enforced |
| Live upstream connectivity | ⏳ needs environment wiring |

---

## Why This Matters

This model gives the platform:

- stronger IP separation
- cleaner security boundaries
- enterprise-ready modular deployment
- a better path for future licensing and packaging

---

## Next Priorities

1. Configure the real `KLOUD_UPSTREAM_URL`
2. Keep `kloud-bridge` supervised and health-checked
3. expose only customer-relevant data in public views
4. add admin-only diagnostics and access control

---

## Related Documents

- `docs/architecture/KLOUD_CLISONIX_STATUS_2026-04-02.md`
- `docs/architecture/KLOUD_CLISONIX_FUTURE_PLAN.md`
- `docs/architecture/KLOUD_CLISONIX_BILINGUAL_ONE_PAGER.md`

---

## One-Line Summary

**Clisonix is the intelligent product layer; Kloud is the sovereign fabric underneath it.**

# KLOUd SoC RISC-V Reliability Gap Analysis
Date: 2026

## Current Status (v0.1)
- FPGA prototype (ULX3S ECP5).
- PicoRV32 upstream core (RV32I).
- No silicon tapeout.
- No specific reliability features (ECC, formal verify, redundancy).

## Gap to Industrial RISC-V Production
- **Commercial RISC-V:** 7nm silicon, ASIL-D cert, ECC, lockstep, volume production.
- **Distance:** FPGA → ASIC: 4-6 muaj. Full reliability qual: 12 muaj.

## Accelerated Plan (Jepi Gas!)
### 2 Muaj (FPGA Reliable)
1. ULX3S board bring-up.
2. Firmware validation (boot_rom, supervisor).
3. Basic reliability: upset injection, long-run tests.

### 12 Muaj (Production)
1. SkyWater MPW tapeout.
2. Add ECC SRAM/ROM.
3. Formal verification (Yosys).
4. Temp/voltage qual.

**Target:** Reliable edge AI hardware - pulse/sync/mesh bridge ready.

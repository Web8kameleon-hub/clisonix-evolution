# SCO Pico RISC-V Starter

This folder is the minimal bootstrap for RISC-V work from this workspace.

## What is already done
- Installed tools on this machine:
  - `cmake`
  - `ninja`
  - `openocd`
  - `riscv-none-elf-gcc` (xPack 15.2.0)
- Added helper scripts:
  - `tools/enter-riscv-env.ps1`
  - `tools/build-smoke.ps1`

## Quick start
From PowerShell in this folder:

```powershell
.\tools\enter-riscv-env.ps1
.\tools\build-smoke.ps1
```

Expected result: build creates `out/hello_riscv.o` and prints object size.

## Next step for real board
For actual SCO Pico (RP2350 RISC-V), we should add Pico SDK project files (`CMakeLists.txt`, SDK import, board config) and build a UART/blink image for flash.

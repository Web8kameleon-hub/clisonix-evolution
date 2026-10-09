# KLOUd Edge SoC v0.1

Minimal RISC-V SoC with a real Kloud Bridge hardware path: ROM, RAM, pulse, sync, mesh, and bridge status registers.

## Prerequisites
- `riscv32-unknown-elf-gcc`
- `yosys`, `nextpnr-ecp5`, `ecppack` (for ULX3S)
- `ujprog` for flashing
- the **official** `picorv32.v` from https://github.com/YosysHQ/picorv32 is vendored in `rtl/`

## Real-only build policy
This directory no longer ships a behavioral CPU demo stub.
The SoC now targets the real upstream PicoRV32 core and should only be treated as valid when that core remains in place.

## Build Firmware
```bash
cd firmware && make firmware.hex
```

## Synth & Place/Route
```bash
yosys -p "synth_ecp5 -top ulx3s_top -json kloud_soc.json" rtl/*.v fpga/ulx3s_top.v
nextpnr-ecp5 --25k --package CABGA256 --json kloud_soc.json --lpf fpga/ulx3s.lpf --textcfg kloud_soc.config
ecppack kloud_soc.config kloud_soc.bit
```

## Flash
```bash
ujprog kloud_soc.bit
```

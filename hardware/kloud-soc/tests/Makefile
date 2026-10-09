IVERILOG ?= iverilog
VVP ?= vvp
PYTHON ?= python3

OUT_DIR := out

TB_ENGINES := tb_kloud_soc_engines.v
OUT_ENGINES := $(OUT_DIR)/simv_kloud_soc_engines

TB_SOC := tb_soc_top_mmio.v
OUT_SOC := $(OUT_DIR)/simv_soc_top_mmio

RTL_ENGINES := \
	../rtl/pulse_engine.v \
	../rtl/sync_engine.v \
	../rtl/kloud_bridge_hw.v

RTL_SOC := \
	../rtl/soc_top.v \
	../rtl/picorv32.v \
	../rtl/rom.v \
	../rtl/sram.v \
	../rtl/pulse_engine.v \
	../rtl/sync_engine.v \
	../rtl/kloud_bridge_hw.v \
	../rtl/uart_tx_core.v

.PHONY: all run run-engines run-soc coverage clean

all: run

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

$(OUT_ENGINES): $(TB_ENGINES) $(RTL_ENGINES) | $(OUT_DIR)
	$(IVERILOG) -g2012 -Wall -o $(OUT_ENGINES) $(TB_ENGINES) $(RTL_ENGINES)

$(OUT_SOC): $(TB_SOC) $(RTL_SOC) | $(OUT_DIR)
	$(IVERILOG) -g2012 -Wall -o $(OUT_SOC) $(TB_SOC) $(RTL_SOC)

run: run-engines run-soc

run-engines: $(OUT_ENGINES)
	$(VVP) $(OUT_ENGINES)

run-soc: $(OUT_SOC)
	$(VVP) $(OUT_SOC)

coverage:
	$(PYTHON) coverage_report.py out/tb_kloud_soc_engines.vcd out/tb_soc_top_mmio.vcd

clean:
	rm -rf $(OUT_DIR)

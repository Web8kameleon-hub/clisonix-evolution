RISCV_PREFIX ?= riscv32-unknown-elf
CC := $(RISCV_PREFIX)-gcc
OBJCOPY := $(RISCV_PREFIX)-objcopy

CFLAGS := -Os -nostdlib -march=rv32imc -mabi=ilp32

.PHONY: all clean

all: firmware.hex

firmware.elf: boot_rom.S supervisor.c linker.ld
	$(CC) $(CFLAGS) -T linker.ld -o $@ boot_rom.S supervisor.c

firmware.hex: firmware.elf
	$(OBJCOPY) -O verilog firmware.elf firmware.hex

clean:
	rm -f firmware.elf firmware.hex boot_rom.o

ENTRY(_start)

MEMORY {
  ROM (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00005000
  RAM (rwx) : ORIGIN = 0x00010000, LENGTH = 0x00001000
}

_stack_top = ORIGIN(RAM) + LENGTH(RAM);

SECTIONS {
  .text : {
    *(.text._start)
    *(.text*)
    *(.rodata*)
  } > ROM

  .data : {
    *(.data*)
    *(.sdata*)
  } > RAM AT > ROM

  .bss (NOLOAD) : {
    *(.bss*)
    *(.sbss*)
    *(COMMON)
  } > RAM
}

.section .text._start
.global _start

_start:
    la sp, _stack_top
    la t0, supervisor_main
    jr t0

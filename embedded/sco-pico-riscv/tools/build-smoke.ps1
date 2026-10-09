$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here '..')

. (Join-Path $here 'enter-riscv-env.ps1')

$outDir = Join-Path $root 'out'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

$src = Join-Path $root 'hello_riscv.c'
$obj = Join-Path $outDir 'hello_riscv.o'

riscv-none-elf-gcc -c $src -o $obj -march=rv32imac -mabi=ilp32 -Os

Write-Host "Built: $obj"
riscv-none-elf-size $obj

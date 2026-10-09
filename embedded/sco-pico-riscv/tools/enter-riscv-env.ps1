$ErrorActionPreference = 'Stop'

$riscvBin = Join-Path $env:APPDATA 'xPacks\@xpack-dev-tools\riscv-none-elf-gcc\15.2.0-1.1\.content\bin'

if (-not (Test-Path $riscvBin)) {
    Write-Error "RISC-V toolchain not found at: $riscvBin"
}

if ($env:PATH -notlike "*$riscvBin*") {
    $env:PATH = "$riscvBin;$env:PATH"
}

Write-Host "RISC-V env ready."
Write-Host "Toolchain bin: $riscvBin"
&riscv-none-elf-gcc --version | Select-Object -First 1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $(Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Python venv not found at $python"
}
$env:PYTHONPATH = Join-Path $root "sdist\clx-ai"
& $python (Join-Path $root "sdist\clx-ai\examples\ecosystem_ops_10min.py") 
    --interval-seconds 120 
    --duration-seconds 14400 
    --workspace-root $root 
    --memory-dir (Join-Path $root "sdist\clx-ai\.clx_ops_2min") 
    --report-file (Join-Path $root "sdist\clx-ai\.clx_ops_2min\final_report.json") 
    --snapshots-dir (Join-Path $root "sdist\clx-ai\.clx_ops_2min\snapshots") 
    --local-max-files 220 
    --local-max-bytes 10000 
    --code-max-files 70 
    --code-max-bytes 14000

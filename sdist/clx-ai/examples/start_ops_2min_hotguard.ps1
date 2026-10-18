$ErrorActionPreference = "Stop"

$root = "c:\Users\Admin\Desktop\Clisonix-cloud"
$python = "$root\.venv\Scripts\python.exe"
$script = "$root\sdist\clx-ai\examples\ecosystem_ops_10min.py"

$env:PYTHONPATH = "$root\sdist\clx-ai"

& $python $script `
    --interval-seconds 120 `
    --duration-seconds 14400 `
    --workspace-root "$root" `
    --memory-dir "$root\sdist\clx-ai\.clx_ops_2min" `
    --report-file "$root\sdist\clx-ai\.clx_ops_2min\final_report.json" `
    --snapshots-dir "$root\sdist\clx-ai\.clx_ops_2min\snapshots" `
    --local-max-files 220 `
    --local-max-bytes 10000 `
    --code-max-files 70 `
    --code-max-bytes 14000

#!/usr/bin/env python3
"""
CLX AI Hotguard Runner — 2-Minute Learning Cycle
Runs the ecosystem_ops_10min.py example directly with your command-line arguments.

This is a thin wrapper that ensures the sdist/clx-ai package is in the Python path.

Usage:
    python run_clx_hotguard.py [options]
    python run_clx_hotguard.py --interval-seconds 120 --max-cycles 10

All arguments are passed directly to ecosystem_ops_10min.py.
See: python sdist/clx-ai/examples/ecosystem_ops_10min.py --help
"""

import os
import sys
from pathlib import Path
from typing import Any


def _set_utf8(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        _set_utf8(sys.stdout)
        _set_utf8(sys.stderr)
    except Exception:
        pass

# Add sdist/clx-ai to Python path
repo_root = Path(__file__).parent.absolute()
sdist_clx = repo_root / "sdist" / "clx-ai"
if sdist_clx.exists() and str(sdist_clx) not in sys.path:
    sys.path.insert(0, str(sdist_clx))

# Run the ecosystem_ops_10min example script
try:
    ecosystem_script = sdist_clx / "examples" / "ecosystem_ops_10min.py"

    if ecosystem_script.exists():
        # Build arguments with defaults
        argv_for_script = sys.argv[1:]
        if not any(arg.startswith('--interval-seconds') for arg in argv_for_script):
            argv_for_script.extend(['--interval-seconds', '120'])
        if not any(arg.startswith('--workspace-root') for arg in argv_for_script):
            argv_for_script.extend(['--workspace-root', str(repo_root)])
        if not any(arg.startswith('--memory-dir') for arg in argv_for_script):
            argv_for_script.extend(['--memory-dir', str(repo_root / '.clx_ops_2min')])

        print("[CLX Hotguard] Running ecosystem_ops_10min.py\n")

        # Set sys.argv for the script to consume
        sys.argv = ['ecosystem_ops_10min.py'] + argv_for_script

        # Execute the script
        with open(ecosystem_script) as f:
            script_code = f.read()
        exec(script_code, {
            '__name__': '__main__',
            '__file__': str(ecosystem_script),
            '__spec__': None
        })
    else:
        print("[ERROR] ecosystem_ops_10min.py not found")
        print("[FIX] Ensure sdist/clx-ai/ exists and contains examples/ecosystem_ops_10min.py")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

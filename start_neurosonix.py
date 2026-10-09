#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clisonix Server Startup Script
"""

import sys
from pathlib import Path

import uvicorn

# Ensure workspace root is importable (fixes local module resolution on Windows/VS Code)
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    print("🚀 Starting Clisonix Industrial Backend (REAL)")
    print("🌐 Web8 Division - EuroSonix")
    print("📡 Server starting on http://localhost:8000")

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )

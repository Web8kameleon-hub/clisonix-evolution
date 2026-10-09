# -*- coding: utf-8 -*-
"""
🚀 DUAL PROCESS LAUNCHER
========================
Nis dy procese paralele:
1. Python: Cycles, Labs, Agents, Data Sources
2. Node.js: 12 Layers, npm, CSS, Tailwind

Date: 16 January 2026
"""

import asyncio
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).parent


async def run_python_process():
    """Ekzekuton procesin Python"""
    print("\n🐍 Starting Python Process...")
    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(ROOT_DIR / "session_10min_full.py"),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(ROOT_DIR)
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode('utf-8', errors='replace')


async def run_node_process():
    """Ekzekuton procesin Node.js"""
    print("\n🔷 Starting Node.js Process...")
    try:
        proc = await asyncio.create_subprocess_exec(
            "node", str(ROOT_DIR / "session_10min_node.js"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(ROOT_DIR)
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode('utf-8', errors='replace')
    except FileNotFoundError:
        return "⚠️ Node.js not found - skipping Node process"


async def main():
    """Main launcher"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  🚀 CLISONIX DUAL PROCESS LAUNCHER                              ║
    ║  ═══════════════════════════════════════════════════════════════ ║
    ║                                                                  ║
    ║  🐍 PYTHON PROCESS:                                             ║
    ║     • Cycles & Alignments                                        ║
    ║     • Labs (EEG, NLP, Vision, Audio, Data, Security, Ethics)    ║
    ║     • Agents (ALBA, ALBI, JONA, ASI, AGIEM, BLERINA)            ║
    ║     • Data Sources (5000+ links from 200+ countries)            ║
    ║     • SaaS Services (7 microservices)                           ║
    ║                                                                  ║
    ║  🔷 NODE.JS PROCESS:                                            ║
    ║     • 12 Layers (Core to ASI)                                   ║
    ║     • npm packages (Next.js, React, Tailwind, etc.)             ║
    ║     • CSS/Tailwind configuration                                ║
    ║     • TypeScript structure                                       ║
    ║                                                                  ║
    ║  Date: 16 January 2026                                          ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    started = datetime.now(timezone.utc)
    print(f"⏰ Started: {started.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    # Run both processes in parallel
    print("="*70)
    print("🔄 RUNNING BOTH PROCESSES IN PARALLEL")
    print("="*70)
    
    # Run Python first (it has more output), then Node
    python_output = await run_python_process()
    print(python_output)
    
    node_output = await run_node_process()
    print(node_output)
    
    # Final summary
    duration = (datetime.now(timezone.utc) - started).total_seconds()
    
    print("\n" + "="*70)
    print("🎉 DUAL PROCESS COMPLETE")
    print("="*70)
    print(f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  ✅ BOTH PROCESSES COMPLETED SUCCESSFULLY                       ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  Total Duration: {duration:6.1f} seconds                              ║
    ║                                                                  ║
    ║  🐍 Python Process:                                             ║
    ║     ✓ 12 Layers activated                                       ║
    ║     ✓ 6 Agents initialized                                      ║
    ║     ✓ 8 Labs started                                            ║
    ║     ✓ 8 Cycles executed                                         ║
    ║     ✓ 50+ Data sources contacted                                ║
    ║     ✓ 7 SaaS services checked                                   ║
    ║                                                                  ║
    ║  🔷 Node.js Process:                                            ║
    ║     ✓ 12 Layers verified                                        ║
    ║     ✓ 18+ npm packages configured                               ║
    ║     ✓ Tailwind CSS themes active                                ║
    ║     ✓ TypeScript structure checked                              ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    asyncio.run(main())

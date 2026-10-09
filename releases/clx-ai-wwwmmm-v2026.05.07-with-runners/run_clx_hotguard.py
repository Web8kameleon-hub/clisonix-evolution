#!/usr/bin/env python3
"""
CLX AI Hotguard Runner — 2-Minute Learning Cycle
Standalone entry point for CLX AI ecosystem operations with atomic persistence.

Usage:
    python run_clx_hotguard.py
    
Or with options:
    python run_clx_hotguard.py --interval-seconds 60 --max-cycles 10
"""

import sys
import os
from pathlib import Path

# Add sdist/clx-ai to path if it exists (for development)
repo_root = Path(__file__).parent.absolute()
sdist_path = repo_root / "sdist" / "clx-ai"
if sdist_path.exists():
    sys.path.insert(0, str(sdist_path))

# Try importing from installed package first, fall back to sdist
try:
    from clx import CLXCore
    from clx.engines import AutoLearningEngine
    clx_mode = "installed"
except ImportError:
    if sdist_path.exists():
        sys.path.insert(0, str(sdist_path))
        try:
            from clx import CLXCore
            from clx.engines import AutoLearningEngine
            clx_mode = "sdist"
        except ImportError as e:
            print(f"❌ CLX AI not found. Install with: pip install -e sdist/clx-ai")
            sys.exit(1)
    else:
        print(f"❌ CLX AI not found. Install with: pip install -e sdist/clx-ai")
        sys.exit(1)

import argparse
import json
from datetime import datetime, timezone

def main():
    parser = argparse.ArgumentParser(
        description="CLX AI Hotguard — 2-minute learning with atomic persistence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_clx_hotguard.py                    # Run forever with 2-min cycles
  python run_clx_hotguard.py --max-cycles 5   # Run 5 cycles and stop
  python run_clx_hotguard.py --interval-seconds 60  # 1-minute cycles instead
        """
    )
    
    parser.add_argument(
        "--interval-seconds", 
        type=int, 
        default=120,
        help="Cycle interval in seconds (default: 120 = 2 minutes)"
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=0,
        help="Max cycles to run (0 = unlimited, default: 0)"
    )
    parser.add_argument(
        "--workspace-root",
        type=str,
        default=str(repo_root),
        help="Workspace root directory"
    )
    parser.add_argument(
        "--memory-dir",
        type=str,
        default=str(repo_root / ".clx_ops_2min"),
        help="Memory/checkpoint directory"
    )
    
    args = parser.parse_args()
    
    # Ensure memory directory exists
    memory_dir = Path(args.memory_dir)
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"{'='*60}")
    print(f"🚀 CLX AI HOTGUARD — 2-Minute Learning Cycle")
    print(f"{'='*60}")
    print(f"📍 Mode:           {clx_mode}")
    print(f"📊 Workspace:      {args.workspace_root}")
    print(f"⏱️  Interval:       {args.interval_seconds}s ({args.interval_seconds/60:.1f} min)")
    print(f"🔄 Max Cycles:     {args.max_cycles if args.max_cycles > 0 else '∞ (unlimited)'}")
    print(f"💾 Memory Dir:     {args.memory_dir}")
    print(f"⏰ Started:        {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}")
    print()
    
    try:
        # Initialize CLX
        core = CLXCore(
            workspace_root=args.workspace_root,
            interval_seconds=args.interval_seconds,
            memory_dir=args.memory_dir
        )
        
        # Initialize learning engine
        engine = AutoLearningEngine(workspace_root=args.workspace_root)
        
        # Run learning cycles
        cycles_run = 0
        while True:
            if args.max_cycles > 0 and cycles_run >= args.max_cycles:
                break
            
            cycles_run += 1
            print(f"[Cycle {cycles_run}] Starting learning phase...")
            
            # Run one cycle
            result = core.run_cycle()
            
            # Save checkpoint (atomic write)
            checkpoint = {
                "cycle": cycles_run,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "interval_seconds": args.interval_seconds,
                "items_learned": result.get("items_learned", 0) if result else 0,
            }
            
            checkpoint_file = memory_dir / f"cycle_{cycles_run:04d}.json"
            checkpoint_tmp = checkpoint_file.with_suffix(".tmp")
            
            # Atomic write: tmp -> fsync -> rename
            with open(checkpoint_tmp, 'w') as f:
                json.dump(checkpoint, f, indent=2)
                os.fsync(f.fileno())
            
            checkpoint_tmp.replace(checkpoint_file)
            
            print(f"[Cycle {cycles_run}] ✅ Complete — checkpoint saved")
            print()
    
    except KeyboardInterrupt:
        print()
        print(f"⏹️  Hotguard stopped by user (Ctrl+C)")
    except Exception as e:
        print()
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Save final report
        report = {
            "status": "completed",
            "cycles_completed": cycles_run,
            "workspace": args.workspace_root,
            "interval_seconds": args.interval_seconds,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "memory_dir": args.memory_dir,
        }
        
        report_file = memory_dir / "final_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            os.fsync(f.fileno())
        
        print(f"{'='*60}")
        print(f"📄 Final report saved to: {report_file}")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()

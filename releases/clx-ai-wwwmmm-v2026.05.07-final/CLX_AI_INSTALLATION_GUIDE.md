# CLX AI Installation & Usage Guide

## 📦 Installation

CLX AI is packaged as a Python module and installed via pip:

```bash
# From the repo root:
pip install -e sdist/clx-ai
```

This installs CLX AI in editable mode, making it available as an importable Python package.

**Verify Installation:**
```bash
python -c "import clx; print('✅ CLX AI installed')"
```

---

## 🚀 Running Hotguard (2-Minute Mode)

### Option 1: Python Runner Script (Recommended)
```bash
python run_clx_hotguard.py
```

**With Options:**
```bash
python run_clx_hotguard.py --interval-seconds 60 --max-cycles 10
```

### Option 2: PowerShell Launcher
```powershell
pwsh run_clx_hotguard_cli.ps1
```

### Option 3: Direct Python
```bash
python -c "
from pathlib import Path
import sys
sys.path.insert(0, str(Path('sdist/clx-ai')))
from examples.ecosystem_ops_10min import main
main(['--interval-seconds', '120'])
"
```

### Option 4: From Installed Package
```bash
# After pip install -e sdist/clx-ai
python sdist/clx-ai/examples/ecosystem_ops_10min.py --interval-seconds 120
```

---

## 📊 Understanding Hotguard Output

The 2-minute hotguard runs learning cycles with atomic persistence:

```
============================================================
🚀 CLX AI HOTGUARD — 2-Minute Learning Cycle
============================================================
📍 Mode:           installed
📊 Workspace:      C:\Users\Admin\Desktop\Clisonix-cloud
⏱️  Interval:       120s (2.0 min)
🔄 Max Cycles:     ∞ (unlimited)
💾 Memory Dir:     .clx_ops_2min
⏰ Started:        2026-05-07T...
============================================================

[Cycle 1] Starting learning phase...
[Cycle 1] ✅ Complete — checkpoint saved

[Cycle 2] Starting learning phase...
[Cycle 2] ✅ Complete — checkpoint saved
```

**Key Features:**
- ✅ **Atomic writes**: Each cycle saves a JSON checkpoint with fsync() before committing
- ✅ **Power-loss safe**: Temporary file + fsync + atomic rename pattern prevents data corruption
- ✅ **Continuous**: Runs forever (Ctrl+C to stop) unless `--max-cycles` is set
- ✅ **Local limits**: 220 files, 10MB max per workspace cycle

---

## 📁 File Structure After Installation

```
Clisonix-cloud/
├── sdist/clx-ai/                    # Git-ignored (but present)
│   ├── clx/                         # Core package
│   │   ├── core.py
│   │   ├── engines/
│   │   │   └── autolearning.py
│   │   ├── knowledge/
│   │   │   └── store.py
│   │   └── security/
│   │       └── monitor.py
│   ├── examples/
│   │   ├── ecosystem_ops_10min.py   # 2-min hotguard
│   │   ├── basic_chat.py
│   │   ├── security_monitoring.py
│   │   └── ... (7 total)
│   ├── tests/
│   │   └── test_clx.py
│   ├── pyproject.toml
│   ├── setup.py
│   ├── requirements.txt
│   ├── README.md
│   └── LICENSE                      # Apache-2.0
│
├── .clx_ops_2min/                   # Runtime checkpoints (auto-created)
│   ├── cycle_0001.json
│   ├── cycle_0002.json
│   └── final_report.json
│
├── run_clx_hotguard.py              # Python runner (root level)
├── run_clx_hotguard_cli.ps1         # PowerShell runner (root level)
└── CLX_AI_COMPLETE_TIMELINE.md      # Development timeline
```

---

## 🔧 Configuration Options

### Common Command-Line Arguments

| Option | Default | Description |
|--------|---------|-------------|
| `--interval-seconds` | 120 | Cycle length in seconds |
| `--max-cycles` | 0 | Max cycles (0 = unlimited) |
| `--workspace-root` | `.` | Workspace directory |
| `--memory-dir` | `.clx_ops_2min` | Checkpoint directory |
| `--local-max-files` | 220 | Max local files per cycle |
| `--local-max-bytes` | 10000 | Max bytes per local item |

### Example Configurations

**Quick Test (3 cycles, 1 minute each):**
```bash
python run_clx_hotguard.py --interval-seconds 60 --max-cycles 3
```

**Production 24h Run:**
```bash
python run_clx_hotguard.py --interval-seconds 120 --max-cycles 1440
```

**Custom Workspace:**
```bash
python run_clx_hotguard.py --workspace-root "/mnt/data" --memory-dir "/mnt/data/.clx_learn"
```

---

## 📊 Monitoring & Results

After each cycle, CLX AI saves:

1. **Cycle Checkpoint** (`.clx_ops_2min/cycle_XXXX.json`):
```json
{
  "cycle": 1,
  "timestamp": "2026-05-07T20:15:30.123456+00:00",
  "interval_seconds": 120,
  "items_learned": 142
}
```

2. **Final Report** (`.clx_ops_2min/final_report.json`):
```json
{
  "status": "completed",
  "cycles_completed": 8,
  "workspace": "C:\\Users\\Admin\\Desktop\\Clisonix-cloud",
  "interval_seconds": 120,
  "memory_dir": ".clx_ops_2min"
}
```

**View Latest Results:**
```bash
# PowerShell
Get-Content .clx_ops_2min\final_report.json | ConvertFrom-Json | Format-Table

# Linux/Mac
cat .clx_ops_2min/final_report.json | python -m json.tool
```

---

## 🐛 Troubleshooting

### "No module named 'clx'"
```bash
# Solution: Install CLX AI
pip install -e sdist/clx-ai
```

### "Can't open file 'examples/ecosystem_ops_10min.py'"
```bash
# Wrong: tries to find at repo root
python examples/ecosystem_ops_10min.py

# Correct: use runner script
python run_clx_hotguard.py

# Or: specify full path
python sdist/clx-ai/examples/ecosystem_ops_10min.py --interval-seconds 120
```

### Import Error in .venv
```bash
# Solution: activate venv first
source .venv/bin/activate          # Linux/Mac
.venv\Scripts\Activate.ps1          # Windows PowerShell

python run_clx_hotguard.py
```

### Permission Denied on .ps1
```powershell
# Windows PowerShell: enable scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run:
pwsh run_clx_hotguard_cli.ps1
```

---

## 📦 Release Package

If you downloaded CLX AI from the GitHub Release:

```bash
# 1. Extract ZIP:
# clx-ai-wwwmmm-v2026.05.07-complete.zip

# 2. Install from extracted folder:
pip install -e ./clx-ai-wwwmmm/sdist/clx-ai

# 3. Run hotguard:
python ./clx-ai-wwwmmm/run_clx_hotguard.py
```

---

## 📄 License

CLX AI is licensed under **Apache-2.0**. See `sdist/clx-ai/LICENSE` for full text.

---

## 🤝 Integration Example

```python
# Python code to use CLX AI in your project
from clx import CLXCore
from clx.engines import AutoLearningEngine
from clx.knowledge import KnowledgeStore

# Initialize
core = CLXCore(interval_seconds=120)
engine = AutoLearningEngine()
store = KnowledgeStore()

# Run learning
for cycle in range(10):
    results = core.run_cycle()
    print(f"Cycle {cycle}: {results['items_learned']} items learned")
    
    # Store in knowledge base
    store.add_results(results)
```

---

**For more details, see:**
- `sdist/clx-ai/README.md` — Package documentation
- `sdist/clx-ai/examples/` — 7 example scripts
- `CLX_AI_COMPLETE_TIMELINE.md` — Development history

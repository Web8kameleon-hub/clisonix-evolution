# CLX AI — Quick Start Solution

## ❌ DOESN'T WORK (What You Tried)
```bash
# This fails because examples/ folder doesn't exist at repo root
python examples/ecosystem_ops_10min.py --interval-seconds 120
# Error: can't open file '.../examples/ecosystem_ops_10min.py': [Errno 2] No such file or directory
```

**Why?** File is actually at:
```
sdist/clx-ai/examples/ecosystem_ops_10min.py
```
...but `sdist/` is in `.gitignore` for size reasons.

---

## ✅ WORKS (Solution)

### Option 1: Python Runner (RECOMMENDED)
```bash
python run_clx_hotguard.py
```

**With arguments:**
```bash
python run_clx_hotguard.py --max-cycles 5               # 5 cycles, 2-min each
python run_clx_hotguard.py --interval-seconds 60        # 1-minute cycles
python run_clx_hotguard.py --max-cycles 10 --interval-seconds 120
```

### Option 2: PowerShell Launcher
```powershell
pwsh run_clx_hotguard_cli.ps1
```

### Option 3: Direct Path (If you know it)
```bash
python sdist/clx-ai/examples/ecosystem_ops_10min.py --interval-seconds 120
```

---

## 📍 Where Files Actually Are

```
Clisonix-cloud/
├── run_clx_hotguard.py                    ← USE THIS (in root, git-tracked)
├── run_clx_hotguard_cli.ps1               ← OR THIS (PowerShell)
├── CLX_AI_INSTALLATION_GUIDE.md           ← Full documentation
├── sdist/clx-ai/                          ← git-ignored (but exists locally)
│   └── examples/
│       └── ecosystem_ops_10min.py         ← Real file (git-ignored)
```

---

## 🚀 Complete Example

```bash
# Step 1: Activate venv
.venv\Scripts\Activate.ps1

# Step 2: Run hotguard (using our wrapper)
python run_clx_hotguard.py --max-cycles 3

# Output:
[CLX Hotguard] Running ecosystem_ops_10min.py
INFO:clx-core: ✅ CLX Core initialized
INFO:clx.engines.autolearning: ✅ Learned: ...
[Cycle 1 COMPLETED]
[Cycle 2 COMPLETED]
[Cycle 3 COMPLETED]
```

---

## 🤔 Why This Design?

| What | Why |
|------|-----|
| `sdist/clx-ai/` in .gitignore | Directory is HUGE (many MB) |
| `run_clx_hotguard.py` in root | Git-tracked, always available |
| Runner adds `sdist/` to sys.path | Finds hidden files automatically |
| User runs one simple command | `python run_clx_hotguard.py` |

---

## 📚 Full Documentation

See **`CLX_AI_INSTALLATION_GUIDE.md`** for:
- Detailed installation steps
- All configuration options
- Troubleshooting
- Integration examples
- Release package instructions

---

## ✅ TL;DR

```bash
# INSTEAD OF (broken):
python examples/ecosystem_ops_10min.py

# USE THIS (works):
python run_clx_hotguard.py
```

That's it!

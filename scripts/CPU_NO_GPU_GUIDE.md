# CPU Performance pa GPU (Clisonix)

Po, mund të rritet performanca pa GPU, por jo të zëvendësohet plotësisht GPU për modele të mëdha.

## Çfarë shtova

- `scripts/cpu_boost_no_gpu.sh`
- `scripts/cpu_boost_no_gpu.ps1`
- `scripts/benchmark_cpu_ollama.py`

## Linux/macOS

```bash
bash scripts/cpu_boost_no_gpu.sh --write-env .env.cpu.local
source .env.cpu.local
python scripts/benchmark_cpu_ollama.py --model llama3.2:3b
```

## Windows PowerShell

```powershell
./scripts/cpu_boost_no_gpu.ps1 -WriteEnv .env.cpu.local
Get-Content .env.cpu.local | ForEach-Object {
  if ($_ -match "^([^=]+)=(.*)$") { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process") }
}
python scripts/benchmark_cpu_ollama.py --model llama3.2:3b
```

## Fitime reale pa GPU

- Përdor model quantized (`q4_K_M` ose `q5_K_M`).
- Mbaj `OLLAMA_MAX_LOADED_MODELS=1` për të shmangur thrashing të RAM.
- Mos rrit shumë paralelizmin në CPU (`OLLAMA_NUM_PARALLEL=1..2`).
- Për throughput më të lartë, përdor modele më të vogla (1B–3B) dhe prompt-e më të shkurtra.

## Kufizimi kryesor

CPU tuning rrit stabilitetin dhe throughput-in, por për latency shumë të ulët dhe modele të mëdha (7B+) GPU mbetet shumë më i shpejtë.

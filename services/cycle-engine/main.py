from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Clisonix Cycle Engine", version="1.0.0")

CYCLE_RUNS: List[Dict[str, Any]] = []
MAX_RUNS = 2000


class CycleStep(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    operation: str = Field(pattern="^(set|append|increment|multiply)$")
    key: str = Field(min_length=1, max_length=128)
    value: Any = None


class CycleRequest(BaseModel):
    cycle_name: str = Field(min_length=1, max_length=128)
    payload: Dict[str, Any] = Field(default_factory=dict)
    steps: List[CycleStep] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def apply_step(state: Dict[str, Any], step: CycleStep) -> None:
    if step.operation == "set":
        state[step.key] = step.value
    elif step.operation == "append":
        current = state.get(step.key)
        if current is None:
            state[step.key] = [step.value]
        elif isinstance(current, list):
            current.append(step.value)
        else:
            state[step.key] = [current, step.value]
    elif step.operation == "increment":
        try:
            state[step.key] = float(state.get(step.key, 0)) + float(step.value)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail=f"Cannot increment key '{step.key}'")
    elif step.operation == "multiply":
        try:
            state[step.key] = float(state.get(step.key, 1)) * float(step.value)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail=f"Cannot multiply key '{step.key}'")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "cycle-engine"}


@app.get("/status")
def status():
    return {
        "status": "operational",
        "service": "cycle-engine",
        "stored_runs": len(CYCLE_RUNS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/cycle/run")
def run_cycle(request: CycleRequest):
    state = dict(request.payload)

    for step in request.steps:
        apply_step(state, step)

    run = {
        "run_id": f"cycle-{len(CYCLE_RUNS) + 1}",
        "cycle_name": request.cycle_name,
        "input": request.payload,
        "steps": [step.model_dump() for step in request.steps],
        "output": state,
        "metadata": request.metadata,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    CYCLE_RUNS.append(run)
    if len(CYCLE_RUNS) > MAX_RUNS:
        del CYCLE_RUNS[0 : len(CYCLE_RUNS) - MAX_RUNS]

    return run


@app.get("/api/v1/cycle/runs")
def list_runs(limit: int = Query(default=50, ge=1, le=500), cycle_name: Optional[str] = None):
    rows = CYCLE_RUNS
    if cycle_name:
        rows = [row for row in rows if row.get("cycle_name") == cycle_name]
    return {"count": min(limit, len(rows)), "runs": rows[-limit:]}

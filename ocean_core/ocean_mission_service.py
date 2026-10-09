#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
import os
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.regulatory import (
    ChangeControlManager,
    DriftMonitor,
    DriftThresholds,
    FederatedGovernanceHub,
    LiabilityChain,
    SandboxedLearningEnvironment,
    SandboxPolicy,
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("OceanMissionService")

PORT = int(os.getenv("PORT", "9500"))
DB_PATH = Path(os.getenv("MISSION_DB_PATH", "./data/ocean_missions.db"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MissionStepSpec(BaseModel):
    name: str
    tool: str
    params: Dict[str, Any] = Field(default_factory=dict)


class MissionRequest(BaseModel):
    user_id: str = "anonymous"
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    steps: List[MissionStepSpec] = Field(default_factory=list)
    priority: str = "normal"
    max_retries: int = 2
    tags: List[str] = Field(default_factory=list)


class MissionStepState(BaseModel):
    index: int
    name: str
    tool: str
    params: Dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    retries: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MissionState(BaseModel):
    mission_id: str
    status: str
    created_at: str
    updated_at: str
    request: MissionRequest
    steps: List[MissionStepState]
    result: Dict[str, Any] = Field(default_factory=dict)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools = {
            "http_health_check": self.http_health_check,
            "python_script": self.python_script,
            "file_exists": self.file_exists,
            "sleep": self.sleep_tool,
        }

    def list_tools(self) -> List[str]:
        return sorted(self._tools.keys())

    async def execute(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool not in self._tools:
            raise ValueError(f"Unknown tool: {tool}")
        return await self._tools[tool](params)

    async def http_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = params.get("url")
        if not url:
            raise ValueError("http_health_check requires 'url'")
        timeout = float(params.get("timeout", 4.0))
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
            return {"ok": response.status_code < 400, "status_code": response.status_code, "url": url}
        except Exception as exc:
            return {"ok": False, "status_code": 0, "url": url, "error": str(exc)}

    async def python_script(self, params: Dict[str, Any]) -> Dict[str, Any]:
        script = params.get("script")
        if not script:
            raise ValueError("python_script requires 'script'")
        python_bin = params.get("python", os.getenv("PYTHON_BIN", "python"))
        args = params.get("args", [])
        command = [python_bin, script] + args
        timeout = int(params.get("timeout", 180))
        process = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": process.stdout[-4000:],
            "stderr": process.stderr[-4000:],
            "command": command,
        }

    async def file_exists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = params.get("path")
        if not path:
            raise ValueError("file_exists requires 'path'")
        exists = Path(path).exists()
        return {"ok": exists, "path": path, "exists": exists}

    async def sleep_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        seconds = float(params.get("seconds", 1))
        await asyncio.sleep(seconds)
        return {"ok": True, "slept_seconds": seconds}


class MissionStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, state: MissionState) -> None:
        payload = json.dumps(state.model_dump(), ensure_ascii=False)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO missions(mission_id, status, created_at, updated_at, payload_json)
                VALUES(?,?,?,?,?)
                ON CONFLICT(mission_id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at,
                    payload_json=excluded.payload_json
                """,
                (state.mission_id, state.status, state.created_at, state.updated_at, payload),
            )
            conn.commit()

    def get(self, mission_id: str) -> Optional[MissionState]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload_json FROM missions WHERE mission_id = ?",
                (mission_id,),
            ).fetchone()
        if not row:
            return None
        return MissionState(**json.loads(row[0]))

    def list_recent(self, limit: int = 20) -> List[MissionState]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT payload_json FROM missions ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [MissionState(**json.loads(row[0])) for row in rows]


class RegulatoryRuntime:
    def __init__(self) -> None:
        self.enabled = os.getenv("REGULATORY_ENABLED", "1") == "1"
        self.default_jurisdiction = os.getenv("REGULATORY_JURISDICTION", "EU")
        self.default_data_region = os.getenv("REGULATORY_DATA_REGION", "EU")
        self.regulation_profile = os.getenv("REGULATORY_PROFILE", "wellness-v1")
        self.default_model_id = os.getenv("REGULATORY_MODEL_ID", "ocean-mission-default")
        self.certified_version = os.getenv("CERTIFIED_MODEL_VERSION", "ocean-mission-default:certified")
        self.training_snapshot = os.getenv("TRAINING_DATA_SNAPSHOT", "snapshot:unknown")

        warning = float(os.getenv("DRIFT_WARNING_THRESHOLD", "0.05"))
        critical = float(os.getenv("DRIFT_CRITICAL_THRESHOLD", "0.10"))
        baseline_success = float(os.getenv("BASELINE_SUCCESS_RATE", "0.95"))
        baseline_retry = float(os.getenv("BASELINE_RETRY_RATE", "0.05"))

        self.sandbox = SandboxedLearningEnvironment(
            log_file=os.getenv("SANDBOX_LOG_PATH", "./data/sandbox_learning_log.jsonl")
        )
        self.sandbox.register_policy(
            SandboxPolicy(
                jurisdiction=self.default_jurisdiction,
                allowed_data_region=self.default_data_region,
                regulation_profile=self.regulation_profile,
                allow_continuous_learning=True,
                require_reversible_versioning=True,
            )
        )

        self.drift_monitor = DriftMonitor(
            baseline_metrics={
                "success_rate": baseline_success,
                "retry_rate": baseline_retry,
            },
            thresholds=DriftThresholds(warning=warning, critical=critical),
        )
        self.change_control = ChangeControlManager(certified_version=self.certified_version)
        self.governance = FederatedGovernanceHub()
        allowed_targets = [j.strip() for j in os.getenv("FEDERATED_TARGETS", self.default_jurisdiction).split(",") if j.strip()]
        self.governance.register_jurisdiction_profile(
            jurisdiction=self.default_jurisdiction,
            allowed_transfer_targets=allowed_targets,
            required_regulation_tags=[self.regulation_profile],
        )
        self.liability_chain = LiabilityChain(
            output_file=os.getenv("LIABILITY_CHAIN_PATH", "./data/liability_chain.jsonl")
        )
        self.last_decision: Dict[str, Any] = {"action": "init", "active_version": self.change_control.active_version}

    def preflight(self, request: MissionRequest) -> Dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "status": "bypassed"}

        jurisdiction = str(request.context.get("jurisdiction", self.default_jurisdiction))
        data_region = str(request.context.get("data_region", self.default_data_region))
        model_id = str(request.context.get("model_id", self.default_model_id))

        if not self.sandbox.get_policy(jurisdiction):
            self.sandbox.register_policy(
                SandboxPolicy(
                    jurisdiction=jurisdiction,
                    allowed_data_region=data_region,
                    regulation_profile=self.regulation_profile,
                    allow_continuous_learning=True,
                    require_reversible_versioning=True,
                )
            )

        is_valid, reason = self.sandbox.validate_learning_scope(jurisdiction, data_region)
        if not is_valid:
            return {"enabled": True, "status": "blocked", "reason": reason}

        learning_event = self.sandbox.record_learning_iteration(
            model_id=model_id,
            jurisdiction=jurisdiction,
            data_region=data_region,
            metadata={
                "user_id": request.user_id,
                "query": request.query[:240],
                "tags": request.tags,
            },
        )

        candidate_version = request.context.get("candidate_version")
        if candidate_version:
            self.change_control.propose_version(str(candidate_version), "mission_context_candidate")

        return {
            "enabled": True,
            "status": "ok",
            "learning_event": learning_event,
            "active_version": self.change_control.active_version,
        }

    def finalize(self, state: MissionState) -> Dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "status": "bypassed"}

        total_steps = max(1, len(state.steps))
        completed_steps = len([s for s in state.steps if s.status == "completed"])
        total_retries = sum(s.retries for s in state.steps)

        current_metrics = {
            "success_rate": completed_steps / total_steps,
            "retry_rate": total_retries / total_steps,
        }
        drift = self.drift_monitor.evaluate(current_metrics)
        decision = self.change_control.enforce_drift_decision(
            drift_state=str(drift["state"]),
            reason=f"mission_id={state.mission_id}",
        )

        jurisdiction = str(state.request.context.get("jurisdiction", self.default_jurisdiction))
        regulation_profile = str(state.request.context.get("regulation_profile", self.regulation_profile))
        model_version = str(decision.get("active_version", self.change_control.active_version))
        training_snapshot = str(state.request.context.get("training_snapshot", self.training_snapshot))

        liability_record = self.liability_chain.link_prediction(
            prediction_id=state.mission_id,
            model_version=model_version,
            training_data_snapshot=training_snapshot,
            jurisdiction=jurisdiction,
            regulation_profile=regulation_profile,
            metadata={
                "status": state.status,
                "query": state.request.query[:240],
                "tags": state.request.tags,
            },
        )

        federated_vector = state.request.context.get("federated_vector")
        federated_event: Optional[Dict[str, Any]] = None
        if isinstance(federated_vector, list) and federated_vector and all(
            isinstance(v, (int, float)) for v in federated_vector
        ):
            try:
                federated_event = self.governance.collect_local_update(
                    jurisdiction=jurisdiction,
                    model_id=str(state.request.context.get("model_id", self.default_model_id)),
                    pattern_vector=[float(v) for v in federated_vector],
                    is_clinical_data=False,
                    metadata={"mission_id": state.mission_id},
                )
            except Exception as exc:
                federated_event = {"error": str(exc)}

        self.last_decision = {
            "timestamp": utc_now(),
            "mission_id": state.mission_id,
            "drift_state": drift["state"],
            "decision": decision,
        }
        return {
            "enabled": True,
            "metrics": current_metrics,
            "drift": drift,
            "decision": decision,
            "liability_record": liability_record,
            "federated_event": federated_event,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "jurisdiction": self.default_jurisdiction,
            "data_region": self.default_data_region,
            "regulation_profile": self.regulation_profile,
            "certified_version": self.change_control.certified_version,
            "active_version": self.change_control.active_version,
            "last_decision": self.last_decision,
            "policies": self.sandbox.export_policies(),
        }


class MissionEngine:
    def __init__(self, store: MissionStore, tools: ToolRegistry) -> None:
        self.store = store
        self.tools = tools
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self._worker: Optional[asyncio.Task] = None

    def default_steps(self, request: MissionRequest) -> List[MissionStepState]:
        query_lower = request.query.lower()
        steps: List[MissionStepState] = [
            MissionStepState(index=1, name="Health check mission service", tool="sleep", params={"seconds": 0.1}),
        ]

        if "excel" in query_lower:
            steps.append(
                MissionStepState(
                    index=len(steps) + 1,
                    name="Generate Excel artifact",
                    tool="python_script",
                    params={"script": "investor-pack/build_investor_excel.py"},
                )
            )
        if "publish" in query_lower or "blog" in query_lower:
            steps.append(
                MissionStepState(
                    index=len(steps) + 1,
                    name="Publish artifact workflow",
                    tool="python_script",
                    params={"script": "investor-pack/publish_investor_boardgrade.py"},
                )
            )

        if not request.steps and len(steps) == 1:
            steps.append(
                MissionStepState(
                    index=2,
                    name="Route and verify request context",
                    tool="sleep",
                    params={"seconds": 0.2},
                )
            )

        return steps

    def build_steps(self, request: MissionRequest) -> List[MissionStepState]:
        if request.steps:
            return [
                MissionStepState(index=i + 1, name=s.name, tool=s.tool, params=s.params)
                for i, s in enumerate(request.steps)
            ]
        return self.default_steps(request)

    async def submit(self, request: MissionRequest) -> MissionState:
        mission_id = f"msn_{uuid.uuid4().hex[:12]}"
        created = utc_now()
        state = MissionState(
            mission_id=mission_id,
            status="queued",
            created_at=created,
            updated_at=created,
            request=request,
            steps=self.build_steps(request),
            result={"message": "Mission queued"},
        )
        self.store.save(state)
        await self.queue.put(mission_id)
        logger.info(f"Queued mission {mission_id}")
        return state

    async def resume(self, mission_id: str) -> MissionState:
        state = self.store.get(mission_id)
        if not state:
            raise HTTPException(status_code=404, detail="Mission not found")
        if state.status not in ["failed", "paused", "queued"]:
            return state
        state.status = "queued"
        state.updated_at = utc_now()
        self.store.save(state)
        await self.queue.put(mission_id)
        return state

    async def run_worker(self) -> None:
        logger.info("Mission worker started")
        while True:
            mission_id = await self.queue.get()
            try:
                await self.execute_mission(mission_id)
            except Exception as exc:
                logger.exception(f"Mission worker error for {mission_id}: {exc}")
            finally:
                self.queue.task_done()

    async def execute_mission(self, mission_id: str) -> None:
        state = self.store.get(mission_id)
        if not state:
            return

        state.status = "running"
        state.updated_at = utc_now()
        self.store.save(state)

        max_retries = max(0, state.request.max_retries)
        for step in state.steps:
            if step.status == "completed":
                continue

            step.status = "running"
            step.started_at = utc_now()
            state.updated_at = utc_now()
            self.store.save(state)

            success = False
            last_error = None
            for attempt in range(max_retries + 1):
                step.retries = attempt
                try:
                    output = await self.tools.execute(step.tool, step.params)
                    step.output = output
                    if output.get("ok", True):
                        success = True
                        break
                    last_error = output.get("error", "Tool returned not ok")
                except Exception as exc:
                    last_error = str(exc)

            step.ended_at = utc_now()
            if success:
                step.status = "completed"
                step.error = None
            else:
                step.status = "failed"
                step.error = last_error or "Unknown error"
                state.status = "failed"
                state.updated_at = utc_now()
                state.result = {"message": "Mission failed", "failed_step": step.index, "error": step.error}
                state.result["regulatory"] = regulatory.finalize(state)
                self.store.save(state)
                return

            state.updated_at = utc_now()
            self.store.save(state)

        state.status = "completed"
        state.updated_at = utc_now()
        state.result = {
            "message": "Mission completed",
            "completed_steps": len([s for s in state.steps if s.status == "completed"]),
            "total_steps": len(state.steps),
        }
        state.result["regulatory"] = regulatory.finalize(state)
        self.store.save(state)


app = FastAPI(title="Ocean Mission Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = MissionStore(DB_PATH)
tools = ToolRegistry()
engine = MissionEngine(store, tools)
regulatory = RegulatoryRuntime()


@app.on_event("startup")
async def startup_event() -> None:
    if engine._worker is None:
        engine._worker = asyncio.create_task(engine.run_worker())
    logger.info(f"Ocean Mission Service started on port {PORT}")


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "ocean-mission-service",
        "status": "online",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/missions/submit",
            "/missions/{mission_id}",
            "/missions/tools",
            "/regulatory/status",
        ],
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "ocean-mission-service",
        "queue_size": engine.queue.qsize(),
        "db_path": str(DB_PATH),
        "timestamp": utc_now(),
    }


@app.get("/missions/tools")
async def mission_tools() -> Dict[str, Any]:
    return {"tools": tools.list_tools()}


@app.post("/missions/submit")
async def submit_mission(request: MissionRequest) -> Dict[str, Any]:
    preflight = regulatory.preflight(request)
    if preflight.get("status") == "blocked":
        raise HTTPException(status_code=400, detail=f"Regulatory preflight blocked: {preflight.get('reason')}")

    mission = await engine.submit(request)
    return {
        "mission_id": mission.mission_id,
        "status": mission.status,
        "created_at": mission.created_at,
        "regulatory_preflight": preflight,
    }


@app.get("/missions/{mission_id}")
async def get_mission(mission_id: str) -> Dict[str, Any]:
    mission = store.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission.model_dump()


@app.post("/missions/{mission_id}/resume")
async def resume_mission(mission_id: str) -> Dict[str, Any]:
    mission = await engine.resume(mission_id)
    return {"mission_id": mission.mission_id, "status": mission.status, "updated_at": mission.updated_at}


@app.get("/missions")
async def list_missions(limit: int = 20) -> Dict[str, Any]:
    missions = store.list_recent(limit=max(1, min(limit, 200)))
    return {"missions": [m.model_dump() for m in missions], "count": len(missions)}


@app.get("/regulatory/status")
async def regulatory_status() -> Dict[str, Any]:
    return regulatory.status()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)

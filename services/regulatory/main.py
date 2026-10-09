from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from .audit_chain import LiabilityChain
    from .change_control import ChangeControlManager, DriftMonitor, DriftThresholds
    from .federated_governance import FederatedGovernanceHub
    from .sandbox import SandboxedLearningEnvironment, SandboxPolicy
except ImportError:
    from audit_chain import LiabilityChain
    from change_control import ChangeControlManager, DriftMonitor, DriftThresholds
    from federated_governance import FederatedGovernanceHub
    from sandbox import SandboxedLearningEnvironment, SandboxPolicy


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class PreflightRequest(BaseModel):
    jurisdiction: str = "EU"
    data_region: str = "EU"
    model_id: str = "clisonix-default"
    user_id: str = "anonymous"
    query: str = ""
    tags: List[str] = Field(default_factory=list)


class DriftRequest(BaseModel):
    current_metrics: Dict[str, float]


class ChangeProposalRequest(BaseModel):
    version_id: str
    rationale: str


class ChangeApprovalRequest(BaseModel):
    reviewer: str


class LiabilityLinkRequest(BaseModel):
    prediction_id: str
    model_version: str
    training_data_snapshot: str
    jurisdiction: str
    regulation_profile: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FederatedCollectRequest(BaseModel):
    jurisdiction: str
    model_id: str
    pattern_vector: List[float]
    is_clinical_data: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FederatedTransferCheckRequest(BaseModel):
    source_jurisdiction: str
    target_jurisdiction: str
    regulation_tags: List[str] = Field(default_factory=list)


class RegulatoryRuntime:
    def __init__(self) -> None:
        self.default_jurisdiction = os.getenv("REGULATORY_JURISDICTION", "EU")
        self.default_data_region = os.getenv("REGULATORY_DATA_REGION", "EU")
        self.regulation_profile = os.getenv("REGULATORY_PROFILE", "wellness-v1")
        self.certified_version = os.getenv("CERTIFIED_MODEL_VERSION", "clisonix-default:certified")

        baseline_success = float(os.getenv("BASELINE_SUCCESS_RATE", "0.95"))
        baseline_retry = float(os.getenv("BASELINE_RETRY_RATE", "0.05"))
        warning = float(os.getenv("DRIFT_WARNING_THRESHOLD", "0.05"))
        critical = float(os.getenv("DRIFT_CRITICAL_THRESHOLD", "0.10"))

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
        self.liability_chain = LiabilityChain(
            output_file=os.getenv("LIABILITY_CHAIN_PATH", "./data/liability_chain.jsonl")
        )
        self.governance = FederatedGovernanceHub()
        targets = [
            x.strip()
            for x in os.getenv("FEDERATED_TARGETS", self.default_jurisdiction).split(",")
            if x.strip()
        ]
        self.governance.register_jurisdiction_profile(
            jurisdiction=self.default_jurisdiction,
            allowed_transfer_targets=targets,
            required_regulation_tags=[self.regulation_profile],
        )

        self.last_preflight: Dict[str, Any] = {}
        self.last_drift: Dict[str, Any] = {}
        self.last_change_decision: Dict[str, Any] = {}

    def ensure_policy(self, jurisdiction: str, data_region: str) -> None:
        if self.sandbox.get_policy(jurisdiction):
            return
        self.sandbox.register_policy(
            SandboxPolicy(
                jurisdiction=jurisdiction,
                allowed_data_region=data_region,
                regulation_profile=self.regulation_profile,
                allow_continuous_learning=True,
                require_reversible_versioning=True,
            )
        )


app = FastAPI(
    title="Clisonix Regulatory Service",
    description="Operational regulatory controls: sandbox, drift, change control, liability, federated governance",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("./data").mkdir(parents=True, exist_ok=True)
runtime = RegulatoryRuntime()


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "clisonix-regulatory",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/health",
            "/api/regulatory/status",
            "/api/regulatory/preflight",
            "/api/regulatory/drift/evaluate",
            "/api/regulatory/change/propose",
            "/api/regulatory/change/approve",
            "/api/regulatory/liability/link",
            "/api/regulatory/federated/collect",
        ],
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "clisonix-regulatory",
        "timestamp": utc_now(),
    }


@app.get("/api/regulatory/status")
async def status() -> Dict[str, Any]:
    return {
        "status": "active",
        "timestamp": utc_now(),
        "jurisdiction": runtime.default_jurisdiction,
        "data_region": runtime.default_data_region,
        "regulation_profile": runtime.regulation_profile,
        "certified_version": runtime.change_control.certified_version,
        "active_version": runtime.change_control.active_version,
        "last_preflight": runtime.last_preflight,
        "last_drift": runtime.last_drift,
        "last_change_decision": runtime.last_change_decision,
        "policies": runtime.sandbox.export_policies(),
    }


@app.post("/api/regulatory/preflight")
async def preflight(payload: PreflightRequest) -> Dict[str, Any]:
    runtime.ensure_policy(payload.jurisdiction, payload.data_region)
    is_valid, reason = runtime.sandbox.validate_learning_scope(payload.jurisdiction, payload.data_region)
    if not is_valid:
        raise HTTPException(status_code=400, detail=reason)

    learning_event = runtime.sandbox.record_learning_iteration(
        model_id=payload.model_id,
        jurisdiction=payload.jurisdiction,
        data_region=payload.data_region,
        metadata={
            "user_id": payload.user_id,
            "query": payload.query[:240],
            "tags": payload.tags,
        },
    )
    runtime.last_preflight = {
        "timestamp": utc_now(),
        "jurisdiction": payload.jurisdiction,
        "model_id": payload.model_id,
        "event_id": learning_event.get("event_id"),
    }
    return {"status": "ok", "learning_event": learning_event}


@app.post("/api/regulatory/drift/evaluate")
async def drift_evaluate(payload: DriftRequest) -> Dict[str, Any]:
    result = runtime.drift_monitor.evaluate(payload.current_metrics)
    decision = runtime.change_control.enforce_drift_decision(
        drift_state=str(result["state"]),
        reason="manual-drift-evaluation",
    )
    runtime.last_drift = result
    runtime.last_change_decision = {"timestamp": utc_now(), **decision}
    return {"drift": result, "decision": decision}


@app.post("/api/regulatory/change/propose")
async def change_propose(payload: ChangeProposalRequest) -> Dict[str, Any]:
    runtime.change_control.propose_version(payload.version_id, payload.rationale)
    return {
        "status": "proposed",
        "pending_version": runtime.change_control.pending_version,
        "active_version": runtime.change_control.active_version,
    }


@app.post("/api/regulatory/change/approve")
async def change_approve(payload: ChangeApprovalRequest) -> Dict[str, Any]:
    approved = runtime.change_control.approve_pending(payload.reviewer)
    if not approved:
        raise HTTPException(status_code=400, detail="No pending version to approve")
    runtime.last_change_decision = {
        "timestamp": utc_now(),
        "action": "approved",
        "active_version": runtime.change_control.active_version,
    }
    return {
        "status": "approved",
        "active_version": runtime.change_control.active_version,
    }


@app.get("/api/regulatory/change/log")
async def change_log() -> Dict[str, Any]:
    return {
        "entries": runtime.change_control.change_log,
        "count": len(runtime.change_control.change_log),
    }


@app.post("/api/regulatory/liability/link")
async def liability_link(payload: LiabilityLinkRequest) -> Dict[str, Any]:
    record = runtime.liability_chain.link_prediction(
        prediction_id=payload.prediction_id,
        model_version=payload.model_version,
        training_data_snapshot=payload.training_data_snapshot,
        jurisdiction=payload.jurisdiction,
        regulation_profile=payload.regulation_profile,
        metadata=payload.metadata,
    )
    return {"status": "linked", "record": record}


@app.get("/api/regulatory/liability/{prediction_id}")
async def liability_get(prediction_id: str) -> Dict[str, Any]:
    record = runtime.liability_chain.get_record(prediction_id)
    if not record:
        raise HTTPException(status_code=404, detail="Prediction record not found")
    return {"record": record}


@app.post("/api/regulatory/federated/collect")
async def federated_collect(payload: FederatedCollectRequest) -> Dict[str, Any]:
    try:
        event = runtime.governance.collect_local_update(
            jurisdiction=payload.jurisdiction,
            model_id=payload.model_id,
            pattern_vector=payload.pattern_vector,
            is_clinical_data=payload.is_clinical_data,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "collected", "event": event}


@app.post("/api/regulatory/federated/can-transfer")
async def federated_can_transfer(payload: FederatedTransferCheckRequest) -> Dict[str, Any]:
    allowed = runtime.governance.can_transfer(
        source_jurisdiction=payload.source_jurisdiction,
        target_jurisdiction=payload.target_jurisdiction,
        regulation_tags=payload.regulation_tags,
    )
    return {"allowed": allowed}


@app.get("/api/regulatory/federated/export")
async def federated_export(min_jurisdictions: int = 2) -> Dict[str, Any]:
    patterns = runtime.governance.export_global_patterns(min_jurisdictions=min_jurisdictions)
    return {"patterns": patterns, "count": len(patterns)}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "9501"))
    uvicorn.run(app, host="0.0.0.0", port=port)

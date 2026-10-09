"""
Ultra-Industrial SaaS Signal API
Author: Ledjan Ahmati
"""

import time
import uuid
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Ultra-Industrial SaaS Signal API")

# Simulated in-memory database for demo

SIGNAL_DB: Dict[str, Dict[str, Any]] = {}
NODE_DB: Dict[str, List[str]] = {}
USER_DB: Dict[str, Dict[str, Any]] = {
    "admin": {"password": "admin123", "role": "admin", "nodes": ["node1", "node2"], "plan": "enterprise", "license": "valid"},
    "user1": {"password": "user123", "role": "user", "nodes": ["node1"], "plan": "free", "license": "trial"}
}
RATE_LIMITS: Dict[str, Dict[str, Any]] = {}
BILLING_DB: Dict[str, Dict[str, Any]] = {}
AUDIT_LOG: List[Dict[str, Any]] = []
WEBHOOKS: Dict[str, str] = {}
QUOTA: Dict[str, int] = {"free": 10, "enterprise": 1000}


@app.get("/")
def root():
    return {"service": "saas-api", "status": "ready"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "saas-api"}


@app.get("/status")
def status():
    return {
        "service": "saas-api",
        "users": len(USER_DB),
        "signals": len(SIGNAL_DB),
        "nodes": len(NODE_DB),
        "status": "operational",
    }

class Signal(BaseModel):
    id: str
    value: float
    meta: Dict[str, Any]
    timestamp: float
    owner: str
    node: str

class SignalCreate(BaseModel):
    value: float
    meta: Dict[str, Any]
    node: str

class BillingEvent(BaseModel):
    username: str
    amount: float
    description: str
    timestamp: float

class WebhookRegister(BaseModel):
    node: str
    url: str

class UserAuth(BaseModel):
    username: str
    password: str

# Simple auth dependency
def get_current_user(auth: UserAuth):
    user = USER_DB.get(auth.username)
    if not user or user["password"] != auth.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return auth.username

def check_rate_limit(user: str):
    now = int(time.time())
    rl = RATE_LIMITS.setdefault(user, {"window": now, "count": 0})
    # Reset window every 60 sekonda
    if now - rl["window"] > 60:
        rl["window"] = now
        rl["count"] = 0
    rl["count"] += 1
    plan = USER_DB[user].get("plan", "free")
    quota = QUOTA.get(plan, 10)
    if rl["count"] > quota:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {quota} requests per minute for plan '{plan}'")

@app.post("/signal/create", response_model=Signal)
def create_signal(data: SignalCreate, auth: UserAuth = Depends()):
    user = get_current_user(auth)
    check_rate_limit(user)
    signal_id = str(uuid.uuid4())
    signal = Signal(
        id=signal_id,
        value=data.value,
        meta=data.meta,
        timestamp=time.time(),
        owner=user,
        node=data.node
    )
    SIGNAL_DB[signal_id] = signal.dict()
    NODE_DB.setdefault(data.node, []).append(signal_id)
    # Audit log
    AUDIT_LOG.append({"event": "create_signal", "user": user, "signal_id": signal_id, "node": data.node, "timestamp": signal.timestamp})
    # Licensing check
    license = USER_DB[user].get("license", "trial")
    if license != "valid":
        raise HTTPException(status_code=403, detail="License not valid")
    # Billing event
    plan = USER_DB[user].get("plan", "free")
    if plan != "free":
        BILLING_DB.setdefault(user, {"total": 0, "events": []})
        BILLING_DB[user]["total"] += 0.01  # Simulate billing per signal
        BILLING_DB[user]["events"].append({"signal_id": signal_id, "amount": 0.01, "timestamp": signal.timestamp})
    # Webhook
    webhook_url = WEBHOOKS.get(data.node)
    if webhook_url:
        AUDIT_LOG.append({"event": "webhook_called", "url": webhook_url, "signal_id": signal_id, "timestamp": signal.timestamp})
    return signal


@app.get("/quota/{username}")
def get_user_quota(username: str):
    user = USER_DB.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    plan = user.get("plan", "free")
    quota = QUOTA.get(plan, 10)
    rl = RATE_LIMITS.get(username, {"count": 0})
    return {"plan": plan, "quota": quota, "used": rl.get("count", 0)}
# --- SaaS Features ---
@app.post("/billing/event")
def billing_event(event: BillingEvent):
    BILLING_DB.setdefault(event.username, {"total": 0, "events": []})
    BILLING_DB[event.username]["total"] += event.amount
    BILLING_DB[event.username]["events"].append({"description": event.description, "amount": event.amount, "timestamp": event.timestamp})
    return {"status": "ok", "total": BILLING_DB[event.username]["total"]}

@app.get("/billing/{username}")
def get_billing(username: str):
    return BILLING_DB.get(username, {"total": 0, "events": []})

@app.get("/audit/log")
def get_audit_log():
    return AUDIT_LOG

@app.post("/webhook/register")
def register_webhook(data: WebhookRegister):
    WEBHOOKS[data.node] = data.url
    return {"status": "registered", "node": data.node, "url": data.url}

@app.get("/monitoring/nodes")
def monitoring_nodes():
    return {node: len(signals) for node, signals in NODE_DB.items()}

@app.get("/license/{username}")
def get_license(username: str):
    user = USER_DB.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"license": user.get("license", "trial"), "plan": user.get("plan", "free")}

@app.get("/signal/{signal_id}", response_model=Signal)
def get_signal(signal_id: str, auth: UserAuth = Depends()):
    user = get_current_user(auth)
    signal = SIGNAL_DB.get(signal_id)
    if not signal or signal["owner"] != user:
        raise HTTPException(status_code=404, detail="Signal not found or access denied")
    return signal

@app.get("/node/{node}/signals", response_model=List[Signal])
def get_node_signals(node: str, auth: UserAuth = Depends()):
    user = get_current_user(auth)
    allowed_nodes = USER_DB[user]["nodes"]
    if node not in allowed_nodes:
        raise HTTPException(status_code=403, detail="Access to node denied")
    signal_ids = NODE_DB.get(node, [])
    return [SIGNAL_DB[sid] for sid in signal_ids if SIGNAL_DB[sid]["owner"] == user]

@app.post("/user/login")
def login(auth: UserAuth):
    user = USER_DB.get(auth.username)
    if not user or user["password"] != auth.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": auth.username, "role": user["role"], "nodes": user["nodes"]}

# SaaS features: multi-tenancy, auth, memorim/shpërndarje sinjalesh
# Ky API mund të zgjerohet me billing, monitoring, licensing, webhook, etj.



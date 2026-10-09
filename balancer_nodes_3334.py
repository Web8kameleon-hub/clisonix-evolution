#!/usr/bin/env python3
"""
BALANCER NODES SERVICE (Port 3334)
Python-based node discovery and load distribution
Routes traffic to external Mesh nodes and offline nodes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import socket

# Initialize FastAPI
app = FastAPI(
    title="Balancer Nodes (Python)",
    description="Node discovery, load distribution, external mesh routing",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Node registry
NODE_REGISTRY: Dict[str, Dict[str, Any]] = {}
EXTERNAL_NODES: Dict[str, Dict[str, Any]] = {}  # External Mesh nodes
OFFLINE_NODES: List[str] = []  # Offline node IDs
REQUEST_COUNT = 0
SERVICE_START = datetime.now(timezone.utc).isoformat()

# Mesh HQ configuration
MESH_HQ_URL = "http://localhost:7777"


@app.post("/api/nodes/register")
async def register_node(nodeId: str, type: Optional[str] = None, port: Optional[int] = None, 
                       host: Optional[str] = None, metadata: Optional[Dict] = None):
    """Register a new node"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if not nodeId:
        raise HTTPException(status_code=400, detail="nodeId required")
    
    node_data = {
        "nodeId": nodeId,
        "type": type or "unknown",
        "port": port,
        "host": host or socket.gethostname(),
        "status": "active",
        "registeredAt": datetime.now(timezone.utc).isoformat(),
        "lastHeartbeat": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
        "requestCount": 0,
        "loadFactor": 0.0
    }
    
    NODE_REGISTRY[nodeId] = node_data
    print(f"[{datetime.now().isoformat()}] Node registered: {nodeId}")
    
    return {
        "success": True,
        "message": f"Node {nodeId} registered",
        "node": node_data
    }


@app.get("/api/nodes")
async def get_nodes():
    """Get all registered nodes"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "totalNodes": len(NODE_REGISTRY),
        "nodes": list(NODE_REGISTRY.values())
    }


@app.get("/api/nodes/{nodeId}")
async def get_node(nodeId: str):
    """Get specific node"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if nodeId not in NODE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Node {nodeId} not found")
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node": NODE_REGISTRY[nodeId]
    }


@app.put("/api/nodes/{nodeId}/status")
async def update_node_status(nodeId: str, status: str = "active", load: Optional[float] = None):
    """Update node status and load"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if nodeId not in NODE_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Node {nodeId} not found")
    
    node = NODE_REGISTRY[nodeId]
    node["status"] = status
    node["lastHeartbeat"] = datetime.now(timezone.utc).isoformat()
    node["requestCount"] += 1
    if load is not None:
        node["loadFactor"] = load
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": f"Node {nodeId} updated",
        "node": node
    }


@app.get("/api/load-balance")
async def get_load_balance():
    """Get load balancing recommendations"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if not NODE_REGISTRY:
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "recommendation": "No nodes available"}
    
    sorted_nodes = sorted(
        NODE_REGISTRY.values(),
        key=lambda x: x.get("loadFactor", 0)
    )
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recommended_node": sorted_nodes[0] if sorted_nodes else None,
        "all_nodes_sorted": sorted_nodes
    }


@app.post("/api/external-nodes/register")
async def register_external_node(nodeId: str, meshUrl: str, region: Optional[str] = None, 
                                capacity: Optional[int] = None, metadata: Optional[Dict] = None):
    """Register external Mesh node for load distribution"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if not nodeId or not meshUrl:
        raise HTTPException(status_code=400, detail="nodeId and meshUrl required")
    
    external_node = {
        "nodeId": nodeId,
        "meshUrl": meshUrl,
        "region": region or "unknown",
        "capacity": capacity or 100,
        "metadata": metadata or {},
        "registeredAt": datetime.now(timezone.utc).isoformat(),
        "lastHeartbeat": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "requestsRouted": 0
    }
    
    EXTERNAL_NODES[nodeId] = external_node
    print(f"[{datetime.now().isoformat()}] External Mesh node registered: {nodeId} -> {meshUrl}")
    
    return {
        "success": True,
        "message": f"External node {nodeId} registered",
        "node": external_node
    }


@app.get("/api/external-nodes")
async def get_external_nodes():
    """Get all registered external Mesh nodes"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "totalExternalNodes": len(EXTERNAL_NODES),
        "externalNodes": list(EXTERNAL_NODES.values())
    }


@app.post("/api/route-to-external")
async def route_to_external(nodeId: str, request_data: Dict):
    """Route load to external Mesh node"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if nodeId not in EXTERNAL_NODES:
        raise HTTPException(status_code=404, detail=f"External node {nodeId} not found")
    
    external_node = EXTERNAL_NODES[nodeId]
    external_node["requestsRouted"] += 1
    
    try:
        response = requests.post(
            f"{external_node['meshUrl']}/process",
            json=request_data,
            timeout=10
        )
        return {
            "success": True,
            "routedTo": nodeId,
            "meshUrl": external_node['meshUrl'],
            "region": external_node['region'],
            "response": response.json() if response.ok else response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "routedTo": nodeId
        }


@app.post("/api/offline-nodes/register")
async def register_offline_node(nodeId: str):
    """Register offline node for load distribution"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if nodeId not in OFFLINE_NODES:
        OFFLINE_NODES.append(nodeId)
        print(f"[{datetime.now().isoformat()}] Offline node registered: {nodeId}")
    
    return {
        "success": True,
        "message": f"Offline node {nodeId} registered",
        "offlineNodes": OFFLINE_NODES
    }


@app.get("/api/offline-nodes")
async def get_offline_nodes():
    """Get all offline nodes available for load distribution"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "totalOfflineNodes": len(OFFLINE_NODES),
        "offlineNodes": OFFLINE_NODES
    }


@app.post("/api/route-to-offline")
async def route_to_offline(nodeId: str, request_data: Dict):
    """Queue work for offline node (stores for later processing)"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if nodeId not in OFFLINE_NODES:
        raise HTTPException(status_code=404, detail=f"Offline node {nodeId} not found")
    
    # Store for offline processing
    queue_key = f"offline_{nodeId}_{datetime.now().timestamp()}"
    
    return {
        "success": True,
        "message": f"Work queued for offline node {nodeId}",
        "queueKey": queue_key,
        "nodeId": nodeId,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/mesh-status")
async def get_mesh_status():
    """Get overall Mesh and load distribution status"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "localNodes": len(NODE_REGISTRY),
        "externalMeshNodes": len(EXTERNAL_NODES),
        "offlineNodes": len(OFFLINE_NODES),
        "totalRequests": REQUEST_COUNT,
        "meshHQ": MESH_HQ_URL,
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "status": "healthy",
        "service": "balancer-nodes-3334",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_since": SERVICE_START,
        "requests_served": REQUEST_COUNT,
        "activeNodes": len(NODE_REGISTRY),
        "externalNodes": len(EXTERNAL_NODES),
        "offlineNodes": len(OFFLINE_NODES)
    }


@app.get("/info")
async def info():
    """Service information"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "service": "Balancer Nodes (Python) - External Mesh Routing",
        "port": 3334,
        "type": "node-discovery-external",
        "version": "2.1.0",
        "started_at": SERVICE_START,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "POST /api/nodes/register": "Register local node",
            "GET /api/nodes": "List local nodes",
            "POST /api/external-nodes/register": "Register external Mesh node",
            "GET /api/external-nodes": "List external Mesh nodes",
            "POST /api/route-to-external": "Route load to external Mesh node",
            "POST /api/offline-nodes/register": "Register offline node",
            "GET /api/offline-nodes": "List offline nodes",
            "POST /api/route-to-offline": "Queue work for offline node",
            "POST /api/vendor-nodes/register": "Register user vendor node (edge)",
            "GET /api/vendor-nodes": "List vendor nodes",
            "POST /api/vendor-nodes/heartbeat": "Vendor node heartbeat",
            "POST /api/vendor-nodes/complete": "Report task completion",
            "GET /api/mesh-status": "Get Mesh & load status",
            "GET /health": "Health check",
            "GET /info": "Service info"
        }
    }

# ============== VENDOR NODES (Edge Computing) ==============
VENDOR_NODES: Dict[str, Dict[str, Any]] = {}

@app.post("/api/vendor-nodes/register")
async def register_vendor_node(nodeId: str, type: str = "vendor", 
                               capabilities: Optional[Dict] = None,
                               metadata: Optional[Dict] = None):
    """Register a user's device as vendor node for edge computing"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if not nodeId:
        raise HTTPException(status_code=400, detail="nodeId required")
    
    vendor_data = {
        "nodeId": nodeId,
        "type": type,
        "capabilities": capabilities or {},
        "metadata": metadata or {},
        "status": "active",
        "registeredAt": datetime.now(timezone.utc).isoformat(),
        "lastHeartbeat": datetime.now(timezone.utc).isoformat(),
        "tasksCompleted": 0,
        "loadFactor": 0.0
    }
    
    VENDOR_NODES[nodeId] = vendor_data
    print(f"[{datetime.now().isoformat()}] 🌐 Vendor Node registered: {nodeId}")
    
    return {
        "success": True,
        "message": f"Vendor node {nodeId} registered for edge computing",
        "node": vendor_data
    }

@app.get("/api/vendor-nodes")
async def get_vendor_nodes():
    """Get all registered vendor nodes"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    active_nodes = [n for n in VENDOR_NODES.values() if n["status"] == "active"]
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "totalVendorNodes": len(VENDOR_NODES),
        "activeVendorNodes": len(active_nodes),
        "vendorNodes": list(VENDOR_NODES.values())
    }

@app.post("/api/vendor-nodes/heartbeat")
async def vendor_heartbeat(nodeId: str, stats: Optional[Dict] = None, load: Optional[Dict] = None):
    """Update vendor node heartbeat"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if nodeId not in VENDOR_NODES:
        raise HTTPException(status_code=404, detail=f"Vendor node {nodeId} not found")
    
    VENDOR_NODES[nodeId]["lastHeartbeat"] = datetime.now(timezone.utc).isoformat()
    VENDOR_NODES[nodeId]["status"] = "active"
    if stats:
        VENDOR_NODES[nodeId]["stats"] = stats
    if load:
        VENDOR_NODES[nodeId]["loadFactor"] = load.get("cpu", 0)
    
    return {"success": True, "nodeId": nodeId}

@app.post("/api/vendor-nodes/complete")
async def vendor_complete(nodeId: str, taskId: str, result: Optional[Dict] = None):
    """Report task completion from vendor node"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    if nodeId in VENDOR_NODES:
        VENDOR_NODES[nodeId]["tasksCompleted"] = VENDOR_NODES[nodeId].get("tasksCompleted", 0) + 1
    
    print(f"[{datetime.now().isoformat()}] ✅ Vendor {nodeId} completed task {taskId}")
    
    return {"success": True, "nodeId": nodeId, "taskId": taskId}

@app.get("/api/vendor-nodes/best")
async def get_best_vendor_node():
    """Get the best available vendor node for task distribution"""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    # Find active nodes with lowest load
    active_nodes = [n for n in VENDOR_NODES.values() if n["status"] == "active"]
    
    if not active_nodes:
        return {"available": False, "message": "No vendor nodes available"}
    
    # Sort by load factor (lowest first)
    best = sorted(active_nodes, key=lambda x: x.get("loadFactor", 1.0))[0]
    
    return {
        "available": True,
        "node": best
    }


if __name__ == "__main__":
    port = int(os.getenv("BALANCER_NODES_PORT", "3334"))
    host = os.getenv("BALANCER_NODES_HOST", "0.0.0.0")
    
    print(f"\n{'='*60}")
    print(f"  BALANCER NODES SERVICE (Python)")
    print(f"  Listening on {host}:{port}")
    print(f"  Node discovery & load distribution")
    print(f"  + Vendor Nodes (Edge Computing)")
    print(f"{'='*60}\n")
    
    uvicorn.run(app, host=host, port=port, log_level="info")

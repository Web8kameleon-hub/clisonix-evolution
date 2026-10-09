from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import json
from datetime import datetime
import asyncio

router = APIRouter()

# Simulated distributed network data
NETWORK_NODES = {
    "node_001": {
        "id": "node_001",
        "name": "Primary AGI Node",
        "status": "active",
        "memory_usage": 62.8,
        "tasks_completed": 1247,
        "uptime": "12d 4h 23m",
        "location": "Frankfurt, DE",
        "capabilities": ["nlp", "vision", "reasoning", "planning"]
    },
    "node_002": {
        "id": "node_002", 
        "name": "Secondary Processing Node",
        "status": "active",
        "cpu_usage": 38.7,
        "memory_usage": 54.1,
        "tasks_completed": 892,
        "uptime": "8d 15h 47m",
        "location": "London, UK",
        "capabilities": ["data_processing", "ml_inference", "storage"]
    },
    "node_003": {
        "id": "node_003",
        "name": "Mesh Network Coordinator",
        "status": "idle",
        "cpu_usage": 12.3,
        "memory_usage": 28.9,
        "tasks_completed": 445,
        "uptime": "5d 2h 11m", 
        "location": "Amsterdam, NL",
        "capabilities": ["coordination", "routing", "monitoring"]
    }
}

NETWORK_STATS = {
    "total_nodes": 3,
    "active_nodes": 2,
    "idle_nodes": 1,
    "total_tasks_completed": 2584,
    "network_throughput": "1.2 GB/s",
    "avg_response_time": "45ms",
    "uptime_percentage": 99.7,
    "last_updated": datetime.now().isoformat()
}

@router.get("/")
async def get_network_overview():
    """Get distributed AGI network overview"""
    return {
        "message": "🌐 Distributed AGI Network Dashboard",
        "status": "operational",
        "stats": NETWORK_STATS,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/nodes")
async def get_all_nodes():
    """Get all network nodes"""
    return {
        "nodes": list(NETWORK_NODES.values()),
        "count": len(NETWORK_NODES),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/nodes/{node_id}")
async def get_node_details(node_id: str):
    """Get specific node details"""
    if node_id not in NETWORK_NODES:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    return {
        "node": NETWORK_NODES[node_id],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stats")
async def get_network_statistics():
    """Get network performance statistics"""
    return {
        "network_stats": NETWORK_STATS,
        "nodes_summary": {
            "active": [node for node in NETWORK_NODES.values() if node["status"] == "active"],
            "idle": [node for node in NETWORK_NODES.values() if node["status"] == "idle"],
            "offline": [node for node in NETWORK_NODES.values() if node["status"] == "offline"]
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/nodes/{node_id}/tasks")
async def assign_task_to_node(node_id: str, task_data: Dict[str, Any]):
    """Assign a task to a specific node"""
    if node_id not in NETWORK_NODES:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    node = NETWORK_NODES[node_id]
    if node["status"] != "active":
        raise HTTPException(status_code=400, detail=f"Node {node_id} is not active")
    
    # Simulate task assignment
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "task_id": task_id,
        "assigned_to": node_id,
        "node_name": node["name"],
        "task_data": task_data,
        "status": "assigned",
        "estimated_completion": "2-5 minutes",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/mesh/topology")
async def get_mesh_topology():
    """Get mesh network topology"""
    topology = {
        "connections": [
            {"from": "node_001", "to": "node_002", "strength": 0.95, "latency": "12ms"},
            {"from": "node_001", "to": "node_003", "strength": 0.87, "latency": "18ms"},
            {"from": "node_002", "to": "node_003", "strength": 0.91, "latency": "15ms"}
        ],
        "cluster_health": "excellent",
        "redundancy_level": "high",
        "failover_ready": True
    }
    
    return {
        "topology": topology,
        "visualization_data": {
            "nodes": [
                {"id": node_id, "label": node["name"], "status": node["status"]}
                for node_id, node in NETWORK_NODES.items()
            ],
            "edges": topology["connections"]
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health") 
async def network_health_check():
    """Network health check"""
    active_count = len([n for n in NETWORK_NODES.values() if n["status"] == "active"])
    total_count = len(NETWORK_NODES)
    
    health_status = "healthy" if active_count >= total_count * 0.5 else "degraded"
    
    return {
        "status": health_status,
        "active_nodes": active_count,
        "total_nodes": total_count,
        "network_uptime": NETWORK_STATS["uptime_percentage"],
        "last_check": datetime.now().isoformat()
    }

@router.post("/broadcast")
async def broadcast_message(message_data: Dict[str, Any]):
    """Broadcast message to all active nodes"""
    active_nodes = [node for node in NETWORK_NODES.values() if node["status"] == "active"]
    
    broadcast_id = f"broadcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "broadcast_id": broadcast_id,
        "message": message_data,
        "recipients": [node["id"] for node in active_nodes],
        "delivered_to": len(active_nodes),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/monitoring/realtime")
async def get_realtime_monitoring():
    """Get real-time monitoring data"""
    import random
    
    # Simulate real-time data
    realtime_data = {
        "network_load": {
            "current": round(random.uniform(20, 80), 1),
            "average": 45.2,
            "peak": 78.9
        },
        "active_connections": random.randint(15, 45),
        "data_throughput": {
            "incoming": f"{round(random.uniform(0.5, 2.5), 1)} GB/s",
            "outgoing": f"{round(random.uniform(0.3, 1.8), 1)} GB/s"
        },
        "task_queue": {
            "pending": random.randint(0, 12),
            "processing": random.randint(3, 15),
            "completed_today": random.randint(100, 500)
        },
        "alerts": [
            {
                "level": "info",
                "message": "Node synchronization completed",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
    
    return {
        "realtime_data": realtime_data,
        "timestamp": datetime.now().isoformat(),
        "refresh_interval": "5s"
    }



"""
SERVICE DISCOVERY ENDPOINTS - Backend API
==========================================
Expose Service Registry to frontend via REST API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["service-discovery"])


@router.post("/service-discovery")
async def discover_service(capability: str):
    """Discover service by capability (Firestore-backed)"""
    from main import get_registry  # Import here to avoid circular import

    registry = get_registry()
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not available")

    service = await registry.find_capability(capability)

    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"No service provides capability: {capability}"
        )

    return {
        "service": service.get("name"),
        "capability": capability,
        "url": service.get("url"),
        "model": service.get("model"),
        "metadata": service.get("metadata", {})
    }


@router.post("/service-info")
async def get_service_info(service: str):
    """Get detailed info about a service"""
    from main import get_registry

    registry = get_registry()
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not available")

    service_data = await registry.discover_service(service)

    if not service_data:
        raise HTTPException(
            status_code=404,
            detail=f"Service not found: {service}"
        )

    return service_data


@router.get("/services")
async def list_all_services():
    """List all registered services"""
    from main import get_registry

    registry = get_registry()
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not available")

    services = await registry.list_services()

    return {
        "count": len(services),
        "services": services,
        "timestamp": str(datetime.utcnow().isoformat())
    }


@router.get("/capabilities/{capability}")
async def get_capability_providers(capability: str):
    """Get all services providing a capability"""
    from main import get_registry

    registry = get_registry()
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not available")

    providers = await registry.get_capability_providers(capability)

    return {
        "capability": capability,
        "providers": providers,
        "count": len(providers),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def registry_status():
    """Check registry health (Firestore-backed)"""
    from main import get_registry

    registry = get_registry()

    if not registry or not registry.db:
        return {
            "status": "offline",
            "mode": "local-fallback",
            "backend": "in-memory",
            "services": len(registry.local_services) if registry else 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    try:
        services = await registry.list_services()
        return {
            "status": "online",
            "mode": "firestore-enabled",
            "backend": "google-firestore",
            "services": len(services),
            "timestamp": datetime.utcnow().isoformat(),
            "free_tier_limits": {"reads_per_day": 50000, "writes_per_day": 20000}
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

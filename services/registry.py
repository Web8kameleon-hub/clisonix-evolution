"""
CLISONIX SERVICE REGISTRY - Google Firestore
============================================
Zero-hardcoding service discovery using Google Firestore.
Free tier: 50,000 reads/day, 20,000 writes/day. Perfect for service registry.
No Redis needed. All services auto-register on startup.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from firebase_admin import credentials as firebase_credentials
    from firebase_admin import firestore as firebase_firestore
    from firebase_admin import initialize_app as firebase_initialize_app
    FIREBASE_AVAILABLE = True
except ImportError:
    firebase_credentials = None
    firebase_firestore = None
    firebase_initialize_app = None
    FIREBASE_AVAILABLE = False

logger = logging.getLogger("service_registry")


class ServiceRegistry:
    """Dynamic service discovery - Google Firestore-backed."""
    
    def __init__(self, firestore_client=None):
        """Initialize with Firestore client or initialize from env."""
        self.db = firestore_client
        self.local_services = {}  # Fallback in-memory storage
        self.heartbeats = {}  # Track active heartbeats
        
        if FIREBASE_AVAILABLE and not self.db:
            self._init_firebase()
    
    def _init_firebase(self):
        """Initialize Firebase from environment."""
        if not FIREBASE_AVAILABLE:
            return
        if firebase_credentials is None or firebase_firestore is None or firebase_initialize_app is None:
            return

        try:
            # Check for Google credentials
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not creds_path and os.path.exists("firebase-key.json"):
                creds_path = "firebase-key.json"
            
            if creds_path:
                creds = firebase_credentials.Certificate(creds_path)
                firebase_initialize_app(creds)
                self.db = firebase_firestore.client()
                logger.info("✅ Firebase initialized from credentials")
            else:
                logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set, using local fallback")
        except Exception as e:
            logger.warning(f"⚠️ Firebase init failed: {e}. Using in-memory fallback.")
            self.db = None
    
    async def register_service(
        self,
        name: str,
        host: str = "localhost",
        port: int = 8000,
        model: str = "default",
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: int = 3600,
    ) -> bool:
        """Register service in Firestore or local storage."""
        service_data = {
            "name": name,
            "host": host,
            "port": port,
            "url": f"http://{host}:{port}",
            "model": model,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
            "registered_at": datetime.utcnow().isoformat(),
            "last_heartbeat": datetime.utcnow().isoformat(),
            "ttl_seconds": ttl_seconds,
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat(),
        }

        try:
            if FIREBASE_AVAILABLE and self.db:
                # Store in Firestore
                self.db.collection("services").document(name).set(service_data)
                logger.info(f"✅ Registered {name} in Firestore")
            else:
                # Fallback to in-memory
                self.local_services[name] = service_data
                logger.info(f"✅ Registered {name} locally")
            
            logger.info(f"   URL: http://{host}:{port}")
            logger.info(f"   Model: {model}")
            logger.info(f"   Capabilities: {', '.join(capabilities or [])}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Registration failed for {name}: {e}")
            # Fallback to local
            self.local_services[name] = service_data
            return False
    
    async def discover_service(self, name: str) -> Optional[Dict[str, Any]]:
        """Discover service by name."""
        try:
            if FIREBASE_AVAILABLE and self.db:
                doc = self.db.collection("services").document(name).get()
                if doc.exists:
                    data = doc.to_dict()
                    # Check if expired
                    if datetime.fromisoformat(data.get("expires_at", "")) > datetime.utcnow():
                        return data
                    else:
                        # Remove expired
                        self.db.collection("services").document(name).delete()
                        return None
            
            # Check local storage
            if name in self.local_services:
                data = self.local_services[name]
                if datetime.fromisoformat(data.get("expires_at", "")) > datetime.utcnow():
                    return data
                else:
                    del self.local_services[name]
                    return None
            
            return None
        
        except Exception as e:
            logger.warning(f"⚠️ Discovery failed for {name}: {e}")
            return None
    
    async def find_capability(self, capability: str) -> Optional[Dict[str, Any]]:
        """Find service providing capability."""
        try:
            if FIREBASE_AVAILABLE and self.db:
                # Query Firestore
                docs = self.db.collection("services").where(
                    "capabilities", "array-contains", capability
                ).limit(1).stream()
                
                for doc in docs:
                    service = doc.to_dict()
                    if datetime.fromisoformat(service.get("expires_at", "")) > datetime.utcnow():
                        return service
            
            # Check local storage
            for service in self.local_services.values():
                if capability in service.get("capabilities", []):
                    if datetime.fromisoformat(service.get("expires_at", "")) > datetime.utcnow():
                        return service
            
            return None
        
        except Exception as e:
            logger.warning(f"⚠️ Capability lookup failed for {capability}: {e}")
            return None
    
    async def list_services(self) -> List[Dict[str, Any]]:
        """List all registered services."""
        services = []
        try:
            if FIREBASE_AVAILABLE and self.db:
                docs = self.db.collection("services").stream()
                for doc in docs:
                    service = doc.to_dict()
                    if datetime.fromisoformat(service.get("expires_at", "")) > datetime.utcnow():
                        services.append(service)
            
            # Add local services
            for service in self.local_services.values():
                if datetime.fromisoformat(service.get("expires_at", "")) > datetime.utcnow():
                    services.append(service)
            
            return services
        
        except Exception as e:
            logger.warning(f"⚠️ List services failed: {e}")
            return services
    
    async def get_capability_providers(self, capability: str) -> List[Dict[str, Any]]:
        """Get all services providing a capability."""
        providers = []
        try:
            if FIREBASE_AVAILABLE and self.db:
                docs = self.db.collection("services").where(
                    "capabilities", "array-contains", capability
                ).stream()
                
                for doc in docs:
                    service = doc.to_dict()
                    if datetime.fromisoformat(service.get("expires_at", "")) > datetime.utcnow():
                        providers.append(service)
            
            # Check local storage
            for service in self.local_services.values():
                if capability in service.get("capabilities", []):
                    if datetime.fromisoformat(service.get("expires_at", "")) > datetime.utcnow():
                        providers.append(service)
            
            return providers
        
        except Exception as e:
            logger.warning(f"⚠️ Get providers failed for {capability}: {e}")
            return providers
    
    async def start_heartbeat(self, service_name: str, interval: int = 30):
        """Start heartbeat to keep registration alive."""
        async def heartbeat_loop():
            while service_name in self.heartbeats:
                try:
                    service = await self.discover_service(service_name)
                    if service:
                        updated = service.copy()
                        updated["last_heartbeat"] = datetime.utcnow().isoformat()
                        updated["expires_at"] = (
                            datetime.utcnow() + timedelta(seconds=service.get("ttl_seconds", 3600))
                        ).isoformat()
                        
                        if FIREBASE_AVAILABLE and self.db:
                            self.db.collection("services").document(service_name).update(updated)
                        else:
                            self.local_services[service_name] = updated
                        
                        logger.debug(f"💓 Heartbeat: {service_name}")
                    
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.warning(f"⚠️ Heartbeat failed for {service_name}: {e}")
                    await asyncio.sleep(interval)
        
        self.heartbeats[service_name] = True
        asyncio.create_task(heartbeat_loop())
        logger.info(f"💓 Heartbeat started for {service_name} (interval={interval}s)")
    
    async def stop_heartbeat(self, service_name: str):
        """Stop heartbeat for service."""
        if service_name in self.heartbeats:
            del self.heartbeats[service_name]
            logger.info(f"✅ Heartbeat stopped for {service_name}")
    
    async def deregister_service(self, service_name: str):
        """Remove service from registry."""
        try:
            if FIREBASE_AVAILABLE and self.db:
                self.db.collection("services").document(service_name).delete()
            
            if service_name in self.local_services:
                del self.local_services[service_name]
            
            await self.stop_heartbeat(service_name)
            logger.info(f"✅ Deregistered {service_name}")
        
        except Exception as e:
            logger.warning(f"⚠️ Deregistration failed for {service_name}: {e}")


# Global instance
_registry: Optional[ServiceRegistry] = None


async def init_registry(firestore_client=None) -> ServiceRegistry:
    """Initialize global registry."""
    global _registry
    _registry = ServiceRegistry(firestore_client)
    return _registry


def get_registry() -> Optional[ServiceRegistry]:
    """Get global registry instance."""
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry

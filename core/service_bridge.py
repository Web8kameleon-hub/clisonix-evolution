"""
CLISONIX SERVICE BRIDGE
========================
Ndërlidhës i shërbimeve - mundëson komunikim midis moduleve me efikasitet absolut.

Përdorimi:
    from core.service_bridge import bridge, call_service, get_all_endpoints
    
    # Thirr një endpoint nga çdo shërbim
    result = await call_service("ocean", "/api/chat", method="POST", data={"message": "Hello"})
    
    # Merr të gjitha endpoints
    endpoints = get_all_endpoints()
"""

import os
import sys
import json
import asyncio
import aiohttp
import httpx
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging

# Import registry
from core.auto_registry import registry, discover_all

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ServiceBridge")

# =============================================================================
# SERVICE BRIDGE
# =============================================================================

class ServiceBridge:
    """Ndërlidhës për komunikim midis shërbimeve"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self._client: Optional[httpx.AsyncClient] = None
        self._sync_client: Optional[httpx.Client] = None
        self._health_cache: Dict[str, Dict] = {}
        
    @property
    def client(self) -> httpx.AsyncClient:
        """Async HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    @property
    def sync_client(self) -> httpx.Client:
        """Sync HTTP client"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(timeout=30.0)
        return self._sync_client
    
    async def close(self):
        """Mbyll clients"""
        if self._client:
            await self._client.aclose()
        if self._sync_client:
            self._sync_client.close()
    
    # =========================================================================
    # SERVICE CALLS
    # =========================================================================
    
    async def call(
        self,
        service: str,
        path: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Thirr një endpoint async"""
        
        # Sigurohu që registry është i zbuluar
        if not registry._discovered:
            discover_all()
        
        # Merr informacionin e shërbimit
        svc = registry.get_service(service)
        if not svc:
            return {"error": f"Shërbimi '{service}' nuk u gjet", "success": False}
        
        url = f"http://localhost:{svc.port}{path}"
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, params=params, headers=headers)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, params=params, headers=headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, params=params, headers=headers)
            else:
                return {"error": f"Metoda '{method}' nuk suportohet", "success": False}
            
            # Parse response
            try:
                result = response.json()
            except:
                result = {"text": response.text}
            
            return {
                "success": response.is_success,
                "status_code": response.status_code,
                "data": result,
                "service": service,
                "url": url
            }
            
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Nuk mund të lidhet me {service} në port {svc.port}",
                "service": service,
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "service": service,
                "url": url
            }
    
    def call_sync(
        self,
        service: str,
        path: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Thirr një endpoint sync"""
        
        # Sigurohu që registry është i zbuluar
        if not registry._discovered:
            discover_all()
        
        # Merr informacionin e shërbimit
        svc = registry.get_service(service)
        if not svc:
            return {"error": f"Shërbimi '{service}' nuk u gjet", "success": False}
        
        url = f"http://localhost:{svc.port}{path}"
        
        try:
            if method.upper() == "GET":
                response = self.sync_client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = self.sync_client.post(url, json=data, params=params, headers=headers)
            elif method.upper() == "PUT":
                response = self.sync_client.put(url, json=data, params=params, headers=headers)
            elif method.upper() == "DELETE":
                response = self.sync_client.delete(url, params=params, headers=headers)
            else:
                return {"error": f"Metoda '{method}' nuk suportohet", "success": False}
            
            try:
                result = response.json()
            except:
                result = {"text": response.text}
            
            return {
                "success": response.is_success,
                "status_code": response.status_code,
                "data": result,
                "service": service,
                "url": url
            }
            
        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Nuk mund të lidhet me {service} në port {svc.port}",
                "service": service,
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "service": service,
                "url": url
            }
    
    # =========================================================================
    # HEALTH CHECKS
    # =========================================================================
    
    async def check_health(self, service: str) -> Dict[str, Any]:
        """Kontrollo shëndetin e një shërbimi"""
        health_paths = ["/health", "/api/health", "/", "/status"]
        
        svc = registry.get_service(service)
        if not svc:
            return {"service": service, "healthy": False, "error": "Shërbimi nuk u gjet"}
        
        for path in health_paths:
            result = await self.call(service, path, method="GET")
            if result.get("success"):
                self._health_cache[service] = {
                    "healthy": True,
                    "port": svc.port,
                    "checked_at": datetime.now().isoformat()
                }
                return {
                    "service": service,
                    "healthy": True,
                    "port": svc.port,
                    "path": path
                }
        
        self._health_cache[service] = {
            "healthy": False,
            "port": svc.port,
            "checked_at": datetime.now().isoformat()
        }
        return {"service": service, "healthy": False, "port": svc.port}
    
    async def check_all_health(self) -> Dict[str, Any]:
        """Kontrollo shëndetin e të gjitha shërbimeve"""
        if not registry._discovered:
            discover_all()
        
        results = {}
        tasks = []
        
        for service_name in registry.services.keys():
            tasks.append(self.check_health(service_name))
        
        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        healthy_count = 0
        for result in health_results:
            if isinstance(result, dict):
                results[result["service"]] = result
                if result.get("healthy"):
                    healthy_count += 1
        
        return {
            "total": len(registry.services),
            "healthy": healthy_count,
            "unhealthy": len(registry.services) - healthy_count,
            "services": results
        }
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
    async def ocean_chat(self, message: str, persona: str = "ocean_general") -> Dict:
        """Dërgo mesazh te Ocean chat"""
        return await self.call("ocean", "/api/chat", method="POST", data={
            "message": message,
            "persona": persona
        })
    
    async def alba_collect(self, data: Dict) -> Dict:
        """Dërgo të dhëna te Alba collector"""
        return await self.call("alba", "/collect", method="POST", data=data)
    
    async def albi_process(self, data: Dict) -> Dict:
        """Proceso të dhëna me Albi"""
        return await self.call("albi", "/process", method="POST", data=data)
    
    async def jona_coordinate(self, task: Dict) -> Dict:
        """Koordino një task me Jona"""
        return await self.call("jona", "/coordinate", method="POST", data=task)
    
    def get_service_url(self, service: str, path: str = "") -> Optional[str]:
        """Merr URL për një shërbim"""
        svc = registry.get_service(service)
        if svc:
            return f"http://localhost:{svc.port}{path}"
        return None
    
    def list_endpoints(self, service: Optional[str] = None) -> List[Dict]:
        """Listo endpoints"""
        if not registry._discovered:
            discover_all()
        
        endpoints = []
        for key, ep in registry.endpoints.items():
            if service is None or ep["service"] == service:
                endpoints.append(ep)
        
        return endpoints


# =============================================================================
# GLOBAL INSTANCE & SHORTCUTS
# =============================================================================

bridge = ServiceBridge()

async def call_service(
    service: str,
    path: str,
    method: str = "GET",
    data: Optional[Dict] = None
) -> Dict:
    """Shortcut për të thirrur një shërbim"""
    return await bridge.call(service, path, method, data)

def call_service_sync(
    service: str,
    path: str,
    method: str = "GET",
    data: Optional[Dict] = None
) -> Dict:
    """Shortcut sync"""
    return bridge.call_sync(service, path, method, data)

async def check_all_health() -> Dict:
    """Kontrollo shëndetin e të gjitha shërbimeve"""
    return await bridge.check_all_health()

def get_all_endpoints() -> List[Dict]:
    """Merr të gjitha endpoints"""
    return bridge.list_endpoints()

def get_service_url(service: str, path: str = "") -> Optional[str]:
    """Merr URL"""
    return bridge.get_service_url(service, path)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clisonix Service Bridge")
    parser.add_argument("--health", action="store_true", help="Kontrollo shëndetin")
    parser.add_argument("--endpoints", action="store_true", help="Listo endpoints")
    parser.add_argument("--call", type=str, help="Thirr endpoint (format: service:path)")
    
    args = parser.parse_args()
    
    async def main():
        if args.health:
            print("\n🏥 Duke kontrolluar shëndetin e shërbimeve...\n")
            result = await check_all_health()
            print(f"✅ Healthy: {result['healthy']}/{result['total']}")
            print(f"❌ Unhealthy: {result['unhealthy']}/{result['total']}")
            print("\n📋 Detajet:")
            for name, info in result['services'].items():
                icon = "✅" if info.get('healthy') else "❌"
                port = info.get('port', 'N/A')
                print(f"  {icon} {name:12} | Port {port}")
        
        if args.endpoints:
            print("\n🌐 Endpoints:")
            endpoints = get_all_endpoints()
            current_service = ""
            for ep in sorted(endpoints, key=lambda x: (x['service'], x['path'])):
                if ep['service'] != current_service:
                    current_service = ep['service']
                    print(f"\n  📦 {current_service.upper()} (:{ep['port']})")
                print(f"      {ep['method']:6} {ep['path']}")
        
        if args.call:
            parts = args.call.split(":")
            if len(parts) == 2:
                service, path = parts
                print(f"\n🔗 Duke thirrur {service}:{path}...")
                result = await bridge.call(service, path)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        
        await bridge.close()
    
    asyncio.run(main())

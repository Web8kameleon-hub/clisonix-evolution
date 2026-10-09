import asyncio
import json
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime

class CycleASIIntegration:
    """Lidhe Cycle Engine me ASI API dhe agents"""
    
    def __init__(self, api_url: str = "http://clisonix-api:8000"):
        self.api_url = api_url
    
    async def link_agents_to_cycle(self, cycle_id: str, agents: List[str]) -> bool:
        """Lidhe agents me cycle"""
        async with httpx.AsyncClient() as client:
            payload = {
                "cycle_id": cycle_id,
                "agents": agents,
                "alignment": "moderate"
            }
            try:
                response = await client.post(
                    f"{self.api_url}/cycles/assign-agents",
                    json=payload,
                    timeout=30.0
                )
                print(f"✓ Agents linked to {cycle_id}")
                return response.status_code == 200
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
    
    async def get_cycle_metrics(self, cycle_id: str) -> Dict:
        """Merr metrics nga cycle"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/cycles/{cycle_id}/metrics",
                    timeout=30.0
                )
                return response.json() if response.status_code == 200 else {}
            except:
                return {}
    
    async def execute_cycle_with_agents(
        self,
        cycle_id: str,
        agents: List[str] = None,
        data: Dict = None
    ) -> bool:
        """Ekzekuto cycle me agents"""
        agents = agents or ["ALBA", "ALBI", "JONA"]
        
        # First link agents
        if not await self.link_agents_to_cycle(cycle_id, agents):
            return False
        
        # Then execute
        async with httpx.AsyncClient() as client:
            payload = {
                "cycle_id": cycle_id,
                "agents": agents,
                "data": data or {}
            }
            try:
                response = await client.post(
                    f"{self.api_url}/cycles/{cycle_id}/execute",
                    json=payload,
                    timeout=30.0
                )
                print(f"✓ Cycle executed: {response.json()}")
                return response.status_code == 200
            except Exception as e:
                print(f"❌ Execution error: {e}")
                return False

async def setup_production_cycle():
    """Setup production cycle sa ASI agents"""
    integration = CycleASIIntegration()
    
    # Link agents
    agents = ["ALBA", "ALBI", "JONA"]
    success = await integration.link_agents_to_cycle("cycle_prod_001", agents)
    
    if success:
        print("🔗 Production cycle linked with all agents")
        metrics = await integration.get_cycle_metrics("cycle_prod_001")
        print(f"📊 Metrics: {metrics}")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(setup_production_cycle())
    print(f"Integration status: {'✓ OK' if result else '❌ Failed'}")

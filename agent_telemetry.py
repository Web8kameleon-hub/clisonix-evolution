"""
Agent Telemetry Integration
Connects AI agents (AGIEM, ASI, Blerina) to Alba/Albi/Jona telemetry pipeline
"""

import json
import time
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentTelemetry")


@dataclass
class AgentMetrics:
    """Standardized metrics structure for AI agents"""
    agent_name: str
    timestamp: float
    status: str
    operation: Optional[str] = None
    duration_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentPulse:
    """Real-time agent health snapshot"""
    agent: str
    role: str
    status: str
    metrics: Dict[str, Any]
    ts: str


class TelemetryRouter:
    """Routes agent telemetry to Alba/Albi/Jona based on data type"""
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1",
        alba_port: int = 5050,
        albi_port: int = 6060,
        jona_port: int = 7070,
        asi_port: int = 8000,
        enabled: bool = True
    ):
        self.base_url = base_url
        self.alba_url = f"{base_url}:{alba_port}"
        self.albi_url = f"{base_url}:{albi_port}"
        self.jona_url = f"{base_url}:{jona_port}"
        self.asi_url = f"{base_url}:{asi_port}"
        self.enabled = enabled
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        logger.info(f"TelemetryRouter initialized (enabled={enabled})")
        logger.info(f"  Alba: {self.alba_url}")
        logger.info(f"  Albi: {self.albi_url}")
        logger.info(f"  Jona: {self.jona_url}")
        logger.info(f"  ASI:  {self.asi_url}")
    
    # ==================== READ OPERATIONS ====================
    
    def get_root(self) -> Dict[str, Any]:
        """Get ASI root service info"""
        try:
            r = self.session.get(f"{self.asi_url}/", timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Failed to get root: {e}")
            return {}
    
    def get_asi_status(self) -> Dict[str, Any]:
        """Get ASI orchestration status"""
        try:
            r = self.session.get(f"{self.asi_url}/asi/status", timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Failed to get ASI status: {e}")
            return {"health": "error", "error": str(e)}
    
    def get_asi_health(self) -> Dict[str, Any]:
        """Get ASI health check"""
        try:
            r = self.session.get(f"{self.asi_url}/asi/health", timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Failed to get ASI health: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def get_agent_metrics(self, agent: str) -> Dict[str, Any]:
        """Get specific agent metrics"""
        path_map = {
            "alba": "/asi/alba/metrics",
            "albi": "/asi/albi/metrics",
            "jona": "/asi/jona/metrics",
        }
        
        if agent.lower() not in path_map:
            logger.error(f"Unknown agent: {agent}")
            return {}
        
        try:
            path = path_map[agent.lower()]
            r = self.session.get(f"{self.asi_url}{path}", timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Failed to get {agent} metrics: {e}")
            return {}
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus exposition format metrics"""
        try:
            r = self.session.get(f"{self.asi_url}/metrics", timeout=5)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.error(f"Failed to get Prometheus metrics: {e}")
            return ""
    
    def pulse(self, agent: str, role: str) -> AgentPulse:
        """Get real-time agent pulse"""
        metrics = self.get_agent_metrics(agent)
        status = "ok" if metrics else "error"
        ts = datetime.now(timezone.utc).isoformat()
        return AgentPulse(
            agent=agent,
            role=role,
            status=status,
            metrics=metrics,
            ts=ts
        )
    
    # ==================== WRITE OPERATIONS ====================
    
    def send_to_alba(self, metrics: AgentMetrics) -> bool:
        """Send raw data collection metrics to Alba"""
        if not self.enabled:
            return True
            
        try:
            payload = {
                "source": metrics.agent_name,
                "timestamp": metrics.timestamp,
                "type": "agent_telemetry",
                "data": asdict(metrics)
            }
            
            response = self.session.post(
                f"{self.alba_url}/api/telemetry/ingest",
                json=payload,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                logger.debug(f"✓ Alba: {metrics.agent_name} telemetry sent")
                return True
            else:
                logger.warning(f"Alba returned {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Alba send failed: {e}")
            return False
    
    def send_to_albi(self, metrics: AgentMetrics) -> bool:
        """Send processing/analytics metrics to Albi"""
        if not self.enabled:
            return True
            
        try:
            payload = {
                "agent": metrics.agent_name,
                "timestamp": metrics.timestamp,
                "operation": metrics.operation,
                "duration_ms": metrics.duration_ms,
                "tokens": {
                    "input": metrics.input_tokens,
                    "output": metrics.output_tokens
                },
                "success": metrics.success,
                "metadata": metrics.metadata or {}
            }
            
            response = self.session.post(
                f"{self.albi_url}/api/analytics/agent",
                json=payload,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                logger.debug(f"✓ Albi: {metrics.agent_name} analytics sent")
                return True
            else:
                logger.warning(f"Albi returned {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Albi send failed: {e}")
            return False
    
    def send_to_jona(self, metrics: AgentMetrics) -> bool:
        """Send coordination/orchestration metrics to Jona"""
        if not self.enabled:
            return True
            
        try:
            payload = {
                "agent": metrics.agent_name,
                "timestamp": metrics.timestamp,
                "status": metrics.status,
                "operation": metrics.operation,
                "success": metrics.success,
                "error": metrics.error
            }
            
            response = self.session.post(
                f"{self.jona_url}/api/coordination/event",
                json=payload,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                logger.debug(f"✓ Jona: {metrics.agent_name} event sent")
                return True
            else:
                logger.warning(f"Jona returned {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Jona send failed: {e}")
            return False
    
    def execute_trinity(
        self,
        command: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Execute Trinity command via ASI"""
        try:
            body = {
                "command": command,
                "payload": payload or {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            r = self.session.post(
                f"{self.asi_url}/asi/execute",
                json=body,
                timeout=timeout
            )
            r.raise_for_status()
            
            result = r.json()
            logger.info(f"✓ Trinity command '{command}' executed: {result.get('status')}")
            return result
            
        except Exception as e:
            logger.error(f"Trinity execute failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def send_all(self, metrics: AgentMetrics) -> Dict[str, bool]:
        """Send metrics to all three services"""
        results = {
            "alba": self.send_to_alba(metrics),
            "albi": self.send_to_albi(metrics),
            "jona": self.send_to_jona(metrics)
        }
        
        success_count = sum(results.values())
        logger.info(
            f"📊 {metrics.agent_name}.{metrics.operation}: "
            f"{success_count}/3 telemetry endpoints reached"
        )
        
        return results


class AgentTelemetryMixin:
    """Mixin class for AI agents to add telemetry capabilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telemetry = TelemetryRouter(
            enabled=kwargs.get("telemetry_enabled", True)
        )
        self._operation_start: Optional[float] = None
        self._current_operation: Optional[str] = None
    
    def start_operation(self, operation_name: str):
        """Mark the start of an operation for timing"""
        self._operation_start = time.time()
        self._current_operation = operation_name
    
    def end_operation(
        self,
        success: bool = True,
        error: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Mark the end of an operation and send telemetry"""
        if self._operation_start is None:
            logger.warning("end_operation called without start_operation")
            return
        
        duration_ms = (time.time() - self._operation_start) * 1000
        
        metrics = AgentMetrics(
            agent_name=getattr(self, "agent_name", self.__class__.__name__),
            timestamp=time.time(),
            status="success" if success else "error",
            operation=self._current_operation,
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            success=success,
            error=error,
            metadata=metadata
        )
        
        self.telemetry.send_all(metrics)
        self._operation_start = None
        self._current_operation = None


# Standalone telemetry sender for scripts
_global_router: Optional[TelemetryRouter] = None


def init_telemetry(
    base_url: str = "http://127.0.0.1",
    alba_port: int = 5050,
    albi_port: int = 6060,
    jona_port: int = 7070,
    asi_port: int = 8000,
    enabled: bool = True
) -> TelemetryRouter:
    """Initialize global telemetry router"""
    global _global_router
    _global_router = TelemetryRouter(
        base_url=base_url,
        alba_port=alba_port,
        albi_port=albi_port,
        jona_port=jona_port,
        asi_port=asi_port,
        enabled=enabled
    )
    return _global_router


def send_agent_telemetry(
    agent_name: str,
    operation: str,
    duration_ms: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, bool]:
    """Send telemetry using global router"""
    if _global_router is None:
        router = init_telemetry()
    else:
        router = _global_router
    
    metrics = AgentMetrics(
        agent_name=agent_name,
        timestamp=time.time(),
        status="success" if success else "error",
        operation=operation,
        duration_ms=duration_ms,
        success=success,
        error=error,
        metadata=metadata
    )
    
    return router.send_all(metrics)


def telemetry_loop(interval: int = 15, max_iterations: Optional[int] = None):
    """
    Main telemetry monitoring loop
    
    Args:
        interval: Seconds between checks
        max_iterations: Max loops (None = infinite)
    """
    logger.info("Starting Agent Telemetry loop")
    
    router = init_telemetry()
    root = router.get_root()
    logger.info(f"Service: {root.get('service')} v{root.get('version')}")
    
    iteration = 0
    
    while True:
        try:
            # Check ASI orchestrator status
            asi = router.get_asi_status()
            health = router.get_asi_health()
            
            # Get Trinity pulses
            alba_pulse = router.pulse("alba", "collector")
            albi_pulse = router.pulse("albi", "analyzer")
            jona_pulse = router.pulse("jona", "synthesizer")
            
            # Health-gated action
            if (
                asi.get("health") == "ok"
                and health.get("status") == "healthy"
                and jona_pulse.metrics.get("alignment_ok", True)
            ):
                # Safe to request analysis cycle
                res = router.execute_trinity("analyze_system", {"priority": "normal"})
                logger.info(f"Executed analyze_system: {json.dumps(res)[:300]}")
            else:
                logger.warning("Health/alignment not OK; deferring actions")
            
            # Consume Prometheus metrics (optional)
            prom = router.get_prometheus_metrics()
            logger.debug(f"Prometheus metrics snapshot len={len(prom)}")
            
            # Emit pulse logs
            for p in (alba_pulse, albi_pulse, jona_pulse):
                logger.info(f"Pulse {p.agent}: {json.dumps(asdict(p))[:500]}")
            
            iteration += 1
            if max_iterations and iteration >= max_iterations:
                logger.info(f"Reached max iterations ({max_iterations}), stopping")
                break
            
        except Exception as e:
            logger.error(f"Telemetry loop error: {e}", exc_info=True)
        
        time.sleep(interval)


if __name__ == "__main__":
    import sys
    
    print("🧪 Testing Agent Telemetry Integration\n")
    
    # Test mode: send test metrics
    if "--test" in sys.argv:
        router = TelemetryRouter()
        
        # Test AGIEM telemetry
        agiem_metrics = AgentMetrics(
            agent_name="AGIEM",
            timestamp=time.time(),
            status="success",
            operation="pipeline_execution",
            duration_ms=1234.56,
            input_tokens=500,
            output_tokens=150,
            success=True,
            metadata={"stage": "data_collection", "nodes": 3}
        )
        
        print("Testing AGIEM -> Alba/Albi/Jona...")
        results = router.send_all(agiem_metrics)
        print(f"Results: {results}\n")
        
        # Test ASI telemetry
        asi_metrics = AgentMetrics(
            agent_name="ASI",
            timestamp=time.time(),
            status="success",
            operation="realtime_analysis",
            duration_ms=567.89,
            success=True,
            metadata={"nodes": ["ALBA", "ALBI", "JONA"], "health_score": 0.95}
        )
        
        print("Testing ASI -> Alba/Albi/Jona...")
        results = router.send_all(asi_metrics)
        print(f"Results: {results}\n")
        
        # Test Blerina telemetry
        blerina_metrics = AgentMetrics(
            agent_name="Blerina",
            timestamp=time.time(),
            status="success",
            operation="youtube_metadata_extraction",
            duration_ms=234.12,
            success=True,
            metadata={"video_id": "dQw4w9WgXcQ", "views": 1721885158}
        )
        
        print("Testing Blerina -> Alba/Albi/Jona...")
        results = router.send_all(blerina_metrics)
        print(f"Results: {results}\n")
        
        print("✅ Telemetry integration test complete")
    
    # Monitor mode: run telemetry loop
    elif "--monitor" in sys.argv:
        max_iter = int(sys.argv[sys.argv.index("--max-iterations") + 1]) if "--max-iterations" in sys.argv else None
        interval = int(sys.argv[sys.argv.index("--interval") + 1]) if "--interval" in sys.argv else 15
        
        telemetry_loop(interval=interval, max_iterations=max_iter)
    
    else:
        print("Usage:")
        print("  python agent_telemetry.py --test")
        print("  python agent_telemetry.py --monitor [--interval 15] [--max-iterations 10]")


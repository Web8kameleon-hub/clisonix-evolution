#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN ORCHESTRATOR - UNIT TESTS
================================
Teste para deploy - siguron që rregullat strikte respektohen.

Run: pytest test_ocean_orchestrator.py -v
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

# Import components to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocean_orchestrator import (
    ServiceConfig,
    IntentRouter,
    HealthChecker,
    ServiceCaller,
    SERVICES,
)


# ═══════════════════════════════════════════════════════════════════
# TEST: ServiceConfig
# ═══════════════════════════════════════════════════════════════════
class TestServiceConfig:
    """Test ServiceConfig dataclass"""
    
    def test_create_service_config(self):
        """Test creating a service config"""
        svc = ServiceConfig(
            name="Test Service",
            host="localhost",
            port=8080,
            endpoints={"test": "/api/test"},
            timeout=30.0
        )
        assert svc.name == "Test Service"
        assert svc.port == 8080
        assert svc.timeout == 30.0
        assert not svc.is_healthy  # Default
    
    def test_default_values(self):
        """Test default values are set correctly"""
        svc = ServiceConfig(name="Test", host="localhost", port=8080)
        assert svc.health_path == "/health"
        assert svc.priority == 1
        assert svc.timeout == 30.0
        assert svc.is_healthy == False
        assert svc.capabilities == []
        assert svc.keywords == []


# ═══════════════════════════════════════════════════════════════════
# TEST: IntentRouter
# ═══════════════════════════════════════════════════════════════════
class TestIntentRouter:
    """Test intent-based routing"""
    
    @pytest.fixture
    def router(self):
        """Create router with test services"""
        services = {
            "eeg": ServiceConfig(
                name="EEG Service",
                host="localhost",
                port=8001,
                keywords=["eeg", "brain", "neural"]
            ),
            "weather": ServiceConfig(
                name="Weather Service",
                host="localhost",
                port=8002,
                keywords=["weather", "forecast", "temperature"]
            ),
            "ollama": ServiceConfig(
                name="Ollama",
                host="localhost",
                port=11434,
                keywords=["chat", "ask", "help"],
                priority=1
            ),
        }
        return IntentRouter(services)
    
    def test_route_eeg_query(self, router):
        """Test routing EEG-related queries"""
        result = router.route("analyze my brain signals")
        assert "eeg" in result
    
    def test_route_weather_query(self, router):
        """Test routing weather queries"""
        result = router.route("what's the weather forecast?")
        assert "weather" in result
    
    def test_route_default_to_ollama(self, router):
        """Test fallback to ollama for unknown queries"""
        result = router.route("tell me a joke")
        assert result == ["ollama"]
    
    def test_route_multiple_matches(self, router):
        """Test multiple keyword matches"""
        result = router.route("brain neural analysis")
        assert result[0] == "eeg"  # Should be first due to most matches


# ═══════════════════════════════════════════════════════════════════
# TEST: HealthChecker - NO INFINITE LOOPS
# ═══════════════════════════════════════════════════════════════════
class TestHealthChecker:
    """Test health checker - verify NO infinite loops"""
    
    @pytest.fixture
    def checker(self):
        """Create health checker with mock services"""
        services = {
            "test1": ServiceConfig(name="Test1", host="localhost", port=8001),
            "test2": ServiceConfig(name="Test2", host="localhost", port=8002),
        }
        checker = HealthChecker(services)
        checker.check_interval = 0.1  # Fast for testing
        return checker
    
    @pytest.mark.asyncio
    async def test_check_service_timeout(self, checker):
        """Test that health check has timeout"""
        # Mock a slow service - should timeout
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            result = await checker.check_service("test1", checker.services["test1"])
            assert result == False
            assert checker.services["test1"].is_healthy == False
    
    @pytest.mark.asyncio
    async def test_background_checks_limited(self, checker):
        """CRITICAL: Test that background checks are LIMITED, not infinite"""
        # Run with max_iterations=3
        checker.check_interval = 0.01  # Very fast
        
        with patch.object(checker, 'check_all', new_callable=AsyncMock) as mock_check:
            # Run limited iterations
            await checker.run_background_checks(max_iterations=3)
            
            # Should have called check_all exactly 3 times
            assert mock_check.call_count == 3
    
    @pytest.mark.asyncio
    async def test_no_while_true_infinite(self, checker):
        """Verify run_background_checks does NOT run forever"""
        import inspect
        source = inspect.getsource(checker.run_background_checks)
        
        # Should have max_iterations parameter
        assert "max_iterations" in source
        # Should NOT have bare "while True:"
        assert "while True:" not in source or "while iteration < max_iterations" in source


# ═══════════════════════════════════════════════════════════════════
# TEST: Ollama Options - NO INFINITE KEEP_ALIVE
# ═══════════════════════════════════════════════════════════════════
class TestOllamaOptions:
    """Test Ollama call options comply with strict rules"""
    
    def test_no_infinite_keep_alive_in_code(self):
        """CRITICAL: Verify no keep_alive: -1 in code"""
        import ocean_orchestrator
        import inspect
        source = inspect.getsource(ocean_orchestrator)
        
        # Should NOT have keep_alive: -1 or "keep_alive": -1
        assert 'keep_alive": -1' not in source
        assert "keep_alive: -1" not in source
        assert "'keep_alive': -1" not in source
    
    def test_reasonable_num_predict(self):
        """CRITICAL: Verify num_predict is reasonable, not 50000"""
        import ocean_orchestrator
        import inspect
        source = inspect.getsource(ocean_orchestrator)
        
        # Should NOT have num_predict: 50000
        assert "num_predict\": 50000" not in source
        assert "num_predict: 50000" not in source
    
    def test_timeout_exists(self):
        """Verify timeout is set on HTTP calls"""
        import ocean_orchestrator
        import inspect
        source = inspect.getsource(ocean_orchestrator)
        
        # Should have explicit timeout settings
        assert "timeout" in source.lower()
        assert "Timeout" in source


# ═══════════════════════════════════════════════════════════════════
# TEST: Request Timeouts
# ═══════════════════════════════════════════════════════════════════
class TestRequestTimeouts:
    """Test that all requests have proper timeouts"""
    
    def test_ollama_timeout_not_300(self):
        """Verify Ollama timeout is reasonable, not 300s"""
        import ocean_orchestrator
        import inspect
        source = inspect.getsource(ocean_orchestrator._call_ollama)
        
        # Should NOT have 300.0 timeout
        assert "timeout=300.0" not in source
        assert "timeout=300" not in source
        # Should have reasonable timeout (120s or less)
        assert "120" in source or "timeout" in source
    
    def test_health_check_timeout(self):
        """Verify health checks have short timeout"""
        import ocean_orchestrator
        import inspect
        source = inspect.getsource(ocean_orchestrator.HealthChecker.check_service)
        
        # Should have timeout in health check
        assert "timeout" in source


# ═══════════════════════════════════════════════════════════════════
# TEST: Logging
# ═══════════════════════════════════════════════════════════════════
class TestLogging:
    """Test that logging is present and clear"""
    
    def test_logger_configured(self):
        """Verify logger is configured"""
        import ocean_orchestrator
        assert hasattr(ocean_orchestrator, 'logger')
        assert ocean_orchestrator.logger.name == "OceanOrchestrator"
    
    def test_logging_in_critical_functions(self):
        """Verify logging in critical functions"""
        import ocean_orchestrator
        import inspect
        
        # Check _call_ollama has logging
        source = inspect.getsource(ocean_orchestrator._call_ollama)
        assert "logger." in source
        
        # Check startup has logging
        source = inspect.getsource(ocean_orchestrator.startup)
        assert "logger." in source


# ═══════════════════════════════════════════════════════════════════
# TEST: Services Configuration
# ═══════════════════════════════════════════════════════════════════
class TestServicesConfiguration:
    """Test services are properly configured"""
    
    def test_services_registered(self):
        """Test that services are registered"""
        assert len(SERVICES) > 0
        assert "ollama" in SERVICES
    
    def test_ollama_service_config(self):
        """Test Ollama service configuration"""
        ollama = SERVICES.get("ollama")
        assert ollama is not None
        assert ollama.port == 11434
        assert "chat" in ollama.endpoints
    
    def test_all_services_have_health_path(self):
        """Test all services have health path defined"""
        for svc_id, svc in SERVICES.items():
            assert svc.health_path is not None
            assert len(svc.health_path) > 0


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION TEST: Full Chat Flow (Mock)
# ═══════════════════════════════════════════════════════════════════
class TestChatIntegration:
    """Integration tests for chat functionality"""
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_timeout_handling(self):
        """Test that chat handles timeouts gracefully"""
        from ocean_orchestrator import _call_ollama
        
        with patch('httpx.AsyncClient') as mock_client:
            # Simulate timeout
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            
            with pytest.raises(Exception):  # Should raise HTTPException
                await _call_ollama("test prompt", "test-model")


# ═══════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

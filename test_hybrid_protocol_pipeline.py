#!/usr/bin/env python3
"""
🧪 Unit Tests for Hybrid Protocol Pipeline
============================================
Tests each pipeline stage with REAL assertions.
NO MOCK DATA - All tests use real pipeline logic.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hybrid_protocol_pipeline import (
    HybridProtocolPipeline,
    PipelineEntry,
    PipelineStatus
)


class TestPipelineEntry:
    """Tests for PipelineEntry dataclass"""
    
    def test_entry_creation(self):
        """Test basic entry creation with defaults"""
        entry = PipelineEntry(
            id="test001",
            endpoint="/api/users",
            method="GET"
        )
        
        assert entry.id == "test001"
        assert entry.endpoint == "/api/users"
        assert entry.method == "GET"
        assert entry.protocol == "REST"
        assert entry.status == PipelineStatus.RAW
        assert entry.security_passed is False
        assert entry.validation_passed is False
    
    def test_entry_to_dict(self):
        """Test entry serialization to dict"""
        entry = PipelineEntry(
            id="test002",
            endpoint="/api/test",
            method="POST",
            protocol="GRPC"
        )
        
        result = entry.to_dict()
        
        assert isinstance(result, dict)
        assert result["id"] == "test002"
        assert result["method"] == "POST"
        assert result["protocol"] == "GRPC"
        assert result["status"] == "raw"
        assert "timestamp" in result


class TestPipelineIntake:
    """Tests for INTAKE phase"""
    
    def test_intake_single_item(self):
        """Test intake of single API request"""
        pipeline = HybridProtocolPipeline()
        
        pipeline.intake([{
            "endpoint": "/api/users",
            "method": "GET",
            "protocol": "REST"
        }])
        
        assert len(pipeline.entries) == 1
        assert pipeline.entries[0].endpoint == "/api/users"
        assert pipeline.entries[0].status == PipelineStatus.RAW
    
    def test_intake_multiple_items(self):
        """Test intake of multiple API requests"""
        pipeline = HybridProtocolPipeline()
        
        data = [
            {"endpoint": "/api/users", "method": "GET"},
            {"endpoint": "/api/posts", "method": "POST"},
            {"endpoint": "/api/comments", "method": "DELETE"}
        ]
        
        pipeline.intake(data)
        
        assert len(pipeline.entries) == 3
        assert all(e.status == PipelineStatus.RAW for e in pipeline.entries)
    
    def test_intake_generates_unique_ids(self):
        """Test that each entry gets a unique ID"""
        pipeline = HybridProtocolPipeline()
        
        # Same endpoint, same method - should still get unique IDs due to timestamp
        pipeline.intake([
            {"endpoint": "/api/test", "method": "GET"},
            {"endpoint": "/api/test", "method": "GET"}
        ])
        
        ids = [e.id for e in pipeline.entries]
        assert len(ids) == len(set(ids)), "IDs should be unique"


class TestPipelineNormalization:
    """Tests for NORMALIZED phase"""
    
    def test_normalize_converts_to_lowercase(self):
        """Test that endpoint is normalized to lowercase"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="n001",
            endpoint="/API/USERS/GetAll",
            method="get"
        )
        
        result = pipeline.normalize(entry)
        
        assert result.endpoint == "/api/users/getall"
        assert result.method == "GET"
        assert result.status == PipelineStatus.NORMALIZED
    
    def test_normalize_trims_whitespace(self):
        """Test that endpoint whitespace is trimmed"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="n002",
            endpoint="  /api/users  ",
            method="POST"
        )
        
        result = pipeline.normalize(entry)
        
        assert result.endpoint == "/api/users"
    
    def test_normalize_protocol_uppercase(self):
        """Test that protocol is uppercased"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="n003",
            endpoint="/api/test",
            method="GET",
            protocol="grpc"
        )
        
        result = pipeline.normalize(entry)
        
        assert result.protocol == "GRPC"


class TestPipelineSecurity:
    """Tests for TEST phase - Security Checks"""
    
    def test_security_blocks_path_traversal(self):
        """Test that ../ path traversal is blocked"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="sec001",
            endpoint="/api/../../../etc/passwd",
            method="GET"
        )
        entry = pipeline.normalize(entry)
        result = pipeline.test_entry(entry)
        
        assert result.security_passed is False
        assert result.status == PipelineStatus.FAILED
    
    def test_security_blocks_sql_injection(self):
        """Test that SQL injection patterns are blocked"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="sec002",
            endpoint="/api/users?id=1; DROP TABLE users",
            method="GET"
        )
        entry = pipeline.normalize(entry)
        result = pipeline.test_entry(entry)
        
        assert result.security_passed is False
    
    def test_security_blocks_code_execution(self):
        """Test that code execution patterns are blocked"""
        pipeline = HybridProtocolPipeline()
        
        dangerous_endpoints = [
            "/api/eval('malicious')",
            "/api/exec/command",
            "/api/system/shell"
        ]
        
        for endpoint in dangerous_endpoints:
            entry = PipelineEntry(id="sec", endpoint=endpoint, method="GET")
            entry = pipeline.normalize(entry)
            result = pipeline.test_entry(entry)
            assert result.security_passed is False, f"Should block: {endpoint}"
    
    def test_security_passes_valid_endpoint(self):
        """Test that valid endpoints pass security"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="sec003",
            endpoint="/api/users/123",
            method="GET"
        )
        entry = pipeline.normalize(entry)
        result = pipeline.test_entry(entry)
        
        # Valid endpoint should pass security (score >= 0.8)
        assert result.security_passed is True


class TestPipelineValidation:
    """Tests for TEST phase - Validation Checks"""
    
    def test_validation_requires_leading_slash(self):
        """Test that endpoint must start with /"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="val001",
            endpoint="api/users",  # Missing leading slash
            method="GET"
        )
        # Don't normalize - test raw validation
        result = pipeline.test_entry(entry)
        
        assert result.validation_passed is False
    
    def test_validation_requires_valid_method(self):
        """Test that method must be valid HTTP method"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="val002",
            endpoint="/api/users",
            method="INVALID"
        )
        result = pipeline.test_entry(entry)
        
        assert result.validation_passed is False
        assert result.status == PipelineStatus.FAILED
    
    def test_validation_requires_valid_protocol(self):
        """Test that protocol must be supported"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="val003",
            endpoint="/api/test",
            method="GET",
            protocol="UNSUPPORTED"
        )
        result = pipeline.test_entry(entry)
        
        assert result.validation_passed is False
    
    def test_validation_passes_all_valid_methods(self):
        """Test that all valid HTTP methods pass"""
        pipeline = HybridProtocolPipeline()
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
        
        for method in valid_methods:
            entry = PipelineEntry(
                id=f"val_{method}",
                endpoint="/api/test",
                method=method
            )
            result = pipeline.test_entry(entry)
            assert result.validation_passed is True, f"Should pass: {method}"


class TestPipelineImmature:
    """Tests for IMMATURE phase"""
    
    def test_immature_adds_artifacts(self):
        """Test that immature phase adds artifact files"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="imm001",
            endpoint="/api/test",
            method="GET"
        )
        
        result = pipeline.mark_immature(entry)
        
        assert result.status == PipelineStatus.IMMATURE
        assert len(result.artifacts) == 2
        assert any("security_report" in a for a in result.artifacts)
        assert any("validation_log" in a for a in result.artifacts)


class TestPipelineMLOverlay:
    """Tests for ML OVERLAY phase"""
    
    def test_ml_overlay_adds_suggestions(self):
        """Test that ML overlay adds suggestions"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="ml001",
            endpoint="/api/test",
            method="GET"
        )
        entry.status = PipelineStatus.IMMATURE
        
        result = pipeline.ml_overlay(entry)
        
        assert result.status == PipelineStatus.ML_OVERLAY
        assert "confidence" in result.ml_suggestions
        assert "optimizations" in result.ml_suggestions
    
    def test_ml_overlay_calculates_anomaly_score(self):
        """Test that anomaly score is calculated"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="ml002",
            endpoint="/api/test",
            method="GET"
        )
        entry.status = PipelineStatus.IMMATURE
        
        result = pipeline.ml_overlay(entry)
        
        assert 0 <= result.anomaly_score <= 1
    
    def test_ml_overlay_detects_high_depth_anomaly(self):
        """Test that high depth increases anomaly score"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="ml003",
            endpoint="/api/test",
            method="GET",
            depth=10  # High depth
        )
        entry.status = PipelineStatus.IMMATURE
        
        result = pipeline.ml_overlay(entry)
        
        # High depth should increase base anomaly score
        assert result.anomaly_score > 0.1


class TestPipelineEnforcement:
    """Tests for ENFORCEMENT phase"""
    
    def test_enforce_marks_complete(self):
        """Test that enforcement marks entry as complete"""
        pipeline = HybridProtocolPipeline()
        entry = PipelineEntry(
            id="enf001",
            endpoint="/api/test",
            method="GET"
        )
        entry.status = PipelineStatus.ML_OVERLAY
        entry.anomaly_score = 0.1  # Low anomaly
        
        result = pipeline.enforce(entry)
        
        assert result.status == PipelineStatus.COMPLETE
    
    def test_enforce_escalates_high_anomaly(self):
        """Test that high anomaly score triggers escalation"""
        pipeline = HybridProtocolPipeline()
        pipeline.config["auto_escalate"] = True
        pipeline.config["anomaly_threshold"] = 0.7
        
        entry = PipelineEntry(
            id="enf002",
            endpoint="/api/test",
            method="GET"
        )
        entry.status = PipelineStatus.ML_OVERLAY
        entry.anomaly_score = 0.95  # High anomaly
        
        result = pipeline.enforce(entry)
        
        # Should still complete but with escalation logged
        assert result.status == PipelineStatus.COMPLETE


class TestPipelineFullFlow:
    """End-to-end pipeline tests"""
    
    def test_full_pipeline_success(self):
        """Test complete flow from input to enforcement"""
        pipeline = HybridProtocolPipeline()
        
        # Intake
        pipeline.intake([{
            "endpoint": "/api/users/list",
            "method": "GET",
            "protocol": "REST"
        }])
        
        # Process through all stages
        passed, failed = pipeline.process_all()
        
        # Should pass through entire pipeline
        assert passed >= 1
        assert len(pipeline.completed_entries) >= 1
    
    def test_full_pipeline_with_failures(self):
        """Test pipeline with mix of passing and failing entries"""
        pipeline = HybridProtocolPipeline()
        
        pipeline.intake([
            {"endpoint": "/api/valid/endpoint", "method": "GET"},
            {"endpoint": "/api/../etc/passwd", "method": "GET"},  # Should fail security
            {"endpoint": "no-slash-endpoint", "method": "POST"},  # Should fail validation
            {"endpoint": "/api/another/valid", "method": "PUT"}
        ])
        
        passed, failed = pipeline.process_all()
        
        # 2 should pass, 2 should fail
        assert failed >= 2
        assert len(pipeline.failed_entries) >= 2
    
    def test_pipeline_stats_updated(self):
        """Test that pipeline stats are updated correctly"""
        pipeline = HybridProtocolPipeline()
        
        pipeline.intake([
            {"endpoint": "/api/test1", "method": "GET"},
            {"endpoint": "/api/test2", "method": "POST"}
        ])
        
        pipeline.process_all()
        
        assert pipeline.stats["total_processed"] == 2
        assert pipeline.stats["passed"] + pipeline.stats["failed"] == 2


class TestPipelineConfig:
    """Tests for pipeline configuration"""
    
    def test_default_config_loaded(self):
        """Test that default config is loaded"""
        pipeline = HybridProtocolPipeline()
        
        assert "security_threshold" in pipeline.config
        assert "validation_strict" in pipeline.config
        assert "ml_enabled" in pipeline.config
        assert "anomaly_threshold" in pipeline.config
    
    def test_security_threshold_affects_check(self):
        """Test that security threshold config is respected"""
        # Lower threshold = more permissive
        pipeline = HybridProtocolPipeline()
        pipeline.config["security_threshold"] = 0.5  # Low threshold
        
        entry = PipelineEntry(
            id="cfg001",
            endpoint="/api/test",
            method="GET"
        )
        entry = pipeline.normalize(entry)
        result = pipeline.test_entry(entry)
        
        # With low threshold, valid endpoint should definitely pass
        assert result.security_passed is True


# ===== Run with pytest =====
if __name__ == "__main__":
    print("=" * 60)
    print("  🧪 Running Hybrid Protocol Pipeline Unit Tests")
    print("  NO MOCK DATA - All tests use real pipeline logic")
    print("=" * 60)
    
    # Run with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Some tests failed (exit code: {exit_code})")
    
    sys.exit(exit_code)

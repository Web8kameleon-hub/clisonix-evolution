"""
Tests for Hybrid Protocol Sovereign System
==========================================
Unit tests for all components.
"""

import unittest
import json
from datetime import datetime

# Import components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.canonical_table import (
    CanonicalTable, CanonicalRow, compute_maturity_state,
    Status, MaturityState
)
from core.parser import parse_input, RESTParser, GraphQLParser
from core.validator import validate_security, validate_schema
from labs.lab_executor import execute_lab, DataValidationLab
from agents.agent_registry import select_agent, AgentRegistry
from ml_overlay.ml_manager import run_ml_models, is_ml_eligible
from enforcement.enforcement_manager import apply_enforcement


class TestCanonicalTable(unittest.TestCase):
    """Tests for canonical table"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.table = CanonicalTable(
            storage_path="data/test_canonical.json",
            excel_path="data/test_canonical.xlsx"
        )
    
    def test_append_row(self):
        """Test appending a row"""
        row = CanonicalRow(
            cycle=1,
            layer="L1",
            variant="A",
            input_type="test",
            source_protocol="REST"
        )
        
        appended = self.table.append(row)
        
        self.assertIsNotNone(appended.row_id)
        self.assertEqual(appended.cycle, 1)
        self.assertEqual(appended.status, Status.RAW.value)
    
    def test_compute_maturity_immature(self):
        """Test maturity computation for immature row"""
        row = {
            'security': 'PENDING',
            'schema_validation': 'PENDING',
            'status': 'RAW',
            'artifacts': None
        }
        
        maturity = compute_maturity_state(row)
        self.assertEqual(maturity, MaturityState.IMMATURE.value)
    
    def test_compute_maturity_maturing(self):
        """Test maturity computation for maturing row"""
        row = {
            'security': 'PASS',
            'schema_validation': 'PASS',
            'status': 'TEST',
            'artifacts': None
        }
        
        maturity = compute_maturity_state(row)
        self.assertEqual(maturity, MaturityState.MATURING.value)
    
    def test_compute_maturity_mature(self):
        """Test maturity computation for mature row"""
        row = {
            'security': 'PASS',
            'schema_validation': 'PASS',
            'status': 'READY',
            'artifacts': ['artifact-1', 'artifact-2']
        }
        
        maturity = compute_maturity_state(row)
        self.assertEqual(maturity, MaturityState.MATURE.value)


class TestParser(unittest.TestCase):
    """Tests for protocol parser"""
    
    def test_parse_rest_input(self):
        """Test parsing REST input"""
        payload = {
            "method": "POST",
            "path": "/api/v1/orders",
            "body": {
                "cycle": 5,
                "layer": "L2",
                "variant": "B",
                "input_type": "order"
            }
        }
        
        result = parse_input(payload, "REST")
        
        self.assertEqual(result['cycle'], 5)
        self.assertEqual(result['layer'], "L2")
        self.assertEqual(result['source_protocol'], "REST")
        self.assertEqual(result['status'], "RAW")
    
    def test_parse_graphql_input(self):
        """Test parsing GraphQL input"""
        payload = {
            "query": "mutation CreateOrder { ... }",
            "variables": {
                "cycle": 3,
                "layer": "L1",
                "variant": "A"
            }
        }
        
        result = parse_input(payload, "GraphQL")
        
        self.assertEqual(result['cycle'], 3)
        self.assertEqual(result['source_protocol'], "GraphQL")
        self.assertEqual(result['input_type'], "mutation")
    
    def test_parse_simple_dict(self):
        """Test parsing simple dictionary"""
        payload = {
            "cycle": 1,
            "layer": "L1",
            "variant": "A",
            "input_type": "grain"
        }
        
        result = parse_input(payload, "REST")
        
        self.assertEqual(result['cycle'], 1)
        self.assertEqual(result['input_type'], "grain")


class TestValidator(unittest.TestCase):
    """Tests for validator"""
    
    def test_validate_schema_pass(self):
        """Test schema validation passing"""
        row = {
            'cycle': 1,
            'layer': 'L1',
            'variant': 'A',
            'input_type': 'test',
            'source_protocol': 'REST'
        }
        
        result = validate_schema(row)
        self.assertEqual(result, 'PASS')
    
    def test_validate_schema_fail_missing_field(self):
        """Test schema validation failing for missing field"""
        row = {
            'cycle': 1,
            'layer': 'L1'
            # Missing: variant, input_type, source_protocol
        }
        
        result = validate_schema(row)
        self.assertEqual(result, 'FAIL')
    
    def test_validate_security_no_auth(self):
        """Test security validation with no auth"""
        row = {'cycle': 1}
        
        result = validate_security(row, method="NONE")
        self.assertEqual(result, 'PASS')


class TestLabExecutor(unittest.TestCase):
    """Tests for lab executor"""
    
    def test_execute_data_validation_lab(self):
        """Test data validation lab"""
        row = {
            'cycle': 1,
            'layer': 'L1',
            'variant': 'A',
            'input_type': 'test',
            'source_protocol': 'REST'
        }
        
        lab_result, artifacts = execute_lab(row)
        
        self.assertIsNotNone(lab_result)
        self.assertIn('labs_executed', lab_result)
        self.assertGreater(lab_result['labs_executed'], 0)
    
    def test_lab_generates_artifacts(self):
        """Test that labs generate artifacts"""
        row = {
            'cycle': 1,
            'layer': 'L1',
            'variant': 'A',
            'input_type': 'test',
            'source_protocol': 'REST'
        }
        
        lab_result, artifacts = execute_lab(row)
        
        # Should generate at least one artifact
        self.assertGreater(len(artifacts), 0)


class TestAgentRegistry(unittest.TestCase):
    """Tests for agent registry"""
    
    def test_select_agent(self):
        """Test agent selection"""
        row = {
            'cycle': 1,
            'layer': 'L1',
            'variant': 'A',
            'input_type': 'test',
            'source_protocol': 'REST'
        }
        
        agent_id = select_agent(row)
        
        self.assertIsNotNone(agent_id)
        self.assertIn('agent-', agent_id)
    
    def test_registry_has_default_agents(self):
        """Test that registry has default agents"""
        registry = AgentRegistry()
        agents = registry.list_agents()
        
        self.assertGreater(len(agents), 0)
        agent_ids = [a['agent_id'] for a in agents]
        self.assertIn('agent-data-processing', agent_ids)


class TestMLOverlay(unittest.TestCase):
    """Tests for ML overlay"""
    
    def test_ml_not_eligible_for_immature(self):
        """Test that ML is not eligible for immature rows"""
        row = {
            'maturity_state': 'IMMATURE'
        }
        
        eligible = is_ml_eligible(row)
        self.assertFalse(eligible)
    
    def test_ml_eligible_for_mature(self):
        """Test that ML is eligible for mature rows"""
        row = {
            'maturity_state': 'MATURE'
        }
        
        eligible = is_ml_eligible(row)
        self.assertTrue(eligible)
    
    def test_ml_results_structure(self):
        """Test ML results have expected structure"""
        row = {
            'cycle': 1,
            'layer': 'L1',
            'variant': 'A',
            'input_type': 'test',
            'source_protocol': 'REST',
            'maturity_state': 'MATURE',
            'security': 'PASS',
            'schema_validation': 'PASS',
            'status': 'READY',
            'artifacts': ['artifact-1']
        }
        
        results = run_ml_models(row)
        
        self.assertTrue(results.get('ml_applied'))
        self.assertIn('ml_score', results)
        self.assertIn('ml_suggested_agent', results)
        self.assertIn('ml_anomaly_prob', results)


class TestEnforcement(unittest.TestCase):
    """Tests for enforcement layer"""
    
    def test_enforcement_not_applied_for_immature(self):
        """Test enforcement not applied for immature rows"""
        row = {
            'maturity_state': 'IMMATURE'
        }
        
        result = apply_enforcement(row)
        
        self.assertFalse(result.get('enforcement_applied'))
    
    def test_enforcement_applied_for_mature(self):
        """Test enforcement applied for mature rows"""
        row = {
            'cycle': 1,
            'layer': 'L1',
            'variant': 'A',
            'input_type': 'test',
            'source_protocol': 'REST',
            'maturity_state': 'MATURE',
            'security': 'PASS',
            'schema_validation': 'PASS',
            'status': 'READY'
        }
        
        result = apply_enforcement(row)
        
        self.assertTrue(result.get('enforcement_applied'))
        self.assertIn('compliance_status', result)


class TestIntegration(unittest.TestCase):
    """Integration tests for full pipeline"""
    
    def test_full_pipeline_flow(self):
        """Test complete pipeline execution"""
        from run_pipeline import run_pipeline, PipelineConfig
        
        input_payload = {
            "cycle": 1,
            "layer": "L1",
            "variant": "A",
            "input_type": "integration_test",
            "data": {"value": 100}
        }
        
        config = PipelineConfig(verbose=False)
        result = run_pipeline(input_payload, "REST", config)
        
        self.assertIsNotNone(result)
        self.assertIn('success', result)
        self.assertIn('final_status', result)
        self.assertIn('steps_completed', result)
        self.assertIn('intake', result['steps_completed'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)

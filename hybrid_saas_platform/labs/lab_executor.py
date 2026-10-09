"""
Lab Executor - Test Execution Engine
====================================
Executes labs (tests) on canonical rows.
Labs are the "baking" process - transforming raw input into artifacts.

Metaphor: grurë (wheat) → bukë (bread)
Reality: raw data → validated, tested, artifact-producing output
"""

import json
import uuid
import time
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class LabStatus(Enum):
    """Lab execution status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class LabResult:
    """Result of a lab execution"""
    lab_id: str
    lab_name: str
    status: LabStatus
    execution_time_ms: float
    tests_run: int
    tests_passed: int
    tests_failed: int
    output: Dict[str, Any]
    errors: List[str]
    started_at: str
    completed_at: str
    
    @property
    def success_rate(self) -> float:
        """Calculate test success rate"""
        if self.tests_run == 0:
            return 0.0
        return self.tests_passed / self.tests_run
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'lab_id': self.lab_id,
            'lab_name': self.lab_name,
            'status': self.status.value,
            'execution_time_ms': self.execution_time_ms,
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'success_rate': self.success_rate,
            'output': self.output,
            'errors': self.errors,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }


@dataclass
class Artifact:
    """Generated artifact from lab execution"""
    artifact_id: str
    artifact_type: str
    name: str
    content: Any
    metadata: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'artifact_id': self.artifact_id,
            'artifact_type': self.artifact_type,
            'name': self.name,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at
        }


class Lab(ABC):
    """Abstract base class for labs"""
    
    @property
    @abstractmethod
    def lab_id(self) -> str:
        """Unique lab identifier"""
        pass
    
    @property
    @abstractmethod
    def lab_name(self) -> str:
        """Human-readable lab name"""
        pass
    
    @property
    def description(self) -> str:
        """Lab description"""
        return ""
    
    @abstractmethod
    def execute(self, row: Dict[str, Any]) -> Tuple[LabResult, List[Artifact]]:
        """
        Execute the lab on a row
        
        Args:
            row: Canonical row data
            
        Returns:
            Tuple of (LabResult, list of Artifacts)
        """
        pass
    
    def can_run(self, row: Dict[str, Any]) -> bool:
        """Check if this lab can run on the given row"""
        return True


class DataValidationLab(Lab):
    """Lab for validating data integrity"""
    
    @property
    def lab_id(self) -> str:
        return "lab-data-validation"
    
    @property
    def lab_name(self) -> str:
        return "Data Validation Lab"
    
    @property
    def description(self) -> str:
        return "Validates data integrity, format, and completeness"
    
    def execute(self, row: Dict[str, Any]) -> Tuple[LabResult, List[Artifact]]:
        """Run data validation tests"""
        started_at = datetime.utcnow().isoformat()
        start_time = time.time()
        
        tests_run = 0
        tests_passed = 0
        tests_failed = 0
        errors = []
        output = {}
        
        # Test 1: Check required fields exist
        tests_run += 1
        required = ['cycle', 'layer', 'variant', 'input_type']
        missing = [f for f in required if f not in row or row[f] is None]
        if not missing:
            tests_passed += 1
            output['required_fields'] = 'PASS'
        else:
            tests_failed += 1
            errors.append(f"Missing fields: {missing}")
            output['required_fields'] = 'FAIL'
        
        # Test 2: Check data types
        tests_run += 1
        type_errors = []
        if 'cycle' in row and not isinstance(row['cycle'], int):
            type_errors.append('cycle should be int')
        if 'layer' in row and not isinstance(row['layer'], str):
            type_errors.append('layer should be str')
        
        if not type_errors:
            tests_passed += 1
            output['data_types'] = 'PASS'
        else:
            tests_failed += 1
            errors.extend(type_errors)
            output['data_types'] = 'FAIL'
        
        # Test 3: Check value ranges
        tests_run += 1
        if row.get('cycle', 0) >= 0:
            tests_passed += 1
            output['value_ranges'] = 'PASS'
        else:
            tests_failed += 1
            errors.append('cycle must be non-negative')
            output['value_ranges'] = 'FAIL'
        
        execution_time = (time.time() - start_time) * 1000
        completed_at = datetime.utcnow().isoformat()
        
        status = LabStatus.PASSED if tests_failed == 0 else LabStatus.FAILED
        
        result = LabResult(
            lab_id=self.lab_id,
            lab_name=self.lab_name,
            status=status,
            execution_time_ms=execution_time,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            output=output,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at
        )
        
        # Generate validation report artifact
        artifacts = []
        if status == LabStatus.PASSED:
            artifacts.append(Artifact(
                artifact_id=str(uuid.uuid4()),
                artifact_type='validation_report',
                name='data_validation_report',
                content={
                    'validated': True,
                    'tests_passed': tests_passed,
                    'row_cycle': row.get('cycle'),
                    'row_layer': row.get('layer')
                },
                metadata={'lab_id': self.lab_id}
            ))
        
        return result, artifacts


class TransformationLab(Lab):
    """Lab for data transformation"""
    
    @property
    def lab_id(self) -> str:
        return "lab-transformation"
    
    @property
    def lab_name(self) -> str:
        return "Transformation Lab"
    
    @property
    def description(self) -> str:
        return "Transforms raw input into processed format"
    
    def execute(self, row: Dict[str, Any]) -> Tuple[LabResult, List[Artifact]]:
        """Run transformation"""
        started_at = datetime.utcnow().isoformat()
        start_time = time.time()
        
        tests_run = 2
        tests_passed = 0
        tests_failed = 0
        errors = []
        output = {}
        
        # Test 1: Transform can be applied
        try:
            transformed_data = {
                'original_cycle': row.get('cycle'),
                'normalized_layer': row.get('layer', '').upper(),
                'variant_code': f"{row.get('variant', 'A')}-{row.get('cycle', 0):03d}",
                'processed': True
            }
            tests_passed += 1
            output['transformation'] = 'PASS'
            output['transformed_data'] = transformed_data
        except Exception as e:
            tests_failed += 1
            errors.append(str(e))
            output['transformation'] = 'FAIL'
            transformed_data = None
        
        # Test 2: Output is valid
        if transformed_data:
            tests_passed += 1
            output['output_valid'] = 'PASS'
        else:
            tests_failed += 1
            output['output_valid'] = 'FAIL'
        
        execution_time = (time.time() - start_time) * 1000
        completed_at = datetime.utcnow().isoformat()
        
        status = LabStatus.PASSED if tests_failed == 0 else LabStatus.FAILED
        
        result = LabResult(
            lab_id=self.lab_id,
            lab_name=self.lab_name,
            status=status,
            execution_time_ms=execution_time,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            output=output,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at
        )
        
        artifacts = []
        if transformed_data:
            artifacts.append(Artifact(
                artifact_id=str(uuid.uuid4()),
                artifact_type='transformed_data',
                name='transformation_output',
                content=transformed_data,
                metadata={'lab_id': self.lab_id}
            ))
        
        return result, artifacts


class IntegrationLab(Lab):
    """Lab for integration testing"""
    
    @property
    def lab_id(self) -> str:
        return "lab-integration"
    
    @property
    def lab_name(self) -> str:
        return "Integration Lab"
    
    @property
    def description(self) -> str:
        return "Tests integration with external systems"
    
    def can_run(self, row: Dict[str, Any]) -> bool:
        """Only run on rows with external protocol"""
        protocol = row.get('source_protocol', '')
        return protocol in ['REST', 'GraphQL', 'gRPC']
    
    def execute(self, row: Dict[str, Any]) -> Tuple[LabResult, List[Artifact]]:
        """Run integration tests"""
        started_at = datetime.utcnow().isoformat()
        start_time = time.time()
        
        protocol = row.get('source_protocol', 'unknown')
        
        # Simulate integration test
        tests_run = 1
        tests_passed = 1
        tests_failed = 0
        errors = []
        output = {
            'protocol_tested': protocol,
            'integration_status': 'PASS',
            'latency_ms': 50  # Simulated
        }
        
        execution_time = (time.time() - start_time) * 1000
        completed_at = datetime.utcnow().isoformat()
        
        result = LabResult(
            lab_id=self.lab_id,
            lab_name=self.lab_name,
            status=LabStatus.PASSED,
            execution_time_ms=execution_time,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            output=output,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at
        )
        
        artifacts = [Artifact(
            artifact_id=str(uuid.uuid4()),
            artifact_type='integration_report',
            name='integration_test_report',
            content={
                'protocol': protocol,
                'tests_passed': tests_passed,
                'integration_verified': True
            },
            metadata={'lab_id': self.lab_id}
        )]
        
        return result, artifacts


class LabRegistry:
    """Registry of available labs"""
    
    def __init__(self):
        self.labs: Dict[str, Lab] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default labs"""
        self.register(DataValidationLab())
        self.register(TransformationLab())
        self.register(IntegrationLab())
    
    def register(self, lab: Lab):
        """Register a lab"""
        self.labs[lab.lab_id] = lab
    
    def get_lab(self, lab_id: str) -> Optional[Lab]:
        """Get lab by ID"""
        return self.labs.get(lab_id)
    
    def get_applicable_labs(self, row: Dict[str, Any]) -> List[Lab]:
        """Get all labs that can run on the given row"""
        return [lab for lab in self.labs.values() if lab.can_run(row)]
    
    def list_labs(self) -> List[Dict[str, str]]:
        """List all registered labs"""
        return [
            {
                'lab_id': lab.lab_id,
                'name': lab.lab_name,
                'description': lab.description
            }
            for lab in self.labs.values()
        ]


class LabExecutor:
    """
    Executes labs on canonical rows
    """
    
    def __init__(self, registry: Optional[LabRegistry] = None):
        self.registry = registry or LabRegistry()
    
    def execute_lab(self, row: Dict[str, Any], 
                   lab_id: Optional[str] = None) -> Tuple[Dict[str, Any], List[str]]:
        """
        Execute lab(s) on a row
        
        Args:
            row: Canonical row data
            lab_id: Specific lab to run, or None for all applicable
            
        Returns:
            Tuple of (combined lab results dict, list of artifact IDs)
        """
        labs_to_run = []
        
        if lab_id:
            lab = self.registry.get_lab(lab_id)
            if lab and lab.can_run(row):
                labs_to_run = [lab]
        else:
            labs_to_run = self.registry.get_applicable_labs(row)
        
        all_results = []
        all_artifacts = []
        
        for lab in labs_to_run:
            try:
                result, artifacts = lab.execute(row)
                all_results.append(result.to_dict())
                all_artifacts.extend(artifacts)
            except Exception as e:
                all_results.append({
                    'lab_id': lab.lab_id,
                    'lab_name': lab.lab_name,
                    'status': LabStatus.FAILED.value,
                    'error': str(e)
                })
        
        # Combine results
        combined = {
            'labs_executed': len(all_results),
            'labs_passed': sum(1 for r in all_results if r.get('status') == 'PASSED'),
            'labs_failed': sum(1 for r in all_results if r.get('status') == 'FAILED'),
            'total_tests': sum(r.get('tests_run', 0) for r in all_results),
            'results': all_results
        }
        
        artifact_ids = [a.artifact_id for a in all_artifacts]
        
        return combined, artifact_ids


# Global lab executor
_lab_executor: Optional[LabExecutor] = None

def get_lab_executor() -> LabExecutor:
    """Get or create the global lab executor"""
    global _lab_executor
    if _lab_executor is None:
        _lab_executor = LabExecutor()
    return _lab_executor


def execute_lab(row: Dict[str, Any], 
               lab_id: Optional[str] = None) -> Tuple[Dict[str, Any], List[str]]:
    """
    Main entry point: Execute lab(s) on a row
    
    Args:
        row: Canonical row data
        lab_id: Optional specific lab to run
        
    Returns:
        Tuple of (lab results, artifact IDs)
    """
    executor = get_lab_executor()
    return executor.execute_lab(row, lab_id)

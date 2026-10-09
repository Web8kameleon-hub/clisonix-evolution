"""
Enforcement Manager - Protocol Sovereignty Layer
=================================================
Enforces protocol standards ONLY after maturity and stability.

Key Principle: "Listen First, Enforce After Maturity"

Functions:
1. Generate canonical API specifications
2. Enforce schema for future inputs
3. Track compliance for partners
4. Auto-reject or auto-map non-compliant inputs
"""

import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance check result"""
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


class EnforcementAction(Enum):
    """Actions taken on non-compliant inputs"""
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    AUTO_MAP = "AUTO_MAP"
    WARN = "WARN"


class EnforcementMode(Enum):
    """Enforcement strictness modes"""
    PASSIVE = "PASSIVE"     # Only observe and log
    ADVISORY = "ADVISORY"   # Warn but accept
    STRICT = "STRICT"       # Reject non-compliant


@dataclass
class SchemaDefinition:
    """Canonical schema definition"""
    schema_id: str
    version: str
    name: str
    required_fields: List[str]
    field_types: Dict[str, str]
    valid_values: Dict[str, List[str]]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'schema_id': self.schema_id,
            'version': self.version,
            'name': self.name,
            'required_fields': self.required_fields,
            'field_types': self.field_types,
            'valid_values': self.valid_values,
            'created_at': self.created_at
        }
    
    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI 3.0 schema format"""
        properties = {}
        for field_name, field_type in self.field_types.items():
            prop = {'type': field_type}
            if field_name in self.valid_values:
                prop['enum'] = self.valid_values[field_name]
            properties[field_name] = prop
        
        return {
            'type': 'object',
            'properties': properties,
            'required': self.required_fields
        }


@dataclass
class ComplianceResult:
    """Result of compliance check"""
    status: ComplianceStatus
    violations: List[str]
    warnings: List[str]
    action_taken: EnforcementAction
    auto_mapped_fields: Dict[str, Any]
    checked_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'violations': self.violations,
            'warnings': self.warnings,
            'action_taken': self.action_taken.value,
            'auto_mapped_fields': self.auto_mapped_fields,
            'checked_at': self.checked_at
        }


@dataclass
class APISpecification:
    """Canonical API specification"""
    spec_id: str
    name: str
    version: str
    base_path: str
    endpoints: List[Dict[str, Any]]
    schemas: Dict[str, SchemaDefinition]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_openapi(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification"""
        paths = {}
        for endpoint in self.endpoints:
            path = endpoint.get('path', '/')
            method = endpoint.get('method', 'get').lower()
            if path not in paths:
                paths[path] = {}
            paths[path][method] = {
                'summary': endpoint.get('summary', ''),
                'description': endpoint.get('description', ''),
                'operationId': endpoint.get('operation_id', ''),
                'responses': {
                    '200': {
                        'description': 'Successful response'
                    }
                }
            }
        
        components_schemas = {}
        for name, schema in self.schemas.items():
            components_schemas[name] = schema.to_openapi()
        
        return {
            'openapi': '3.0.0',
            'info': {
                'title': self.name,
                'version': self.version
            },
            'servers': [{'url': self.base_path}],
            'paths': paths,
            'components': {
                'schemas': components_schemas
            }
        }


class SchemaEnforcer:
    """
    Enforces schema compliance on incoming data
    """
    
    def __init__(self, mode: EnforcementMode = EnforcementMode.ADVISORY):
        self.mode = mode
        self.schemas: Dict[str, SchemaDefinition] = {}
        self._create_canonical_schema()
    
    def _create_canonical_schema(self):
        """Create the default canonical row schema"""
        canonical = SchemaDefinition(
            schema_id='canonical-row-v1',
            version='1.0.0',
            name='Canonical Row Schema',
            required_fields=['cycle', 'layer', 'variant', 'input_type', 'source_protocol'],
            field_types={
                'cycle': 'integer',
                'layer': 'string',
                'variant': 'string',
                'input_type': 'string',
                'source_protocol': 'string',
                'status': 'string',
                'security': 'string',
                'schema_validation': 'string',
                'maturity_state': 'string'
            },
            valid_values={
                'status': ['RAW', 'NORMALIZED', 'TEST', 'READY', 'FAIL', 'ARCHIVED'],
                'security': ['PASS', 'FAIL', 'PENDING'],
                'schema_validation': ['PASS', 'FAIL', 'PENDING'],
                'maturity_state': ['IMMATURE', 'MATURING', 'MATURE'],
                'source_protocol': ['REST', 'GraphQL', 'gRPC', 'Webhook', 'File']
            }
        )
        self.schemas['canonical-row'] = canonical
    
    def register_schema(self, schema: SchemaDefinition):
        """Register a schema"""
        self.schemas[schema.schema_id] = schema
    
    def check_compliance(self, data: Dict[str, Any], 
                        schema_id: str = 'canonical-row') -> ComplianceResult:
        """
        Check if data complies with schema
        
        Args:
            data: Input data to check
            schema_id: Schema to validate against
            
        Returns:
            ComplianceResult with details
        """
        schema = self.schemas.get(schema_id)
        if not schema:
            return ComplianceResult(
                status=ComplianceStatus.PENDING,
                violations=[f"Schema not found: {schema_id}"],
                warnings=[],
                action_taken=EnforcementAction.WARN,
                auto_mapped_fields={}
            )
        
        violations = []
        warnings = []
        auto_mapped = {}
        
        # Check required fields
        for field in schema.required_fields:
            if field not in data or data[field] is None:
                violations.append(f"Missing required field: {field}")
        
        # Check field types
        for field_name, expected_type in schema.field_types.items():
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if expected_type == 'integer' and not isinstance(value, int):
                    if isinstance(value, str) and value.isdigit():
                        auto_mapped[field_name] = int(value)
                        warnings.append(f"Auto-converted {field_name} to integer")
                    else:
                        violations.append(f"Field {field_name} should be integer")
                elif expected_type == 'string' and not isinstance(value, str):
                    auto_mapped[field_name] = str(value)
                    warnings.append(f"Auto-converted {field_name} to string")
        
        # Check valid values
        for field_name, valid_values in schema.valid_values.items():
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if value not in valid_values:
                    # Try case-insensitive match
                    upper_value = str(value).upper()
                    if upper_value in valid_values:
                        auto_mapped[field_name] = upper_value
                        warnings.append(f"Auto-mapped {field_name} to uppercase: {upper_value}")
                    else:
                        violations.append(f"Invalid value for {field_name}: {value}. Valid: {valid_values}")
        
        # Determine status
        if not violations:
            status = ComplianceStatus.COMPLIANT
        elif len(violations) <= 2 and auto_mapped:
            status = ComplianceStatus.PARTIAL
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        # Determine action based on mode
        if self.mode == EnforcementMode.PASSIVE:
            action = EnforcementAction.ACCEPT
        elif self.mode == EnforcementMode.ADVISORY:
            action = EnforcementAction.AUTO_MAP if auto_mapped else EnforcementAction.WARN
        else:  # STRICT
            action = EnforcementAction.REJECT if violations else EnforcementAction.ACCEPT
        
        return ComplianceResult(
            status=status,
            violations=violations,
            warnings=warnings,
            action_taken=action,
            auto_mapped_fields=auto_mapped
        )


class APISpecGenerator:
    """
    Generates canonical API specifications from mature data
    """
    
    def __init__(self):
        self.generated_specs: Dict[str, APISpecification] = {}
    
    def generate_from_rows(self, rows: List[Dict[str, Any]], 
                          name: str = "Canonical API",
                          version: str = "1.0.0") -> APISpecification:
        """
        Generate API spec from collection of rows
        
        Analyzes mature rows to create canonical specification
        """
        # Analyze protocols used
        protocols = set()
        input_types = set()
        layers = set()
        
        for row in rows:
            if row.get('maturity_state') == 'MATURE':
                protocols.add(row.get('source_protocol', ''))
                input_types.add(row.get('input_type', ''))
                layers.add(row.get('layer', ''))
        
        # Generate endpoints based on patterns
        endpoints = []
        
        for input_type in input_types:
            if not input_type:
                continue
            
            # Create CRUD endpoints for each input type
            base_path = f"/{input_type.lower().replace(' ', '-')}"
            
            endpoints.extend([
                {
                    'path': base_path,
                    'method': 'GET',
                    'summary': f'List {input_type}',
                    'operation_id': f'list_{input_type.lower()}'
                },
                {
                    'path': base_path,
                    'method': 'POST',
                    'summary': f'Create {input_type}',
                    'operation_id': f'create_{input_type.lower()}'
                },
                {
                    'path': f'{base_path}/{{id}}',
                    'method': 'GET',
                    'summary': f'Get {input_type}',
                    'operation_id': f'get_{input_type.lower()}'
                },
                {
                    'path': f'{base_path}/{{id}}',
                    'method': 'PUT',
                    'summary': f'Update {input_type}',
                    'operation_id': f'update_{input_type.lower()}'
                }
            ])
        
        # Create schemas
        canonical_schema = SchemaDefinition(
            schema_id='canonical-row',
            version='1.0.0',
            name='CanonicalRow',
            required_fields=['cycle', 'layer', 'variant', 'input_type', 'source_protocol'],
            field_types={
                'cycle': 'integer',
                'layer': 'string',
                'variant': 'string',
                'input_type': 'string',
                'source_protocol': 'string',
                'status': 'string'
            },
            valid_values={
                'status': ['RAW', 'NORMALIZED', 'TEST', 'READY', 'FAIL', 'ARCHIVED']
            }
        )
        
        spec = APISpecification(
            spec_id=hashlib.md5(f"{name}-{version}".encode()).hexdigest()[:8],
            name=name,
            version=version,
            base_path='/api/v1',
            endpoints=endpoints,
            schemas={'CanonicalRow': canonical_schema}
        )
        
        self.generated_specs[spec.spec_id] = spec
        return spec


class ComplianceTracker:
    """
    Tracks compliance status for partners/sources
    """
    
    def __init__(self):
        self.compliance_history: Dict[str, List[ComplianceResult]] = {}
    
    def record(self, source: str, result: ComplianceResult):
        """Record a compliance check result"""
        if source not in self.compliance_history:
            self.compliance_history[source] = []
        self.compliance_history[source].append(result)
    
    def get_compliance_rate(self, source: str) -> float:
        """Get compliance rate for a source"""
        history = self.compliance_history.get(source, [])
        if not history:
            return 0.0
        
        compliant = sum(
            1 for r in history 
            if r.status in [ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIAL]
        )
        return compliant / len(history)
    
    def get_summary(self, source: str) -> Dict[str, Any]:
        """Get compliance summary for a source"""
        history = self.compliance_history.get(source, [])
        return {
            'source': source,
            'total_checks': len(history),
            'compliance_rate': self.get_compliance_rate(source),
            'compliant': sum(1 for r in history if r.status == ComplianceStatus.COMPLIANT),
            'partial': sum(1 for r in history if r.status == ComplianceStatus.PARTIAL),
            'non_compliant': sum(1 for r in history if r.status == ComplianceStatus.NON_COMPLIANT)
        }


class EnforcementManager:
    """
    Main enforcement orchestrator
    
    Key Rule: Enforcement only activates after MATURE status and stability
    """
    
    def __init__(self, mode: EnforcementMode = EnforcementMode.ADVISORY):
        self.mode = mode
        self.schema_enforcer = SchemaEnforcer(mode)
        self.spec_generator = APISpecGenerator()
        self.compliance_tracker = ComplianceTracker()
    
    def is_enforcement_eligible(self, row: Dict[str, Any]) -> bool:
        """
        Check if enforcement should be applied
        
        Rule: Only MATURE rows with stable history
        """
        maturity = row.get('maturity_state', 'IMMATURE')
        return maturity == 'MATURE'
    
    def apply_enforcement(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply enforcement layer to a row
        
        Args:
            row: Canonical row data (should be MATURE)
            
        Returns:
            Dict with enforcement results
        """
        if not self.is_enforcement_eligible(row):
            return {
                'enforcement_applied': False,
                'reason': 'Row not eligible (not MATURE)'
            }
        
        # Check compliance
        source = row.get('source_protocol', 'unknown')
        compliance = self.schema_enforcer.check_compliance(row)
        
        # Track compliance
        self.compliance_tracker.record(source, compliance)
        
        # Generate spec if needed
        # (In real system, this would be periodic, not per-row)
        
        return {
            'enforcement_applied': True,
            'enforcement_mode': self.mode.value,
            'compliance_status': compliance.status.value,
            'compliance_violations': compliance.violations,
            'compliance_warnings': compliance.warnings,
            'action_taken': compliance.action_taken.value,
            'auto_mapped_fields': compliance.auto_mapped_fields,
            'source_compliance_rate': self.compliance_tracker.get_compliance_rate(source)
        }
    
    def generate_api_spec(self, rows: List[Dict[str, Any]], 
                         name: str = "Canonical API") -> Dict[str, Any]:
        """
        Generate canonical API specification from mature rows
        
        Args:
            rows: List of canonical rows
            name: API specification name
            
        Returns:
            OpenAPI 3.0 specification
        """
        mature_rows = [r for r in rows if r.get('maturity_state') == 'MATURE']
        
        if not mature_rows:
            return {'error': 'No MATURE rows available for spec generation'}
        
        spec = self.spec_generator.generate_from_rows(mature_rows, name)
        return spec.to_openapi()


# Global enforcement manager
_enforcement_manager: Optional[EnforcementManager] = None

def get_enforcement_manager(mode: EnforcementMode = EnforcementMode.ADVISORY) -> EnforcementManager:
    """Get or create the global enforcement manager"""
    global _enforcement_manager
    if _enforcement_manager is None:
        _enforcement_manager = EnforcementManager(mode)
    return _enforcement_manager


def apply_enforcement(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point: Apply enforcement to a row
    
    Args:
        row: Canonical row data
        
    Returns:
        Dict with enforcement results
    """
    manager = get_enforcement_manager()
    return manager.apply_enforcement(row)


def generate_canonical_api_spec(rows: List[Dict[str, Any]], 
                               name: str = "Canonical API") -> Dict[str, Any]:
    """
    Generate canonical API specification
    
    Args:
        rows: List of canonical rows
        name: API name
        
    Returns:
        OpenAPI 3.0 specification
    """
    manager = get_enforcement_manager()
    return manager.generate_api_spec(rows, name)

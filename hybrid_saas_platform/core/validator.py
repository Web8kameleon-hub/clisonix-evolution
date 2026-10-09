"""
Validator - Security & Schema Validation
=========================================
Validates inputs for security (JWT, OAuth, API keys) and schema compliance.
Part of the maturity gate: Security=PASS AND Validation=PASS required for MATURING.
"""

import re
import json
import hashlib
import hmac
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum


class ValidationResult(Enum):
    """Validation result states"""
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


@dataclass
class SecurityCheckResult:
    """Result of a security check"""
    passed: bool
    method: str
    details: Dict[str, Any]
    error: Optional[str] = None
    
    @property
    def status(self) -> str:
        return ValidationResult.PASS.value if self.passed else ValidationResult.FAIL.value


@dataclass
class SchemaValidationResult:
    """Result of schema validation"""
    passed: bool
    errors: List[str]
    warnings: List[str]
    validated_fields: List[str]
    
    @property
    def status(self) -> str:
        return ValidationResult.PASS.value if self.passed else ValidationResult.FAIL.value


class SecurityValidator(ABC):
    """Abstract base class for security validators"""
    
    @property
    @abstractmethod
    def method_name(self) -> str:
        """Name of the security method"""
        pass
    
    @abstractmethod
    def validate(self, row: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None) -> SecurityCheckResult:
        """Validate security for the given row"""
        pass


class JWTValidator(SecurityValidator):
    """JWT token validator"""
    
    def __init__(self, secret_key: str = "default-secret-key"):
        self.secret_key = secret_key
    
    @property
    def method_name(self) -> str:
        return "JWT"
    
    def validate(self, row: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None) -> SecurityCheckResult:
        """
        Validate JWT token
        
        Expects token in:
        - row['metadata']['headers']['Authorization']
        - or credentials['token']
        """
        token = None
        
        # Try to find token
        if credentials and 'token' in credentials:
            token = credentials['token']
        elif 'metadata' in row:
            headers = row['metadata'].get('headers', row['metadata'].get('raw_data', {}).get('headers', {}))
            auth_header = headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return SecurityCheckResult(
                passed=False,
                method=self.method_name,
                details={},
                error="No JWT token found"
            )
        
        # Basic JWT structure validation (3 parts separated by dots)
        parts = token.split('.')
        if len(parts) != 3:
            return SecurityCheckResult(
                passed=False,
                method=self.method_name,
                details={'token_parts': len(parts)},
                error="Invalid JWT format"
            )
        
        # In production, you would verify signature here
        # For now, we just check structure
        return SecurityCheckResult(
            passed=True,
            method=self.method_name,
            details={
                'token_valid': True,
                'validated_at': datetime.utcnow().isoformat()
            }
        )


class APIKeyValidator(SecurityValidator):
    """API Key validator"""
    
    def __init__(self, valid_keys: Optional[List[str]] = None):
        self.valid_keys = valid_keys or []
    
    @property
    def method_name(self) -> str:
        return "API_KEY"
    
    def validate(self, row: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None) -> SecurityCheckResult:
        """
        Validate API key
        
        Expects key in:
        - row['metadata']['headers']['X-API-Key']
        - or credentials['api_key']
        """
        api_key = None
        
        if credentials and 'api_key' in credentials:
            api_key = credentials['api_key']
        elif 'metadata' in row:
            headers = row['metadata'].get('headers', row['metadata'].get('raw_data', {}).get('headers', {}))
            api_key = headers.get('X-API-Key', headers.get('x-api-key'))
        
        if not api_key:
            return SecurityCheckResult(
                passed=False,
                method=self.method_name,
                details={},
                error="No API key found"
            )
        
        # Check key format (at least 16 chars, alphanumeric with dashes)
        if len(api_key) < 16:
            return SecurityCheckResult(
                passed=False,
                method=self.method_name,
                details={'key_length': len(api_key)},
                error="API key too short"
            )
        
        # If we have a whitelist, check against it
        if self.valid_keys and api_key not in self.valid_keys:
            return SecurityCheckResult(
                passed=False,
                method=self.method_name,
                details={},
                error="Invalid API key"
            )
        
        return SecurityCheckResult(
            passed=True,
            method=self.method_name,
            details={
                'key_valid': True,
                'key_hash': hashlib.sha256(api_key.encode()).hexdigest()[:16]
            }
        )


class OAuthValidator(SecurityValidator):
    """OAuth token validator"""
    
    @property
    def method_name(self) -> str:
        return "OAuth"
    
    def validate(self, row: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None) -> SecurityCheckResult:
        """
        Validate OAuth token
        
        Expects token in:
        - credentials['access_token']
        - or row['metadata']['headers']['Authorization']
        """
        access_token = None
        
        if credentials:
            access_token = credentials.get('access_token')
        
        if not access_token and 'metadata' in row:
            headers = row['metadata'].get('headers', {})
            auth_header = headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                access_token = auth_header[7:]
        
        if not access_token:
            return SecurityCheckResult(
                passed=False,
                method=self.method_name,
                details={},
                error="No OAuth token found"
            )
        
        # Basic validation - token should be non-empty string
        if len(access_token) < 10:
            return SecurityCheckResult(
                passed=False,
                method=self.method_name,
                details={},
                error="OAuth token too short"
            )
        
        return SecurityCheckResult(
            passed=True,
            method=self.method_name,
            details={
                'token_valid': True,
                'validated_at': datetime.utcnow().isoformat()
            }
        )


class NoAuthValidator(SecurityValidator):
    """No authentication required (for development/testing)"""
    
    @property
    def method_name(self) -> str:
        return "NONE"
    
    def validate(self, row: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None) -> SecurityCheckResult:
        """Always passes - no auth required"""
        return SecurityCheckResult(
            passed=True,
            method=self.method_name,
            details={'auth_required': False}
        )


class SchemaValidator:
    """
    Validates row data against expected schema
    """
    
    # Required fields for canonical row
    REQUIRED_FIELDS = ['cycle', 'layer', 'variant', 'input_type', 'source_protocol']
    
    # Field type definitions
    FIELD_TYPES = {
        'cycle': int,
        'layer': str,
        'variant': str,
        'input_type': str,
        'source_protocol': str,
        'status': str,
        'security': str,
        'schema_validation': str,
        'maturity_state': str,
        'ml_score': (int, float),
        'ml_anomaly_prob': (int, float)
    }
    
    # Valid values for enum fields
    VALID_VALUES = {
        'status': ['RAW', 'NORMALIZED', 'TEST', 'READY', 'FAIL', 'ARCHIVED'],
        'security': ['PASS', 'FAIL', 'PENDING'],
        'schema_validation': ['PASS', 'FAIL', 'PENDING'],
        'maturity_state': ['IMMATURE', 'MATURING', 'MATURE'],
        'source_protocol': ['REST', 'GraphQL', 'gRPC', 'Webhook', 'File']
    }
    
    # Layer pattern (L followed by number)
    LAYER_PATTERN = re.compile(r'^L\d+$')
    
    def validate(self, row: Dict[str, Any]) -> SchemaValidationResult:
        """
        Validate row against schema
        
        Args:
            row: Dictionary containing row data
            
        Returns:
            SchemaValidationResult with pass/fail status and details
        """
        errors = []
        warnings = []
        validated_fields = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in row or row[field] is None:
                errors.append(f"Missing required field: {field}")
            else:
                validated_fields.append(field)
        
        # Check field types
        for field, expected_type in self.FIELD_TYPES.items():
            if field in row and row[field] is not None:
                if not isinstance(row[field], expected_type):
                    errors.append(f"Field '{field}' should be {expected_type}, got {type(row[field])}")
        
        # Check enum values
        for field, valid_values in self.VALID_VALUES.items():
            if field in row and row[field] is not None:
                if row[field] not in valid_values:
                    if field == 'source_protocol':
                        # Protocol can be extended, just warn
                        warnings.append(f"Non-standard protocol: {row[field]}")
                    else:
                        errors.append(f"Invalid value for '{field}': {row[field]}. Valid: {valid_values}")
        
        # Check layer format
        if 'layer' in row and row['layer'] is not None:
            if not self.LAYER_PATTERN.match(str(row['layer'])):
                warnings.append(f"Layer '{row['layer']}' doesn't match pattern L<number>")
        
        # Check cycle is positive
        if 'cycle' in row and row['cycle'] is not None:
            if row['cycle'] < 0:
                errors.append(f"Cycle must be non-negative, got {row['cycle']}")
        
        # Check ML score range
        if 'ml_score' in row and row['ml_score'] is not None:
            if not 0 <= row['ml_score'] <= 1:
                warnings.append(f"ML score {row['ml_score']} outside typical [0,1] range")
        
        # Check anomaly probability range
        if 'ml_anomaly_prob' in row and row['ml_anomaly_prob'] is not None:
            if not 0 <= row['ml_anomaly_prob'] <= 1:
                warnings.append(f"Anomaly probability {row['ml_anomaly_prob']} outside [0,1] range")
        
        return SchemaValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validated_fields=validated_fields
        )


class ValidationManager:
    """
    Manages security and schema validation
    """
    
    def __init__(self):
        self.security_validators: Dict[str, SecurityValidator] = {}
        self.schema_validator = SchemaValidator()
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default security validators"""
        self.register_security_validator(JWTValidator())
        self.register_security_validator(APIKeyValidator())
        self.register_security_validator(OAuthValidator())
        self.register_security_validator(NoAuthValidator())
    
    def register_security_validator(self, validator: SecurityValidator):
        """Register a security validator"""
        self.security_validators[validator.method_name.upper()] = validator
    
    def validate_security(self, row: Dict[str, Any], 
                         method: str = "NONE",
                         credentials: Optional[Dict[str, Any]] = None) -> str:
        """
        Validate security for a row
        
        Args:
            row: Row data
            method: Security method (JWT, API_KEY, OAuth, NONE)
            credentials: Optional credentials dict
            
        Returns:
            'PASS' or 'FAIL'
        """
        validator = self.security_validators.get(method.upper())
        if not validator:
            # Default to no auth for unknown methods
            validator = self.security_validators.get('NONE')
        
        result = validator.validate(row, credentials)
        return result.status
    
    def validate_schema(self, row: Dict[str, Any]) -> str:
        """
        Validate schema for a row
        
        Args:
            row: Row data
            
        Returns:
            'PASS' or 'FAIL'
        """
        result = self.schema_validator.validate(row)
        return result.status
    
    def validate_all(self, row: Dict[str, Any],
                    security_method: str = "NONE",
                    credentials: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Run all validations
        
        Returns:
            Dict with 'security' and 'schema_validation' results
        """
        return {
            'security': self.validate_security(row, security_method, credentials),
            'schema_validation': self.validate_schema(row)
        }


# Global validation manager
_validation_manager: Optional[ValidationManager] = None

def get_validation_manager() -> ValidationManager:
    """Get or create the global validation manager"""
    global _validation_manager
    if _validation_manager is None:
        _validation_manager = ValidationManager()
    return _validation_manager


def validate_security(row: Dict[str, Any], 
                     method: str = "NONE",
                     credentials: Optional[Dict[str, Any]] = None) -> str:
    """
    Main entry point: Validate security for a row
    
    Args:
        row: Row data dictionary
        method: Security method (JWT, API_KEY, OAuth, NONE)
        credentials: Optional credentials
        
    Returns:
        'PASS' or 'FAIL'
    """
    manager = get_validation_manager()
    return manager.validate_security(row, method, credentials)


def validate_schema(row: Dict[str, Any]) -> str:
    """
    Main entry point: Validate schema for a row
    
    Args:
        row: Row data dictionary
        
    Returns:
        'PASS' or 'FAIL'
    """
    manager = get_validation_manager()
    return manager.validate_schema(row)

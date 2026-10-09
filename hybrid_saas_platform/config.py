"""
Configuration for Hybrid Protocol Sovereign System
===================================================
Central configuration for all components.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class Environment(Enum):
    """Deployment environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class StorageConfig:
    """Storage configuration"""
    data_dir: str = "data"
    canonical_table_json: str = "data/canonical_table.json"
    canonical_table_excel: str = "data/canonical_table.xlsx"
    artifacts_dir: str = "data/artifacts"
    logs_dir: str = "logs"


@dataclass
class SecurityConfig:
    """Security configuration"""
    default_method: str = "NONE"  # NONE, JWT, API_KEY, OAuth
    jwt_secret: str = field(default_factory=lambda: os.environ.get("JWT_SECRET", "change-me-in-production"))
    api_key_header: str = "X-API-Key"
    valid_api_keys: List[str] = field(default_factory=list)
    oauth_issuer: str = ""
    oauth_audience: str = ""


@dataclass
class MLConfig:
    """ML Overlay configuration"""
    enabled: bool = True
    classifier_enabled: bool = True
    recommender_enabled: bool = True
    anomaly_detector_enabled: bool = True
    anomaly_threshold: float = 0.5  # Alert if anomaly_prob > this
    min_confidence_for_suggestion: float = 0.6


@dataclass
class EnforcementConfig:
    """Enforcement Layer configuration"""
    enabled: bool = True
    mode: str = "ADVISORY"  # PASSIVE, ADVISORY, STRICT
    auto_map_enabled: bool = True
    reject_on_violation: bool = False  # Only in STRICT mode
    compliance_tracking_enabled: bool = True


@dataclass
class LabsConfig:
    """Labs configuration"""
    enabled: bool = True
    default_labs: List[str] = field(default_factory=lambda: [
        "lab-data-validation",
        "lab-transformation"
    ])
    timeout_seconds: int = 30
    max_retries: int = 3


@dataclass
class AgentsConfig:
    """Agents configuration"""
    enabled: bool = True
    max_concurrent_tasks_per_agent: int = 10
    default_agent: str = "agent-data-processing"
    auto_select: bool = True


@dataclass
class PipelineConfig:
    """Pipeline execution configuration"""
    verbose_logging: bool = True
    run_labs: bool = True
    run_ml: bool = True
    run_enforcement: bool = True
    export_excel_on_complete: bool = False


@dataclass
class SystemConfig:
    """Main system configuration"""
    environment: Environment = Environment.DEVELOPMENT
    system_name: str = "Hybrid Protocol Sovereign System"
    version: str = "1.0.0"
    
    # Component configs
    storage: StorageConfig = field(default_factory=StorageConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    enforcement: EnforcementConfig = field(default_factory=EnforcementConfig)
    labs: LabsConfig = field(default_factory=LabsConfig)
    agents: AgentsConfig = field(default_factory=AgentsConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    
    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Create configuration from environment variables"""
        env = os.environ.get("HYBRID_ENV", "development")
        environment = Environment(env) if env in [e.value for e in Environment] else Environment.DEVELOPMENT
        
        return cls(
            environment=environment,
            security=SecurityConfig(
                default_method=os.environ.get("SECURITY_METHOD", "NONE"),
                jwt_secret=os.environ.get("JWT_SECRET", "change-me"),
                valid_api_keys=os.environ.get("API_KEYS", "").split(",") if os.environ.get("API_KEYS") else []
            ),
            ml=MLConfig(
                enabled=os.environ.get("ML_ENABLED", "true").lower() == "true",
                anomaly_threshold=float(os.environ.get("ANOMALY_THRESHOLD", "0.5"))
            ),
            enforcement=EnforcementConfig(
                enabled=os.environ.get("ENFORCEMENT_ENABLED", "true").lower() == "true",
                mode=os.environ.get("ENFORCEMENT_MODE", "ADVISORY")
            )
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'environment': self.environment.value,
            'system_name': self.system_name,
            'version': self.version,
            'storage': {
                'data_dir': self.storage.data_dir,
                'artifacts_dir': self.storage.artifacts_dir
            },
            'security': {
                'default_method': self.security.default_method,
                'api_key_header': self.security.api_key_header
            },
            'ml': {
                'enabled': self.ml.enabled,
                'anomaly_threshold': self.ml.anomaly_threshold
            },
            'enforcement': {
                'enabled': self.enforcement.enabled,
                'mode': self.enforcement.mode
            },
            'labs': {
                'enabled': self.labs.enabled,
                'timeout_seconds': self.labs.timeout_seconds
            },
            'agents': {
                'enabled': self.agents.enabled,
                'auto_select': self.agents.auto_select
            }
        }


# Global configuration instance
_config: Optional[SystemConfig] = None

def get_config() -> SystemConfig:
    """Get or create the global configuration"""
    global _config
    if _config is None:
        _config = SystemConfig.from_env()
    return _config


def set_config(config: SystemConfig):
    """Set the global configuration"""
    global _config
    _config = config

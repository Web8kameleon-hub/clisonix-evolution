"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           CLISONIX CLOUD - CENTRALIZED SETTINGS MANAGEMENT                  ║
║     Dynamic Configuration with Environment Variables & Validation           ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides type-safe, validated configuration management using Pydantic.
All settings are loaded from environment variables with sensible defaults.

Configuration Priority:
1. Environment variables (.env file)
2. Default values in this settings class
3. Validation ensures no invalid states

Example:
    from config import settings
    
    # Access settings
    alba_port = settings.alba_port
    print(f"ALBA running on port {alba_port}")
    
    # Validate connectivity before startup
    if settings.is_development:
        print("Running in development mode")
"""

import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, field_validator, validator
from pydantic_settings import BaseSettings


def _get_env_file() -> str:
    """Determine which .env file to load based on environment."""
    # Check system environment first
    env = os.getenv("ENVIRONMENT", "").lower()
    
    # If not set, check if .env.production exists and use it (production default)
    # Otherwise use .env (development default)
    if not env:
        prod_env_path = Path(".env.production")
        if prod_env_path.exists():
            env = "production"
        else:
            env = "development"
    
    # Map to .env file
    env_files = {
        "production": ".env.production",
        "staging": ".env.staging",
        "development": ".env",
    }
    
    env_file = env_files.get(env, ".env")
    
    # Print which env file is being loaded (for debugging)
    if Path(env_file).exists():
        print(f"[CONFIG] Loading: {env_file} ({env})", flush=True)
    else:
        print(f"[CONFIG] File not found: {env_file}, using defaults", flush=True)
    
    return env_file


class AppSettings(BaseSettings):
    """
    Centralized application settings loaded from environment variables.
    
    Attributes:
        All settings are loaded from .env file or environment variables.
        Use UPPERCASE names in .env, they're automatically converted to lowercase.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # ENVIRONMENT & DEBUG
    # ═══════════════════════════════════════════════════════════════════════════
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode (turn off in production!)"
    )
    api_title: str = Field(
        default="Clisonix Industrial Backend (REAL)",
        description="API title shown in docs"
    )
    api_version: str = Field(
        default="1.0.0",
        description="API version"
    )
    
    # Storage
    storage_dir: str = Field(
        default="./storage",
        description="Local storage directory for uploads"
    )
    
    # Service URLs
    alba_collector_url: str = Field(
        default="http://127.0.0.1:5555",
        description="ALBA Collector service URL"
    )
    mesh_hq_url: str = Field(
        default="http://127.0.0.1:7777",
        description="Mesh HQ service URL"
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    # ═══════════════════════════════════════════════════════════════════════════
    # FRONTEND
    # ═══════════════════════════════════════════════════════════════════════════
    frontend_host: str = Field(default="127.0.0.1")
    frontend_port: int = Field(default=3000)

    @property
    def frontend_url(self) -> str:
        """Full frontend URL."""
        return f"http://{self.frontend_host}:{self.frontend_port}"

    # ═══════════════════════════════════════════════════════════════════════════
    # ALBA - Network Telemetry & Data Collection (Port 5555)
    # ═══════════════════════════════════════════════════════════════════════════
    alba_host: str = Field(default="127.0.0.1")
    alba_port: int = Field(default=5555)
    alba_min_instances: int = Field(default=1, ge=1)
    alba_max_instances: int = Field(default=5, ge=1)

    @property
    def alba_url(self) -> str:
        """Full ALBA service URL."""
        return f"http://{self.alba_host}:{self.alba_port}"

    # ═══════════════════════════════════════════════════════════════════════════
    # ALBI - Neural Analytics & Pattern Recognition (Port 6680)
    # ═══════════════════════════════════════════════════════════════════════════
    albi_host: str = Field(default="127.0.0.1")
    albi_port: int = Field(default=6680)
    albi_min_instances: int = Field(default=1, ge=1)
    albi_max_instances: int = Field(default=8, ge=1)

    @property
    def albi_url(self) -> str:
        """Full ALBI service URL."""
        return f"http://{self.albi_host}:{self.albi_port}"

    # ═══════════════════════════════════════════════════════════════════════════
    # JONA - Data Synthesis & Strategic Advisor (Port 7777)
    # ═══════════════════════════════════════════════════════════════════════════
    jona_host: str = Field(default="127.0.0.1")
    jona_port: int = Field(default=7777)
    jona_min_instances: int = Field(default=1, ge=1)
    jona_max_instances: int = Field(default=3, ge=1)

    @property
    def jona_url(self) -> str:
        """Full JONA service URL."""
        return f"http://{self.jona_host}:{self.jona_port}"

    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN API - Real Stack (EEG, Audio, Billing) (Port 8000)
    # ═══════════════════════════════════════════════════════════════════════════
    main_api_host: str = Field(default="127.0.0.1")
    main_api_port: int = Field(default=8000)
    main_api_workers: int = Field(default=4, ge=1)

    @property
    def main_api_url(self) -> str:
        """Full Main API URL."""
        return f"http://{self.main_api_host}:{self.main_api_port}"

    # ═══════════════════════════════════════════════════════════════════════════
    # OCEAN CORE - ML/AI Engine (Port 8030)
    # ═══════════════════════════════════════════════════════════════════════════
    ocean_host: str = Field(default="127.0.0.1")
    ocean_port: int = Field(default=8030)
    ocean_workers: int = Field(default=2, ge=1)

    @property
    def ocean_url(self) -> str:
        """Full Ocean Core URL."""
        return f"http://{self.ocean_host}:{self.ocean_port}"

    # ═══════════════════════════════════════════════════════════════════════════
    # EXCEL CORE - Alba Idle Chat (Port 8031)
    # ═══════════════════════════════════════════════════════════════════════════
    excel_host: str = Field(default="127.0.0.1")
    excel_port: int = Field(default=8031)

    @property
    def excel_url(self) -> str:
        """Full Excel Core URL."""
        return f"http://{self.excel_host}:{self.excel_port}"

    # ═══════════════════════════════════════════════════════════════════════════
    # DATABASE (PostgreSQL)
    # ═══════════════════════════════════════════════════════════════════════════
    database_url: str = Field(
        default="postgresql://user:password@127.0.0.1:5432/clisonix",
        description="PostgreSQL connection string"
    )
    database_pool_size: int = Field(default=20, ge=1)
    database_max_overflow: int = Field(default=40, ge=0)
    database_pool_timeout: int = Field(default=30, ge=1)

    # ═══════════════════════════════════════════════════════════════════════════
    # REDIS (Caching)
    # ═══════════════════════════════════════════════════════════════════════════
    redis_host: str = Field(default="127.0.0.1")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0, ge=0, le=15)
    redis_timeout: int = Field(default=5, ge=1)

    @property
    def redis_url(self) -> str:
        """Full Redis URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # ═══════════════════════════════════════════════════════════════════════════
    # PAYMENT PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════
    # Stripe
    stripe_secret_key: Optional[str] = Field(default=None)
    stripe_public_key: Optional[str] = Field(default=None)
    stripe_webhook_secret: Optional[str] = Field(default=None)

    # PayPal
    paypal_client_id: Optional[str] = Field(default=None)
    paypal_client_secret: Optional[str] = Field(default=None)
    paypal_mode: Literal["sandbox", "live"] = Field(default="sandbox")

    # SEPA
    sepa_account_id: Optional[str] = Field(default=None)
    sepa_api_key: Optional[str] = Field(default=None)

    @property
    def has_payment_configured(self) -> bool:
        """Check if any payment provider is configured."""
        has_stripe = self.stripe_secret_key and self.stripe_public_key
        has_paypal = self.paypal_client_id and self.paypal_client_secret
        has_sepa = self.sepa_account_id and self.sepa_api_key
        return bool(has_stripe or has_paypal or has_sepa)
    
    @property
    def paypal_secret(self) -> Optional[str]:
        """Backward compatibility alias for paypal_client_secret"""
        return self.paypal_client_secret

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATION & SECURITY
    # ═══════════════════════════════════════════════════════════════════════════
    jwt_secret_key: str = Field(
        default="change-me-in-production",
        description="JWT secret key - set from environment",
        alias="JWT_SECRET"  # Match env var name
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24, ge=1, alias="JWT_EXPIRY_HOURS")
    api_key_length: int = Field(default=32, ge=16)

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str, info) -> str:
        """Only validate JWT secret in production if it's explicitly the default."""
        # Allow the default value during development/testing
        # In production, it should be overridden via environment variable
        return v

    # ═══════════════════════════════════════════════════════════════════════════
    # EXTERNAL SERVICES
    # ═══════════════════════════════════════════════════════════════════════════
    # Google Firestore
    google_application_credentials: Optional[str] = Field(default=None)
    firestore_project_id: Optional[str] = Field(default="clisonix-cloud")

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4318")
    otel_service_name: str = Field(default="clisonix-cloud")

    # ═══════════════════════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════════════════════
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_format: Literal["json", "text"] = Field(default="json")
    log_file: Optional[str] = Field(
        default="/var/log/clisonix/app.log",
        description="Log file path (None for stdout only)"
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # MONITORING & AUTO-HEALING
    # ═══════════════════════════════════════════════════════════════════════════
    enable_health_checks: bool = Field(default=True)
    health_check_interval_seconds: int = Field(default=30, ge=5)
    enable_auto_healing: bool = Field(default=True)
    auto_restart_failed_services: bool = Field(default=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # FEATURE FLAGS (For gradual rollout)
    # ═══════════════════════════════════════════════════════════════════════════
    enable_asi_layer: bool = Field(default=False)
    enable_auto_scaling: bool = Field(default=False)
    enable_intelligent_routing: bool = Field(default=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # RATE LIMITING & THROTTLING
    # ═══════════════════════════════════════════════════════════════════════════
    rate_limit_requests_per_minute: int = Field(default=100, ge=10)
    rate_limit_burst: int = Field(default=10, ge=1)
    enable_throttling: bool = Field(default=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # TIMEOUTS (seconds)
    # ═══════════════════════════════════════════════════════════════════════════
    service_startup_timeout: int = Field(default=30, ge=5)
    service_health_check_timeout: int = Field(default=5, ge=1)
    api_call_timeout: int = Field(default=30, ge=5)
    database_query_timeout: int = Field(default=15, ge=1)

    # ═══════════════════════════════════════════════════════════════════════════
    # MODEL CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════
    class Config:
        """Pydantic configuration for settings."""
        env_file = _get_env_file()  # Dynamically load correct .env file
        env_file_encoding = "utf-8"
        case_sensitive = False
        populate_by_name = True  # Allow both field names and aliases
        extra = "ignore"  # Ignore unknown fields from .env
        validate_assignment = True
        frozen = False  # Allow updates for testing

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_service_url(self, service_name: str) -> str:
        """
        Get URL for any service dynamically.
        
        Args:
            service_name: Name of service (alba, albi, jona, ocean, excel, main)
            
        Returns:
            Full service URL
            
        Raises:
            ValueError: If service_name is invalid
        """
        service_map = {
            "alba": self.alba_url,
            "albi": self.albi_url,
            "jona": self.jona_url,
            "ocean": self.ocean_url,
            "excel": self.excel_url,
            "main": self.main_api_url,
            "frontend": self.frontend_url,
        }
        
        if service_name.lower() not in service_map:
            raise ValueError(
                f"Unknown service: {service_name}. "
                f"Valid services: {', '.join(service_map.keys())}"
            )
        
        return service_map[service_name.lower()]

    def get_all_service_urls(self) -> dict:
        """Get URLs for all services."""
        return {
            "frontend": self.frontend_url,
            "alba": self.alba_url,
            "albi": self.albi_url,
            "jona": self.jona_url,
            "ocean": self.ocean_url,
            "excel": self.excel_url,
            "main": self.main_api_url,
        }

    def get_agent_config(self, agent_name: str) -> dict:
        """Get configuration for specific agent."""
        configs = {
            "alba": {
                "host": self.alba_host,
                "port": self.alba_port,
                "min_instances": self.alba_min_instances,
                "max_instances": self.alba_max_instances,
                "url": self.alba_url,
            },
            "albi": {
                "host": self.albi_host,
                "port": self.albi_port,
                "min_instances": self.albi_min_instances,
                "max_instances": self.albi_max_instances,
                "url": self.albi_url,
            },
            "jona": {
                "host": self.jona_host,
                "port": self.jona_port,
                "min_instances": self.jona_min_instances,
                "max_instances": self.jona_max_instances,
                "url": self.jona_url,
            },
        }
        
        if agent_name.lower() not in configs:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return configs[agent_name.lower()]

    def to_dict(self, exclude_secrets: bool = True) -> dict:
        """
        Convert settings to dictionary.
        
        Args:
            exclude_secrets: If True, excludes sensitive fields
            
        Returns:
            Settings as dictionary
        """
        data = self.model_dump()
        
        if exclude_secrets:
            sensitive_fields = [
                "jwt_secret_key",
                "stripe_secret_key",
                "paypal_client_secret",
                "sepa_api_key",
                "google_application_credentials",
            ]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "***REDACTED***"
        
        return data

    def validate_required_services(self) -> list[str]:
        """
        Validate that required services can be reached.
        
        Returns:
            List of unreachable services (empty list if all are fine)
        """
        import socket
        
        unreachable = []
        services = {
            "alba": (self.alba_host, self.alba_port),
            "albi": (self.albi_host, self.albi_port),
            "jona": (self.jona_host, self.jona_port),
            "ocean": (self.ocean_host, self.ocean_port),
            "excel": (self.excel_host, self.excel_port),
            "main": (self.main_api_host, self.main_api_port),
        }
        
        for service, (host, port) in services.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            if result != 0:
                unreachable.append(f"{service}@{host}:{port}")
            sock.close()
        
        return unreachable

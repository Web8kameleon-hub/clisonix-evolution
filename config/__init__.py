"""
Configuration package for Clisonix Cloud.

This package provides centralized, validated configuration management
using Pydantic settings with environment variable support.

Configuration Priority:
1. .env.production (if ENVIRONMENT=production)
2. .env.staging (if ENVIRONMENT=staging)  
3. .env (development default)
4. Environment variables
5. Hardcoded defaults

Usage:
    from config import settings
    
    print(settings.alba_port)  # Access any configuration value
    print(settings.environment)
    print(settings.database_url)
"""

from config.settings import AppSettings

# Global settings instance - loads from appropriate .env file based on ENVIRONMENT
settings = AppSettings()

# Log configuration status
print(f"[CONFIG] Settings loaded: {settings.environment.upper()}")
print(f"[CONFIG] JWT: {'Yes' if settings.jwt_secret_key != 'change-me-in-production' else 'DEFAULT'}")
print(f"[CONFIG] Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'localhost'}")
print(f"[CONFIG] Redis: {settings.redis_url}")
print(f"[CONFIG] Services: ALBA({settings.alba_port}) ALBI({settings.albi_port}) JONA({settings.jona_port}) Ocean({settings.ocean_port})")

__all__ = ["settings", "AppSettings"]

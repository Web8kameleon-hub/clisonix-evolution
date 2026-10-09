"""
DEMO - How to use the Centralized Configuration System

This shows how settings work throughout the application.
"""

from config import settings


def demo_basic_access():
    """Show basic access to settings."""
    print("\n" + "="*70)
    print("DEMO 1: BASIC ACCESS")
    print("="*70)
    
    print(f"\nEnvironment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Is Development: {settings.is_development}")
    print(f"Is Production: {settings.is_production}")


def demo_service_urls():
    """Show how to access service URLs dynamically."""
    print("\n" + "="*70)
    print("DEMO 2: SERVICE URLS (No Hardcoding!)")
    print("="*70)
    
    print(f"\nFrontend:   {settings.frontend_url}")
    print(f"ALBA:       {settings.alba_url}")
    print(f"ALBI:       {settings.albi_url}")
    print(f"JONA:       {settings.jona_url}")
    print(f"Ocean:      {settings.ocean_url}")
    print(f"Excel:      {settings.excel_url}")
    print(f"Main API:   {settings.main_api_url}")


def demo_dynamic_service_config():
    """Show how to get config for specific agent."""
    print("\n" + "="*70)
    print("DEMO 3: DYNAMIC AGENT CONFIGURATION")
    print("="*70)
    
    for agent in ["alba", "albi", "jona"]:
        config = settings.get_agent_config(agent)
        print(f"\n{agent.upper()} Config:")
        print(f"  URL:          {config['url']}")
        print(f"  Min instances: {config['min_instances']}")
        print(f"  Max instances: {config['max_instances']}")


def demo_database_config():
    """Show database configuration."""
    print("\n" + "="*70)
    print("DEMO 4: DATABASE CONFIGURATION")
    print("="*70)
    
    print(f"\nDatabase URL:        {settings.database_url}")
    print(f"Pool Size:           {settings.database_pool_size}")
    print(f"Max Overflow:        {settings.database_max_overflow}")
    print(f"Pool Timeout:        {settings.database_pool_timeout}")
    
    print(f"\nRedis URL:           {settings.redis_url}")
    print(f"Redis Host:          {settings.redis_host}")
    print(f"Redis Port:          {settings.redis_port}")


def demo_feature_flags():
    """Show feature flags for gradual rollout."""
    print("\n" + "="*70)
    print("DEMO 5: FEATURE FLAGS (For Gradual Rollout)")
    print("="*70)
    
    print(f"\nASI Layer Enabled:          {settings.enable_asi_layer}")
    print(f"Auto-Scaling Enabled:       {settings.enable_auto_scaling}")
    print(f"Intelligent Routing:        {settings.enable_intelligent_routing}")
    print(f"Auto-Healing Enabled:       {settings.enable_auto_healing}")
    print(f"Health Checks Enabled:      {settings.enable_health_checks}")


def demo_all_services():
    """Show all service URLs at once."""
    print("\n" + "="*70)
    print("DEMO 6: ALL SERVICES DYNAMIC MAP")
    print("="*70)
    
    all_urls = settings.get_all_service_urls()
    for service, url in all_urls.items():
        print(f"  {service:15} → {url}")


def demo_settings_as_dict():
    """Show how to get all settings as dict (with secrets redacted)."""
    print("\n" + "="*70)
    print("DEMO 7: SETTINGS AS DICTIONARY (Public Version)")
    print("="*70)
    
    settings_dict = settings.to_dict(exclude_secrets=True)
    
    print("\nCore Settings:")
    print(f"  Environment:        {settings_dict['environment']}")
    print(f"  Debug:              {settings_dict['debug']}")
    print(f"  Log Level:          {settings_dict['log_level']}")
    print(f"  JWT Algorithm:      {settings_dict['jwt_algorithm']}")
    print(f"  JWT Expiration:     {settings_dict['jwt_expiration_hours']} hours")
    print(f"  Rate Limit:         {settings_dict['rate_limit_requests_per_minute']}/min")


def demo_service_lookup():
    """Show dynamic service URL lookup."""
    print("\n" + "="*70)
    print("DEMO 8: DYNAMIC SERVICE LOOKUP")
    print("="*70)
    
    service_names = ["alba", "albi", "jona", "ocean", "excel", "main", "frontend"]
    
    for service in service_names:
        url = settings.get_service_url(service)
        print(f"  get_service_url('{service:10}') → {url}")


def demo_timeouts():
    """Show timeout configurations."""
    print("\n" + "="*70)
    print("DEMO 9: TIMEOUT CONFIGURATIONS")
    print("="*70)
    
    print(f"\nService Startup Timeout:    {settings.service_startup_timeout}s")
    print(f"Service Health Check:       {settings.service_health_check_timeout}s")
    print(f"API Call Timeout:           {settings.api_call_timeout}s")
    print(f"Database Query Timeout:     {settings.database_query_timeout}s")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " CLISONIX CONFIGURATION SYSTEM - DEMONSTRATION ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    demo_basic_access()
    demo_service_urls()
    demo_dynamic_service_config()
    demo_database_config()
    demo_feature_flags()
    demo_all_services()
    demo_settings_as_dict()
    demo_service_lookup()
    demo_timeouts()
    
    print("\n" + "="*70)
    print("✅ Configuration system is working perfectly!")
    print("="*70)
    print("\nUsage in your code:")
    print("  from config import settings")
    print("  url = settings.alba_url")
    print("  host = settings.alba_host")
    print("  port = settings.alba_port")
    print("="*70 + "\n")

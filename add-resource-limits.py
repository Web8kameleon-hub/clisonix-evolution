#!/usr/bin/env python3
"""
Add resource limits to all services in docker-compose.yml
This prevents uncontrolled memory growth and capacity issues.
"""

import sys

import yaml


def add_resource_limits(compose_dict):
    """Add deploy.resources.limits to all services"""

    if 'services' not in compose_dict:
        return compose_dict

    services = compose_dict['services']

    # Resource profiles by service type
    profiles = {
        'database': {'cpus': '1.0', 'memory': '2G', 'res_cpu': '0.5', 'res_mem': '1G'},
        'cache': {'cpus': '0.5', 'memory': '512M', 'res_cpu': '0.25', 'res_mem': '256M'},
        'api': {'cpus': '1.0', 'memory': '768M', 'res_cpu': '0.5', 'res_mem': '512M'},
        'ml': {'cpus': '1.5', 'memory': '1G', 'res_cpu': '0.75', 'res_mem': '512M'},
        'monitoring': {'cpus': '0.5', 'memory': '512M', 'res_cpu': '0.25', 'res_mem': '256M'},
        'worker': {'cpus': '0.5', 'memory': '512M', 'res_cpu': '0.25', 'res_mem': '256M'},
        'lab': {'cpus': '0.25', 'memory': '256M', 'res_cpu': '0.125', 'res_mem': '128M'},
        'default': {'cpus': '0.5', 'memory': '512M', 'res_cpu': '0.25', 'res_mem': '256M'},
    }

    # Service type detection
    db_keywords = ['postgres', 'mongodb', 'redis', 'neo4j', 'minio']
    cache_keywords = ['redis', 'cache', 'memcached']
    api_keywords = ['api', 'ocean', 'kloud', 'albix', '-core', 'matia', 'service']
    ml_keywords = ['alba', 'albi', 'jona', 'ollama', 'ai', 'ml', 'model']
    monitoring_keywords = ['prometheus', 'grafana', 'tempo', 'jaeger', 'victoria']
    worker_keywords = ['worker', 'job', 'queue', 'celery', 'task']
    lab_keywords = ['lab-']

    for service_name, service_config in services.items():
        if not isinstance(service_config, dict):
            continue

        # Detect service type
        service_type = 'default'

        if any(kw in service_name for kw in lab_keywords):
            service_type = 'lab'
        elif any(kw in service_name for kw in db_keywords):
            service_type = 'database'
        elif any(kw in service_name for kw in cache_keywords):
            service_type = 'cache'
        elif any(kw in service_name for kw in ml_keywords):
            service_type = 'ml'
        elif any(kw in service_name for kw in monitoring_keywords):
            service_type = 'monitoring'
        elif any(kw in service_name for kw in worker_keywords):
            service_type = 'worker'
        elif any(kw in service_name for kw in api_keywords):
            service_type = 'api'

        profile = profiles[service_type]

        # Add deploy section with resource limits
        if 'deploy' not in service_config:
            service_config['deploy'] = {}

        if 'resources' not in service_config['deploy']:
            service_config['deploy']['resources'] = {}

        service_config['deploy']['resources']['limits'] = {
            'cpus': profile['cpus'],
            'memory': profile['memory'],
        }

        service_config['deploy']['resources']['reservations'] = {
            'cpus': profile['res_cpu'],
            'memory': profile['res_mem'],
        }

    return compose_dict

if __name__ == '__main__':
    # Read docker-compose.yml
    with open('docker-compose.yml', 'r') as f:
        compose = yaml.safe_load(f)

    # Add resource limits
    compose = add_resource_limits(compose)

    # Write back with proper formatting
    with open('docker-compose.yml', 'w') as f:
        yaml.dump(compose, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✅ Added resource limits to {len(compose.get('services', {}))} services")
    print("Services by type:")
    for service_name in compose.get('services', {}).keys():
        if any(kw in service_name for kw in ['lab-']):
            print(f"  LAB:      {service_name}")

    sys.exit(0)

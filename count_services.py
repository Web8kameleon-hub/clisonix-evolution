#!/usr/bin/env python3
import os

import yaml


def count_services_in_compose(file_path):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        if data and 'services' in data:
            return len(data['services']), list(data['services'].keys())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return 0, []

# Count all docker-compose files
compose_files = [
    'docker-compose.yml',
    'docker-compose.75-services.yml',
    'docker-compose.unified.yml',
    'docker-compose.api.yml',
    'docker-compose.ocean-core.yml'
]

print("=" * 80)
print("CLISONIX CLOUD - MICROSERVICES INVENTORY")
print("=" * 80)

total_services = 0
all_services_set = set()
services_by_file = {}

for compose_file in compose_files:
    file_path = f'c:\\Users\\Admin\\Desktop\\Clisonix-cloud\\{compose_file}'
    if os.path.exists(file_path):
        count, services_list = count_services_in_compose(file_path)
        if count > 0:
            services_by_file[compose_file] = {
                'count': count,
                'services': services_list
            }
            total_services += count
            all_services_set.update(services_list)
            print(f"\n{compose_file}: {count} services")
            for service in services_list[:10]:  # Show first 10
                print(f"  - {service}")
            if len(services_list) > 10:
                print(f"  ... and {len(services_list) - 10} more services")

print("\n" + "=" * 80)
print(f"TOTAL UNIQUE SERVICES (across all files): {len(all_services_set)}")
print(f"TOTAL SERVICE INSTANCES: {total_services}")
print("=" * 80)

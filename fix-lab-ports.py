#!/usr/bin/env python3
"""
Fix lab port numbers in docker-compose.yml
Each lab should have PORT env var matching its exposed port
"""

import yaml

# Lab port mapping (port_number -> lab_name)
labs = {
    9101: 'lab-elbasan',
    9102: 'lab-tirana',
    9103: 'lab-durres',
    9104: 'lab-vlore',
    9105: 'lab-shkoder',
    9106: 'lab-korce',
    9107: 'lab-saranda',
    9108: 'lab-prishtina',
    9109: 'lab-kostur',
    9110: 'lab-athens',
    9111: 'lab-rome',
    9112: 'lab-zurich',
    9113: 'lab-beograd',
    9114: 'lab-sofia',
    9115: 'lab-zagreb',
    9116: 'lab-ljubljana',
    9117: 'lab-vienna',
    9118: 'lab-prague',
    9119: 'lab-budapest',
    9120: 'lab-bucharest',
    9121: 'lab-istanbul',
    9122: 'lab-cairo',
    9123: 'lab-jerusalem',
}

with open('docker-compose.yml', 'r') as f:
    compose = yaml.safe_load(f)

fixed_count = 0
for port, lab_name in labs.items():
    if lab_name in compose['services']:
        service = compose['services'][lab_name]

        # Set PORT environment variable to match the port
        if 'environment' not in service:
            service['environment'] = {}

        service['environment']['PORT'] = str(port)

        # Ensure port mapping is correct
        if 'ports' not in service:
            service['ports'] = []

        # Update ports to match
        service['ports'] = [f'{port}:{port}']

        fixed_count += 1

print(f"✅ Fixed {fixed_count} lab services with correct port numbers")

with open('docker-compose.yml', 'w') as f:
    yaml.dump(compose, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print("docker-compose.yml updated - labs now have matching PORT env and exposed ports")

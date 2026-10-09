import pathlib

import yaml

p = pathlib.Path('docker-compose.unified.yml')
print('exists', p.exists())
if not p.exists():
    raise SystemExit(1)

d = yaml.safe_load(p.read_text(encoding='utf-8')) or {}
print('services', len((d.get('services') or {})))
print('has_volumes', 'volumes' in d)
print('has_networks', 'networks' in d)

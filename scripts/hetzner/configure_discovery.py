"""Enable the real GRAM service and correct discovery deployment addresses."""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
path = root / 'docker-compose.unified.yml'
text = path.read_text(encoding='utf-8')
if not re.search(r'^  gram:', text, re.M):
    text = text.replace('services:\n', '''services:
  gram:
    build:
      context: .
      dockerfile: packages/gram/Dockerfile
    container_name: clisonix-gram
    environment:
      MPLCONFIGDIR: /tmp/matplotlib
    restart: unless-stopped
''', 1)
match = re.search(r'^  web:\n.*?(?=^  \S|\Z)', text, re.M | re.S)
assert match, 'web service missing'
block = match.group()
block = re.sub(r'^      GRAM_(?:INTERNAL_URL|URL):.*\n', '', block, flags=re.M)
block = block.replace('    environment:\n', '    environment:\n      GRAM_INTERNAL_URL: http://clisonix-gram:9710\n      GRAM_URL: http://clisonix-gram:9710\n', 1)
text = text[:match.start()] + block + text[match.end():]
text = text.replace('  intelligence-lab:\n', '  intelligence-lab:\n    image: clisonix-intelligence-lab:latest\n', 1)
match = re.search(r'^  intelligence-lab:\n.*?(?=^  \S|\Z)', text, re.M | re.S)
assert match, 'intelligence-lab service missing'
text = text[:match.start()] + match.group().replace('    profiles:\n      - research\n', '') + text[match.end():]
path.write_text(text, encoding='utf-8', newline='\n')
route = root / 'apps/web/app/api/service-discovery/route.ts'
text = route.read_text(encoding='utf-8')
if 'const KLOUD_BRIDGE_BASE =' not in text:
    text = text.replace('type KnownService = {', '''const KLOUD_BRIDGE_BASE =
  process.env.KLOUD_BRIDGE_URL ||
  (isDev ? "http://localhost:8889" : "http://clisonix-kloud-bridge:8889");

type KnownService = {''', 1)
text = text.replace('`${API_BASE}/api/kloud-bridge/status`', '`${KLOUD_BRIDGE_BASE}/status`')
text = text.replace('health: "/api/kloud-bridge/health"', 'health: "/health"')
route.write_text(text, encoding='utf-8', newline='\n')

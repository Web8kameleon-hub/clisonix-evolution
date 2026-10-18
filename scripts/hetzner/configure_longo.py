"""Switch the unified API to Longo while preserving legacy database files."""
import pathlib
import re
import sys


def configure(text):
    if re.search(r"^  longo:", text, re.M):
        raise ValueError("Longo already configured; inspect configuration before rerunning")
    for name in ("postgres", "analytics", "userdata"):
        text, count = re.subn(
            rf"(^  {name}:\n)", r'\1    profiles: [legacy-postgres]\n', text, count=1, flags=re.M
        )
        if count != 1:
            raise ValueError(f"Missing service: {name}")
    match = re.search(r"^  api:\n.*?(?=^  \S|\Z)", text, re.M | re.S)
    if not match:
        raise ValueError("Missing API service")
    api = match.group()
    api = re.sub(r"^      DATABASE_URL:.*$", "      LONGO_URL: http://longo:8030", api, flags=re.M)
    api = api.replace("      postgres:\n", "      longo:\n")
    api = api.replace("import socket; socket.create_connection(('postgres',5432),2).close();", "import os, urllib.request, socket; urllib.request.urlopen(os.environ['LONGO_URL'] + '/health', timeout=3).close();")
    if "LONGO_URL: http://longo:8030" not in api or "urllib.request.urlopen" not in api:
        raise ValueError("Unexpected API configuration")
    text = text[:match.start()] + api + text[match.end():]
    service = '''  longo:
    image: clisonix-longo:latest
    build:
      context: ./java-longo
      dockerfile: Dockerfile
    container_name: clisonix-longo
    environment:
      LONGO_PORT: '8030'
      LONGO_STORAGE_PATH: /data/longo.bin
    volumes:
      - longo_data:/data
    healthcheck:
      test: [CMD, java, --add-modules, java.net.http, -cp, /app/longo.jar, com.clisonix.longo.HealthProbe]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
'''
    text = text.replace("services:\n", "services:\n" + service, 1)
    text = text.replace("\nvolumes:\n", "\nvolumes:\n  longo_data:\n    external: true\n    name: ${LONGO_VOLUME_NAME:-clisonix_longo-data}\n", 1)
    return text


if __name__ == '__main__':
    path = pathlib.Path(sys.argv[1])
    result = configure(path.read_text(encoding='utf-8'))
    path.write_text(result, encoding='utf-8', newline='\n')

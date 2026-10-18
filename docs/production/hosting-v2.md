# Production hosting inventory

`compose-hosting.yml` is the current 198-service production manifest. The
January `docker-compose.75-services.yml` is a historical stack and is no longer
the default input for the Swarm deploy script.

On the Hetzner host, from `/opt/clisonix.com`:

```bash
bash scripts/hetzner/hosting_v2.sh inventory
bash scripts/hetzner/hosting_v2.sh check
bash scripts/hetzner/hosting_v2.sh deploy web api nginx
```

`inventory` does not need secrets or change containers. `check` verifies the
production environment, Compose configuration, and repository guard. `deploy`
rebuilds the named services and their Compose dependencies. Pass `all` as the
sole service argument only for a planned full-stack deployment.

The required values are listed in `hosting-v2.env.example`. Set them in the
server's `.env.production`; the example file must never contain real secrets.
The inventory counts Compose containers by declared `container_name`, while the
total Docker count also includes Swarm tasks and other stacks. These counts are
different by design.

The host has an NVIDIA RTX 4000 SFF Ada. On 2026-09-16, the loaded kernel
module was 595.84 while the installed userspace library and module on disk
were 595.91.07. `nvidia-smi` failed and the live Ollama container ran with
`OLLAMA_NUM_GPU=0` and no Docker GPU device request. Repair the driver mismatch
and verify `nvidia-smi` and Docker GPU access before applying
`compose-hosting.gpu.yml` to Ollama. Do not include the GPU overlay in an
automatic deploy while that preflight fails.

The Kloud Bridge endpoint `/integrations/domains` checks
`www.neurosonic.eu/api/health` and `aiagi.io/api/v1/status` as JSON APIs.
`/integrations/services` probes fixed read-only OS-CLX and Neurosonic contracts
and reports each service independently. HTML responses are never reported as a
working fabric API. The
Neurosonic deployment currently reports `NEUROSONIC_CLOUD_BASE_URL is not
configured` at `/api/cloud/bridge`; its deployment environment must be set
and tested before claiming the reverse Auth/Billing bridge is connected.
The canonical Lightning SPP source is the private
`Web8kameleon-hub/Lightning-SPP-3.14` repository. Its production service is
not listening on the host's documented `127.0.0.1:11400` port, and the OS-CLX
Lightning integration currently returns 502. Neurosonic's internal Lightning
stats endpoint is a separate live API.

Ocean chat pages now request one JSON answer. Batica-Zbatica context comes
from the user's browser-supplied conversation history; the dedicated server
side Batica store was removed. Large document uploads still need a bounded
memory implementation before 1 GiB files can be safely processed end to end.

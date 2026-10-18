# GHCR Pull Deploy Runbook (No SSH / No Port 22)

This runbook migrates production to pull-based auto deploy using GHCR + Watchtower.

## Goal

- Remove SSH-based deploy dependency.
- Keep auto-deploy from Git commits.
- Auto-start containers after reboot.
- Keep port 22 closed to the public internet.

## Prerequisites

- Docker and Docker Compose plugin on server.
- Public access to GHCR from server over HTTPS (port 443 outbound).
- Existing `docker-compose.75-services.yml` on server.

## 1. Configure GitHub workflows

Use these workflows:

- `.github/workflows/ghcr-build-push.yml`
- `.github/workflows/ghcr-deploy-health-gate.yml`

Health gate URL configuration:

- Defaults are already set in `.github/workflows/ghcr-deploy-health-gate.yml`.
- You can override URLs when triggering workflow_dispatch manually.

Optional for web build args:

- `AUTH_SECRET`
- `NEXTAUTH_SECRET`

## 2. Prepare server for pull-based deploy

1. Login to GHCR on server:

```bash
echo "$GHCR_PAT" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
```

2. Ensure external network exists:

```bash
docker network create clisonix-net || true
```

3. Deploy with override file:

```bash
docker compose \
  -f docker-compose.75-services.yml \
  -f docker-compose.autodeploy-ghcr.yml \
  pull api web ocean-core watchtower

docker compose \
  -f docker-compose.75-services.yml \
  -f docker-compose.autodeploy-ghcr.yml \
  up -d api web ocean-core watchtower
```

4. Run local health gate:

```bash
bash scripts/deploy-health-gate.sh
```

## 3. Autostart after reboot

1. Ensure Docker starts on boot:

```bash
sudo systemctl enable docker
sudo systemctl restart docker
```

2. Services already use `restart: unless-stopped` in override.

## 4. Close SSH port 22

Apply both provider firewall and host firewall.

Hetzner Cloud Firewall:

- Remove inbound allow rule for TCP/22.
- Keep only required HTTP/HTTPS rules.

Host firewall (UFW example):

```bash
sudo ufw deny 22/tcp
sudo ufw reload
sudo ufw status
```

If iptables is used:

```bash
sudo iptables -A INPUT -p tcp --dport 22 -j DROP
sudo ip6tables -A INPUT -p tcp --dport 22 -j DROP
```

## 5. Validation checklist

- New commit to `main` publishes images to GHCR.
- Server pulls fresh images automatically via Watchtower.
- Health endpoints return HTTP 200.
- Port 22 is not reachable from internet.

## Rollback

Pin image tag explicitly:

```bash
export CLISONIX_IMAGE_TAG=sha-<known-good>

docker compose \
  -f docker-compose.75-services.yml \
  -f docker-compose.autodeploy-ghcr.yml \
  up -d api web ocean-core

bash scripts/deploy-health-gate.sh
```

## clisonix-evolution integration

This repository uses `ocean_core/` as the Ocean source directory and publishes
`clisonix-evolution-api`, `clisonix-evolution-web`, and `clisonix-evolution-ocean-core`.
These image names are separate from the existing clisonix.com production images.
Adding these files does not install or activate Watchtower on GEX44.
The public health workflow checks availability; it does not prove that the new
commit is deployed. Verify the running image digest before declaring a release live.

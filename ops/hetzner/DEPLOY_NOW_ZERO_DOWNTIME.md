# Hetzner Deploy Now (Zero-Downtime)

## Locked Parameters

- Target host: `46.225.14.83`
- Canonical compose file: `docker-compose.production.yml`
- Fallback compose file (legacy): `docker-compose.yml`

## Scope

- Deploy only Ocean services without stopping all core containers.
- Keep rollback path ready before any update.

## Preconditions (GO)

- Local git is clean and synced with `main`.
- SSH key access to target host is confirmed.
- Existing stack is healthy (`/health` endpoints return success).
- Backup directory exists on server: `/root/clisonix-backups`.

## Hard NO-GO

- Unknown target host.
- Missing compose file locally and no fallback file available.
- Failing health checks before deployment.
- No backup created.

## Execution

### 1) Quick preflight from local machine

```bash
ssh root@46.225.14.83 "echo SSH_OK && hostname && docker --version && docker-compose --version"
ssh root@46.225.14.83 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

### 2) Run safe deploy script

```bash
./HETZNER_DEPLOY_v2.sh 46.225.14.83 root 22
```

Optional explicit compose override:

```bash
COMPOSE_FILE=docker-compose.production.yml ./HETZNER_DEPLOY_v2.sh 46.225.14.83 root 22
```

### 3) Immediate health verification

```bash
curl -sf http://46.225.14.83:8030/health && echo "ocean-core ok"
curl -sf http://46.225.14.83:8033/health && echo "ocean-core-multimodal ok"
curl -sf http://46.225.14.83:8035/health && echo "ocean-core-strict-chat ok"
curl -sf http://46.225.14.83:8032/health && echo "ocean-core-blerina ok"
```

## Rollback

If service health degrades after deploy:

```bash
ssh root@46.225.14.83 "ls -t /root/clisonix-backups/docker-compose.production.yml.* | head -1"
ssh root@46.225.14.83 "cp /root/clisonix-backups/docker-compose.production.yml.<TIMESTAMP> /root/Clisonix-cloud/docker-compose.production.yml"
ssh root@46.225.14.83 "cd /root/Clisonix-cloud && docker-compose -f docker-compose.production.yml restart"
```

## Evidence to Record

- Operator
- Timestamp
- Git commit
- Compose file used
- Backup artifact path
- Health check outputs
- Outcome (GO or rollback)

# CI/CD Autopilot (All Green)

## Goal

Automate the full path:

1. Commit code
2. Push to `main`
3. Deploy to Hetzner
4. Rebuild Docker services
5. Run health gates

If health checks fail, workflow exits with failure and prints service logs.

## New Workflow

- File: `.github/workflows/auto-deploy-all-green.yml`
- Trigger:
  - push on `main` (app/ocean/services/compose/workflow paths)
  - manual `workflow_dispatch`

This is the only supported deploy workflow.

## Legacy Workflows

Legacy deploy workflows were removed to avoid parallel deployment paths and drift:

- `.github/workflows/deploy.yml`
- `.github/workflows/deploy-docker.yml`
- `.github/workflows/deploy-ssh.yml`
- `.github/workflows/deploy-helm.yml`
- `.github/workflows/rebuild-docker-manual.yml`

Use only `auto-deploy-all-green.yml` for server rollout.

## Required GitHub Secret

- `HETZNER_SSH_KEY` (private key for root SSH deploy)

## Default Deploy Set

`web,api,ocean-core,billing-core,user-management`

Compose file default:
`docker-compose.75-services.yml`

## Local One-Command CLI

Use:

`./scripts/cicd-cli.ps1 -Message "feat: my change" -Branch main`

This helper will:

- commit all local changes
- push to branch
- trigger workflow `🚦 Auto Deploy (All Green)`

### Useful flags

- `-NoCommit` (skip commit)
- `-NoPush` (skip push)
- `-NoDeploy` (skip workflow trigger)
- `-Services "web,api,ocean-core"` (manual service set for dispatch)

## Health Gates

During deploy, workflow checks:

- `web` → `http://localhost:3000/api/health-check`
- `api` → `http://localhost:8000/health`
- `ocean-core` → `http://localhost:8030/health`
- `billing-core` → `http://localhost:8095/health`
- `user-management` → `http://localhost:8071/health`

Any failed gate marks deployment red.

## Recommended Branch Protection

For true "all green only":

1. Enable branch protection on `main`
2. Require status check: `🧪 Preflight`
3. Require status check: `🚀 Deploy + Health Gate`

This blocks broken deploys from being considered successful.

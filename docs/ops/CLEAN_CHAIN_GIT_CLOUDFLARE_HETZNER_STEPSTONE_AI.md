# Clean Chain: Git + Cloudflare + Hetzner + Stepstone AI Agents

## Objective

Ky workflow krijon nje zinxhir te paster deploy-i:

- Git (`main`) si source of truth
- Hetzner (`178.63.89.121`) si runtime target
- Cloudflare si edge/cache layer
- Stepstone AI agents per gate dhe verifikim kritik

## Files

- Workflow: `.github/workflows/clean-chain-git-cloudflare-hetzner-ai.yml`
- Agent manifest: `agents.yml`
- Runtime verification script: `scripts/hetzner/post_deploy_verify_auth_billing_ocean.sh`
- Ultra checklist: `docs/ops/GEX44_CLEAN_DEPLOY_ULTRA_CHECKLIST.md`

## Required GitHub Secrets

- `HETZNER_SSH_KEY`
- `CF_API_TOKEN`
- `CF_ZONE_ID`

Opsional per runtime deploy (vendosen ne server `.env.production`):

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `NEXTAUTH_SECRET`
- `NEXT_PUBLIC_API_URL`
- `INTERNAL_API_KEY`

## Stepstone Stages

1. `stepstone-preflight`
2. `stepstone-quality-gate`
3. `stepstone-hetzner-deploy`
4. `stepstone-cloudflare-sync`
5. `stepstone-ai-agent-gate`

## Trigger Modes

### Push on main

- Ekzekuton chain automatik kur ndryshon workflow/agents/spec/verify scripts.

### Manual dispatch

- `deploy_scope=critical`: deploy vetem sherbimet kritike
- `deploy_scope=full`: deploy full stack
- `cloudflare_mode=skip|purge-api-and-root`

## Clean Contract

- Nese preflight ose quality gate deshton, deploy nuk vazhdon.
- Nese deploy deshton, cloudflare step nuk ekzekutohet.
- Nese cloudflare step deshton, AI agent gate nuk kalon.
- Nuk shpallet sukses pa kaluar verifikimi final.

## Operational Sequence (High Level)

1. Validate `agents.yml`, OpenAPI syntax, dhe scripts.
2. Run quality policy checks (no fake/mock fallback patterns).
3. SSH deploy ne Hetzner me compose validation dhe startup.
4. Run runtime API verification (`auth+billing+paywall+ocean`).
5. Purge Cloudflare cache per endpointet kritike.
6. Validate AI agent map and health endpoint contract.

## Recommended Branch Policy

- Require successful status check:
  `Clean Chain Git-Cloudflare-Hetzner-AI / Stepstone 5 - AI Agent Gate`

## Notes

- Workflow target host eshte serveri i ri `178.63.89.121`.
- Per rotacion hosti ne te ardhmen, ndrysho `HETZNER_IP` ne workflow dhe `target.host` ne `agents.yml`.

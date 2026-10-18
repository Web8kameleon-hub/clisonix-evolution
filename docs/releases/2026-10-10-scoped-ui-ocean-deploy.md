# Scoped UI and Ocean deployment

## Issue

Production had uncommitted homepage, account, authentication and Ocean changes.
The local checkout also contained Ocean and status improvements absent from main.
Both sources were combined against origin/main without overwriting the production
checkout. Excel and Labs source files matched main and required no deployment.

## Documentation

The homepage and /app share PlatformWorkspaceClient, including the report action.
Ocean forwards the existing user identity and supports clearing conversation memory.
The status UI consumes fresh observations persisted in Redis.

Authentication secrets were removed from Web build ARG/ENV and Compose build args;
the existing runtime environment remains the source of authentication secrets.
Web Docker context excludes every .env variant. Existing main dependency versions
and its lockfile were retained, and the build explicitly uses Webpack.

Only web, ocean-core, api, ocean-mission-service, translation-node and
ocean-core-multimodal were recreated. The Python changes were layered onto the
installed images, preserving their existing dependencies. Web used a complete
production build. The release is stored at
/opt/clisonix-releases/20261010-scoped-79bf85ad8.

deploy_changed_services.py captures the exact running environment, networks,
ports, volumes, resource settings, health checks and previous image tags. Private
runtime snapshots stay on the server. Every restart uses --no-deps. A container
identity change after preparation stops deployment, and a failed health gate
restores previous images for the services already attempted.

The existing broad automatic deployment workflows now require explicit opt-in
variables: AUTO_DEPLOY_ALL_SERVICES for Auto Deploy and SWARM_FULL_STACK_DEPLOY
in addition to SWARM_AUTO_DEPLOY for the full Swarm rollout. Manual triggers remain.

## Tests

99 Python tests passed; two platform-dependent tests were skipped. TypeScript,
64 Ocean HumanThinking routing checks and the Web production build passed.
The changed-file secret scan found no secrets. Deployment tests cover preservation
of runtime configuration, refusal to overwrite a changed container, exclusion of
unrelated source files, and automatic rollback after failed health checks.

All six deployed containers passed their Docker health checks. Web, Ocean Core,
API and Translation HTTP health endpoints returned 200. A Web canary served the
new homepage and its authentication provider endpoint returned 200. The deployed
origin served the new connected workspace. Redis recorded the fresh status sample,
and the status API measured six healthy services. The unrelated containers kept
their original IDs throughout deployment.

## Edge cases

The bare clisonix.com domain still returned HTTP 403 during verification.
www.clisonix.com returned cached old homepage HTML with cf-cache-status HIT;
an uncached query URL returned HTTP 200 with the new connected workspace.
Available Cloudflare API credentials were unusable or empty, so no successful
cache purge is claimed. These public edge restrictions remain separate from the
healthy deployed origin. No Cloudflare security policy was changed.

## Benchmark

No performance improvement is claimed. Status history counts observed checks,
not unobserved availability.

## Rollback

Run the release's scripts/hetzner/deploy_changed_services.py with mode rollback,
--release /opt/clisonix-releases/20261010-scoped-79bf85ad8 and the explicit
--services web,ocean-core,api,ocean-mission-service,translation-node,ocean-core-multimodal.
The private rollback snapshot restores previous images and runtime configuration.
It does not reset the repository or delete collected evidence.

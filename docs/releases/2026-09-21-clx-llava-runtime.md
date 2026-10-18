# CLX and LLaVA runtime restoration — 2026-09-21

## Scope

This release restores the deployable runtime path for CLX agent, CLX-I vision,
CLX hybrid and the Ollama-hosted LLaVA model. It does not declare those
capabilities available merely because source files or documentation exist.

## Corrected configuration

- CLX-I listens on port `8048` consistently in the service and health check.
- The requested vision model is explicit: `llava:7b`.
- Ollama health no longer succeeds unconditionally.
- CLX-I health is degraded when the configured vision model is absent.
- CLX services deploy through an isolated Swarm rollout instead of the unrelated
  full-stack path.

## Production truth gate

The rollout must complete all of these checks:

1. Ollama container is running and attached to the private Swarm overlay.
2. At least 8 GB free disk is available before pulling a missing vision model.
3. `ollama list` contains the configured LLaVA model.
4. CLX agent, CLX-I and CLX hybrid reach container health.
5. CLX-I reports `dependencies.vision_model=ready`.
6. A real one-pixel PNG request reaches LLaVA and returns non-empty model output.

A failed step aborts the rollout. No placeholder response is accepted.

## Evidence state

- Curiosity text generation was independently verified in production with
  `llama3.1:8b`, returning streamed `OCEAN_OK`.
- CLX/LLaVA are **configured for rollout**, not yet claimed production-ready.
- Production-ready status requires the deployment workflow and real inference
  gate above to succeed.

## Canonical source audit — 2026-09-22

The repository-level runtime truth audit now derives evidence from platform-owned
sources and does not treat file presence as service health.

Observed canonical inventory:

- 23 city laboratories declared by `config/city-labs.registry.json`
- 84 engine source files
- 22 orchestrator source files
- 14 Gram source files
- 60 `all_pillars` artifacts
- 170 `generated_medical_pillars` artifacts
- 3 `lagter_pillars` artifacts
- 42 public module routes after removing the invalid localhost backend card
- 33 routes with detected API wiring, still functionally unverified
- 9 reachable routes without a detected module-specific API contract

The January `registry_export.json` is explicitly classified as a historical
snapshot, not current runtime health. Direct production Swarm inventory remains
a separate read-only verification scope and must not export private host
metadata without explicit authorization.

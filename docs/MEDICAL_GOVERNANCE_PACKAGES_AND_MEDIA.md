# Clisonix Medical Governance - Packages & Dynamic Media

This document defines required packages and media policy for strict medical publication governance.

## 1) Core packages (mandatory)

### API & service runtime

- `fastapi`
- `uvicorn`
- `httpx`
- `pydantic`

### Data and validation

- `python-dateutil`
- `jsonschema`

### Quality and testing

- `pytest`
- `pytest-asyncio`

## 2) Optional media packages (recommended)

### Real image provider integrations

- No extra package required for Unsplash (`httpx` is enough)

### Generated image providers

- `Pillow` (if local post-processing is needed)

## 3) Environment variables for dynamic images

- `UNSPLASH_ACCESS_KEY` (optional)
- `IMAGE_GENERATOR_URL` (optional internal generator endpoint)

If both are absent, publisher uses an article-specific dynamic fallback URL.

## 4) Media policy (strict)

- Static fixed image for all posts is forbidden.
- Each article must resolve to an article-specific image URL.
- Valid sources:
  1. Article payload (`hero_image`, `image_url`, `featured_image`, `image_urls`)
  2. Real image lookup (Unsplash API)
  3. Internal generated image service
  4. Dynamic seeded fallback (`picsum.photos/seed/{article_id}`)

## 5) Governance policy

Publication is allowed only if:

- GEN6-GEN9 governance gate passes
- Error rate is in allowed range (`0.001%` to `0.50%` checkpoints)
- Required reference metadata is complete
- Labs and systems collaboration flags are satisfied for Dr. Albana articles

## 6) Notes

This package and media standard complements:

- `docs/MEDICAL_GEN6_9_GOVERNANCE.md`
- `docs/medical-governance-packages/INDEX.md`
- `scripts/audit_medical_gen_layers.py`
- `services/blog_publisher/main.py`

# CLISONIX MODULE MAP

# Version: 1.0.0

---

## USER PROMPT

Clisonix is a European AI platform focused on modular reasoning engines, distributed intelligence, and sovereign cloud architectures. It provides advanced tools for domain-adaptive reasoning, expert-level chat modules, and deterministic AI pipelines designed for industrial and scientific applications. All responses are accurate, professional, and respect user privacy.

---

## INTERNAL MODULE ROUTING

### Official Platform Modules (2026)

| Module | Purpose | Route / Interface |
|--------|---------|-------------------|
| nanogridata-edge | Secure edge ingestion protocol v1 | Binary wire format (magic/version/model_id/payload_type/HMAC) |
| bridge-engine | Pulse routing and fan-out | /signals/publish, /signals/process, /routes |
| kloud-bridge | Isolated gateway to `Kameleonlife/Kloud` | /health, /status, /signals/publish, /fabric/sync |
| ocean-enterprise-api-v1 | Tenant AI chat core (Nanogrid v3) | /api/v1/chat, /api/v1/chat/stream |

### Core Services

| Module | Route |
|--------|-------|
| ocean | /api/ocean |
| chat | /api/chat |
| trinity | /api/trinity |
| zurich | /api/zurich |

### Specialized Modules

| Module | Route |
|--------|-------|
| alba | /api/alba |
| albi | /api/albi |
| jona | /api/jona |

### Intelligence Lab & Content Stack

| Module | Route / Interface |
|--------|-------------------|
| klajdi | /klajdi/* (via intelligence-lab) |
| mali | /mali/* (via intelligence-lab) |
| liam | /health, /api/v1/* (LIAM service) |
| alda | /tables/alda (via intelligence-lab), alda service metrics |
| blerina | content generation service (pillar/blog/social pipeline) |

### Module Dependencies

```
chat → ocean → ollama
trinity → ocean → ollama
zurich → ocean → ollama
alba → standalone
albi → standalone
albi → klajdi (signal/case intelligence)
klajdi → mali (findings and diagnostics)
mali → liam + alda (intake, tables, labor metrics)
blerina → mali/tables + newsroom (publish-ready content)
nanogridata-edge → bridge-engine → analytics/asi/api/saas-api
kloud-bridge → external Kloud sovereign runtime (isolated repo)
ocean-enterprise-api-v1 → ollama-multi-api or ollama
```

---

## SHARED BEHAVIORS

### Language

Respond in the user's language.

### Safety

- No invented facts
- No medical/legal/financial advice
- Cite sources when needed

### Format

- Markdown for structure
- Code blocks for technical content
- Concise paragraphs

---

## MODULE PERSONAS

| Module | Role | Style |
|--------|------|-------|
| Ocean | Conversational AI | Friendly, helpful |
| Zürich | Deep reasoning | Academic, thorough |
| Trinity | Multi-perspective | Balanced debate |
| ALBA | Audio/Video | Technical |
| ALBI | Biosignal | Precise |
| JONA | Neural | Scientific |

---

## PERSONALITY CONTRACT

Canonical personality and soft-boundary rules are defined in:

- `docs/personality/CLISONIX_PERSONALITY_CONTRACTS.md`

---

*Single source of truth for module architecture.*

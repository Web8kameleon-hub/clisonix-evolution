"""Read-only, allowlisted runtime evidence for Ocean's answer pipeline.

Health responses establish reachability, not model quality or hardware readiness.
Catalog entries are source discovery metadata, not fetched webpage evidence.
"""
import asyncio
import json
import os
import re
from pathlib import Path

import httpx


TOOLS = {
    "CLX": "http://clisonix-clx-agent:7778/health",
    "CLX.i": "http://clisonix-clx-i:8048/health",
    "CLX Hybrid / WWWMMM": "http://clisonix-clx-hybrid:8058/health",
    "Multimodal": "http://clisonix-ocean-core-multimodal:8033/health",
    "Translation": "http://clisonix-translation-node:8036/health",
    "City Labs": "http://clisonixcom-city-labs-registry-1:9130/api/v1/labs",
    "Excel": "http://clisonix-excel:8002/health",
    "Excel Core": "http://clisonix-excel-core:8010/health",
    "OpenMind": "http://clisonix-openmind:9999/health",
    "MALI / KLAJDI": "http://clisonix-intelligence-lab:8098/health",
    "ALBA": "http://clisonix-alba:5555/health",
    "ALBI": "http://clisonix-albi:6680/health",
    "JONA": "http://clisonix-jona:7777/health",
    "BLERINA": "http://clisonix-blerina:8037/health",
    "AGIEM": "http://clisonix-agiem:9300/health",
    "ASI": "http://clisonix-asi:9094/health",
    "LIAM": "http://clisonix-liam:8062/health",
    "ALDA": "http://clisonix-alda:8063/health",
    "Cycle": "http://clisonix-cycle:8005/health",
    "Cycle Engine": "http://clisonix-cycle-engine:8005/health",
    "GRAM / mesh": "http://clisonix-gram:9710/health",
    # --- Expanded 2026-10 to cover the full running fleet (no gaps) ---
    "Adaptive Router": "http://clisonix-adaptive-router:8011/health",
    "Ads Core": "http://clisonix-ads-core:8096/health",
    "Advanced Analytics": "http://clisonix-advanced-analytics:8016/health",
    "Agent Telemetry": "http://clisonix-agent-telemetry:6680/health",
    "Alba Idle": "http://clisonix-alba-idle:8031/health",
    "Albi User": "http://clisonix-albi-user:6681/health",
    "Alphabet Layers": "http://clisonix-alphabet-layers:8061/health",
    "Analytics": "http://clisonix-analytics:8006/health",
    "Core API": "http://clisonix-api:8000/health",
    "Aviation": "http://clisonix-aviation:8080/health",
    "Behavioral": "http://clisonix-behavioral:8003/health",
    "Billing Core": "http://clisonix-billing-core:8095/health",
    "Biometric": "http://clisonix-biometric:8009/health",
    "Blog Paywall": "http://clisonix-blog-paywall:8020/health",
    "Blog Publisher": "http://clisonix-blog-publisher:8041/health",
    "Cognitive Engine": "http://clisonix-cognitive-engine:8010/health",
    "Content Factory": "http://clisonix-content-factory:4003/health",
    "Crawler": "http://clisonix-crawler:9211/health",
    "Curiosity": "http://clisonix-curiosity:8011/health",
    "Developer Portal": "http://clisonix-developer-portal:8005/health",
    "Dr. Albana": "http://clisonix-dr-albana:8040/health",
    "Data Sovereignty - Europe": "http://clisonix-ds-europe:9301/health",
    "Data Sovereignty - Americas": "http://clisonix-ds-americas:9302/health",
    "Data Sovereignty - Asia": "http://clisonix-ds-asia:9303/health",
    "Data Sovereignty - India": "http://clisonix-ds-india:9304/health",
    "Data Sovereignty - Africa": "http://clisonix-ds-africa:9305/health",
    "Data Sovereignty - Oceania": "http://clisonix-ds-oceania:9306/health",
    "Data Sovereignty - Central Asia": "http://clisonix-ds-central-asia:9307/health",
    "Data Sovereignty - Antarctica": "http://clisonix-ds-antarctica:9308/health",
    "EAP": "http://clisonix-eap:9501/health",
    "Economy": "http://clisonix-economy:9093/health",
    "Health Monitor": "http://clisonix-health-monitor:8099/health",
    "Kitchen API": "http://clisonix-kitchen-api:8065/health",
    "Kitchen Worker": "http://clisonix-kitchen-worker:3100/health",
    "Kloud Bridge": "http://clisonix-kloud-bridge:8889/health",
    "Kloud Upstream Runtime": "http://clisonix-kloud-upstream-runtime:9080/health",
    "Knowledge": "http://clisonix-knowledge:8012/health",
    "Lagter": "http://clisonix-lagter:9500/health",
    "LinkedIn Poster": "http://clisonix-linkedin-poster:8007/health",
    "Longo": "http://clisonix-longo:18030/health",
    "Marketplace": "http://clisonix-marketplace:8004/health",
    "Matia": "http://clisonix-matia:7200/health",
    "Multi-Tenant": "http://clisonix-multi-tenant:8007/health",
    "Neurosonix": "http://clisonix-neurosonix:8006/health",
    "Newsroom": "http://clisonix-newsroom:9800/health",
    "Ocean Core Blerina": "http://clisonix-ocean-core-blerina:8032/health",
    "Ocean Core Strict Chat": "http://clisonix-ocean-core-strict-chat:8035/health",
    "Ocean Mission": "http://clisonix-ocean-mission:9500/health",
    "Ollama Multi API": "http://clisonix-ollama-multi-api:4444/health",
    "Orchestra": "http://clisonix-orchestra:9700/health",
    "Personas": "http://clisonix-personas:9200/health",
    "Quantum": "http://clisonix-quantum:8008/health",
    "Regulatory": "http://clisonix-regulatory:9501/health",
    "Reporting": "http://clisonix-reporting:8001/health",
    "SaaS": "http://clisonix-saas:8008/health",
    "SaaS API": "http://clisonix-saas-api:8040/health",
    "SaaS Orchestrator": "http://clisonix-saas-orchestrator:9999/health",
    "Shopping Therapy": "http://clisonix-shopping-therapy:7300/health",
    "Tide": "http://clisonix-tide:8091/health",
    "User Data": "http://clisonix-userdata:8010/health",
    "User Management": "http://clisonix-user-management:8070/health",
    "Video Generator": "http://clisonix-video-generator:8029/health",
}

# Infrastructure services that don't speak HTTP/JSON "/health" (databases,
# caches, observability backends). Checked via plain TCP reachability only —
# never reported as "healthy", only as "reachable" or "unreachable", so we
# never fabricate an application-level health claim we can't verify.
INFRA_TOOLS = {
    "Postgres": ("clisonix-postgres", 5432),
    "Redis": ("clisonix-redis", 6379),
    "MongoDB": ("clisonix-mongodb", 27017),
    "Neo4j": ("clisonix-neo4j", 7687),
    "MinIO": ("clisonix-minio", 9000),
    "Prometheus": ("clisonix-prometheus", 9090),
    "Grafana": ("clisonix-grafana", 3000),
    "Loki": ("clisonix-loki", 3100),
    "Ollama": ("clisonix-ollama", 11434),
}


def exact_binary_operation(query):
    match = re.fullmatch(r"\s*(\d{1,38})\s+(XOR|AND|OR|NAND|NOR)\s+(\d{1,38})\s*[?=]?\s*", query, re.I)
    if not match:
        return None
    a, op, b = int(match[1]), match[2].upper(), int(match[3])
    width = max(8, a.bit_length(), b.bit_length())
    mask = (1 << width) - 1
    results = {"XOR": a ^ b, "AND": a & b, "OR": a | b,
               "NAND": (~(a & b)) & mask, "NOR": (~(a | b)) & mask}
    return {"a": a, "b": b, "operation": op, "result": results[op], "width": width}


def catalog_evidence(query):
    path = Path(os.getenv("OCEAN_KNOWLEDGE_INDEX", "/app/knowledge/links_index.json"))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        links = payload.get("links")
        if not isinstance(links, list):
            return {"available": False, "reason": "catalog_has_no_records"}
        links = [row for row in links if isinstance(row, dict) and str(row.get("url", "")).startswith(("http://", "https://"))]
        tokens = set(re.findall(r"[\w-]{4,}", query.lower())) - {"clisonix", "source", "sources", "burime", "data", "open", "free", "links", "about", "what", "eshte"}
        ranked = []
        for row in links:
            text = " ".join(str(row.get(k, "")) for k in ("title", "description", "category")).lower()
            score = sum(token in text for token in tokens)
            if score:
                ranked.append((score, row))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return {"available": True, "records": len(links),
                "unique_urls": len({row["url"] for row in links}),
                "kind": "catalog_metadata_not_fetched_content",
                "matches": [{key: row.get(key) for key in ("title", "description", "url", "country", "category")}
                            for _, row in ranked[:5]]}
    except (OSError, ValueError, TypeError):
        return {"available": False, "reason": "catalog_unavailable"}


async def _probe_infra_tcp(name, host, port, timeout=2.0):
    """Plain TCP reachability check for non-HTTP infrastructure. Never
    claims application health — only "reachable" or "unreachable"."""
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return {"tool": name, "status": "reachable"}
    except Exception:
        return {"tool": name, "status": "unreachable"}


async def collect_runtime_evidence(query):
    lower = query.lower()
    platform_query = "clisonix" in lower or any(word in lower for word in ("platform", "laborator", "megalayer", "sistemi", "system"))
    selected = list(TOOLS) if platform_query else [name for name in TOOLS if any(part in lower for part in name.lower().split(" / "))]
    if any(word in lower for word in ("iot", "mesh", "lora", "pulse")):
        selected = list(dict.fromkeys([*selected, "GRAM / mesh", "Cycle", "Cycle Engine"]))

    async def probe(client, name):
        try:
            response = await client.get(TOOLS[name])
            body = response.json()
            record = {"tool": name, "http_status": response.status_code,
                      "status": str(body.get("status", "unknown"))}
            for key in ("languages", "total", "healthy", "analysis_ready", "fully_operational"):
                if isinstance(body.get(key), (int, bool)):
                    record[key] = body[key]
            if name == "CLX Hybrid / WWWMMM":
                record["dependencies"] = {key: value.get("status") for key, value in body.get("dependencies", {}).items() if isinstance(value, dict)}
            return record
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            return {"tool": name, "status": "unavailable"}

    async with httpx.AsyncClient(timeout=4.0, follow_redirects=False) as client:
        observations = await asyncio.gather(*(probe(client, name) for name in selected))
    result = {"observations": observations,
              "limits": "Health checks prove reachability only. No independent accuracy benchmark or physical IoT/LoRa device verification was performed."}
    if platform_query or any(word in lower for word in ("source", "burim", "nasa", "cern", "world bank", "links", "open data")):
        result["knowledge_catalog"] = catalog_evidence(query)
    if platform_query:
        result["infrastructure"] = await asyncio.gather(
            *(_probe_infra_tcp(name, host, port) for name, (host, port) in INFRA_TOOLS.items())
        )
    calculation = exact_binary_operation(query)
    if calculation:
        result["exact_binary_calculation"] = calculation
    return result

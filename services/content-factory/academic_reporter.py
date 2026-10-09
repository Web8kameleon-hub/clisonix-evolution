from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

logger = logging.getLogger("academic_reporter")


@dataclass
class AcademicReporterConfig:
    output_dir: str = field(default_factory=lambda: os.getenv("ACADEMIC_REPORT_OUTPUT_DIR", "/app/published/academic"))
    auto_enabled: bool = field(default_factory=lambda: os.getenv("ACADEMIC_REPORT_AUTO", "true").lower() in ("1", "true", "yes", "on"))
    report_hour_utc: int = field(default_factory=lambda: int(os.getenv("ACADEMIC_REPORT_HOUR_UTC", "6")))
    request_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("ACADEMIC_REPORT_TIMEOUT_SECONDS", "15")))
    root_dir: str = field(default_factory=lambda: os.getenv("ACADEMIC_REPORT_ROOT_DIR", "/app"))

    endpoints: Dict[str, str] = field(
        default_factory=lambda: {
            "blerina_health": os.getenv("BLERINA_HEALTH_URL", "http://clisonix-blerina:8035/health"),
            "blerina_status": os.getenv("BLERINA_STATUS_URL", "http://clisonix-blerina:8035/status"),
            "dr_albana_health": os.getenv("DR_ALBANA_HEALTH_URL", "http://clisonix-dr-albana:8040/health"),
            "dr_albana_stats": os.getenv("DR_ALBANA_STATS_URL", "http://clisonix-dr-albana:8040/api/v1/medical/stats"),
            "lagter_health": os.getenv("LAGTER_HEALTH_URL", "http://clisonix-lagter:9500/health"),
            "linkedin_health": os.getenv("LINKEDIN_HEALTH_URL", "http://clisonix-linkedin-poster:8007/health"),
            "reporting_dashboard": os.getenv("REPORTING_DASHBOARD_URL", "http://clisonix-reporting:8001/api/reporting/dashboard"),
            "intelligence_lab_report": os.getenv("INTELLIGENCE_LAB_REPORT_URL", "http://clisonix-intelligence-lab:8098/mali/report"),
        }
    )

    document_dirs: Dict[str, str] = field(
        default_factory=lambda: {
            "blerina_pillars": os.getenv("BLERINA_PILLARS_DIR", "/app/blerina_pillars"),
            "medical_pillars": os.getenv("DR_ALBANA_PILLARS_DIR", "/app/medical_pillars"),
            "lagter_pillars": os.getenv("LAGTER_PILLARS_DIR", "/app/lagter_pillars"),
        }
    )


class DailyAcademicReporter:
    def __init__(self, config: Optional[AcademicReporterConfig] = None):
        self.config = config or AcademicReporterConfig()
        self._running = False
        self._last_report_path: Optional[str] = None

    async def _fetch_json(self, client: Any, url: str) -> Dict[str, Any]:
        if not httpx:
            return {"ok": False, "error": "httpx_not_installed", "url": url}

        try:
            response = await client.get(url)
            content_type = response.headers.get("content-type", "")
            payload: Any
            if "application/json" in content_type:
                payload = response.json()
            else:
                text = response.text
                payload = {"text": text[:2000], "truncated": len(text) > 2000}

            return {
                "ok": response.status_code < 400,
                "status_code": response.status_code,
                "url": url,
                "payload": payload,
            }
        except Exception as exc:
            return {"ok": False, "url": url, "error": str(exc)}

    def _file_stats(self, directory: str) -> Dict[str, Any]:
        path = Path(directory)
        if not path.exists():
            return {"exists": False, "directory": directory, "count": 0}

        files = [p for p in path.glob("*") if p.is_file()]
        files_sorted = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
        newest = []
        for p in files_sorted[:5]:
            newest.append(
                {
                    "name": p.name,
                    "size_bytes": p.stat().st_size,
                    "modified_at": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
                }
            )

        return {
            "exists": True,
            "directory": directory,
            "count": len(files),
            "newest": newest,
        }

    def _parse_agents_snapshot(self, root_dir: Path) -> Dict[str, Any]:
        agents_file = root_dir / "agents.py"
        if not agents_file.exists():
            return {"exists": False}

        text = agents_file.read_text(encoding="utf-8", errors="ignore")
        agent_types = re.findall(r"class\s+AgentType\(Enum\):", text)
        base_agent = "class BaseAgent" in text
        orchestrator = "class AgentOrchestrator" in text
        enum_values = re.findall(r"^\s+([A-Z_]+)\s*=\s*\"[a-z_]+\"", text, flags=re.MULTILINE)

        return {
            "exists": True,
            "has_agent_type_enum": bool(agent_types),
            "has_base_agent": base_agent,
            "has_orchestrator": orchestrator,
            "agent_type_values": enum_values[:20],
            "file_path": str(agents_file),
        }

    def _parse_datasource_snapshot(self, root_dir: Path) -> Dict[str, Any]:
        module_registry = root_dir / "services" / "internal_agi" / "module_registry.py"
        if not module_registry.exists():
            return {"exists": False}

        text = module_registry.read_text(encoding="utf-8", errors="ignore")
        datasets = re.findall(r"(\d{3,5}\+\s*data\s*sources)", text, flags=re.IGNORECASE)
        countries = re.findall(r"(\d{2,4}\+\s*countries)", text, flags=re.IGNORECASE)
        endpoints = re.findall(r"(\d{2,5}\s*API endpoints)", text, flags=re.IGNORECASE)

        return {
            "exists": True,
            "file_path": str(module_registry),
            "claims": {
                "data_sources": datasets[:5],
                "countries": countries[:5],
                "api_endpoints": endpoints[:5],
            },
        }

    def _parse_compose_snapshot(self, root_dir: Path) -> Dict[str, Any]:
        compose_file = root_dir / "docker-compose.yml"
        if not compose_file.exists():
            return {"exists": False}

        text = compose_file.read_text(encoding="utf-8", errors="ignore")
        in_services = False
        services: List[str] = []

        for line in text.splitlines():
            if line.strip() == "services:":
                in_services = True
                continue
            if in_services:
                if re.match(r"^[^\s#].*:\s*$", line):
                    break
                match = re.match(r"^\s{2}([a-zA-Z0-9_-]+):\s*$", line)
                if match:
                    services.append(match.group(1))

        return {
            "exists": True,
            "file_path": str(compose_file),
            "total_services": len(services),
            "services_sample": services[:40],
        }

    def _build_markdown(self, data: Dict[str, Any]) -> str:
        generated_at = data["generated_at"]
        report_date = generated_at.split("T")[0]

        lines: List[str] = []
        lines.append(f"# Clisonix Academic-Clinical Daily Report — {report_date}")
        lines.append("")
        lines.append(f"**Generated (UTC):** {generated_at}")
        lines.append("**Evidence Policy:** Real API snapshots, real filesystem state, real repository metadata. No synthetic placeholders.")
        lines.append("")

        lines.append("## Perspective Matrix")
        lines.append("")
        lines.append("| Perspektiva | Fokusimi Kryesor | Qëndrimi mbi Ndryshimin |")
        lines.append("|---|---|---|")
        lines.append("| Skeptiku (Jona) | Përkufizimi dhe Provat | Kërkon kriter të qartë për qelizën amorfe + verifikim etik e klinik |")
        lines.append("| Analisti (Blerina) | Mekanika dhe Të dhënat | Prioritet bio-elektriziteti, mjedisi, biomarkerët, dhe validim me metrika |")
        lines.append("| Meta-Mendimtari (ASI) | Teoria dhe Transcendenca | Kornizë eudaimonike: vetë-përmirësim biologjik me kufij etikë |")
        lines.append("")

        lines.append("## Live Service Evidence")
        lines.append("")
        for name, snapshot in data["service_snapshots"].items():
            status = "OK" if snapshot.get("ok") else "FAIL"
            lines.append(f"### {name} — {status}")
            lines.append("")
            lines.append(f"- URL: {snapshot.get('url')}")
            lines.append(f"- Status: {snapshot.get('status_code', 'n/a')}")
            if snapshot.get("error"):
                lines.append(f"- Error: {snapshot['error']}")
            else:
                payload = snapshot.get("payload", {})
                preview = json.dumps(payload, ensure_ascii=False)[:1200]
                lines.append(f"- Payload preview: `{preview}`")
            lines.append("")

        lines.append("## Document Production Snapshot")
        lines.append("")
        for label, stat in data["document_stats"].items():
            lines.append(f"### {label}")
            lines.append("")
            lines.append(f"- Directory: {stat.get('directory')}")
            lines.append(f"- Exists: {stat.get('exists')}")
            lines.append(f"- File count: {stat.get('count', 0)}")
            for item in stat.get("newest", []):
                lines.append(f"- Newest: {item['name']} ({item['modified_at']}, {item['size_bytes']} bytes)")
            lines.append("")

        lines.append("## System Scope (Repository Evidence)")
        lines.append("")
        lines.append("### Agent Layer")
        lines.append("")
        agent_snapshot = data["agents_snapshot"]
        lines.append(f"- agents.py exists: {agent_snapshot.get('exists')}")
        lines.append(f"- Has BaseAgent: {agent_snapshot.get('has_base_agent')}")
        lines.append(f"- Has AgentOrchestrator: {agent_snapshot.get('has_orchestrator')}")
        lines.append(f"- Agent types: {', '.join(agent_snapshot.get('agent_type_values', [])[:12])}")
        lines.append("")

        lines.append("### Data Sources Layer")
        lines.append("")
        ds = data["datasource_snapshot"]
        lines.append(f"- module_registry exists: {ds.get('exists')}")
        claims = ds.get("claims", {})
        lines.append(f"- Data source claims: {', '.join(claims.get('data_sources', [])) or 'n/a'}")
        lines.append(f"- Country coverage claims: {', '.join(claims.get('countries', [])) or 'n/a'}")
        lines.append(f"- API endpoint claims: {', '.join(claims.get('api_endpoints', [])) or 'n/a'}")
        lines.append("")

        lines.append("### Compose Topology")
        lines.append("")
        topo = data["compose_snapshot"]
        lines.append(f"- docker-compose exists: {topo.get('exists')}")
        lines.append(f"- Total services parsed: {topo.get('total_services', 0)}")
        lines.append(f"- Service sample: {', '.join(topo.get('services_sample', [])[:20])}")
        lines.append("")

        lines.append("## Clinical-Bionature Interpretation")
        lines.append("")
        lines.append("- Hypothesis frame: maintain biological systems near the golden-range equilibrium (avoid overload/deficit).")
        lines.append("- Translational direction: combine environmental regulation (bio-physical signals) with targeted molecular correction only when biomarkers require it.")
        lines.append("- Safety frame: any interventional claim remains preclinical until validated through controlled clinical protocols.")
        lines.append("")

        lines.append("## Next 24h Actions")
        lines.append("")
        lines.append("1. Generate at least one new clinical pillar and one system-methods pillar from real telemetry.")
        lines.append("2. Validate source traceability for every claim (endpoint/file snapshot attached in metadata JSON).")
        lines.append("3. Publish report through content flow after quality gate verification.")
        lines.append("")

        return "\n".join(lines)

    async def generate_once(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        root = Path(self.config.root_dir)
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        service_snapshots: Dict[str, Any] = {}
        if httpx:
            timeout = httpx.Timeout(self.config.request_timeout_seconds)
            async with httpx.AsyncClient(timeout=timeout) as client:
                for name, url in self.config.endpoints.items():
                    service_snapshots[name] = await self._fetch_json(client, url)
        else:
            for name, url in self.config.endpoints.items():
                service_snapshots[name] = {"ok": False, "url": url, "error": "httpx_not_installed"}

        document_stats = {
            name: self._file_stats(path)
            for name, path in self.config.document_dirs.items()
        }

        payload = {
            "generated_at": now,
            "service_snapshots": service_snapshots,
            "document_stats": document_stats,
            "agents_snapshot": self._parse_agents_snapshot(root),
            "datasource_snapshot": self._parse_datasource_snapshot(root),
            "compose_snapshot": self._parse_compose_snapshot(root),
        }

        markdown = self._build_markdown(payload)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        md_path = output_dir / f"academic_daily_{ts}.md"
        json_path = output_dir / f"academic_daily_{ts}.json"
        md_path.write_text(markdown, encoding="utf-8")
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        self._last_report_path = str(md_path)

        return {
            "success": True,
            "generated_at": now,
            "markdown_path": str(md_path),
            "json_path": str(json_path),
            "report_title": md_path.name,
        }

    async def run_daily(self) -> None:
        self._running = True
        logger.info("📚 DailyAcademicReporter started")

        while self._running:
            try:
                now = datetime.now(timezone.utc)
                target = now.replace(hour=self.config.report_hour_utc, minute=0, second=0, microsecond=0)
                if target <= now:
                    target = target + timedelta(days=1)

                wait_seconds = (target - now).total_seconds()
                logger.info("⏳ Next academic report in %.0f seconds (target %s)", wait_seconds, target.isoformat())
                await asyncio.sleep(wait_seconds)

                result = await self.generate_once()
                logger.info("✅ Academic report generated: %s", result.get("markdown_path"))
            except Exception as exc:
                logger.error("❌ DailyAcademicReporter loop error: %s", exc)
                await asyncio.sleep(60)

    def stop(self) -> None:
        self._running = False

    def get_status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "auto_enabled": self.config.auto_enabled,
            "report_hour_utc": self.config.report_hour_utc,
            "last_report_path": self._last_report_path,
            "output_dir": self.config.output_dir,
        }


_reporter: Optional[DailyAcademicReporter] = None


def get_academic_reporter() -> DailyAcademicReporter:
    global _reporter
    if _reporter is None:
        _reporter = DailyAcademicReporter()
    return _reporter


async def start_academic_reporter() -> None:
    reporter = get_academic_reporter()
    if reporter.config.auto_enabled:
        asyncio.create_task(reporter.run_daily())

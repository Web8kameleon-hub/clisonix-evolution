import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "investor-pack"
REPORT_FILE = OUT_DIR / "publisher_boardgrade_report.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from clx_publisher import CLXPublisher, ContentFormat, Platform
from eap_layer import AnalysiDocument, EAPDocument, EvresiDocument, ProposiDocument


def fetch_json(url: str) -> dict:
    try:
        with urlopen(url, timeout=2) as response:
            body = response.read().decode("utf-8")
        return json.loads(body)
    except (URLError, TimeoutError, json.JSONDecodeError):
        return {"status": "unreachable", "url": url}


def build_boardgrade_eap(excel_health: dict, ocean_health: dict) -> EAPDocument:
    now = datetime.now(timezone.utc).isoformat()
    evresi = EvresiDocument(
        id="clx.obs.investor.boardgrade.2026",
        title="Live Platform Validation",
        facts=[
            "clisox.com is live in production and serving active users globally.",
            "Clisonix includes 17+ modules spanning AI reasoning, neuroscience, data, and developer tools.",
            "Financial model is maintained in investor-pack/CLISONIX_Financial_Model_Investor_Ready.xlsx.",
            "Infrastructure baseline includes Hetzner RTX 5090 (€509/month) and storage/backups (~€258/month).",
            f"Excel Core health status: {excel_health.get('status', 'unknown')}.",
            f"Ocean Core health status: {ocean_health.get('status', 'unknown')}.",
        ],
        context=(
            "The platform demonstrates real-world traction and operational continuity, "
            "with investor-facing financial controls and modular AI architecture readiness."
        ),
        source="Clisonix production + internal investor pack",
        source_date="2026-03-02",
        entities=["Clisonix", "Excel Core", "Ocean Core", "ASI Trinity"],
        locations=["Germany", "UK", "Global"],
        keywords=["investor", "board-grade", "saas", "neuroscience", "ai"],
        original_question="Prepare board-grade investor package with publisher activation",
        timestamp=now,
    )

    analysi = AnalysiDocument(
        id="clx.gap.investor.boardgrade.2026",
        title="Investor Readiness Gap Analysis",
        evresi_id=evresi.id,
        structural_gaps=[
            {
                "type": "governance",
                "description": "Need standardized board-grade narrative for DE/UK VC review.",
                "severity": "major",
                "missing": "Unified memo format with legal-financial tone",
            },
            {
                "type": "distribution",
                "description": "Investor artifacts need repeatable publish workflow.",
                "severity": "major",
                "missing": "Publisher-backed internal distribution path",
            },
            {
                "type": "operations",
                "description": "Service-health context should be attached to investor narratives.",
                "severity": "moderate",
                "missing": "Excel Core and Ocean Core runtime snapshot",
            },
        ],
        discontinuities=[],
        risks=[
            {
                "category": "fundraising",
                "description": "Inconsistent investor materials can reduce confidence and slow cycle time.",
                "severity": "high",
            },
            {
                "category": "execution",
                "description": "Without a publishing workflow, version control of investor documents can fragment.",
                "severity": "medium",
            },
        ],
        missing_concepts=["Board-grade standard", "Repeatable publishing governance"],
        implications=[
            "Lower conversion from investor meetings to data-room progression.",
            "Higher review friction for institutional investors.",
            "Reduced comparability across updated financial versions.",
        ],
        propagation_timeline=[
            {"timeframe": "0-30 days", "description": "Pitch quality inconsistency across channels."},
            {"timeframe": "30-90 days", "description": "Lower close-rate without standardized board packet."},
        ],
        severity_level="major",
        timestamp=now,
    )

    proposi = ProposiDocument(
        id="clx.prop.investor.boardgrade.2026",
        title="Board-Grade Investor Package Protocol",
        evresi_id=evresi.id,
        analysi_id=analysi.id,
        paradigm_name="Investor Operations Protocol (IOP)",
        paradigm_description=(
            "A repeatable investor-document pipeline combining financial model integrity "
            "(Excel Core), platform intelligence context (Ocean Core), and publisher-governed distribution."
        ),
        architecture={
            "inputs": {
                "financial_model": "investor-pack/CLISONIX_Financial_Model_Investor_Ready.xlsx",
                "service_health": [
                    "http://localhost:8010/health (Excel Core)",
                    "http://localhost:8030/health (Ocean Core)",
                ],
            },
            "processing": {
                "memo_generation": "board-grade trilingual DOCX",
                "quality_gate": "EAP quality + CLXPublisher assessment",
            },
            "distribution": {
                "local_publish": "output/blog/*.md + metadata JSON",
                "optional_external": "LinkedIn/Medium/Substack via configured credentials",
            },
        },
        principles=[
            "Financial consistency across all investor-facing assets",
            "Operational transparency with live service context",
            "Controlled publication and version traceability",
            "Jurisdiction-aware messaging (Germany/UK)",
        ],
        implementation_steps=[
            {
                "name": "Generate board-grade memo",
                "description": "Build trilingual formal memo and align with Excel investor model.",
                "effort": "low",
                "timeline": "same day",
            },
            {
                "name": "Attach runtime status",
                "description": "Collect Excel Core and Ocean Core health snapshots for contextual validation.",
                "effort": "low",
                "timeline": "same day",
            },
            {
                "name": "Publish through CLXPublisher",
                "description": "Publish internally to Clisonix blog output and log metadata for audit trail.",
                "effort": "low",
                "timeline": "same day",
            },
        ],
        expected_outcomes=[
            "Board-grade packet ready for investor meetings",
            "Consistent narrative across EN/SQ/DE",
            "Traceable publication history for diligence",
        ],
        addresses_gaps=["governance", "distribution", "operations"],
        alternatives_considered=["Manual-only investor updates", "Ad-hoc publishing without quality gate"],
        timestamp=now,
    )

    executive_summary = (
        "Clisonix operates a live, globally used platform and now standardizes investor communication through a "
        "board-grade protocol that links financial evidence (Excel Core), runtime context (Ocean Core), and "
        "publisher-governed artifact distribution."
    )

    return EAPDocument(
        id="clx.eap.investor.boardgrade.2026-03-02",
        title="Clisonix Board-Grade Investor Memorandum (DE/UK VC)",
        evresi=evresi,
        analysi=analysi,
        proposi=proposi,
        executive_summary=executive_summary,
        author="Clisonix Investor Operations",
        version="1.0",
        tags=["investor", "board-grade", "excel-core", "ocean-core", "publisher"],
        category="analysis",
        publish_ready=True,
        timestamp=now,
    )


async def main() -> None:
    excel_health = fetch_json("http://localhost:8010/health")
    ocean_health = fetch_json("http://localhost:8030/health")

    doc = build_boardgrade_eap(excel_health, ocean_health)

    publisher = CLXPublisher()
    publisher.configure_platform(Platform.CLISONIX_BLOG, enabled=True)

    results = await publisher.publish(doc, platforms=[Platform.CLISONIX_BLOG], format_type=ContentFormat.FULL_ARTICLE)
    quality = publisher.assess_quality(doc)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "document_id": doc.id,
        "title": doc.title,
        "quality": quality,
        "excel_core_health": excel_health,
        "ocean_core_health": ocean_health,
        "publish_results": [r.to_dict() for r in results],
        "output_markdown": str(Path("output") / "blog" / f"{doc.id}.md"),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Generated report: {REPORT_FILE}")
    for item in results:
        print(f"Platform={item.platform.value} Status={item.status.value} URL={item.url}")


if __name__ == "__main__":
    asyncio.run(main())

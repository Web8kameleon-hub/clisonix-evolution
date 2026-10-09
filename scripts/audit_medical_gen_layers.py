#!/usr/bin/env python3
"""
Audit strict medical GEN6-GEN9 publication readiness.

Usage:
  python scripts/audit_medical_gen_layers.py --error-rate 0.004 \
      --references-file refs.json

Exit codes:
  0 = PASS
  1 = FAIL
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

DOC_REQUIRED_SECTIONS: Dict[str, List[str]] = {
    "docs/medical-governance-packages/CORE_GOVERNANCE_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory visual assets",
    ],
    "docs/medical-governance-packages/LABORATORY_PROTOCOL_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory controls",
    ],
    "docs/medical-governance-packages/AUDIT_COMPLIANCE_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory controls",
    ],
    "docs/medical-governance-packages/ACADEMIC_PUBLICATION_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory controls",
    ],
    "docs/medical-governance-packages/VISUAL_COMMUNICATION_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory visual assets",
    ],
    "docs/medical-governance-packages/TRAINING_ONBOARDING_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory visual assets",
    ],
    "docs/medical-governance-packages/DATA_INTEGRITY_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory controls",
    ],
    "docs/medical-governance-packages/BIOMARKER_VALIDATION_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory controls",
    ],
    "docs/medical-governance-packages/COMPARATIVE_OUTCOMES_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory controls",
    ],
    "docs/medical-governance-packages/PUBLICATION_GOVERNANCE_PACKAGE.md": [
        "## Purpose",
        "## Required documents",
        "## Mandatory controls",
    ],
}

DEFAULT_SECTION_TEMPLATE = """## {section}

- TODO: Fill this section according to Clisonix-Clisonix protocol.
- Include measurable criteria, owner, review cadence, and evidence links.
"""


def _parse_error_rate(raw_value: str, unit: str) -> float:
    normalized = raw_value.strip().replace(",", ".")
    value = float(normalized)

    if unit == "percent":
        value = value / 100

    if value < 0:
        raise ValueError("error rate must be non-negative")

    return value


def _load_references(path: str | None) -> List[Dict[str, Any]]:
    if not path:
        return []

    refs_path = Path(path)
    if not refs_path.exists():
        raise FileNotFoundError(f"references file not found: {refs_path}")

    with refs_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("references"), list):
        return payload["references"]

    raise ValueError("references file must be a list or an object with 'references' list")


def _scan_document_for_sections(file_path: Path, required_sections: List[str]) -> Dict[str, Any]:
    if not file_path.exists():
        return {
            "file": str(file_path),
            "exists": False,
            "missing_sections": required_sections,
            "status": "FAIL",
        }

    content = file_path.read_text(encoding="utf-8")
    missing_sections = [section for section in required_sections if section not in content]

    return {
        "file": str(file_path),
        "exists": True,
        "missing_sections": missing_sections,
        "status": "PASS" if len(missing_sections) == 0 else "FAIL",
    }


def _rewrite_missing_sections(file_path: Path, missing_sections: List[str]) -> Tuple[bool, List[str]]:
    if not file_path.exists() or not missing_sections:
        return False, []

    content = file_path.read_text(encoding="utf-8")
    appended_sections: List[str] = []

    for section in missing_sections:
        section_title = section.replace("## ", "").strip()
        snippet = DEFAULT_SECTION_TEMPLATE.format(section=section_title)
        if snippet not in content:
            content = content.rstrip() + "\n\n" + snippet.strip() + "\n"
            appended_sections.append(section)

    if appended_sections:
        file_path.write_text(content, encoding="utf-8")
        return True, appended_sections

    return False, []


def run_clisonix_clisonix_doc_protocol(repo_root: Path, rewrite: bool) -> Dict[str, Any]:
    """Blerina-style intelligence pass: find documentation gaps and optionally rewrite."""
    results: List[Dict[str, Any]] = []
    rewritten_files: List[Dict[str, Any]] = []

    for rel_path, required_sections in DOC_REQUIRED_SECTIONS.items():
        abs_path = repo_root / rel_path
        scan_result = _scan_document_for_sections(abs_path, required_sections)

        if rewrite and scan_result["status"] == "FAIL" and scan_result.get("exists"):
            changed, appended = _rewrite_missing_sections(abs_path, scan_result.get("missing_sections", []))
            if changed:
                rewritten_files.append(
                    {
                        "file": rel_path,
                        "appended_sections": appended,
                    }
                )
                # rescan after rewrite
                scan_result = _scan_document_for_sections(abs_path, required_sections)

        scan_result["file"] = rel_path
        results.append(scan_result)

    failed_files = [r["file"] for r in results if r.get("status") != "PASS"]

    return {
        "protocol": "clisonix-clisonix-doc-gaps",
        "status": "PASS" if len(failed_files) == 0 else "FAIL",
        "files_checked": len(results),
        "failed_files": failed_files,
        "rewritten_files": rewritten_files,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Clisonix medical GEN6-GEN9 layers")
    parser.add_argument(
        "--error-rate",
        type=str,
        required=True,
        help="Measured error rate. Accepts dot/comma decimals (e.g., 0.004 or 0,004)",
    )
    parser.add_argument(
        "--error-unit",
        type=str,
        choices=["ratio", "percent"],
        default="ratio",
        help="Input unit for --error-rate: ratio (default) or percent",
    )
    parser.add_argument("--references-file", type=str, default=None, help="JSON file with references")
    parser.add_argument(
        "--scan-doc-gaps",
        action="store_true",
        help="Run Clisonix-Clisonix document gap protocol against governance package files",
    )
    parser.add_argument(
        "--rewrite-doc-gaps",
        action="store_true",
        help="Append template sections for missing governance package headings",
    )
    args = parser.parse_args()

    measured_error_rate = _parse_error_rate(args.error_rate, args.error_unit)

    repo_root = Path(__file__).resolve().parents[1]
    ocean_core = repo_root / "ocean-core"
    if str(ocean_core) not in sys.path:
        sys.path.insert(0, str(ocean_core))

    from laboratories import get_laboratory_network  # type: ignore[import-not-found]

    references = _load_references(args.references_file)
    network = get_laboratory_network()

    gate_result = network.validate_medical_publication_gate(
        measured_error_rate=measured_error_rate,
        references=references,
    )

    medical_layers = network.get_medical_gen_layers()
    quality_layers = network.get_quality_protocol_layers()
    quality_eval = network.evaluate_quality_layer(measured_error_rate)
    output = {
        "status": gate_result["status"],
        "gate": gate_result,
        "medical_layers": medical_layers,
        "quality_protocol_layers": quality_layers,
        "quality_layer_evaluation": quality_eval,
    }

    doc_protocol_result: Dict[str, Any] | None = None
    if args.scan_doc_gaps or args.rewrite_doc_gaps:
        doc_protocol_result = run_clisonix_clisonix_doc_protocol(
            repo_root=repo_root,
            rewrite=args.rewrite_doc_gaps,
        )
        output["clisonix_clisonix_document_protocol"] = doc_protocol_result

    overall_passed = gate_result["status"] == "PASS"
    if doc_protocol_result is not None:
        overall_passed = overall_passed and doc_protocol_result.get("status") == "PASS"
        output["status"] = "PASS" if overall_passed else "FAIL"

    print(json.dumps(output, indent=2, ensure_ascii=False))

    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

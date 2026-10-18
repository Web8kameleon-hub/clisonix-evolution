"""Regression guard for the DeepSeek-introduced fabrication bug.

On 2026-10-12, a direct server-side edit (branch `server-ocean-fix`,
commit f37db57f0, applied only to a root-level copy of ocean_core_full.py,
never merged to `main`) replaced the honest HTTP 503 refusal in the live
research evidence gate with an "[UNVERIFIED — no live source found...]"
disclaimer instruction that tells the model to "answer using internal
knowledge" anyway. That reintroduced exactly the fabrication problem
NO_FAKE_DATA_POLICY.md forbids (fabricated VC valuations, hospital counts,
population figures, etc. with no retrieved evidence).

This test statically inspects the `_needs_live_research_evidence` gate
inside `process_query_full` and asserts the "no evidence retrieved" and
"required source missing" branches both refuse via HTTPException(503)
rather than falling through to free generation.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "ocean-core" / "ocean_core_full.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")


def _live_research_evidence_block() -> str:
    tree = ast.parse(SOURCE)
    func = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "process_query_full"
    )
    for node in ast.walk(func):
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Call)
            and isinstance(node.test.func, ast.Name)
            and node.test.func.id == "_needs_live_research_evidence"
        ):
            segment = ast.get_source_segment(SOURCE, node)
            if segment:
                return segment
    raise AssertionError(
        "_needs_live_research_evidence gate not found inside process_query_full; "
        "update this test if the gate was intentionally restructured."
    )


class LiveResearchHonestyRegressionTests(unittest.TestCase):
    def test_missing_evidence_refuses_instead_of_fabricating(self) -> None:
        block = _live_research_evidence_block()
        self.assertIn("raise HTTPException(", block)
        self.assertIn("status_code=503", block)
        # Exact DeepSeek regression this guards against: swapping the
        # honest refusal for an instruction telling the model to answer
        # anyway from "internal knowledge" behind a disclaimer prefix.
        self.assertNotIn("UNVERIFIED", block)
        self.assertNotIn("internal knowledge", block.lower())
        self.assertNotIn("answer using internal knowledge", block.lower())

    def test_missing_required_source_also_refuses(self) -> None:
        block = _live_research_evidence_block()
        self.assertIn("missing_sources", block)
        # Both the "no evidence at all" and "a specifically required source
        # (e.g. Eurostat, PubMed) came back empty" paths must refuse via
        # 503 - never substitute another source or answer uncited.
        self.assertEqual(block.count("raise HTTPException("), 2)


if __name__ == "__main__":
    unittest.main()

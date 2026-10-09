import json
import unittest
from unittest.mock import patch

from fastapi.responses import JSONResponse

from apps.api import main as api_main


class OceanPipelineGuardrailsTests(unittest.TestCase):
    def test_build_citation_links_excludes_service_health_urls(self):
        provenance = [
            {"source": "dr_albana", "type": "service_health", "url": "http://localhost:8040/health"},
            {"source": "INSTAT", "type": "internal_registry", "url": "https://www.instat.gov.al/api/cpi.json", "verified_by": "jona"},
        ]

        citations = api_main.build_citation_links(provenance)

        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["url"], "https://www.instat.gov.al/api/cpi.json")
        self.assertEqual(citations[0]["type"], "internal_registry")

    def test_ocean_pipeline_fails_when_link_is_required_but_not_in_response(self):
        async def fake_query_ocean_core(query: str, curiosity_level: str = "curious"):
            return {
                "response": "CPI for the latest month is 103.2.",
                "persona_used": "Ocean-Core",
                "confidence": 0.92,
                "sources_consulted": ["INSTAT CPI Dataset"],
            }

        async def fake_get_asi_trinity_metrics():
            return {"overall_status": "operational"}

        async def fake_get_jona_filtered_sources(limit: int = 100):
            return {
                "status": "ok",
                "count": 1,
                "filter": "jona_internal_registry",
                "sources": [
                    {
                        "id": "instat-cpi",
                        "name": "INSTAT CPI",
                        "endpoint": "https://www.instat.gov.al/api/cpi.json",
                        "type": "dataset",
                        "status": "active",
                        "verified_by": "jona",
                    }
                ],
            }

        async def fake_fetch_service_health(base_url: str, service_name: str):
            return {"service": service_name, "url": f"{base_url}/health", "status": "healthy", "http_status": 200}

        request = api_main.OceanPipelineRequest(
            query="Më jep CPI të Shqipërisë nga INSTAT për muajin e fundit, me linkun e dataset-it JSON",
            curiosity_level="curious",
            require_real_data=True,
            include_sources=True,
            allow_fallback=False,
            min_citations=1,
        )

        with patch.object(api_main, "query_ocean_core", fake_query_ocean_core), patch.object(
            api_main, "get_asi_trinity_metrics", fake_get_asi_trinity_metrics
        ), patch.object(api_main, "get_jona_filtered_sources", fake_get_jona_filtered_sources), patch.object(
            api_main, "fetch_service_health", fake_fetch_service_health
        ):
            result = api_main.asyncio.run(api_main.ocean_pipeline(request))

        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 412)
        payload = json.loads(result.body)
        self.assertEqual(payload["status"], "HARD_FAIL")
        self.assertIn("response_missing_inline_source_url", payload["errors"])

    def test_ocean_pipeline_passes_when_response_contains_citation_url(self):
        citation_url = "https://www.instat.gov.al/api/cpi.json"

        async def fake_query_ocean_core(query: str, curiosity_level: str = "curious"):
            return {
                "response": f"CPI latest month: 103.2. Source: {citation_url}",
                "persona_used": "Ocean-Core",
                "confidence": 0.94,
                "sources_consulted": [
                    {
                        "name": "INSTAT CPI",
                        "url": citation_url,
                        "verified_by": "jona",
                    }
                ],
            }

        async def fake_get_asi_trinity_metrics():
            return {"overall_status": "operational"}

        async def fake_get_jona_filtered_sources(limit: int = 100):
            return {"status": "ok", "count": 0, "filter": "jona_internal_registry", "sources": []}

        async def fake_fetch_service_health(base_url: str, service_name: str):
            return {"service": service_name, "url": f"{base_url}/health", "status": "healthy", "http_status": 200}

        request = api_main.OceanPipelineRequest(
            query="Më jep CPI të Shqipërisë nga INSTAT për muajin e fundit, me linkun e dataset-it JSON",
            curiosity_level="curious",
            require_real_data=True,
            include_sources=True,
            allow_fallback=False,
            min_citations=1,
        )

        with patch.object(api_main, "query_ocean_core", fake_query_ocean_core), patch.object(
            api_main, "get_asi_trinity_metrics", fake_get_asi_trinity_metrics
        ), patch.object(api_main, "get_jona_filtered_sources", fake_get_jona_filtered_sources), patch.object(
            api_main, "fetch_service_health", fake_fetch_service_health
        ):
            result = api_main.asyncio.run(api_main.ocean_pipeline(request))

        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["result"]["metadata"]["citations_count"], 1)
        self.assertTrue(any(c.get("url") == citation_url for c in result["result"]["provenance"]["citations"]))


if __name__ == "__main__":
    unittest.main()

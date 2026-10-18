import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


nin_engine = load_module("nin_engine_under_test", ROOT / "ocean-core" / "nin_engine.py")
location_labs = load_module(
    "location_labs_under_test",
    ROOT / "apps" / "api" / "location_labs_engine.py",
)
klajdi = load_module(
    "klajdi_under_test",
    ROOT / "services" / "intelligence-lab" / "klajdi_lab.py",
)
mali = load_module(
    "mali_under_test",
    ROOT / "services" / "intelligence-lab" / "mali_core.py",
)


class FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def json(self):
        return {"status": "healthy", "upstreams_live": 1}


class FakeAsyncClient:
    response = FakeResponse()
    requested_url = None

    def __init__(self, **_kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def get(self, url):
        type(self).requested_url = url
        return type(self).response


class SelectiveAsyncClient(FakeAsyncClient):
    async def get(self, url):
        return FakeResponse(status_code=503 if "tirana" in url else 200)


class NinEngineTests(unittest.TestCase):
    def test_get_nin_engine_returns_singleton(self):
        self.assertIs(nin_engine.get_nin_engine(), nin_engine.get_nin_engine())

    def test_analysis_updates_shared_statistics(self):
        engine = nin_engine.get_nin_engine()
        before = engine.get_statistics()["total_analyses"]
        intent = engine.analyze("Please analyze this laboratory.")

        self.assertEqual(intent.type.value, "request")
        self.assertEqual(engine.get_statistics()["total_analyses"], before + 1)


class LocationLabIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_process_uses_real_gateway_without_synthetic_metrics(self):
        config = location_labs.LOCATION_LABS_CONFIG[location_labs.LocationRegion.TIRANA]
        processor = location_labs.LocationLabProcessor(config)
        FakeAsyncClient.response = FakeResponse()

        with patch.object(location_labs.httpx, "AsyncClient", FakeAsyncClient):
            result = await processor.process()

        self.assertEqual(
            FakeAsyncClient.requested_url,
            "http://lab-tirana:9100/health",
        )
        self.assertIsNone(result.sample_count)
        self.assertIsNone(result.artifacts_generated)
        self.assertIsNone(result.data_quality_score)
        self.assertEqual(result.metadata["upstream_health"]["status"], "healthy")

    async def test_process_fails_when_gateway_is_unavailable(self):
        config = location_labs.LOCATION_LABS_CONFIG[location_labs.LocationRegion.TIRANA]
        processor = location_labs.LocationLabProcessor(config)
        FakeAsyncClient.response = FakeResponse(status_code=503)

        with patch.object(location_labs.httpx, "AsyncClient", FakeAsyncClient):
            with self.assertRaisesRegex(RuntimeError, "HTTP 503"):
                await processor.process()

    async def test_process_all_preserves_healthy_and_unavailable_labs(self):
        engine = location_labs.LocationLabsEngine()
        await engine.initialize()
        engine.labs = {
            location_labs.LocationRegion.TIRANA: engine.labs[location_labs.LocationRegion.TIRANA],
            location_labs.LocationRegion.ELBASAN: engine.labs[location_labs.LocationRegion.ELBASAN],
        }

        with patch.object(location_labs.httpx, "AsyncClient", SelectiveAsyncClient):
            observations = await engine.process_all_labs()

        self.assertEqual([item["status"] for item in observations], ["unavailable", "healthy"])


class IntelligenceLabIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_klajdi_reports_unavailable_without_simulated_data(self):
        FakeAsyncClient.response = FakeResponse(status_code=503)
        labor = klajdi.KnostLabor()

        with patch.object(klajdi.httpx, "AsyncClient", FakeAsyncClient):
            observation = await labor._observe_http("http://liam:8062/api/v1/status")

        self.assertEqual(observation["status"], "unavailable")
        self.assertEqual(observation["status_code"], 503)
        self.assertNotIn("simulated", observation)

    async def test_mali_tables_do_not_fabricate_unavailable_metrics(self):
        class UnavailableIntake:
            async def intake_from_liam(self):
                return {"status": "error", "error": "LIAM unavailable"}

            async def intake_from_alda(self):
                return {"status": "error", "error": "ALDA unavailable"}

        tabulator = mali.ExcelTabulator(UnavailableIntake())
        liam_table = await tabulator.generate_liam_matrix_table()
        alda_table = await tabulator.generate_alda_labor_table()

        self.assertIsNone(liam_table["raw_data"])
        self.assertIsNone(liam_table["markdown"])
        self.assertIsNone(alda_table["raw_data"])
        self.assertIsNone(alda_table["markdown"])


if __name__ == "__main__":
    unittest.main()

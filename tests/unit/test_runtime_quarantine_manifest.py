"""Container presence and health must never become execution evidence."""
import importlib.util
import sys
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "runtime_audit", Path(__file__).resolve().parents[2] / "scripts/audit_runtime_capabilities.py"
)
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)


class QuarantineManifestTests(unittest.TestCase):
    def manifest(self, containers):
        return audit.quarantine_manifest(
            {"services": [{"service": "ocean", "runtime_owner": "production"}]},
            {"checked_at": "2026-09-29T00:00:00+00:00", "containers": containers},
        )

    def test_healthy_is_not_real(self):
        result = self.manifest([{"service": "ocean", "runtime_owner": "production",
                                 "container": "ocean-1", "state": "running", "health": "healthy"}])
        row = result["services"][0]
        self.assertEqual(row["classification"], "UNKNOWN")
        self.assertEqual(row["production_access"], "DENY")
        self.assertFalse(result["routing_enforced"])

    def test_other_project_cannot_supply_presence(self):
        result = self.manifest([{"service": "ocean", "runtime_owner": "development",
                                 "container": "dev-ocean", "state": "running"}])
        self.assertEqual(result["services"][0]["observed_instances"], [])
        self.assertEqual(len(result["services"]), 2)

    def test_absence_is_not_proof_of_dead_implementation(self):
        result = self.manifest([])
        self.assertEqual(result["summary"]["DEAD"], 0)
        self.assertEqual(result["summary"]["UNKNOWN"], 1)


if __name__ == "__main__":
    unittest.main()

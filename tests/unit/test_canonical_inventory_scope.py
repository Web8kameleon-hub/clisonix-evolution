import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "canonical_inventory", Path(__file__).resolve().parents[2] / "scripts/docs/generate_canonical_manifest.py"
)
inventory = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = inventory
spec.loader.exec_module(inventory)


class InventoryScopeTests(unittest.TestCase):
    def test_compose_hosting_and_yaml_are_included(self):
        paths = (Path("compose-hosting.yml"), Path("docker-compose.yaml"), Path("notes.txt"))
        with patch.object(inventory, "tracked_files", return_value=paths):
            self.assertEqual(inventory.list_compose_files(), list(paths[:2]))

    def test_networks_and_volumes_are_not_services(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "compose-hosting.yml"
            path.write_text("services:\n  ocean:\n    image: ocean\nvolumes:\n  data:\nnetworks:\n  fabric:\n")
            with patch.object(inventory, "ROOT", root):
                self.assertEqual([s.service for s in inventory.parse_compose_services(path)], ["ocean"])


if __name__ == "__main__":
    unittest.main()

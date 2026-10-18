from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class ModuleCapabilityManifest:
    module_id: str
    declared_capabilities: List[str]
    supports_simulation: bool = False
    supports_live_execution: bool = False
    requires: List[str] = field(default_factory=list)
    runtime_state: str = "offline"
    active_connector: Optional[str] = None
    active_capabilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "declared_capabilities": list(self.declared_capabilities),
            "active_capabilities": list(self.active_capabilities or self.declared_capabilities),
            "supports_simulation": self.supports_simulation,
            "supports_live_execution": self.supports_live_execution,
            "requires": list(self.requires),
            "active_connector": self.active_connector,
            "runtime_state": self.runtime_state,
        }


class OceanCapabilityRegistry:
    """Single source of truth for module capabilities and runtime constraints."""

    def __init__(self) -> None:
        self._manifests: Dict[str, ModuleCapabilityManifest] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        defaults = [
            ModuleCapabilityManifest(
                module_id="nanogrid-zeiss",
                declared_capabilities=["inspect_status", "prepare_workflow"],
                active_capabilities=["inspect_status", "prepare_workflow"],
                supports_simulation=True,
                supports_live_execution=False,
                requires=["zeiss_connector", "authenticated_operator"],
                runtime_state="offline",
                active_connector=None,
            ),
            ModuleCapabilityManifest(
                module_id="curiosity-ocean",
                declared_capabilities=["inspect_status", "prepare_workflow"],
                active_capabilities=["inspect_status"],
                supports_simulation=True,
                supports_live_execution=False,
                requires=["authenticated_operator"],
                runtime_state="offline",
                active_connector=None,
            ),
        ]

        for manifest in defaults:
            self.register(manifest)

    def register(self, manifest: ModuleCapabilityManifest) -> None:
        self._manifests[manifest.module_id] = manifest

    def get(self, module_id: str) -> Optional[ModuleCapabilityManifest]:
        return self._manifests.get(module_id)

    def list_manifests(self) -> List[Dict[str, Any]]:
        return [manifest.to_dict() for manifest in self._manifests.values()]

    def is_capability_supported(self, module_id: str, capability: str) -> bool:
        manifest = self.get(module_id)
        if not manifest:
            return False
        return capability in set(manifest.declared_capabilities)

    def missing_requirements(self, module_id: str, provided_requirements: Optional[Set[str]] = None) -> List[str]:
        manifest = self.get(module_id)
        if not manifest:
            return []
        provided = provided_requirements or set()
        return sorted(req for req in manifest.requires if req not in provided)


_registry: Optional[OceanCapabilityRegistry] = None


def get_ocean_capability_registry() -> OceanCapabilityRegistry:
    global _registry
    if _registry is None:
        _registry = OceanCapabilityRegistry()
    return _registry

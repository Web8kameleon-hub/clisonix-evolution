import time
from typing import Any, Dict, List

from .base import BaseProvider, ProviderRequest, ProviderResponse, ProviderStatus, ProviderType
from ..wwwmmm.scanner import get_scanner
from ..wwwmmm.stigma import get_stigma
from ..wwwmmm.resonance import get_resonance
from ..wwwmmm.zero_noise import get_zero_noise
from ..wwwmmm.printer import get_printer, PrintFormat
from ..wwwmmm.nanodb import get_nanodb
from ..wwwmmm.memory import get_memory, get_film_memory
from ..wwwmmm.zing import get_zing
from ..wwwmmm.lighting import get_lighting


class WWWMMMProvider(BaseProvider):
    """Deterministic WWWMMM provider using local engines only."""

    def __init__(self):
        self._scanner = get_scanner()
        self._stigma = get_stigma()
        self._resonance = get_resonance()
        self._zero_noise = get_zero_noise()
        self._printer = get_printer()
        self._nodedb = get_nanodb()
        self._memory = get_memory()
        self._film_memory = get_film_memory()
        self._zing = get_zing()
        self._lighting = get_lighting()

    @property
    def name(self) -> str:
        return "wwwmmm"

    @property
    def type(self) -> ProviderType:
        return ProviderType.WWWMMM

    async def health_check(self) -> ProviderStatus:
        return ProviderStatus.AVAILABLE

    def get_models(self) -> List[str]:
        return ["wwwmmm-lightning", "wwwmmm-normal", "wwwmmm-conservative"]

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "streaming": True,
            "raw_sse": True,
            "deterministic": True,
            "no_json_rendering": True,
        }

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        start = time.perf_counter()
        prompt = (request.prompt or "").strip()
        if not prompt:
            return ProviderResponse(
                content="",
                model="wwwmmm-lightning",
                provider=self.name,
                status=ProviderStatus.UNAVAILABLE,
                error="empty_prompt",
                latency_ms=round((time.perf_counter() - start) * 1000.0, 3),
            )

        clean_prompt, noise = self._zero_noise.denoise(prompt)
        scan = self._scanner.scan(clean_prompt)
        stigma = self._stigma.analyze({
            "nanovolt_level": scan.nanovolt_level,
            "confidence": scan.confidence,
        })
        resonance = self._resonance.resonate({
            "nanovolt_level": scan.nanovolt_level,
            "tokens": scan.tokens,
            "confidence": scan.confidence,
        })
        lighting = self._lighting.choose(scan.nanovolt_level)
        self._zing.react("route_wwwmmm")

        request_node = self._nodedb.create_node(
            "request",
            {
                "fingerprint": scan.fingerprint,
                "tokens": scan.tokens,
                "nanovolt_level": scan.nanovolt_level,
            },
        )

        response_text = (
            f"WWWMMM[{stigma['profile']}] signal={scan.fingerprint} "
            f"nv={scan.nanovolt_level} tide={resonance.tide_level:.3f} "
            f"res={resonance.resonance_score:.3f} hz={resonance.frequency_hz:.2f} "
            f"lighting={lighting.name}"
        )

        response_node = self._nodedb.create_node("response", {"content": response_text})
        self._nodedb.connect(request_node, response_node)

        pressure = float(stigma.get("speed", 0.5))
        self._memory.store({"prompt": clean_prompt, "response": response_text}, pressure=pressure)
        film_id = f"film_{request_node}"
        self._film_memory.write_film(film_id, {"response": response_text}, stigma=float(stigma.get("depth", 0.5)))

        latency_ms = round((time.perf_counter() - start) * 1000.0, 3)
        return ProviderResponse(
            content=response_text,
            model=f"wwwmmm-{stigma['profile']}",
            provider=self.name,
            status=ProviderStatus.AVAILABLE,
            latency_ms=latency_ms,
            metadata={
                "fingerprint": scan.fingerprint,
                "nanovolt_level": scan.nanovolt_level,
                "noise_ratio": noise.noise_ratio,
                "stigma": stigma,
                "resonance": {
                    "tide_level": resonance.tide_level,
                    "mesh_energy": resonance.mesh_energy,
                    "frequency_hz": resonance.frequency_hz,
                    "score": resonance.resonance_score,
                },
                "node_request": request_node,
                "node_response": response_node,
                "film_id": film_id,
            },
        )

    async def stream(self, request: ProviderRequest):
        base = await self.generate(request)
        if base.status != ProviderStatus.AVAILABLE:
            yield base
            return

        payload = {"response": base.content}
        for event in self._printer.render_sse_events(payload, chunk_size=24):
            yield ProviderResponse(
                content=event,
                model=base.model,
                provider=self.name,
                status=ProviderStatus.AVAILABLE,
                latency_ms=base.latency_ms,
                metadata=base.metadata,
            )

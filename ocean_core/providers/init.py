import logging
from .registry import get_provider_registry
from .ollama_provider import OllamaProvider
from .lightning_provider import LightningProvider
from .wwwmmm_provider import WWWMMMProvider

logger = logging.getLogger("provider-init")

def initialize_all_providers():
    registry = get_provider_registry()

    try:
        wwwmmm = WWWMMMProvider()
        registry.register(wwwmmm, default=True)
        logger.info("✅ WWWMMM Provider registered (default)")
    except Exception as e:
        logger.error(f"❌ Failed to register WWWMMM: {e}")

    try:
        ollama = OllamaProvider()
        registry.register(ollama)
        logger.info("✅ Ollama Provider registered (fallback)")
    except Exception as e:
        logger.error(f"❌ Failed to register Ollama: {e}")

    try:
        lightning = LightningProvider()
        registry.register(lightning)
        logger.info("✅ Lightning Provider registered")
    except Exception as e:
        logger.error(f"❌ Failed to register Lightning: {e}")

    return registry

async def health_check_all():
    return await get_provider_registry().health_check_all()

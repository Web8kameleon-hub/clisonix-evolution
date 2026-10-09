"""
Runtime Initialization - Inicializon runtime-in
"""

import logging
from ocean_core.providers.init import initialize_all_providers

logger = logging.getLogger("runtime-init")

_runtime = None

def initialize_runtime():
    global _runtime
    if _runtime is not None:
        return _runtime

    providers = initialize_all_providers()
    logger.info("✅ Runtime initialized")
    
    _runtime = {
        "providers": providers,
        "initialized": True,
    }
    return _runtime

def get_runtime():
    return initialize_runtime()

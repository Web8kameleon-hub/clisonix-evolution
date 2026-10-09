#!/usr/bin/env python3
"""
OCEAN CORE FULL v5.0.0 - Entry Point
Complete production brain with all advanced systems
"""
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OceanCoreFull-EntryPoint")

# Ensure we're in the right directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        logger.info("🌊 Starting Ocean Core Full v5.0.0...")
        
        # Import and run the main app
        import uvicorn

        from ocean_core_full import app
        
        port = int(os.getenv("OCEAN_PORT", "8030"))
        host = os.getenv("OCEAN_HOST", "0.0.0.0")
        
        logger.info(f"🚀 Starting server on {host}:{port}")
        logger.info("📚 Features:")
        logger.info("  ✅ MegaLayerEngine - 14 billion combinations")
        logger.info("  ✅ ResponseOrchestratorV5 - Production Brain")
        logger.info("  ✅ TrinityDebate - 5 persona AI debate")
        logger.info("  ✅ Zürich Engine - 9-stage deterministic reasoning")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Failed to start Ocean Core Full: {e}", exc_info=True)
        sys.exit(1)

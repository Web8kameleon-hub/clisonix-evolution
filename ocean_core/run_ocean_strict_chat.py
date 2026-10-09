#!/usr/bin/env python3
"""
Ocean Strict Chat v1.0 - Entry Point
Admin strict mode with rule enforcement
Port: 8035
"""
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OceanStrictChat-EntryPoint")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        logger.info("🌊 Starting Ocean Strict Chat v1.0...")
        
        import uvicorn

        from ocean_strict_chat import app
        
        port = int(os.getenv("OCEAN_PORT", "8035"))
        host = os.getenv("OCEAN_HOST", "0.0.0.0")
        
        logger.info(f"🚀 Starting server on {host}:{port}")
        logger.info("📚 Features:")
        logger.info("  🔒 Strict Mode - Rule enforcement without deviation")
        logger.info("  👨‍💼 Admin Chat - Administrative interface")
        logger.info("  ⚡ Performance - Optimized for strict operations")
        
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"❌ Failed to start Ocean Strict Chat: {e}", exc_info=True)
        sys.exit(1)

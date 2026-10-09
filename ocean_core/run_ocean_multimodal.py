#!/usr/bin/env python3
"""
Ocean Multimodal Engine v1.0 - Entry Point
Vision, Audio, Document, and Multimodal Analysis
"""
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OceanMultimodal-EntryPoint")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        logger.info("🌊 Starting Ocean Multimodal Engine v1.0...")
        
        import uvicorn

        from ocean_multimodal import app
        
        port = int(os.getenv("OCEAN_PORT", "8033"))
        host = os.getenv("OCEAN_HOST", "0.0.0.0")
        
        logger.info(f"🚀 Starting server on {host}:{port}")
        logger.info("📚 Features:")
        logger.info("  👁️  Vision - Image analysis, object detection, OCR")
        logger.info("  🎙️  Audio - Speech-to-text, transcription")
        logger.info("  📄 Document - Text extraction, document reasoning")
        logger.info("  🧠 Reasoning - LLM-powered inference")
        
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"❌ Failed to start Ocean Multimodal: {e}", exc_info=True)
        sys.exit(1)

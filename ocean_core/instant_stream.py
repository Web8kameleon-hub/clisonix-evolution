#!/usr/bin/env python3
"""
⚡ INSTANT STREAM - Zero-Overhead Streaming
==========================================
Problemi: Çdo request harxhon kohë në:
- Language detection (HTTP call)
- Knowledge seeds lookup
- System prompt building

Zgjidhja:
- Pre-built prompts në memorie
- Zero pre-processing
- Direct stream to Ollama
- Keep-alive connection

TTFT Target: <2 sekonda

Author: Clisonix Team
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
from typing import AsyncGenerator, Optional

import httpx

logger = logging.getLogger("InstantStream")

# ═══════════════════════════════════════════════════════════════════
# CONFIG - Pre-built dhe cached
# ═══════════════════════════════════════════════════════════════════

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://clisonix-ollama:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")

# Pre-built system prompts - NUK rikompozohen çdo herë!
PROMPTS = {
    "default": "You are Curiosity Ocean, a helpful AI. Respond in the user's language. Be concise and start immediately.",

    "sq": "Ti je Curiosity Ocean, AI i Clisonix. Përgjigju në shqip. Fillo menjëherë pa hyrje.",

    "en": "You are Curiosity Ocean, AI assistant. Be helpful and concise. Start responding immediately.",

    "de": "Du bist Curiosity Ocean, KI-Assistent. Antworte präzise auf Deutsch. Beginne sofort.",

    "fast": "AI assistant. Answer directly.",  # Minimal prompt për TTFT minimale
}

# Pre-built options - NUK rikompozohen!
FAST_OPTIONS = {
    "temperature": 0.7,
    "num_ctx": 2048,       # Minimal context për TTFT të shpejtë
    "top_k": 40,
    "num_predict": -1,
}

NORMAL_OPTIONS = {
    "temperature": 0.7,
    "num_ctx": 4096,
    "top_p": 0.9,
    "num_predict": -1,
}

# ═══════════════════════════════════════════════════════════════════
# PERSISTENT HTTP CLIENT - Keep-alive connection
# ═══════════════════════════════════════════════════════════════════

# Global client me keep-alive - nuk hapet connection çdo herë
_client: Optional[httpx.AsyncClient] = None

async def get_client() -> httpx.AsyncClient:
    """Get or create persistent HTTP client."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(180.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        logger.info("🔌 Created persistent HTTP client")
    return _client


async def close_client():
    """Close client on shutdown."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        logger.info("🔌 Closed HTTP client")


# ═══════════════════════════════════════════════════════════════════
# INSTANT LANGUAGE DETECTION - No HTTP calls!
# ═══════════════════════════════════════════════════════════════════

# Albanian markers - instant detection
SQ_MARKERS = {"ë", "ç", "një", "për", "që", "është", "kam", "vlla", "shqip", "mirë", "faleminderit"}
DE_MARKERS = {"ü", "ö", "ä", "ß", "ist", "nicht", "haben", "werden", "können"}
# Add more as needed

def detect_language_instant(text: str) -> str:
    """
    Instant language detection - NO HTTP calls!
    Returns language code in <1ms.
    """
    text_lower = text.lower()

    # Check Albanian
    if any(m in text_lower for m in SQ_MARKERS):
        return "sq"

    # Check German
    if any(m in text_lower for m in DE_MARKERS):
        return "de"

    # Default to English
    return "en"


# ═══════════════════════════════════════════════════════════════════
# ZERO-OVERHEAD STREAMING
# ═══════════════════════════════════════════════════════════════════

async def instant_stream(
    prompt: str,
    mode: str = "normal",  # "fast", "normal", "full"
    model: str = None
) -> AsyncGenerator[str, None]:
    """
    Zero-overhead streaming.

    Args:
        prompt: User message
        mode: "fast" (2s TTFT), "normal" (better quality)
        model: Override model

    Yields:
        Response tokens as they arrive
    """
    # Instant language detection
    lang = detect_language_instant(prompt)

    # Get pre-built prompt (no generation!)
    system_prompt = PROMPTS.get(lang, PROMPTS["default"])
    if mode == "fast":
        system_prompt = PROMPTS["fast"]

    # Get pre-built options (no dict building!)
    options = FAST_OPTIONS if mode == "fast" else NORMAL_OPTIONS

    # Build minimal message structure
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    # Get persistent client
    client = await get_client()

    try:
        async with client.stream(
            "POST",
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": model or MODEL,
                "messages": messages,
                "stream": True,
                "options": options
            }
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            content = data["message"]["content"]
                            if content:
                                yield content
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        logger.error(f"Stream error: {e}")
        yield f"\n[Error: {str(e)}]"


# ═══════════════════════════════════════════════════════════════════
# MEGA LAYER INSTANT - Pre-computed context
# ═══════════════════════════════════════════════════════════════════

# Pre-computed mega layer context për topics të zakonshme
MEGA_LAYER_CACHE = {
    "consciousness": "🧠 Neural correlates, phenomenology, hard problem, IIT theory",
    "ai": "🤖 Machine learning, neural networks, transformers, AGI research",
    "physics": "⚛️ Quantum mechanics, relativity, thermodynamics, particle physics",
    "philosophy": "💭 Epistemology, ontology, ethics, metaphysics",
    "clisonix": "🌊 Industrial AI platform, EEG processing, ALBI, ALBA, JONA engines",
}

def get_mega_context_instant(prompt: str) -> Optional[str]:
    """Get pre-computed mega layer context instantly."""
    prompt_lower = prompt.lower()

    for topic, context in MEGA_LAYER_CACHE.items():
        if topic in prompt_lower:
            return context

    return None


async def instant_stream_with_context(
    prompt: str,
    mode: str = "normal"
) -> AsyncGenerator[str, None]:
    """
    Streaming with instant mega layer context.
    Still zero HTTP overhead for pre-processing.
    """
    # Get instant context
    mega_context = get_mega_context_instant(prompt)

    # If we have context, prepend it
    enhanced_prompt = prompt
    if mega_context:
        enhanced_prompt = f"Context: {mega_context}\n\nQuestion: {prompt}"

    async for token in instant_stream(enhanced_prompt, mode):
        yield token


# ═══════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════

def get_instant_stream_stats() -> dict:
    """Get stats about instant stream."""
    return {
        "prompts_cached": len(PROMPTS),
        "mega_contexts_cached": len(MEGA_LAYER_CACHE),
        "client_active": _client is not None and not _client.is_closed if _client else False,
        "ollama_host": OLLAMA_HOST,
        "model": MODEL,
    }


# ═══════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    async def test():
        print("⚡ Testing Instant Stream...")
        print(f"Stats: {get_instant_stream_stats()}")

        prompt = sys.argv[1] if len(sys.argv) > 1 else "What is light?"
        print(f"\nPrompt: {prompt}")
        print(f"Language: {detect_language_instant(prompt)}")
        print("\nResponse:")

        async for token in instant_stream(prompt, mode="fast"):
            print(token, end="", flush=True)
        print()

    asyncio.run(test())

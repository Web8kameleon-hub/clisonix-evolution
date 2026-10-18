"""Internal GPU transcription and dynamic neural speech capabilities."""
import asyncio
import base64
import binascii
import os
import tempfile
import time
from contextlib import asynccontextmanager

import edge_tts
from fastapi import FastAPI, HTTPException, Request, Response
from faster_whisper import WhisperModel
from faster_whisper.tokenizer import LANGUAGES
import numpy as np

MODEL = os.getenv("VOICE_WHISPER_MODEL", "large-v3-turbo")
CAPABILITY_TTL_SECONDS = max(60, int(os.getenv("VOICE_CAPABILITY_TTL_SECONDS", "3600")))
DEFAULT_LANGUAGE = os.getenv("VOICE_DEFAULT_LANGUAGE", "").strip().lower()
model = None
slots = asyncio.Semaphore(1)
speech_slots = asyncio.Semaphore(2)
voice_registry = {}
voice_registry_updated = 0.0
voice_registry_lock = asyncio.Lock()


def load_model():
    instance = WhisperModel(MODEL, device="cuda", compute_type="int8_float16", download_root="/models", cpu_threads=2)
    segments, _ = instance.transcribe(np.zeros(16000, dtype=np.float32), beam_size=1)
    list(segments)
    return instance


def normalize_language(value):
    if not isinstance(value, str):
        return ""
    return value.strip().split("-", 1)[0].lower()


async def refresh_voice_registry(force=False):
    global voice_registry, voice_registry_updated
    now = time.monotonic()
    if voice_registry and not force and now - voice_registry_updated < CAPABILITY_TTL_SECONDS:
        return voice_registry
    async with voice_registry_lock:
        now = time.monotonic()
        if voice_registry and not force and now - voice_registry_updated < CAPABILITY_TTL_SECONDS:
            return voice_registry
        try:
            available = await edge_tts.list_voices()
        except Exception as exc:
            if voice_registry:
                return voice_registry
            raise HTTPException(503, "Neural voice registry unavailable") from exc

        discovered = {}
        whisper_languages = set(LANGUAGES)
        for item in available:
            locale = str(item.get("Locale") or "").strip()
            short_name = str(item.get("ShortName") or "").strip()
            language = normalize_language(locale)
            if not locale or not short_name or language not in whisper_languages:
                continue
            entry = discovered.setdefault(language, {
                "code": language,
                "label": str(LANGUAGES.get(language) or language).title(),
                "locales": set(),
                "voices": [],
            })
            entry["locales"].add(locale)
            entry["voices"].append({
                "id": short_name,
                "locale": locale,
                "gender": str(item.get("Gender") or "unspecified").lower(),
                "name": str(item.get("FriendlyName") or short_name),
            })

        normalized = {}
        for language, entry in discovered.items():
            voices = sorted(entry["voices"], key=lambda voice: (voice["locale"], voice["name"], voice["id"]))
            normalized[language] = {
                **entry,
                "locales": sorted(entry["locales"]),
                "voices": voices,
                "default_voice": voices[0]["id"],
            }
        if not normalized:
            raise HTTPException(503, "No compatible speech capabilities discovered")
        voice_registry = normalized
        voice_registry_updated = time.monotonic()
        return voice_registry


def capability_payload(registry):
    languages = sorted(registry.values(), key=lambda item: (item["label"], item["code"]))
    preferred = DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in registry else languages[0]["code"]
    return {
        "version": "voice-capabilities-v1",
        "source": "runtime-discovery",
        "model": MODEL,
        "device": "cuda",
        "default_language": preferred,
        "languages": languages,
    }


@asynccontextmanager
async def lifespan(app):
    global model
    model = await asyncio.to_thread(load_model)
    try:
        await refresh_voice_registry(force=True)
    except HTTPException:
        # Transcription remains available while the remote TTS registry recovers.
        pass
    yield
    model = None


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)


@app.get("/health")
def health():
    return {
        "status": "healthy" if model is not None else "loading",
        "model": MODEL,
        "device": "cuda",
        "voice_registry": "ready" if voice_registry else "unavailable",
        "language_count": len(voice_registry),
    }


@app.get("/capabilities")
async def capabilities(refresh: bool = False):
    registry = await refresh_voice_registry(force=refresh)
    return capability_payload(registry)


def transcribe(audio, language):
    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as handle:
            handle.write(audio)
            path = handle.name
        language_name = str(LANGUAGES.get(language) or language)
        segments, info = model.transcribe(
            path, language=language, beam_size=3, condition_on_previous_text=False,
            initial_prompt=f"A natural, precise conversation in {language_name}.",
            vad_filter=True, vad_parameters={"min_silence_duration_ms": 500},
            hallucination_silence_threshold=1.0,
        )
        if info.duration > 35:
            raise HTTPException(413, "Please use voice turns shorter than 30 seconds")
        text = " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()
        if not text:
            raise HTTPException(422, "No speech detected. Please speak again.")
        return {
            "transcript": text,
            "language": info.language,
            "language_probability": round(float(info.language_probability), 4),
            "model": MODEL,
            "device": "cuda",
        }
    finally:
        if path is not None:
            os.unlink(path)


@app.post("/transcribe")
async def transcription(request: Request):
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 6000000:
            raise HTTPException(413, "Recording too large")
    import json
    try:
        body = json.loads(data)
        if not isinstance(body, dict):
            raise HTTPException(400, "Invalid audio payload")
        language = normalize_language(body.get("language"))
        if language not in LANGUAGES:
            raise HTTPException(400, "Unsupported transcription language")
        audio = base64.b64decode(body["audio_base64"], validate=True)
    except (KeyError, TypeError, ValueError, binascii.Error) as exc:
        raise HTTPException(400, "Invalid audio payload") from exc
    if len(audio) < 100 or len(audio) > 4500000:
        raise HTTPException(400, "Invalid recording size")
    started = time.monotonic()
    async with slots:
        if await request.is_disconnected():
            raise HTTPException(499, "Request cancelled")
        result = await asyncio.to_thread(transcribe, audio, language)
    result["processing_time_ms"] = round((time.monotonic() - started) * 1000)
    return result


@app.post("/synthesize")
async def synthesize(request: Request):
    import json
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 12000:
            raise HTTPException(413, "Speech phrase too large")
    try:
        body = json.loads(data)
        if not isinstance(body, dict):
            raise ValueError()
        text = body.get("text", "")
        language = normalize_language(body.get("language"))
        registry = await refresh_voice_registry()
        profile = registry.get(language)
        if not profile:
            raise HTTPException(400, "Unsupported speech language")
        requested_voice = str(body.get("voice") or "").strip()
        allowed_voices = {item["id"] for item in profile["voices"]}
        voice = requested_voice or profile["default_voice"]
        if voice not in allowed_voices:
            raise HTTPException(400, "Voice does not match the selected language")
        if not isinstance(text, str) or not text.strip() or len(text) > 2400:
            raise ValueError()
    except HTTPException:
        raise
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(400, "Invalid speech phrase") from exc
    async with speech_slots:
        for attempt in range(3):
            if await request.is_disconnected():
                raise HTTPException(499, "Request cancelled")
            try:
                audio = bytearray()
                communicate = edge_tts.Communicate(text.strip(), voice, connect_timeout=10, receive_timeout=20)
                async for packet in communicate.stream():
                    if packet["type"] == "audio":
                        audio.extend(packet["data"])
                    if len(audio) > 2000000:
                        raise ValueError("Speech audio too large")
                if not audio:
                    raise ValueError("Empty speech")
                return Response(bytes(audio), media_type="audio/mpeg", headers={"Cache-Control": "no-store", "X-Voice-Used": voice})
            except Exception:
                if attempt == 2:
                    raise HTTPException(503, "Neural voice temporarily unavailable")
                await asyncio.sleep(0.25 * (attempt + 1))

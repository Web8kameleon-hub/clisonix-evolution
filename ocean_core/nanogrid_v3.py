#!/usr/bin/env python3
"""
Ocean Nanogrid v3 - Clean & Fast
================================
~200 lines vs 1100 lines. Same functionality.
"""
import base64
import hashlib
import importlib.util
import json
import os
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from prompts import build_prompt

# Config
OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
VISION_MODEL = os.getenv("VISION_MODEL", "llava:latest")
PORT = int(os.getenv("PORT", "8030"))
RATE_LIMIT = 1000  # per hour
TOOL_SCAN_MAX = int(os.getenv("TOOL_SCAN_MAX", "800"))

# State
_client: Optional[httpx.AsyncClient] = None
rate_limits: dict = defaultdict(list)
memory: dict = defaultdict(list)  # session_id -> messages
tool_catalog: list[dict] = []
tool_index: dict[str, list[dict]] = defaultdict(list)
tool_last_scan: float = 0.0
startup_state: dict = {
    "ready": False,
    "warmup_ok": False,
    "warmup_error": None,
    "started_at": None,
}

PROMPT_VERSION = "nanogrid-v3-prompt-2026-03-05"
HTTP2_AVAILABLE = importlib.util.find_spec("h2") is not None

SHORT_GREETINGS = {
    "mirmengjes", "mirëmengjes", "mirëmëngjes", "miremengjes", "mir dita", "pershendetje", "përshëndetje",
    "good morning", "good afternoon", "good evening", "hello", "hi", "hey",
    "bonjour", "salut", "buenos dias", "buen día", "hola",
    "guten morgen", "hallo", "buongiorno", "ciao",
    "bom dia", "olá", "ola", "dobroe utro", "dobry den",
    "ohayo", "konnichiwa", "ni hao", "annyeong", "marhaba",
}

LANG_GREETING_RESPONSES = {
    "sq": "Mirëmëngjes! 👋 Si mund të të ndihmoj sot?",
    "en": "Good morning! 👋 How can I help you today?",
    "de": "Guten Morgen! 👋 Wie kann ich dir heute helfen?",
    "fr": "Bonjour ! 👋 Comment puis-je vous aider aujourd'hui ?",
    "es": "¡Buenos días! 👋 ¿Cómo puedo ayudarte hoy?",
    "it": "Buongiorno! 👋 Come posso aiutarti oggi?",
    "pt": "Bom dia! 👋 Como posso ajudar você hoje?",
    "tr": "Günaydın! 👋 Bugün size nasıl yardımcı olabilirim?",
    "ar": "صباح الخير! 👋 كيف يمكنني مساعدتك اليوم؟",
}

TTS_VOICES = {
    "en": "en-US-AriaNeural",
    "en-male": "en-US-GuyNeural",
    "sq": "sq-AL-AnilaNeural",
    "de": "de-DE-KatjaNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "tr": "tr-TR-EmelNeural",
    "ar": "ar-EG-SalmaNeural",
}

_whisper_model = None

TOOL_GLOB_PATTERNS = [
    "*_api.py",
    "*_service.py",
    "*_server.py",
    "*_engine.py",
    "*gateway*.py",
    "*protocol*.py",
    "*.ts",
]

# FastAPI
app = FastAPI(title="Ocean Nanogrid", version="3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Req(BaseModel):
    message: Optional[str] = None
    query: Optional[str] = None


class Res(BaseModel):
    response: str
    time: float


class AudioRequest(BaseModel):
    audio_base64: str
    language: str = "auto"


class DocumentRequest(BaseModel):
    content: str
    encoding: str = "text"  # text | base64
    action: str = "summarize"  # summarize | analyze | extract
    doc_type: Optional[str] = None
    filename: Optional[str] = None


class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    voice: Optional[str] = None
    rate: str = "+0%"
    pitch: str = "+0Hz"


class VoiceConversationRequest(BaseModel):
    audio_base64: str
    language: str = "auto"
    voice: Optional[str] = None
    curiosity_level: str = "curious"
    user_id: Optional[str] = None


class VisionRequest(BaseModel):
    image_base64: str
    prompt: str = "Describe this image in detail"
    extract_text: bool = False


class OmniRequest(BaseModel):
    action: str = "auto"  # auto|chat|audio_transcribe|vision|document|tts|voice
    message: Optional[str] = None
    query: Optional[str] = None
    language: str = "auto"
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    audio_base64: Optional[str] = None
    image_base64: Optional[str] = None
    prompt: Optional[str] = None

    content: Optional[str] = None
    encoding: str = "text"
    document_action: str = "summarize"
    doc_type: Optional[str] = None
    filename: Optional[str] = None

    text: Optional[str] = None
    voice: Optional[str] = None
    rate: str = "+0%"
    pitch: str = "+0Hz"
    return_audio_base64: bool = False


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=300.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            http2=HTTP2_AVAILABLE,
        )
    return _client


def check_rate(user_id: str, is_admin: bool) -> tuple[bool, int]:
    """Rate limit check. Admins bypass."""
    if is_admin:
        return True, 9999

    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    rate_limits[user_id] = [t for t in rate_limits[user_id] if t > hour_ago]

    if len(rate_limits[user_id]) >= RATE_LIMIT:
        return False, 0

    rate_limits[user_id].append(now)
    return True, RATE_LIMIT - len(rate_limits[user_id])


def is_admin(msg: str, user_id: str) -> bool:
    """Detect admin by keywords."""
    check = (msg + user_id).lower()
    return any(x in check for x in ["ledjan", "ahmati", "admin"])


def add_memory(session: str, role: str, content: str):
    """Store message in conversation memory."""
    memory[session].append({"role": role, "content": content})
    if len(memory[session]) > 20:
        memory[session] = memory[session][-20:]


def get_language_hint(request: Request) -> str:
    """Extract best-effort language hint from headers."""
    explicit = request.headers.get("X-Language") or request.headers.get("X-User-Language")
    if explicit:
        return explicit.strip()

    accept_language = request.headers.get("Accept-Language", "").strip()
    if not accept_language:
        return ""

    return accept_language.split(",")[0].split(";")[0].strip()


def _normalize_text(text: str) -> str:
    value = (text or "").strip().lower()
    for ch in ["!", "?", ".", ",", ":", ";", "'", '"', "(", ")", "[", "]"]:
        value = value.replace(ch, "")
    value = " ".join(value.split())
    value = value.replace("ë", "e")
    return value


def greeting_response(query: str, language_hint: str) -> Optional[str]:
    normalized = _normalize_text(query)
    if not normalized:
        return None

    if normalized not in SHORT_GREETINGS and not any(normalized.startswith(g + " ") for g in SHORT_GREETINGS):
        return None

    lang = (language_hint or "").split("-")[0].lower()
    if not lang:
        if any(token in normalized for token in ["mir", "pershendetje", "përshëndetje"]):
            lang = "sq"
        else:
            lang = "en"

    return LANG_GREETING_RESPONSES.get(lang, LANG_GREETING_RESPONSES["en"])


async def check_model_health() -> dict:
    client = await get_client()
    result = {
        "model": MODEL,
        "ollama": OLLAMA,
        "version_ok": False,
        "model_present": None,
        "error": None,
    }

    try:
        version_resp = await client.get(f"{OLLAMA}/api/version", timeout=10.0)
        result["version_ok"] = version_resp.status_code == 200

        tags_resp = await client.get(f"{OLLAMA}/api/tags", timeout=10.0)
        if tags_resp.status_code == 200:
            models = tags_resp.json().get("models", [])
            names = {item.get("name", "") for item in models}
            result["model_present"] = MODEL in names
    except Exception as exc:
        result["error"] = str(exc)

    return result


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _tool_kind(path: Path) -> str:
    name = path.name.lower()
    if "protocol" in name:
        return "protocol"
    if "gateway" in name:
        return "gateway"
    if "api" in name:
        return "api"
    if "service" in name or "server" in name:
        return "service"
    if "engine" in name:
        return "engine"
    return "module"


def refresh_tool_catalog(force: bool = False) -> dict:
    global tool_catalog, tool_index, tool_last_scan

    now = time.time()
    if not force and tool_catalog and (now - tool_last_scan) < 300:
        return {
            "updated": False,
            "count": len(tool_catalog),
            "last_scan": round(tool_last_scan, 2),
        }

    root = _repo_root()
    discovered: list[dict] = []
    count = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith((".git/", ".venv/", "node_modules/", "__pycache__/", "build/", "dist/")):
            continue
        if not any(path.match(pattern) for pattern in TOOL_GLOB_PATTERNS):
            continue

        discovered.append(
            {
                "name": path.stem,
                "path": rel,
                "kind": _tool_kind(path),
            }
        )
        count += 1
        if count >= TOOL_SCAN_MAX:
            break

    discovered.sort(key=lambda x: (x["kind"], x["name"]))
    index: dict[str, list[dict]] = defaultdict(list)
    for item in discovered:
        tokens = {item["name"].lower(), item["kind"].lower()}
        for token in list(tokens):
            if "_" in token:
                tokens.update(part for part in token.split("_") if part)
        for token in tokens:
            index[token].append(item)

    tool_catalog = discovered
    tool_index = index
    tool_last_scan = now
    return {
        "updated": True,
        "count": len(tool_catalog),
        "last_scan": round(tool_last_scan, 2),
    }


def build_tool_context(query: str) -> str:
    q = (query or "").lower()
    if not q:
        return ""

    hits: list[dict] = []
    seen = set()
    for token in q.replace("/", " ").replace("-", " ").split():
        if len(token) < 3:
            continue
        for item in tool_index.get(token, []):
            key = item["path"]
            if key in seen:
                continue
            hits.append(item)
            seen.add(key)
            if len(hits) >= 6:
                break
        if len(hits) >= 6:
            break

    if not hits:
        return ""

    lines = ["Available repo tools potentially relevant to this request:"]
    for item in hits:
        lines.append(f"- {item['name']} ({item['kind']}): {item['path']}")
    return "\n".join(lines)


async def generate_llm_response(user_text: str, system_prompt: str, temperature: float = 0.4) -> str:
    client = await get_client()
    response = await client.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "stream": False,
            "options": {"num_ctx": 8192, "temperature": temperature},
        },
    )
    if response.status_code >= 400:
        raise HTTPException(502, f"LLM upstream error: {response.status_code}")
    return response.json().get("message", {}).get("content", "")


def decode_document_content(req: DocumentRequest) -> Tuple[str, str]:
    if req.encoding == "text":
        return req.content, "text"

    if req.encoding != "base64":
        raise HTTPException(400, f"Unsupported encoding: {req.encoding}")

    if not req.content:
        raise HTTPException(400, "Document content is empty")

    try:
        raw = base64.b64decode(req.content)
    except Exception as exc:
        raise HTTPException(400, "Invalid base64 document") from exc

    ext = (req.doc_type or "").lower().strip(".")
    name = (req.filename or "").lower()

    if ext == "pdf" or name.endswith(".pdf"):
        try:
            from io import BytesIO

            from pypdf import PdfReader  # type: ignore[import-not-found]

            reader = PdfReader(BytesIO(raw))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            return text.strip(), "pdf"
        except ImportError as exc:
            raise HTTPException(500, "PDF parser not installed. Install: pip install pypdf") from exc

    if ext == "docx" or name.endswith(".docx"):
        try:
            from io import BytesIO

            from docx import Document  # type: ignore[import-not-found]

            doc = Document(BytesIO(raw))
            text = "\n".join(p.text for p in doc.paragraphs)
            return text.strip(), "docx"
        except ImportError as exc:
            raise HTTPException(500, "DOCX parser not installed. Install: pip install python-docx") from exc

    try:
        return raw.decode("utf-8", errors="ignore").strip(), "base64-text"
    except Exception as exc:
        raise HTTPException(400, "Unable to decode document") from exc


def _voice_for_language(language: str, voice: Optional[str]) -> str:
    if voice:
        return voice
    lang = (language or "en").split("-")[0].lower()
    return TTS_VOICES.get(lang, TTS_VOICES["en"])


async def _transcribe_audio_base64(audio_base64: str, language: str = "auto") -> dict:
    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as exc:
        raise HTTPException(400, "Invalid audio base64") from exc

    if len(audio_bytes) < 100:
        raise HTTPException(400, "Audio data too small")
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(413, "Audio too large (max 25MB)")

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        from faster_whisper import WhisperModel  # type: ignore[import-not-found]

        global _whisper_model  # pylint: disable=global-statement
        if _whisper_model is None:
            _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

        segments, info = _whisper_model.transcribe(
            tmp_path,
            language=language if language not in {"auto", ""} else None,
            beam_size=5,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        if not transcript:
            transcript = "[No speech detected in audio]"

        return {
            "status": "success",
            "transcript": transcript,
            "language": getattr(info, "language", language),
            "language_probability": round(getattr(info, "language_probability", 0.0), 2),
            "duration_seconds": round(getattr(info, "duration", 0.0), 2),
            "word_count": len(transcript.split()),
            "engine": "faster-whisper",
        }
    except ImportError:
        return {
            "status": "whisper_not_available",
            "message": "faster-whisper is not installed",
            "install_command": "pip install faster-whisper",
        }
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


async def _synthesize_tts_mp3(text: str, language: str, voice: Optional[str], rate: str, pitch: str) -> Tuple[bytes, str]:
    try:
        import edge_tts  # type: ignore[import-not-found]
    except ImportError as exc:
        raise HTTPException(500, "TTS engine not available. Install: pip install edge-tts") from exc

    selected_voice = _voice_for_language(language, voice)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        communicate = edge_tts.Communicate(text=text, voice=selected_voice, rate=rate, pitch=pitch)
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as handler:
            audio_data = handler.read()
        return audio_data, selected_voice
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _decode_image_base64(image_base64: str) -> bytes:
    try:
        decoded = base64.b64decode(image_base64)
    except Exception as exc:
        raise HTTPException(400, "Invalid base64 image data") from exc

    if len(decoded) < 100:
        raise HTTPException(400, "Image data too small or invalid")
    if len(decoded) > 10 * 1024 * 1024:
        raise HTTPException(413, "Image too large (max 10MB)")
    return decoded


# ═══════════════════════════════════════════════════════════════════
# LIFECYCLE
# ═══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Preload model for zero cold start."""
    client = await get_client()
    try:
        startup_state["started_at"] = int(time.time())
        refresh_tool_catalog(force=True)
        await client.get(f"{OLLAMA}/api/version")
        print("🟢 Nanogrid v3 ready")

        print(f"🔥 Preloading {MODEL}...")
        await client.post(
            f"{OLLAMA}/api/generate",
            json={"model": MODEL, "prompt": "", "keep_alive": "24h"},
            timeout=60.0
        )
        startup_state["ready"] = True
        startup_state["warmup_ok"] = True
        print(f"🚀 {MODEL} warm - zero cold start!")
    except Exception as e:
        startup_state["ready"] = True
        startup_state["warmup_ok"] = False
        startup_state["warmup_error"] = str(e)
        print(f"🟡 Ready, Ollama will connect on first request: {e}")


@app.on_event("shutdown")
async def shutdown():
    global _client
    if _client:
        await _client.aclose()


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {"service": "Ocean Nanogrid", "version": "3.0", "model": MODEL}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ready": startup_state["ready"],
        "warmup_ok": startup_state["warmup_ok"],
    }


@app.post("/api/v1/chat", response_model=Res)
async def chat(req: Req, request: Request):
    """Non-streaming chat."""
    t0 = time.time()
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")

    client_host = request.client.host if request.client else "anon"
    user_id = request.headers.get("X-User-ID") or client_host or "anon"
    session = request.headers.get("X-Session-ID") or user_id
    admin = is_admin(q, user_id)

    # Rate limit
    allowed, remaining = check_rate(user_id, admin)
    if not allowed:
        raise HTTPException(429, "Rate limit exceeded - upgrade at clisonix.com/pricing")

    add_memory(session, "user", q)
    language_hint = get_language_hint(request)

    quick = greeting_response(q, language_hint)
    if quick:
        add_memory(session, "assistant", quick)
        return Res(response=quick, time=round(time.time() - t0, 2))

    # Build prompt with history
    history = memory.get(session, [])
    prompt = build_prompt(
        is_admin=admin,
        conversation_history=history,
        user_message=q,
        language_hint=language_hint,
    )
    tool_context = build_tool_context(q)
    if tool_context:
        prompt = f"{prompt}\n\n{tool_context}"

    client = await get_client()
    try:
        r = await client.post(f"{OLLAMA}/api/chat", json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": q}
            ],
            "stream": False,
            "options": {"num_ctx": 8192, "temperature": 0.7}
        })
        resp = r.json().get("message", {}).get("content", "")
        add_memory(session, "assistant", resp)
    except Exception as e:
        raise HTTPException(500, str(e))

    return Res(response=resp, time=round(time.time() - t0, 2))


@app.post("/api/v1/chat/stream")
async def chat_stream(req: Req, request: Request):
    """Streaming chat - first token in ~1s."""
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")

    client_host = request.client.host if request.client else "anon"
    user_id = request.headers.get("X-User-ID") or client_host or "anon"
    session = request.headers.get("X-Session-ID") or user_id
    admin = is_admin(q, user_id)

    allowed, _ = check_rate(user_id, admin)
    if not allowed:
        raise HTTPException(429, "Rate limit exceeded")

    add_memory(session, "user", q)
    history = memory.get(session, [])
    language_hint = get_language_hint(request)

    quick = greeting_response(q, language_hint)
    if quick:
        add_memory(session, "assistant", quick)

        async def quick_stream():
            yield quick

        return StreamingResponse(quick_stream(), media_type="text/plain")

    prompt = build_prompt(
        is_admin=admin,
        conversation_history=history,
        user_message=q,
        language_hint=language_hint,
    )
    tool_context = build_tool_context(q)
    if tool_context:
        prompt = f"{prompt}\n\n{tool_context}"

    async def generate():
        client = httpx.AsyncClient(timeout=httpx.Timeout(None, connect=30.0), http2=HTTP2_AVAILABLE)
        try:
            async with client.stream("POST", f"{OLLAMA}/api/chat", json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": q}
                ],
                "stream": True,
                "options": {"num_ctx": 8192, "temperature": 0.7}
            }) as response:
                full = ""
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                full += content
                                yield content
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
                add_memory(session, "assistant", full)
        finally:
            await client.aclose()

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/api/v1/audio/transcribe")
async def audio_transcribe(req: AudioRequest):
    t0 = time.time()
    result = await _transcribe_audio_base64(req.audio_base64, req.language)
    result["processing_time"] = round(time.time() - t0, 2)
    return result


@app.post("/api/v1/vision/analyze")
async def vision_analyze(req: VisionRequest):
    t0 = time.time()
    _decode_image_base64(req.image_base64)

    prompt = req.prompt
    if req.extract_text:
        prompt = "Extract all visible text from this image. Return only the extracted text in the same language as found."

    client = await get_client()
    try:
        response = await client.post(
            f"{OLLAMA}/api/generate",
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [req.image_base64],
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=60.0,
        )

        if response.status_code >= 400:
            return {
                "status": "model_not_found",
                "message": f"Vision model {VISION_MODEL} is unavailable",
                "install_command": f"ollama pull {VISION_MODEL}",
            }

        payload = response.json()
        analysis = payload.get("response", "")

        return {
            "status": "success",
            "analysis": analysis,
            "mode": "ocr" if req.extract_text else "vision",
            "model": VISION_MODEL,
            "processing_time": round(time.time() - t0, 2),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Vision error: {exc}") from exc


@app.post("/api/v1/document/analyze")
async def document_analyze(req: DocumentRequest):
    t0 = time.time()
    text, source_type = decode_document_content(req)
    if not text:
        raise HTTPException(400, "Document text is empty after decoding")

    if len(text) > 120000:
        text = text[:120000]

    action = (req.action or "summarize").lower().strip()
    if action not in {"summarize", "analyze", "extract"}:
        raise HTTPException(400, "Invalid action. Use summarize|analyze|extract")

    if action == "summarize":
        user_prompt = f"Summarize this document clearly in the document language:\n\n{text}"
    elif action == "extract":
        user_prompt = (
            "Extract key entities and facts from this document in JSON-like bullets "
            "(people, organizations, dates, locations, numbers):\n\n" + text
        )
    else:
        user_prompt = f"Analyze this document deeply and provide actionable insights:\n\n{text}"

    system_prompt = (
        "You are an enterprise document analyst. "
        "Return precise, factual output in the same language as the document."
    )
    analysis = await generate_llm_response(user_prompt, system_prompt, temperature=0.2)

    return {
        "status": "success",
        "action": action,
        "analysis": analysis,
        "summary": analysis if action == "summarize" else None,
        "source_type": source_type,
        "chars": len(text),
        "processing_time": round(time.time() - t0, 2),
    }


@app.post("/api/v1/tts")
async def text_to_speech(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(400, "Text cannot be empty")

    t0 = time.time()
    audio_data, selected_voice = await _synthesize_tts_mp3(
        text=req.text.strip(),
        language=req.language,
        voice=req.voice,
        rate=req.rate,
        pitch=req.pitch,
    )
    processing_time = round(time.time() - t0, 3)

    return StreamingResponse(
        iter([audio_data]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=speech.mp3",
            "X-Processing-Time": f"{processing_time}s",
            "X-Voice-Used": selected_voice,
            "X-Text-Length": str(len(req.text)),
        },
    )


@app.get("/api/v1/tts/voices")
async def tts_voices():
    return {
        "voices": TTS_VOICES,
        "total": len(TTS_VOICES),
        "engine": "Microsoft Edge Neural TTS",
    }


@app.post("/api/v1/voice/conversation")
async def voice_conversation(req: VoiceConversationRequest, request: Request):
    t0 = time.time()

    stt_started = time.time()
    stt = await _transcribe_audio_base64(req.audio_base64, req.language)
    stt_time = round(time.time() - stt_started, 3)
    if stt.get("status") != "success":
        raise HTTPException(500, stt.get("message") or "Could not transcribe audio")

    transcript = (stt.get("transcript") or "").strip()
    if not transcript or transcript == "[No speech detected in audio]":
        raise HTTPException(400, "Could not transcribe audio. Please speak clearly.")

    client_host = request.client.host if request.client else "anon"
    user_id = req.user_id or request.headers.get("X-User-ID") or client_host
    session = request.headers.get("X-Session-ID") or str(user_id)
    add_memory(session, "user", transcript)

    llm_started = time.time()
    language_hint = req.language if req.language != "auto" else ""
    base_prompt = build_prompt(
        is_admin=False,
        conversation_history=memory.get(session, []),
        user_message=transcript,
        language_hint=language_hint,
    )
    assistant_text = await generate_llm_response(transcript, base_prompt, temperature=0.5)
    llm_time = round(time.time() - llm_started, 3)
    add_memory(session, "assistant", assistant_text)

    tts_started = time.time()
    detected_language = stt.get("language") or req.language or "en"
    audio_data, selected_voice = await _synthesize_tts_mp3(
        text=assistant_text,
        language=str(detected_language),
        voice=req.voice,
        rate="+0%",
        pitch="+0Hz",
    )
    tts_time = round(time.time() - tts_started, 3)

    return StreamingResponse(
        iter([audio_data]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=voice_response.mp3",
            "X-Transcript": transcript[:500],
            "X-Response-Text": assistant_text[:1000],
            "X-Processing-Time": f"{round(time.time() - t0, 3)}s",
            "X-STT-Time": f"{stt_time}s",
            "X-LLM-Time": f"{llm_time}s",
            "X-TTS-Time": f"{tts_time}s",
            "X-Voice-Used": selected_voice,
            "X-Detected-Language": str(detected_language),
        },
    )


@app.post("/api/v1/omni")
async def omni(req: OmniRequest, request: Request):
    t0 = time.time()

    action = (req.action or "auto").strip().lower()
    if action == "auto":
        if req.audio_base64 and req.return_audio_base64:
            action = "voice"
        elif req.audio_base64:
            action = "audio_transcribe"
        elif req.image_base64:
            action = "vision"
        elif req.content:
            action = "document"
        elif req.text:
            action = "tts"
        else:
            action = "chat"

    if action == "audio_transcribe":
        if not req.audio_base64:
            raise HTTPException(400, "audio_base64 is required for audio_transcribe")
        result = await _transcribe_audio_base64(req.audio_base64, req.language)
        result["action"] = action
        result["processing_time"] = round(time.time() - t0, 2)
        return result

    if action == "vision":
        if not req.image_base64:
            raise HTTPException(400, "image_base64 is required for vision")
        result = await vision_analyze(
            VisionRequest(
                image_base64=req.image_base64,
                prompt=req.prompt or "Describe this image in detail",
                extract_text=False,
            )
        )
        result["action"] = action
        return result

    if action == "document":
        if not req.content:
            raise HTTPException(400, "content is required for document")
        result = await document_analyze(
            DocumentRequest(
                content=req.content,
                encoding=req.encoding,
                action=req.document_action,
                doc_type=req.doc_type,
                filename=req.filename,
            )
        )
        result["action"] = action
        return result

    if action == "tts":
        text = (req.text or req.message or req.query or "").strip()
        if not text:
            raise HTTPException(400, "text/message/query is required for tts")
        audio_data, selected_voice = await _synthesize_tts_mp3(
            text=text,
            language=req.language,
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch,
        )
        return {
            "status": "success",
            "action": action,
            "voice": selected_voice,
            "audio_base64": base64.b64encode(audio_data).decode("ascii"),
            "processing_time": round(time.time() - t0, 2),
        }

    if action == "voice":
        if not req.audio_base64:
            raise HTTPException(400, "audio_base64 is required for voice")

        stt = await _transcribe_audio_base64(req.audio_base64, req.language)
        if stt.get("status") != "success":
            raise HTTPException(500, stt.get("message") or "Could not transcribe audio")

        transcript = (stt.get("transcript") or "").strip()
        if not transcript or transcript == "[No speech detected in audio]":
            raise HTTPException(400, "Could not transcribe audio. Please speak clearly.")

        client_host = request.client.host if request.client else "anon"
        user_id = req.user_id or request.headers.get("X-User-ID") or client_host
        session = req.session_id or request.headers.get("X-Session-ID") or str(user_id)
        add_memory(session, "user", transcript)

        language_hint = req.language if req.language != "auto" else ""
        base_prompt = build_prompt(
            is_admin=False,
            conversation_history=memory.get(session, []),
            user_message=transcript,
            language_hint=language_hint,
        )
        assistant_text = await generate_llm_response(transcript, base_prompt, temperature=0.5)
        add_memory(session, "assistant", assistant_text)

        audio_data, selected_voice = await _synthesize_tts_mp3(
            text=assistant_text,
            language=str(stt.get("language") or req.language or "en"),
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch,
        )

        return {
            "status": "success",
            "action": action,
            "transcript": transcript,
            "response": assistant_text,
            "voice": selected_voice,
            "audio_base64": base64.b64encode(audio_data).decode("ascii"),
            "processing_time": round(time.time() - t0, 2),
        }

    if action != "chat":
        raise HTTPException(400, "Invalid action. Use auto|chat|audio_transcribe|vision|document|tts|voice")

    q = (req.message or req.query or "").strip()
    if not q:
        raise HTTPException(400, "message or query is required for chat")

    client_host = request.client.host if request.client else "anon"
    user_id = req.user_id or request.headers.get("X-User-ID") or client_host
    session = req.session_id or request.headers.get("X-Session-ID") or str(user_id)
    admin = is_admin(q, str(user_id))

    allowed, _ = check_rate(str(user_id), admin)
    if not allowed:
        raise HTTPException(429, "Rate limit exceeded")

    add_memory(session, "user", q)
    language_hint = req.language if req.language != "auto" else get_language_hint(request)

    quick = greeting_response(q, language_hint)
    if quick:
        add_memory(session, "assistant", quick)
        return {
            "status": "success",
            "action": action,
            "response": quick,
            "processing_time": round(time.time() - t0, 2),
        }

    prompt = build_prompt(
        is_admin=admin,
        conversation_history=memory.get(session, []),
        user_message=q,
        language_hint=language_hint,
    )
    tool_context = build_tool_context(q)
    if tool_context:
        prompt = f"{prompt}\n\n{tool_context}"

    response = await generate_llm_response(q, prompt, temperature=0.7)
    add_memory(session, "assistant", response)
    return {
        "status": "success",
        "action": action,
        "response": response,
        "processing_time": round(time.time() - t0, 2),
    }


# ═══════════════════════════════════════════════════════════════════
# UTILITY ENDPOINTS (minimal)
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/status")
async def status():
    prompt_hash = hashlib.sha256(
        build_prompt(is_admin=False, conversation_history=[], user_message="status", language_hint="en").encode("utf-8")
    ).hexdigest()[:16]

    return {
        "model": MODEL,
        "ollama": OLLAMA,
        "prompt_version": PROMPT_VERSION,
        "prompt_hash": prompt_hash,
        "active_sessions": len(memory),
        "rate_tracked_users": len(rate_limits),
        "tool_catalog_count": len(tool_catalog),
        "tool_last_scan": round(tool_last_scan, 2) if tool_last_scan else None,
        "warmup_ok": startup_state["warmup_ok"],
        "warmup_error": startup_state["warmup_error"],
    }


@app.get("/api/v1/diagnostics")
async def diagnostics():
    model_health = await check_model_health()
    return {
        "startup": startup_state,
        "model_health": model_health,
        "prompt_version": PROMPT_VERSION,
        "tool_catalog_count": len(tool_catalog),
    }


@app.get("/api/v1/tools")
async def list_tools(kind: Optional[str] = None, q: Optional[str] = None, limit: int = 100):
    if not tool_catalog:
        refresh_tool_catalog(force=True)

    items = tool_catalog
    if kind:
        k = kind.lower().strip()
        items = [item for item in items if item["kind"] == k]
    if q:
        query = q.lower().strip()
        items = [item for item in items if query in item["name"].lower() or query in item["path"].lower()]

    safe_limit = max(1, min(limit, 500))
    return {
        "count": len(items),
        "returned": min(len(items), safe_limit),
        "items": items[:safe_limit],
    }


@app.post("/api/v1/tools/refresh")
async def refresh_tools():
    result = refresh_tool_catalog(force=True)
    return {"status": "ok", **result}


@app.delete("/api/v1/memory/{session_id}")
async def clear_memory(session_id: str):
    """Clear conversation memory for a session."""
    if session_id in memory:
        del memory[session_id]
        return {"cleared": True}
    return {"cleared": False, "reason": "session not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

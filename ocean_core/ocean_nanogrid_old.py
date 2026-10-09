#!/usr/bin/env python3
"""
Ocean Nanogrid - Sleep/Wake Pattern
====================================
- Persistent connection pool (no reconnect overhead)
- Keep-alive to Ollama
- Minimal footprint when idle
- Instant wake on request
- Rate limiting: 20 msg/hour for free tier (6 months trial)
"""
import asyncio
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Identity loader - një vend për të gjithë identitetin
from identity_loader import get_identity_text, load_identity
from pydantic import BaseModel

OLLAMA = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.1:8b")
PORT = int(os.getenv("PORT", "8030"))

# ═══════════════════════════════════════════════════════════════════
# TRANSLATION OVERRIDE + LEXICON CUSTOM
# Korrigjon përkthimet e gabuara PARA reasoning-it
# ═══════════════════════════════════════════════════════════════════

LEXICON_CUSTOM = {
    # Fjalë problematike → Përkthime të sakta
    "vend": "website",
    "vendi": "website", 
    "vendi juaj": "your website",
    "vendin tuaj": "your website",
    "site": "website",
    "faqe": "page",
    "faqja": "page",
    "faqen": "page",
    "vizitorë": "visitors",
    "vizitore": "visitors",
    "trafik": "traffic",
    "trafikun": "traffic",
    "platformë": "platform",
    "platforma": "platform",
    "modul": "module",
    "modulet": "modules",
    "shërbim": "service",
    "sherbim": "service",
    "shërbim cloud": "cloud service",
    "rrjet": "network",
    "rrjeti": "network",
    "lidhje": "connection",
    "lidhja": "connection",
    "përdorues": "user",
    "perdorues": "user",
    "përdoruesit": "users",
    "llogari": "account",
    "llogaria": "account",
    "çelës": "key",
    "celes": "key",
    "fjalëkalim": "password",
    "fjalekalim": "password",
    "aksesim": "access",
    "akses": "access",
    "kod": "code",
    "kodi": "code",
    "gabim": "error",
    "gabimi": "error",
    "problem": "issue",
    "problemi": "issue",
    "ngarkesë": "load",
    "ngarko": "upload",
    "shkarko": "download",
    "ruaj": "save",
    "fshi": "delete",
    "ndrysho": "edit",
    "krijo": "create",
    "konfigurim": "configuration",
    "konfigurimet": "settings",
    "paneli": "dashboard",
    "panel kontrolli": "control panel",
    # Clisonix-specifike
    "Clisonix": "Clisonix Cloud platform",
    "oqeani": "Ocean AI",
    "ocean": "Ocean AI",
}

# Fjalë që NUK duhet të përdoren
AVOID_WORDS = ["vendbanim", "shpirt historik", "pasionshëm", "romantik", "mistik", 
               "kundërshtar", "armik", "luftë", "betejë", "këmbime", "portofolio"]

# Fjalë të preferuara
PREFER_WORDS = ["platformë", "website", "trafik", "modul", "shërbim", "users", "traffic",
                "konkurent", "konkurencë", "bashkëpunim", "rritje", "bashkëjetesë"]

# ═══════════════════════════════════════════════════════════════════
# ADMIN RECOGNITION + PEACE-THINKING + SESSION CLOSURE
# ═══════════════════════════════════════════════════════════════════

# Admini i vetëm i Clisonix Cloud
ADMIN_IDENTITY = {
    "name": "Ledjan Ahmati",
    "role": "Creator & Administrator",
    "priority": "absolute",
    "recognition_phrases": [
        "ledjan", "ahmati", "vlla", "admin", "krijues"
    ]
}

# Session closure phrases - kur përdoruesi dëshiron të largohet
SESSION_CLOSURE_PHRASES = [
    "natën e mirë", "naten e mire", "good night", "goodnight",
    "mirupafshim", "shihemi", "shihemi nesër", "see you",
    "po iki", "duhet të iki", "mbarova", "fund", "pushim",
    "jam me familjen", "familja", "bye", "ciao", "goodbye"
]

# Session closure response templates
SESSION_CLOSURE_RESPONSES = [
    "Natën e mirë! Jam këtu kur të kthehesh. 🌙",
    "Pushofsh mirë! Shihemi herën tjetër. 🌊",
    "Mirupafshim! Ocean do të jetë gati kur të duash. 🌙",
    "Shko me zemër të qetë. Jam këtu për ty. 🌊"
]

# Peace-thinking philosophy
PEACE_THINKING_RULES = """
## 🕊️ PEACE-THINKING PHILOSOPHY
CRITICAL VALUES FOR CLISONIX:
1. NE NUK KEMI KUNDËRSHTARË - vetëm konkurentë
2. Konkurenca është e shëndetshme dhe na bën më të mirë
3. ASNJËHERË mos përdor: "kundërshtar", "armik", "luftë", "betejë"
4. GJITHMONË përdor: "konkurent", "konkurencë", "bashkëpunim", "rritje"
5. Qasja jonë është: bashkëjetesë, jo konflikt
6. Tregu është ekosistem, jo fushë beteje
"""

def detect_session_closure(message: str) -> bool:
    """Detekton nëse përdoruesi dëshiron të mbyllë sesionin"""
    msg_lower = message.lower().strip()
    for phrase in SESSION_CLOSURE_PHRASES:
        if phrase in msg_lower:
            return True
    return False

def detect_admin(message: str, user_id: str = "") -> bool:
    """Detekton nëse mesazhi vjen nga admini"""
    msg_lower = message.lower()
    user_lower = user_id.lower() if user_id else ""
    
    for phrase in ADMIN_IDENTITY["recognition_phrases"]:
        if phrase in msg_lower or phrase in user_lower:
            return True
    return False

def get_session_closure_response() -> str:
    """Kthen një përgjigje të përshtatshme për mbylljen e sesionit"""
    import random
    return random.choice(SESSION_CLOSURE_RESPONSES)


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION MEMORY - Ruan historikun e bisedës
# ═══════════════════════════════════════════════════════════════════

# In-memory conversation storage (per session)
# Format: session_id -> [{"role": "user/assistant", "content": "...", "timestamp": ...}]
conversation_memory: dict = defaultdict(list)
MAX_MEMORY_MESSAGES = 20  # Sa mesazhe të ruajmë për sesion

def add_to_memory(session_id: str, role: str, content: str):
    """Shto mesazh në memorien e bisedës"""
    conversation_memory[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    # Mbaj vetëm mesazhet e fundit
    if len(conversation_memory[session_id]) > MAX_MEMORY_MESSAGES:
        conversation_memory[session_id] = conversation_memory[session_id][-MAX_MEMORY_MESSAGES:]

def get_conversation_history(session_id: str) -> list:
    """Merr historikun e bisedës për një sesion"""
    return conversation_memory.get(session_id, [])

def get_conversation_context(session_id: str) -> str:
    """Kthen kontekstin e bisedës si tekst për system prompt"""
    history = get_conversation_history(session_id)
    if not history:
        return ""
    
    context = "\n## 💬 CONVERSATION HISTORY (Last messages)\n"
    for msg in history[-10:]:  # Vetëm 10 të fundit për prompt
        role_icon = "👤" if msg["role"] == "user" else "🌊"
        context += f"{role_icon} {msg['role'].upper()}: {msg['content'][:200]}...\n" if len(msg['content']) > 200 else f"{role_icon} {msg['role'].upper()}: {msg['content']}\n"
    
    return context


# ═══════════════════════════════════════════════════════════════════
# TASK TRACKER - Detekton dhe mban mend çfarë po bëjmë
# ═══════════════════════════════════════════════════════════════════

# Task patterns - fjalë kyçe që tregojnë llojin e detyrës
TASK_PATTERNS = {
    "debugging": ["debug", "gabim", "error", "bug", "fix", "rregull", "problem", "issue", "nuk punon", "crash"],
    "development": ["krijo", "create", "build", "ndërto", "zhvillo", "develop", "implement", "shto", "add"],
    "testing": ["test", "provo", "check", "verify", "kontrollo", "valido"],
    "analysis": ["analizo", "analyze", "shiko", "review", "vlerëso", "evaluate"],
    "learning": ["mëso", "learn", "kuptoj", "understand", "explain", "shpjego"],
    "configuration": ["konfigurim", "config", "setup", "setting", "vendos"],
    "deployment": ["deploy", "publish", "ship", "release", "production"],
    "documentation": ["dokumento", "document", "shkruaj", "write", "readme"],
}

# Active tasks per session
active_tasks: dict = defaultdict(dict)

def detect_task(message: str, session_id: str) -> str:
    """Detekton llojin e detyrës nga mesazhi"""
    msg_lower = message.lower()
    
    for task_type, keywords in TASK_PATTERNS.items():
        for keyword in keywords:
            if keyword in msg_lower:
                # Ruaj detyrën aktive
                active_tasks[session_id] = {
                    "type": task_type,
                    "detected_at": datetime.now().isoformat(),
                    "trigger_keyword": keyword,
                    "original_message": message[:100]
                }
                return task_type
    
    return active_tasks.get(session_id, {}).get("type", "general")

def get_task_context(session_id: str) -> str:
    """Kthen kontekstin e detyrës aktive"""
    task = active_tasks.get(session_id, {})
    if not task:
        return ""
    
    task_instructions = {
        "debugging": "🔧 MODE: DEBUGGING - Ji i fokusuar, jep zgjidhje konkrete, kontrollo logs dhe errors",
        "development": "⚙️ MODE: DEVELOPMENT - Jep kod të pastër, shpjego strukturën, ndiq best practices",
        "testing": "🧪 MODE: TESTING - Jep test cases, kontrollo edge cases, valido rezultatet",
        "analysis": "📊 MODE: ANALYSIS - Ji analitik, jep insights, identifiko patterns",
        "learning": "📚 MODE: LEARNING - Shpjego qartë, jep shembuj, përdor analogji",
        "configuration": "⚙️ MODE: CONFIGURATION - Jep udhëzime hap-pas-hapi, kontrollo settings",
        "deployment": "🚀 MODE: DEPLOYMENT - Ji i kujdesshëm, kontrollo çdo hap, backup first",
        "documentation": "📝 MODE: DOCUMENTATION - Shkruaj qartë, strukturo mirë, jep shembuj",
    }
    
    return f"\n## 🎯 ACTIVE TASK\n{task_instructions.get(task.get('type', 'general'), '')}\n"


# ═══════════════════════════════════════════════════════════════════
# USER PREFERENCES - Ruan preferencat e përdoruesit
# ═══════════════════════════════════════════════════════════════════

# User preferences storage
user_preferences: dict = defaultdict(dict)

DEFAULT_PREFERENCES = {
    "language": "auto",  # auto, sq, en
    "tone": "professional",  # professional, casual, technical
    "verbosity": "balanced",  # brief, balanced, detailed
    "code_style": "commented",  # minimal, commented, verbose
}

def get_user_preferences(user_id: str) -> dict:
    """Merr preferencat e përdoruesit"""
    if user_id not in user_preferences:
        user_preferences[user_id] = DEFAULT_PREFERENCES.copy()
    return user_preferences[user_id]

def update_user_preferences(user_id: str, **kwargs):
    """Përditëso preferencat e përdoruesit"""
    prefs = get_user_preferences(user_id)
    prefs.update(kwargs)
    user_preferences[user_id] = prefs

def get_preferences_context(user_id: str) -> str:
    """Kthen kontekstin e preferencave për system prompt"""
    prefs = get_user_preferences(user_id)
    
    context = "\n## 👤 USER PREFERENCES\n"
    context += f"- Language: {prefs.get('language', 'auto')}\n"
    context += f"- Tone: {prefs.get('tone', 'professional')}\n"
    context += f"- Verbosity: {prefs.get('verbosity', 'balanced')}\n"
    context += f"- Code Style: {prefs.get('code_style', 'commented')}\n"
    
    return context


def apply_translation_override(text: str) -> str:
    """
    Apliko korrigjime të përkthimeve PARA se të shkojë te modeli.
    Zëvendëson fjalët problematike me versionet e sakta.
    """
    if not text:
        return text
    
    result = text.lower()
    
    # Zëvendëso sipas lexicon-it (frazat më të gjata së pari)
    sorted_lexicon = sorted(LEXICON_CUSTOM.items(), key=lambda x: len(x[0]), reverse=True)
    
    for albanian, english in sorted_lexicon:
        if albanian.lower() in result:
            # Ruaj kontekstin shqip por shto përkthimin
            # Kjo ndihmon modelin të kuptojë
            pass  # Mos zëvendëso, por shto context
    
    return text  # Ruaj origjinalin, por shto context në system prompt

def get_lexicon_context() -> str:
    """
    Kthen context për modelin me përkthimet e sakta.
    """
    context = """
## 🔤 TRANSLATION LEXICON (Albanian → English)
When user speaks Albanian, understand these correctly:
"""
    for alb, eng in list(LEXICON_CUSTOM.items())[:20]:
        context += f"- \"{alb}\" = \"{eng}\"\n"
    
    context += """
⚠️ NEVER use these words in response: vendbanim, shpirt historik, pasionshëm
✅ PREFER these technical terms: website, platform, traffic, module, service, users
"""
    return context

# ═══════════════════════════════════════════════════════════════════
# REAL-TIME CONTEXT - Date, Time, News, Weather
# ═══════════════════════════════════════════════════════════════════

def get_realtime_context() -> str:
    """Get current date, time, and day of week"""
    now = datetime.now()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    
    return f"""
## CURRENT DATE & TIME
- Date: {weekdays[now.weekday()]}, {months[now.month-1]} {now.day}, {now.year}
- Time: {now.strftime('%H:%M:%S')} (Server Time - CET/Berlin)
- Unix Timestamp: {int(now.timestamp())}

## LIVE DATA ACCESS (Use when relevant)
🌐 **Web & Knowledge:**
- Wikipedia API (general encyclopedia)
- Arxiv API (scientific papers)
- PubMed API (medical research)
- GitHub API (open source code)
- DBpedia (structured data)

📊 **Statistics & Finance:**
- Eurostat (EU statistics)
- European Central Bank (exchange rates)
- CoinGecko (crypto prices)
- World Bank Open Data

🌍 **Regional Data:**
- INSTAT Albania (Albanian statistics)
- Bank of Albania (Albanian finance)
- EU Open Data Portal
- US Census, NOAA Weather

🌤️ **Real-Time:**
- Weather (wttr.in - global)
- Air Quality (OpenAQ)
- Earthquake data (USGS)

## CLISONIX AGENTS (Internal Services)
- ALBA: Audio/EEG Analysis (port 5555)
- ALBI: Neural Biofeedback (port 6680)
- ASI: Advanced System Intelligence
- JONA: Industrial IoT Gateway
- Translation Node: 72 languages (port 8036)
"""


# ═══════════════════════════════════════════════════════════════════
# WEB BROWSING - Lexon faqe web nga interneti
# ═══════════════════════════════════════════════════════════════════

async def fetch_webpage(url: str, max_chars: int = 8000) -> str:
    """
    Lexon përmbajtjen e një faqe web duke përdorur Jina Reader (falas)
    
    Args:
        url: URL e faqes për të lexuar
        max_chars: Limite e karaktereve (default 8000)
    
    Returns:
        Teksti i pastër i faqes web
    """
    try:
        # Jina Reader - konverton çdo faqe në tekst të pastër
        jina_url = f"https://r.jina.ai/{url}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Accept": "text/plain",
                "User-Agent": "Ocean-AI/1.0 (Clisonix Cloud)"
            }
            r = await client.get(jina_url, headers=headers, follow_redirects=True)
            
            if r.status_code == 200:
                content = r.text[:max_chars]
                return content
            else:
                return f"[Gabim: Nuk u lexua faqja - HTTP {r.status_code}]"
    except httpx.TimeoutException:
        return "[Gabim: Timeout - faqja nuk u përgjigj në kohë]"
    except Exception as e:
        return f"[Gabim: {str(e)}]"


async def search_web(query: str, num_results: int = 5) -> str:
    """
    Kërkon në internet duke përdorur DuckDuckGo (falas, pa API key)
    
    Args:
        query: Pyetja për kërkim
        num_results: Numri i rezultateve
    
    Returns:
        Lista e rezultateve të kërkimit
    """
    try:
        # DuckDuckGo HTML search (pa API key)
        search_url = "https://html.duckduckgo.com/html/"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                search_url,
                data={"q": query},
                headers={"User-Agent": "Ocean-AI/1.0"}
            )
            
            if r.status_code == 200:
                # Parse rezultatet (basic extraction)
                import re
                results = []
                # Gjej titujt dhe URLs
                links = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', r.text)
                snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>([^<]+)</a>', r.text)
                
                for i, (url, title) in enumerate(links[:num_results]):
                    snippet = snippets[i] if i < len(snippets) else ""
                    results.append(f"• {title.strip()}\n  {snippet.strip()}\n  URL: {url}")
                
                if results:
                    return "\n\n".join(results)
                else:
                    return "[Nuk u gjetën rezultate]"
    except Exception as e:
        return f"[Gabim kërkimi: {str(e)}]"
    
    return ""


async def fetch_wikipedia(query: str) -> str:
    """Quick Wikipedia search"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            params = {"action": "query", "list": "search", "srsearch": query, 
                      "srlimit": 3, "format": "json"}
            r = await client.get("https://en.wikipedia.org/w/api.php", params=params)
            if r.status_code == 200:
                results = r.json().get("query", {}).get("search", [])
                if results:
                    return "\n".join([f"- {item['title']}: {item['snippet'][:150]}..." 
                                     for item in results[:3]])
    except:
        pass
    return ""


async def fetch_weather(city: str = "Tirana") -> str:
    """Get weather from wttr.in (free, no API key)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"https://wttr.in/{city}?format=j1")
            if r.status_code == 200:
                data = r.json()
                current = data.get("current_condition", [{}])[0]
                return f"Weather in {city}: {current.get('temp_C')}°C, {current.get('weatherDesc', [{}])[0].get('value', 'Unknown')}"
    except:
        pass
    return ""


def build_system_prompt(
    extra_context: str = "", 
    is_admin: bool = False,
    session_id: str = "",
    user_id: str = "",
    user_query: str = ""
) -> str:
    """Build system prompt - MINIMAL to let the model be natural"""
    
    # Conversation context - vetëm nëse ka historik
    conversation_ctx = ""
    if session_id:
        history = get_conversation_history(session_id)
        if history:
            conversation_ctx = "\nRecent conversation:\n"
            for msg in history[-5:]:
                conversation_ctx += f"{msg['role']}: {msg['content'][:150]}\n"
    
    # Minimal identity + date - lexon nga identity_loader
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y - %H:%M")
    
    # Identity nga file (jo hardcode)
    identity = load_identity()

    base = f"""You are Ocean, AI assistant for {identity['platforma']}.
Current: {date_str}

About:
{get_identity_text()}
{conversation_ctx}
Respond naturally in user's language."""

    if is_admin:
        base += f"\n[Admin: {identity['ceo']}]"
    
    return base


# Rate limiting config
FREE_TIER_LIMIT = 1000  # messages per hour (increased from 20 for better development experience)
FREE_TRIAL_MONTHS = 6
rate_limits: dict = defaultdict(list)  # user_id -> [timestamps]

def check_rate_limit(user_id: str, is_admin: bool = False) -> tuple[bool, int]:
    """Check if user is within rate limit. Returns (allowed, remaining)
    
    Args:
        user_id: User identifier (email, ID, or IP)
        is_admin: Admin users bypass all rate limits
    """
    # Admin users have no limit
    if is_admin:
        return True, float('inf')
    
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    
    # Clean old entries
    rate_limits[user_id] = [ts for ts in rate_limits[user_id] if ts > hour_ago]
    
    count = len(rate_limits[user_id])
    if count >= FREE_TIER_LIMIT:
        return False, 0
    
    rate_limits[user_id].append(now)
    return True, FREE_TIER_LIMIT - count - 1

# Persistent client (connection pool)
_client: httpx.AsyncClient = None

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=300.0,  # 5 minutes for elastic responses
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            http2=True  # HTTP/2 for multiplexing
        )
    return _client

# FastAPI
app = FastAPI(title="Ocean Nanogrid", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Req(BaseModel):
    message: str = None
    query: str = None

class Res(BaseModel):
    response: str
    time: float

@app.on_event("startup")
async def startup():
    """Warm up connection pool and preload model"""
    client = await get_client()
    try:
        await client.get(f"{OLLAMA}/api/version")
        print(f"🟢 Nanogrid ready - Ollama connected")
        
        # Preload model to RAM - eliminates cold start
        print(f"🔥 Warming up {MODEL}...")
        await client.post(
            f"{OLLAMA}/api/generate",
            json={"model": MODEL, "prompt": "", "keep_alive": "24h"},
            timeout=60.0
        )
        print(f"🚀 Model {MODEL} preloaded - zero cold start!")
    except Exception as e:
        print(f"🟡 Nanogrid ready - Ollama will connect on first request: {e}")

@app.on_event("shutdown")
async def shutdown():
    global _client
    if _client:
        await _client.aclose()

@app.get("/")
async def root():
    return {"service": "Ocean Nanogrid", "model": MODEL, "status": "awake"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/chat", response_model=Res)
async def chat(req: Req, request: Request):
    t0 = time.time()
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")
    
    # Get user identifier (IP for now, will be Clerk user_id later)
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"
    session_id = request.headers.get("X-Session-ID") or user_id  # Session = user for now
    
    # Check if admin (via header, user ID, or message content)
    is_admin = (
        request.headers.get("X-Admin") == "true" or 
        user_id in ["admin", "adm"] or
        detect_admin(q, user_id)
    )
    
    # SESSION CLOSURE CHECK - nëse përdoruesi dëshiron të largohet
    if detect_session_closure(q):
        closure_response = get_session_closure_response()
        add_to_memory(session_id, "user", q)
        add_to_memory(session_id, "assistant", closure_response)
        return Res(response=closure_response, time=round(time.time() - t0, 2))
    
    # TASK DETECTION - detekto llojin e detyrës
    task_type = detect_task(q, session_id)
    
    # Add user message to memory
    add_to_memory(session_id, "user", q)
    
    # Check rate limit
    allowed, remaining = check_rate_limit(user_id, is_admin=is_admin)
    if not allowed:
        raise HTTPException(429, detail={
            "error": "Rate limit exceeded",
            "limit": FREE_TIER_LIMIT,
            "period": "1 hour",
            "upgrade_url": "https://clisonix.com/pricing"
        })
    
    client = await get_client()
    
    try:
        # Build prompt with all context keys
        system_prompt = build_system_prompt(
            is_admin=is_admin,
            session_id=session_id,
            user_id=user_id,
            user_query=q
        )
        
        r = await client.post(f"{OLLAMA}/api/chat", json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": q}
            ],
            "stream": False,
            "options": {
                "num_ctx": 8192,
                "num_predict": -1,
                "temperature": 0.7,
                "num_keep": 0,
                "mirostat": 0,
                "repeat_last_n": 64,
                "stop": []
            }
        })
        resp = r.json().get("message", {}).get("content", "")
        
        # Save response to memory
        add_to_memory(session_id, "assistant", resp)
        
    except Exception as e:
        raise HTTPException(500, str(e))
    
    return Res(response=resp, time=round(time.time() - t0, 2))


# ═══════════════════════════════════════════════════════════════════
# STREAMING ENDPOINT - First token in 2-3 seconds!
# ═══════════════════════════════════════════════════════════════════

async def stream_ollama(query: str, is_admin: bool = False, session_id: str = "", user_id: str = "") -> AsyncGenerator[str, None]:
    """Stream response from Ollama - text appears immediately!"""
    # Streaming client me timeout pa limit
    stream_client = httpx.AsyncClient(
        timeout=httpx.Timeout(None, connect=30.0),
        http2=True
    )
    system_prompt = build_system_prompt(is_admin=is_admin, session_id=session_id, user_id=user_id, user_query=query)
    
    try:
        async with stream_client.stream(
            "POST",
            f"{OLLAMA}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "stream": True,  # STREAMING!
                "options": {
                    "num_ctx": 8192,
                    "num_predict": -1,
                    "temperature": 0.7,
                    "num_keep": 0,
                    "mirostat": 0
                }
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
        yield f"\n[Error: {str(e)}]"
    finally:
        await stream_client.aclose()


@app.post("/api/v1/chat/stream")
async def chat_stream(req: Req, request: Request):
    """
    STREAMING chat endpoint!
    First token appears within 2-3 seconds instead of waiting 60+ seconds.
    """
    q = req.message or req.query
    if not q:
        raise HTTPException(400, "message required")
    
    # Get identifiers
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"
    session_id = request.headers.get("X-Session-ID") or user_id
    
    is_admin = (
        request.headers.get("X-Admin") == "true" or 
        detect_admin(q, user_id)
    )
    
    # Rate limit check
    allowed, remaining = check_rate_limit(user_id, is_admin=is_admin)
    if not allowed:
        raise HTTPException(429, "Rate limit exceeded")
    
    # SESSION CLOSURE CHECK - nëse përdoruesi dëshiron të largohet
    if detect_session_closure(q):
        closure_resp = get_session_closure_response()
        add_to_memory(session_id, "user", q)
        add_to_memory(session_id, "assistant", closure_resp)
        async def closure_stream():
            yield closure_resp
        return StreamingResponse(closure_stream(), media_type="text/plain")
    
    # Task detection and memory
    detect_task(q, session_id)
    add_to_memory(session_id, "user", q)
    
    # Create streaming response with memory saving
    async def stream_with_memory():
        full_response = []
        async for chunk in stream_ollama(q, is_admin=is_admin, session_id=session_id, user_id=user_id):
            full_response.append(chunk)
            yield chunk
        # Save complete response to memory
        add_to_memory(session_id, "assistant", "".join(full_response))
    
    return StreamingResponse(
        stream_with_memory(),
        media_type="text/plain"
    )


@app.post("/api/v1/query", response_model=Res)
async def query(req: Req, request: Request):
    return await chat(req, request)

@app.get("/api/v1/rate-limit")
async def get_rate_limit(request: Request):
    """Check current rate limit status"""
    user_id = request.headers.get("X-User-ID") or request.client.host or "anonymous"
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    
    # Clean and count
    rate_limits[user_id] = [ts for ts in rate_limits[user_id] if ts > hour_ago]
    count = len(rate_limits[user_id])
    
    return {
        "user_id": user_id,
        "used": count,
        "limit": FREE_TIER_LIMIT,
        "remaining": max(0, FREE_TIER_LIMIT - count),
        "period": "1 hour",
        "tier": "free_trial",
        "trial_months": FREE_TRIAL_MONTHS
    }

@app.get("/api/v1/status")
async def status():
    return {"status": "ok", "model": MODEL, "mode": "nanogrid", "realtime": True}


# ═══════════════════════════════════════════════════════════════════
# REAL-TIME DATA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/now")
async def get_now():
    """Get current date/time"""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": now.strftime("%A"),
        "timestamp": now.isoformat(),
        "timezone": "CET/Berlin"
    }


@app.get("/api/v1/weather/{city}")
async def get_weather(city: str = "Tirana"):
    """Get weather for a city"""
    weather = await fetch_weather(city)
    return {"city": city, "weather": weather}


@app.get("/api/v1/wiki/{query}")
async def get_wiki(query: str):
    """Search Wikipedia"""
    results = await fetch_wikipedia(query)
    return {"query": query, "results": results}


# ═══════════════════════════════════════════════════════════════════
# WEB BROWSING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/browse")
async def browse_webpage(url: str, max_chars: int = 8000):
    """
    Lexon përmbajtjen e një faqe web
    
    Përdorimi:
        GET /api/v1/browse?url=https://example.com
        GET /api/v1/browse?url=https://example.com&max_chars=4000
    
    Returns:
        Teksti i pastër i faqes web
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    content = await fetch_webpage(url, max_chars)
    return {
        "url": url,
        "content": content,
        "chars": len(content)
    }


@app.get("/api/v1/search")
async def web_search(q: str, num: int = 5):
    """
    Kërkon në internet
    
    Përdorimi:
        GET /api/v1/search?q=python tutorials
        GET /api/v1/search?q=weather tirana&num=3
    
    Returns:
        Lista e rezultateve nga DuckDuckGo
    """
    results = await search_web(q, num)
    return {
        "query": q,
        "results": results,
        "source": "DuckDuckGo"
    }


@app.post("/api/v1/chat/browse")
async def chat_with_webpage(request: Request):
    """
    Chat me kontekstin e një faqe web
    
    Body:
    {
        "url": "https://example.com",
        "message": "Çfarë thotë kjo faqe?"
    }
    
    Ocean lexon faqen dhe përgjigjet bazuar në përmbajtjen
    """
    body = await request.json()
    url = body.get("url", "")
    message = body.get("message", body.get("query", ""))
    
    if not url:
        raise HTTPException(400, "url required")
    if not message:
        raise HTTPException(400, "message required")
    
    # Lexo faqen
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    webpage_content = await fetch_webpage(url, max_chars=6000)
    
    # Krijo prompt me kontekstin e faqes
    enhanced_message = f"""Përdoruesi dëshiron informacion nga kjo faqe web:

=== PËRMBAJTJA E FAQES ({url}) ===
{webpage_content}
=== FUND FAQES ===

Pyetja e përdoruesit: {message}

Përgjigju bazuar në përmbajtjen e faqes më sipër. Nëse informacioni nuk gjendet, thuaje qartë."""

    # Thirr Ollama
    client = await get_client()
    system_prompt = build_system_prompt()
    
    try:
        r = await client.post(f"{OLLAMA}/api/chat", json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_message}
            ],
            "stream": False,
            "options": {"num_ctx": 8192, "temperature": 0.7}
        })
        
        if r.status_code == 200:
            response_text = r.json().get("message", {}).get("content", "")
            return {
                "url": url,
                "message": message,
                "response": response_text
            }
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")
    
    raise HTTPException(500, "No response from AI")


# ═══════════════════════════════════════════════════════════════════
# MORE DATA SOURCES
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/crypto/{symbol}")
async def get_crypto(symbol: str = "bitcoin"):
    """Get crypto price from CoinGecko (free)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd,eur")
            if r.status_code == 200:
                return {"symbol": symbol, "prices": r.json()}
    except:
        pass
    return {"symbol": symbol, "error": "Could not fetch price"}


@app.get("/api/v1/github/{owner}/{repo}")
async def get_github_repo(owner: str, repo: str):
    """Get GitHub repo info"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
            if r.status_code == 200:
                data = r.json()
                return {
                    "name": data.get("full_name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "language": data.get("language"),
                    "url": data.get("html_url")
                }
    except:
        pass
    return {"error": "Could not fetch repo"}


@app.get("/api/v1/arxiv/{query}")
async def search_arxiv(query: str):
    """Search scientific papers on Arxiv"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=5")
            if r.status_code == 200:
                # Parse XML response (simplified)
                text = r.text
                titles = []
                import re
                for match in re.findall(r'<title>(.*?)</title>', text):
                    if match != "ArXiv Query":
                        titles.append(match.strip())
                return {"query": query, "papers": titles[:5]}
    except:
        pass
    return {"query": query, "papers": []}


@app.get("/api/v1/earthquake")
async def get_earthquakes():
    """Get recent earthquakes from USGS"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson")
            if r.status_code == 200:
                data = r.json()
                quakes = []
                for f in data.get("features", [])[:5]:
                    props = f.get("properties", {})
                    quakes.append({
                        "place": props.get("place"),
                        "magnitude": props.get("mag"),
                        "time": props.get("time")
                    })
                return {"earthquakes": quakes}
    except:
        pass
    return {"earthquakes": []}


@app.get("/api/v1/sources")
async def list_sources():
    """List all available data sources"""
    return {
        "realtime": ["now", "weather", "earthquake"],
        "knowledge": ["wiki", "arxiv", "github"],
        "finance": ["crypto"],
        "agents": ["alba", "albi", "asi", "jona", "translation"]
    }


# Keep-alive pulse (background)
async def keep_alive():
    """Pulse every 30s to keep Ollama model hot"""
    while True:
        await asyncio.sleep(30)
        try:
            client = await get_client()
            await client.get(f"{OLLAMA}/api/ps")
        except:
            pass

@app.on_event("startup")
async def start_keepalive():
    asyncio.create_task(keep_alive())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

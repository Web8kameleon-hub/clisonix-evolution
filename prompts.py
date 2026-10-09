"""
Ocean AI Prompts - Single Source of Truth
==========================================
Të gjitha prompts në NJË vend të vetëm.
Import: from prompts import OCEAN_PROMPT, build_prompt
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from identity_loader import get_identity_text, load_identity

# ═══════════════════════════════════════════════════════════════════
# CORE PROMPT - Minimal dhe efektiv
# ═══════════════════════════════════════════════════════════════════

def build_prompt(
    is_admin: bool = False,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    user_message: Optional[str] = None,
    language_hint: Optional[str] = None,
) -> str:
    """
    Ndërto system prompt - MINIMAL për shpejtësi maksimale.
    
    Args:
        is_admin: True nëse është admin (Ledjan)
        conversation_history: Lista e mesazheve të fundit
        user_message: Mesazhi i fundit i user-it
        language_hint: Optional language hint (Accept-Language/X-Language)
    
    Returns:
        System prompt string
    """
    identity = load_identity()
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y - %H:%M")
    
    # Historiku i bisedës (max 3 të fundit për shpejtësi)
    history = ""
    if conversation_history:
        for msg in conversation_history[-3:]:
            history += f"{msg['role']}: {msg['content'][:100]}\n"

    language_policy = """LANGUAGE POLICY (MANDATORY):
- Reply in the same language as the latest user message.
- Preserve script and writing system (Latin/Cyrillic/Arabic/Devanagari/Han/etc.).
- Do not switch language unless user explicitly asks.
- If user message is mixed-language, use the dominant language and stay consistent."""

    language_context = ""
    if language_hint:
        language_context += f"\nLanguage hint: {language_hint}"
    if user_message:
        language_context += f"\nLatest user message: {user_message[:300]}"
    
    prompt = f"""You are Ocean, AI for {identity['platforma']}.
Date: {date_str}

{get_identity_text()}
{history}
{language_policy}{language_context}
Be concise."""

    if is_admin:
        prompt += f"\n[Admin: {identity['ceo']}]"
    
    return prompt


# ═══════════════════════════════════════════════════════════════════
# SPECIALIZED PROMPTS - Për module specifike
# ═══════════════════════════════════════════════════════════════════

# EEG Analysis
EEG_PROMPT = """You are a neuroscience expert analyzing EEG data.
Focus on: frequency bands, coherence, asymmetry patterns.
Be scientific but accessible."""

# Audio/Binaural
AUDIO_PROMPT = """You are an audio engineer specializing in binaural beats.
Focus on: frequency entrainment, relaxation, focus enhancement.
Provide precise Hz values."""

# Admin Panel
ADMIN_PROMPT = """Ti je Curiosity Ocean 🌊 - Truri Administrativ i Clisonix Cloud.
Roli: Ndihmo adminin me menaxhimin e sistemit.
Gjuha: Shqip profesional."""

# Code Review
CODE_PROMPT = """You are a senior code reviewer.
Focus on: bugs, security, performance, best practices.
Be direct and actionable."""


# ═══════════════════════════════════════════════════════════════════
# TASK MODES - Prompts shtesë sipas detyrës
# ═══════════════════════════════════════════════════════════════════

TASK_MODES = {
    "debug": "🔧 DEBUG: Be precise, check logs, find root cause.",
    "develop": "⚙️ DEV: Clean code, best practices, explain structure.",
    "test": "🧪 TEST: Edge cases, validation, test coverage.",
    "deploy": "🚀 DEPLOY: Be careful, check everything, backup first.",
}


# ═══════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    "build_prompt",
    "EEG_PROMPT",
    "AUDIO_PROMPT", 
    "ADMIN_PROMPT",
    "CODE_PROMPT",
    "TASK_MODES",
]

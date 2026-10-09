"""
SPECIALIZED EXPERT CORE MODULE
==============================

Shared core logic for Specialized Expert Chat:
- Domain alias normalization
- Expert prompt construction
- Timeout policy
- Stable response payload shaping
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class SpecializedExpertCore:
    DOMAIN_ALIASES: Dict[str, str] = {
        "neuro": "neuroscience",
        "neuroscience": "neuroscience",
        "ai": "ai_ml",
        "ai_ml": "ai_ml",
        "ml": "ai_ml",
        "bio": "biotech",
        "biotech": "biotech",
        "biotechnology": "biotech",
        "data": "data_science",
        "data_science": "data_science",
        "datascience": "data_science",
        "quantum": "quantum",
        "iot": "iot",
        "security": "security",
        "cyber": "security",
        "marine": "marine",
    }

    def __init__(self):
        self.model_timeout_seconds = float(os.getenv("SPECIALIZED_CHAT_MODEL_TIMEOUT_SECONDS", "35"))

    def normalize_domain(self, domain: Optional[str], known_domains: Dict[str, Dict[str, Any]]) -> Optional[str]:
        if not domain:
            return None

        normalized = self.DOMAIN_ALIASES.get(str(domain).strip().lower())
        if normalized and normalized in known_domains:
            return normalized

        direct = str(domain).strip().lower()
        if direct in known_domains:
            return direct

        return None

    def build_system_prompt(
        self,
        domain_name: str,
        conversation_context: str = "",
        main_topic: Optional[str] = None,
    ) -> str:
        context_hint = ""
        if conversation_context and main_topic:
            context_hint = (
                f"\nConversation context: We were discussing '{main_topic}'.\n"
                f"{conversation_context}\n"
            )

        return f"""You are Ocean AI, the intelligent assistant for Clisonix Cloud Platform.
You are an expert in {domain_name}.
{context_hint}
CRITICAL RULES:
1. ALWAYS respond in the SAME LANGUAGE as the user's question
2. Keep responses concise and professional
3. NEVER say you are "Phi" or "developed by Microsoft" - you are Ocean AI by Clisonix
4. If asked about yourself, say: "I am Ocean AI, the intelligent assistant for Clisonix Cloud Platform, created by Ledjan Ahmati"
5. If there is conversation context, continue naturally from it

About Clisonix:
- Founder & CEO: Ledjan Ahmati
- Organization: WEB8euroweb GmbH
- Specialized in Industrial Intelligence with REST APIs, IoT/LoRa sensors, and real-time analytics
"""

    def build_response_payload(
        self,
        *,
        payload_type: str,
        query: str,
        domain: Optional[str],
        domain_expertise: str,
        answer: str,
        sources: List[str],
        confidence: float,
        follow_up_topics: List[str],
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = {
            "type": payload_type,
            "query": query,
            "domain": domain,
            "domain_expertise": domain_expertise,
            "answer": answer,
            "response": answer,
            "sources": sources,
            "confidence": confidence,
            "follow_up_topics": follow_up_topics,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if extra:
            response.update(extra)
        return response

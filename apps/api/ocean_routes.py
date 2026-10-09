<<<<<<< HEAD
"""
Curiosity Ocean Routes - Integrated with Groq (LLM) + Hybrid Biometric API
Real-time conversational system with biometric context awareness
Author: Ledjan Ahmati
License: Closed Source
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse

try:
    from groq_ocean_integration import get_groq_client
except ImportError:
    from .groq_ocean_integration import get_groq_client

logger = logging.getLogger("curiosity_ocean_routes")

router = APIRouter(prefix="/api/ocean", tags=["Curiosity Ocean"])

# Configuration from environment
HYBRID_BIOMETRIC_API = os.getenv(
    "HYBRID_BIOMETRIC_API",
    "http://127.0.0.1:8000"  # Internal API endpoint
)
GROQ_API = "groq"  # Via groq_ocean_integration


class OceanSession:
    """Manages Ocean conversation session with biometric data"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[Dict[str, str]] = []
        self.biometric_context: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        self.last_activity = datetime.utcnow()
    
    def update_biometric(self, data: Dict[str, Any]):
        """Update biometric context from Hybrid API"""
        self.biometric_context.update(data)
        self.last_activity = datetime.utcnow()


# In-memory session storage (use Redis in production)
_sessions: Dict[str, OceanSession] = {}


# ============================================================================
# 🌊 CURIOSITY OCEAN ENDPOINTS
# ============================================================================


@router.post("/chat")
async def ocean_chat(
    question: str,
    session_id: Optional[str] = None,
    use_biometric_context: bool = True
) -> Dict[str, Any]:
    """
    Chat with Curiosity Ocean
    
    - Uses Groq for LLM responses (fast & intelligent)
    - Optionally includes Hybrid Biometric context (user's health data)
    - Maintains conversation history per session
    
    Args:
        question: User's question
        session_id: Existing session or create new
        use_biometric_context: Include health data in context
    
    Returns:
        Response with answer, biometric insights, and session info
    """
    try:
        # Create or get session
        if not session_id:
            session_id = str(__import__('uuid').uuid4())
        
        if session_id not in _sessions:
            _sessions[session_id] = OceanSession(session_id)
        
        session = _sessions[session_id]
        
        # Get Groq client
        groq = get_groq_client()
        
        # Fetch biometric context if enabled
        biometric_data = None
        if use_biometric_context:
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    # Get latest phone sensor data from Hybrid API
                    resp = await client.get(
                        f"{HYBRID_BIOMETRIC_API}/api/phone/sensors",
                        headers={"X-Session-ID": session_id}
                    )
                    if resp.status_code == 200:
                        biometric_data = resp.json()
                        session.update_biometric(biometric_data)
            except Exception as e:
                logger.warning(f"Could not fetch biometric data: {e}")
        
        # Build context-aware prompt
        system_message = """You are Curiosity Ocean, an intelligent conversational AI integrated with health monitoring.
You have access to real-time biometric data from the user.
Be helpful, curious, and consider their health context when relevant."""
        
        if biometric_data:
            hr = biometric_data.get("heartRate", {}).get("value", "unknown")
            temp = biometric_data.get("temperature", {}).get("value", "unknown")
            system_message += f"\n\nCurrent user biometrics: Heart Rate={hr} bpm, Temperature={temp}°C"
        
        # Prepare messages for Groq
        messages = [{"role": "system", "content": system_message}]
        messages.extend(session.conversation_history)
        
        # Get response from Groq
        groq_response = await groq.chat(
            question=question,
            conversation_history=messages
        )
        
        if "error" in groq_response:
            logger.error(f"Groq error: {groq_response['error']}")
            answer = groq_response.get("answer", "I encountered an error processing your question.")
        else:
            answer = groq_response.get("answer", "")
        
        # Store in session history
        session.add_message("user", question)
        session.add_message("assistant", answer)
        
        return {
            "success": True,
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "biometric_context": biometric_data or None,
            "conversation_length": len(session.conversation_history),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Ocean chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/stream")
async def ocean_chat_stream(
    question: str,
    session_id: Optional[str] = None
) -> StreamingResponse:
    """Stream Groq response for real-time chat"""
    try:
        if not session_id:
            session_id = str(__import__('uuid').uuid4())
        
        if session_id not in _sessions:
            _sessions[session_id] = OceanSession(session_id)
        
        session = _sessions[session_id]
        groq = get_groq_client()
        
        async def generate():
            async for chunk in groq.stream_chat(
                question=question,
                conversation_history=session.conversation_history
            ):
                yield chunk
            
            session.add_message("user", question)
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/biometric-insights")
async def get_biometric_insights(session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get biometric insights from Hybrid API
    
    Returns:
        Current health metrics from phone sensors + clinic devices
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            # Get phone sensors
            phone_resp = await client.get(
                f"{HYBRID_BIOMETRIC_API}/api/phone/sensors"
            )
            
            # Get clinical data
            clinic_resp = await client.get(
                f"{HYBRID_BIOMETRIC_API}/api/clinic/stream",
                headers={"X-Session-ID": session_id or "default"}
            )
            
            phone_data = phone_resp.json() if phone_resp.status_code == 200 else {}
            clinic_data = clinic_resp.json() if clinic_resp.status_code == 200 else {}
            
            return {
                "success": True,
                "phone_sensors": phone_data,
                "clinic_devices": clinic_data,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Biometric insights error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "phone_sensors": {},
            "clinic_devices": {}
        }


@router.get("/session/{session_id}")
async def get_session_info(session_id: str) -> Dict[str, Any]:
    """Get conversation session information"""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _sessions[session_id]
    return {
        "session_id": session_id,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "conversation_length": len(session.conversation_history),
        "biometric_data_points": len(session.biometric_context),
        "biometric_keys": list(session.biometric_context.keys())
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """End conversation session"""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"status": "deleted", "session_id": session_id}
    
    raise HTTPException(status_code=404, detail="Session not found")


@router.get("/status")
async def ocean_status() -> Dict[str, Any]:
    """Get Curiosity Ocean status"""
    groq = get_groq_client()
    
    # Test Hybrid Biometric API
    hybrid_healthy = False
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(f"{HYBRID_BIOMETRIC_API}/health")
            hybrid_healthy = resp.status_code == 200
    except:
        pass
    
    return {
        "service": "Curiosity Ocean",
        "status": "operational",
        "components": {
            "groq_llm": groq.get_status(),
            "hybrid_biometric": {
                "endpoint": HYBRID_BIOMETRIC_API,
                "status": "healthy" if hybrid_healthy else "unavailable"
            }
        },
        "active_sessions": len(_sessions),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/test-integration")
async def test_integration() -> Dict[str, Any]:
    """Test Groq + Hybrid Biometric integration"""
    results = {}
    
    # Test Groq
    groq = get_groq_client()
    groq_status = groq.get_status()
    results["groq"] = groq_status
    
    if groq_status["configured"]:
        try:
            response = await groq.chat("Hello, are you working?")
            results["groq"]["test"] = "success"
            results["groq"]["sample_response"] = response.get("answer", "")[:100]
        except Exception as e:
            results["groq"]["test"] = "failed"
            results["groq"]["error"] = str(e)
    
    # Test Hybrid Biometric API
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{HYBRID_BIOMETRIC_API}/api/phone/sensors")
            results["hybrid_biometric"] = {
                "status": "connected",
                "endpoint": HYBRID_BIOMETRIC_API,
                "response_time_ms": resp.elapsed.total_seconds() * 1000
            }
    except Exception as e:
        results["hybrid_biometric"] = {
            "status": "disconnected",
            "endpoint": HYBRID_BIOMETRIC_API,
            "error": str(e)
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "integration_test": results
    }


# ============================================================================
# 🧠 ADVANCED FEATURES
# ============================================================================


@router.post("/analyze-with-context")
async def analyze_with_biometric_context(
    question: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Advanced analysis combining:
    - Groq LLM intelligence
    - Real-time biometric data
    - Personalized insights
    """
    try:
        # Get biometric data
        biometric_resp = await get_biometric_insights(session_id)
        
        # Add biometric context to question
        context_prompt = f"""
Question: {question}

Biometric Context:
- Heart Rate: {biometric_resp.get('phone_sensors', {}).get('heartRate', {}).get('value', 'N/A')} bpm
- Temperature: {biometric_resp.get('phone_sensors', {}).get('temperature', {}).get('value', 'N/A')}°C
- Clinical Data Available: {bool(biometric_resp.get('clinic_devices', {}))}

Please provide insights considering this health context.
"""
        
        # Chat with context
        response = await ocean_chat(
            question=context_prompt,
            session_id=session_id,
            use_biometric_context=True
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Context analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
=======
"""
Curiosity Ocean Routes - Local AI + Hybrid Biometric API
Real-time conversational system with biometric context awareness
Author: Ledjan Ahmati
License: Closed Source
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse

from .clisonix_ai_engine import ClisonixAIEngine
from .clisonix_identity import IdentityLanguage, get_clisonix_identity

logger = logging.getLogger("curiosity_ocean_routes")

router = APIRouter(prefix="/api/ocean", tags=["Curiosity Ocean"])

# Configuration from environment
HYBRID_BIOMETRIC_API = os.getenv(
    "HYBRID_BIOMETRIC_API",
    "http://127.0.0.1:8000"  # Internal API endpoint
)
# Ocean-Core: primary AI brain for all chat responses
OCEAN_CORE_URL = os.getenv("OCEAN_CORE_URL", "http://clisonix-ocean-core:8030")
LOCAL_AI = "clisonix-local"
local_ai_engine = ClisonixAIEngine()


class OceanSession:
    """Manages Ocean conversation session with biometric data"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_history: List[Dict[str, str]] = []
        self.biometric_context: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        self.last_activity = datetime.utcnow()
    
    def update_biometric(self, data: Dict[str, Any]):
        """Update biometric context from Hybrid API"""
        self.biometric_context.update(data)
        self.last_activity = datetime.utcnow()


# In-memory session storage (use Redis in production)
_sessions: Dict[str, OceanSession] = {}


# ============================================================================
# 🔷 CLISONIX IDENTITY ENDPOINTS
# ============================================================================


@router.get("/identity")
async def get_identity(language: str = "en") -> Dict[str, Any]:
    """
    Get Clisonix system identity and self-awareness
    
    Args:
        language: Language code (sq, en, it, es, fr, de)
    
    Returns:
        Complete system identity, capabilities, and architecture
    """
    try:
        # Map language string to enum
        lang_map = {
            "sq": IdentityLanguage.ALBANIAN,
            "en": IdentityLanguage.ENGLISH,
            "it": IdentityLanguage.ITALIAN,
            "es": IdentityLanguage.SPANISH,
            "fr": IdentityLanguage.FRENCH,
            "de": IdentityLanguage.GERMAN,
        }
        lang = lang_map.get(language, IdentityLanguage.ENGLISH)
        
        identity = get_clisonix_identity()
        
        return {
            "success": True,
            "identity": {
                "name": identity.identity.name,
                "version": identity.identity.version,
                "type": identity.identity.type,
                "layers": identity.identity.layers,
                "mission": identity.identity.mission
            },
            "introduction": identity.get_identity_intro(lang),
            "full_description": identity.get_full_identity(lang),
            "trinity_system": identity.get_trinity_description(lang),
            "curiosity_ocean": identity.get_ocean_description(lang),
            "purpose": identity.get_purpose(lang),
            "capabilities": identity.get_capabilities(lang),
            "system_status": identity.get_system_status(lang),
            "language": language
        }
    except Exception as e:
        logger.error(f"Error fetching identity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/identity/trinity")
async def get_trinity_info(language: str = "en") -> Dict[str, Any]:
    """
    Get ASI Trinity system information
    
    Args:
        language: Language code
    
    Returns:
        Trinity architecture (ALBA, ALBI, JONA)
    """
    try:
        identity = get_clisonix_identity()
        return {
            "success": True,
            "trinity": identity.trinity_architecture,
            "description": identity.get_trinity_description(IdentityLanguage.ENGLISH if language == "en" else IdentityLanguage.ALBANIAN)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/identity/layers")
async def get_layers_info(language: str = "en") -> Dict[str, Any]:
    """
    Get all 12 layers of Clisonix architecture
    
    Args:
        language: Language code
    
    Returns:
        Complete layer hierarchy with descriptions
    """
    try:
        lang_map = {
            "sq": IdentityLanguage.ALBANIAN,
            "en": IdentityLanguage.ENGLISH,
            "it": IdentityLanguage.ITALIAN,
            "es": IdentityLanguage.SPANISH,
            "fr": IdentityLanguage.FRENCH,
            "de": IdentityLanguage.GERMAN,
        }
        lang = lang_map.get(language, IdentityLanguage.ENGLISH)
        
        identity = get_clisonix_identity()
        
        layers = {}
        for i in range(1, 13):
            layers[f"Layer {i}"] = identity.get_layer_description(i, lang)
        
        return {
            "success": True,
            "total_layers": 12,
            "layers": layers,
            "language": language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def ocean_chat(
    question: str,
    session_id: Optional[str] = None,
    use_biometric_context: bool = True,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Chat with Curiosity Ocean
    
    - Uses local Clisonix AI for responses
    - Optionally includes Hybrid Biometric context (user's health data)
    - Maintains conversation history per session
    
    Args:
        question: User's question
        session_id: Existing session or create new
        use_biometric_context: Include health data in context
    
    Returns:
        Response with answer, biometric insights, and session info
    """
    try:
        # Create or get session
        if not session_id:
            session_id = str(__import__('uuid').uuid4())
        
        if session_id not in _sessions:
            _sessions[session_id] = OceanSession(session_id)
        
        session = _sessions[session_id]
        
        # Fetch biometric context if enabled
        biometric_data = None
        if use_biometric_context:
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    # Get latest phone sensor data from Hybrid API
                    resp = await client.get(
                        f"{HYBRID_BIOMETRIC_API}/api/phone/sensors",
                        headers={"X-Session-ID": session_id}
                    )
                    if resp.status_code == 200:
                        biometric_data = resp.json()
                        session.update_biometric(biometric_data)
            except Exception as e:
                logger.warning(f"Could not fetch biometric data: {e}")
        
        # Build context-aware prompt
        system_message = """You are Curiosity Ocean, an intelligent conversational AI integrated with health monitoring.
You have access to real-time biometric data from the user.
Be helpful, curious, and consider their health context when relevant."""
        
        if biometric_data:
            hr = biometric_data.get("heartRate", {}).get("value", "unknown")
            temp = biometric_data.get("temperature", {}).get("value", "unknown")
            system_message += f"\n\nCurrent user biometrics: Heart Rate={hr} bpm, Temperature={temp}°C"
        
        # Route to ocean-core for AI response
        try:
            async with httpx.AsyncClient(timeout=60) as oc_client:
                oc_resp = await oc_client.post(
                    f"{OCEAN_CORE_URL}/api/v1/chat",
                    json={"message": question, "language": language},
                )
                oc_resp.raise_for_status()
                answer = oc_resp.json().get("response", "")
        except Exception as oc_err:
            logger.warning(f"Ocean-Core unavailable, falling back to local engine: {oc_err}")
            local_response = local_ai_engine.curiosity_ocean_chat(
                question=question,
                mode="curious",
                ultra_thinking=False,
            )
            answer = str(local_response.get("response", ""))
        
        # Store in session history
        session.add_message("user", question)
        session.add_message("assistant", answer)
        
        return {
            "success": True,
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "biometric_context": biometric_data or None,
            "conversation_length": len(session.conversation_history),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Ocean chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/stream")
async def ocean_chat_stream(
    question: str,
    session_id: Optional[str] = None
) -> StreamingResponse:
    """Stream local AI response for real-time chat"""
    try:
        if not session_id:
            session_id = str(__import__('uuid').uuid4())
        
        if session_id not in _sessions:
            _sessions[session_id] = OceanSession(session_id)
        
        session = _sessions[session_id]
        
        async def generate():
            text_parts: list = []
            # Stream from ocean-core
            try:
                async with httpx.AsyncClient(timeout=90) as oc_client:
                    async with oc_client.stream(
                        "POST",
                        f"{OCEAN_CORE_URL}/api/v1/chat/stream",
                        json={"message": question, "language": "sq"},
                    ) as oc_stream:
                        async for line in oc_stream.aiter_lines():
                            if line:
                                chunk = line[6:].strip() if line.startswith("data: ") else line.strip()
                                if chunk and chunk not in ("[DONE]", "ping", ""):
                                    text_parts.append(chunk)
                                    yield f"data: {chunk}\n\n"
            except Exception as oc_err:
                logger.warning(f"Ocean-Core stream unavailable, falling back: {oc_err}")
                local_response = local_ai_engine.curiosity_ocean_chat(
                    question=question, mode="curious", ultra_thinking=False,
                )
                text = str(local_response.get("response", ""))
                for word in text.split():
                    yield f"data: {word}\n\n"
                    await asyncio.sleep(0.01)
                text_parts = [text]

            full_text = " ".join(text_parts)
            session.add_message("user", question)
            session.add_message("assistant", full_text)
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/biometric-insights")
async def get_biometric_insights(session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get biometric insights from Hybrid API
    
    Returns:
        Current health metrics from phone sensors + clinic devices
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            # Get phone sensors
            phone_resp = await client.get(
                f"{HYBRID_BIOMETRIC_API}/api/phone/sensors"
            )
            
            # Get clinical data
            clinic_resp = await client.get(
                f"{HYBRID_BIOMETRIC_API}/api/clinic/stream",
                headers={"X-Session-ID": session_id or "default"}
            )
            
            phone_data = phone_resp.json() if phone_resp.status_code == 200 else {}
            clinic_data = clinic_resp.json() if clinic_resp.status_code == 200 else {}
            
            return {
                "success": True,
                "phone_sensors": phone_data,
                "clinic_devices": clinic_data,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Biometric insights error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "phone_sensors": {},
            "clinic_devices": {}
        }


@router.get("/session/{session_id}")
async def get_session_info(session_id: str) -> Dict[str, Any]:
    """Get conversation session information"""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _sessions[session_id]
    return {
        "session_id": session_id,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "conversation_length": len(session.conversation_history),
        "biometric_data_points": len(session.biometric_context),
        "biometric_keys": list(session.biometric_context.keys())
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> Dict[str, str]:
    """End conversation session"""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"status": "deleted", "session_id": session_id}
    
    raise HTTPException(status_code=404, detail="Session not found")


@router.get("/status")
async def ocean_status() -> Dict[str, Any]:
    """Get Curiosity Ocean status"""
    # Test Hybrid Biometric API
    hybrid_healthy = False
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(f"{HYBRID_BIOMETRIC_API}/health")
            hybrid_healthy = resp.status_code == 200
    except:
        pass
    
    return {
        "service": "Curiosity Ocean",
        "status": "operational",
        "components": {
            "local_ai": {
                "provider": LOCAL_AI,
                "status": "healthy",
                "mode": "local-only",
            },
            "hybrid_biometric": {
                "endpoint": HYBRID_BIOMETRIC_API,
                "status": "healthy" if hybrid_healthy else "unavailable"
            }
        },
        "active_sessions": len(_sessions),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/test-integration")
async def test_integration() -> Dict[str, Any]:
    """Test local AI + Hybrid Biometric integration"""
    results = {}

    try:
        response = local_ai_engine.curiosity_ocean_chat("Hello, are you working?")
        results["local_ai"] = {
            "provider": LOCAL_AI,
            "configured": True,
            "test": "success",
            "sample_response": str(response.get("response", ""))[:100],
        }
    except Exception as e:
        results["local_ai"] = {
            "provider": LOCAL_AI,
            "configured": False,
            "test": "failed",
            "error": str(e),
        }
    
    # Test Hybrid Biometric API
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{HYBRID_BIOMETRIC_API}/api/phone/sensors")
            results["hybrid_biometric"] = {
                "status": "connected",
                "endpoint": HYBRID_BIOMETRIC_API,
                "response_time_ms": resp.elapsed.total_seconds() * 1000
            }
    except Exception as e:
        results["hybrid_biometric"] = {
            "status": "disconnected",
            "endpoint": HYBRID_BIOMETRIC_API,
            "error": str(e)
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "integration_test": results
    }


# ============================================================================
# 🧠 ADVANCED FEATURES
# ============================================================================


@router.post("/analyze-with-context")
async def analyze_with_biometric_context(
    question: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Advanced analysis combining:
    - Local AI intelligence
    - Real-time biometric data
    - Personalized insights
    """
    try:
        # Get biometric data
        biometric_resp = await get_biometric_insights(session_id)
        
        # Add biometric context to question
        context_prompt = f"""
Question: {question}

Biometric Context:
- Heart Rate: {biometric_resp.get('phone_sensors', {}).get('heartRate', {}).get('value', 'N/A')} bpm
- Temperature: {biometric_resp.get('phone_sensors', {}).get('temperature', {}).get('value', 'N/A')}°C
- Clinical Data Available: {bool(biometric_resp.get('clinic_devices', {}))}

Please provide insights considering this health context.
"""
        
        # Chat with context
        response = await ocean_chat(
            question=context_prompt,
            session_id=session_id,
            use_biometric_context=True
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Context analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
>>>>>>> c1f6cec4fc9d5b7cab11712c7a2c12433881c0d0

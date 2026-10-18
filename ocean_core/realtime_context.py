"""
OCEAN REALTIME CONTEXT - Real date/time, real IP geolocation, real system evidence
===================================================================================

NO_FAKE_DATA_POLICY compliant: every value returned here is either a real,
independently verifiable measurement (server clock, a real external IP
geolocation lookup, a real health probe of a Clisonix service) or an explicit
"unavailable"/"unknown" marker. Nothing is invented or guessed.

This module answers the class of questions the LLM has no business guessing at:
  - "what time/date is it"
  - "which city/country am I in" (derived from the request's real client IP)
  - "is the Clisonix system up / are all services connected"
"""
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx
from fastapi import Request

logger = logging.getLogger("ocean_realtime_context")

# ip-api.com: free, no API key, ~45 req/min/IP. Honest source, not fabricated.
_GEOIP_URL_TEMPLATE = os.getenv("OCEAN_GEOIP_URL", "http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,timezone,query")
_GEOIP_TIMEOUT_S = float(os.getenv("OCEAN_GEOIP_TIMEOUT_S", "3.0"))
_GEOIP_CACHE_TTL_S = float(os.getenv("OCEAN_GEOIP_CACHE_TTL_S", "600"))

_PRIVATE_IP_PREFIXES = ("10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.3",
                        "192.168.", "127.", "::1", "fc00:", "fd00:")

_geoip_cache: Dict[str, Dict[str, Any]] = {}


def extract_client_ip(http_request: Optional[Request]) -> str:
    """Best-effort, real (not fabricated) client IP extraction.

    Mirrors the existing `_extract_client_id` convention used elsewhere in
    ocean_core_full.py so the two stay consistent.
    """
    if http_request is None:
        return ""
    forwarded = (http_request.headers.get("x-forwarded-for", "") or "").split(",")[0].strip()
    if forwarded:
        return forwarded
    real_ip = (http_request.headers.get("x-real-ip", "") or "").strip()
    if real_ip:
        return real_ip
    client = getattr(http_request, "client", None)
    return client.host if client else ""


def _is_private_ip(ip: str) -> bool:
    return not ip or any(ip.startswith(prefix) for prefix in _PRIVATE_IP_PREFIXES) or ip == "unknown"


def get_server_time() -> Dict[str, Any]:
    """Real server clock. Always available, never fabricated."""
    now = datetime.now(timezone.utc)
    local = datetime.now().astimezone()
    return {
        "utc_iso": now.isoformat(),
        "utc_date": now.strftime("%Y-%m-%d"),
        "utc_time": now.strftime("%H:%M:%S"),
        "server_local_iso": local.isoformat(),
        "server_local_date": local.strftime("%Y-%m-%d"),
        "server_local_time": local.strftime("%H:%M"),
        "server_timezone": local.tzname() or "UTC",
    }


async def geolocate_ip(ip: str) -> Optional[Dict[str, Any]]:
    """Real IP geolocation via an external lookup. Returns None (not a guess)
    when the IP is private/unknown or the lookup fails for any reason."""
    if _is_private_ip(ip):
        return None

    cached = _geoip_cache.get(ip)
    if cached and (time.time() - cached["_cached_at"]) < _GEOIP_CACHE_TTL_S:
        return cached["data"]

    url = _GEOIP_URL_TEMPLATE.format(ip=ip)
    try:
        async with httpx.AsyncClient(timeout=_GEOIP_TIMEOUT_S) as client:
            response = await client.get(url)
        if response.status_code != 200:
            return None
        body = response.json()
        if str(body.get("status", "")).lower() != "success":
            return None
        data = {
            "ip": ip,
            "city": body.get("city") or None,
            "region": body.get("regionName") or None,
            "country": body.get("country") or None,
            "timezone": body.get("timezone") or None,
            "source": "ip-api.com",
        }
        _geoip_cache[ip] = {"data": data, "_cached_at": time.time()}
        return data
    except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
        logger.info(f"geolocate_ip unavailable for {ip}: {exc}")
        return None


_DATETIME_PATTERNS = {
    "sq": ["sa eshte ora", "sa është ora", "sa eshte data", "sa është data", "cfare date",
           "çfarë date", "ora lokale", "data e sotme", "sa eshte ora lokale"],
    "en": ["what time is it", "what's the time", "current time", "what is the date",
           "what's the date", "today's date", "local time", "what day is it"],
    "de": ["wie spät ist es", "welches datum", "aktuelle uhrzeit", "wie viel uhr"],
}

_LOCATION_PATTERNS = {
    "sq": ["ne cilin qytet", "në cilin qytet", "ku jam", "ku ndodhem", "cili qytet jam",
           "ne cilin vend jam", "në cilin vend jam"],
    "en": ["which city", "what city am i", "where am i", "my location", "my city",
           "what country am i"],
    "de": ["welche stadt", "wo bin ich"],
}

_SYSTEM_PATTERNS = {
    "sq": ["lidhje me sistemin", "sistemi clisonix", "a jane lidhur te gjitha",
           "a funksionon platforma", "statusi i sistemit"],
    "en": ["clisonix system status", "is the system connected", "are all services up",
           "platform status", "system health"],
}


def detect_realtime_intent(prompt: str) -> Optional[str]:
    """Narrow, high-precision intent match. Returns "datetime", "location",
    "system" or None. Deliberately conservative: a miss falls through to the
    normal pipeline, it never blocks or degrades existing behavior."""
    sample = (prompt or "").strip().lower()
    if not sample:
        return None

    for patterns in _LOCATION_PATTERNS.values():
        if any(p in sample for p in patterns):
            return "location"
    for patterns in _DATETIME_PATTERNS.values():
        if any(p in sample for p in patterns):
            return "datetime"
    for patterns in _SYSTEM_PATTERNS.values():
        if any(p in sample for p in patterns):
            return "system"
    return None


async def build_datetime_answer(lang_code: str, ip: str) -> str:
    server = get_server_time()
    geo = await geolocate_ip(ip)

    if geo and geo.get("timezone"):
        try:
            import zoneinfo
            user_now = datetime.now(zoneinfo.ZoneInfo(geo["timezone"]))
            user_date = user_now.strftime("%Y-%m-%d")
            user_time = user_now.strftime("%H:%M")
            place = ", ".join(part for part in (geo.get("city"), geo.get("country")) if part)
            if lang_code == "sq":
                return (f"Sipas rajonit tënd ({place}, {geo['timezone']}): ora lokale është {user_time}, "
                        f"data {user_date}. (Ora e serverit: {server['server_local_time']} {server['server_timezone']}.)")
            if lang_code == "de":
                return (f"In deiner Region ({place}, {geo['timezone']}): es ist {user_time} Uhr, Datum {user_date}. "
                        f"(Serverzeit: {server['server_local_time']} {server['server_timezone']}.)")
            return (f"In your region ({place}, {geo['timezone']}): the local time is {user_time}, date {user_date}. "
                    f"(Server time: {server['server_local_time']} {server['server_timezone']}.)")
        except Exception as exc:  # zoneinfo lookup failures are not fatal
            logger.info(f"zoneinfo conversion failed for {geo.get('timezone')}: {exc}")

    if lang_code == "sq":
        return (f"Nuk kam akses në orën e saktë lokale të pajisjes tënde, por ora e serverit "
                f"(UTC) është {server['utc_time']}, data {server['utc_date']}.")
    if lang_code == "de":
        return (f"Ich habe keinen Zugriff auf die genaue lokale Uhrzeit deines Geräts, aber die "
                f"Serverzeit (UTC) ist {server['utc_time']}, Datum {server['utc_date']}.")
    return (f"I don't have access to your device's exact local time, but the server time "
            f"(UTC) is {server['utc_time']}, date {server['utc_date']}.")


async def build_location_answer(lang_code: str, ip: str) -> str:
    geo = await geolocate_ip(ip)
    if geo and (geo.get("city") or geo.get("country")):
        place = ", ".join(part for part in (geo.get("city"), geo.get("region"), geo.get("country")) if part)
        if lang_code == "sq":
            return f"Bazuar në IP-në e kërkesës sate, je afërsisht në: {place}. (Burimi: {geo['source']}, jo GPS i saktë.)"
        if lang_code == "de":
            return f"Basierend auf deiner IP-Adresse bist du ungefähr hier: {place}. (Quelle: {geo['source']}, keine exakte GPS-Ortung.)"
        return f"Based on your request's IP address, you're approximately in: {place}. (Source: {geo['source']}, not precise GPS.)"

    if lang_code == "sq":
        return "Nuk kam të dhëna të vërteta për vendndodhjen tënde (IP private/lokale ose kërkesa dështoi). Nuk po shpik një përgjigje."
    if lang_code == "de":
        return "Ich habe keine echten Standortdaten für dich (private/lokale IP oder die Abfrage ist fehlgeschlagen). Ich erfinde keine Antwort."
    return "I don't have real location data for you (private/local IP or the lookup failed). I won't make one up."


async def build_realtime_answer(prompt: str, lang_code: str, http_request: Optional[Request]) -> Optional[str]:
    """Single entry point for the chat handlers. Returns None when the prompt
    doesn't match a realtime intent, so callers fall through unchanged."""
    intent = detect_realtime_intent(prompt)
    if intent is None:
        return None

    ip = extract_client_ip(http_request)

    if intent == "datetime":
        return await build_datetime_answer(lang_code, ip)
    if intent == "location":
        return await build_location_answer(lang_code, ip)
    if intent == "system":
        try:
            from runtime_tools import collect_runtime_evidence
            evidence = await collect_runtime_evidence(prompt)
            observations = evidence.get("observations", [])
            # Services report their own health status in different wording
            # ("healthy", "ok", "operational", "active", "running"). Only
            # genuinely missing/unreachable/unknown responses count against
            # connectivity, so the count reflects real reachability, not a
            # single literal string match.
            healthy_words = {"healthy", "ok", "operational", "active", "running"}
            healthy = sum(1 for o in observations if str(o.get("status", "")).lower() in healthy_words)
            total = len(observations)
            unclear = [o["tool"] for o in observations if str(o.get("status", "")).lower() not in healthy_words]
            infra = evidence.get("infrastructure", [])
            infra_reachable = sum(1 for o in infra if o.get("status") == "reachable")
            unclear_note = f" Not reporting a clear healthy status: {', '.join(unclear)}." if unclear else ""
            if lang_code == "sq":
                return (f"Kontrollova direkt {total} shërbime të Clisonix: {healthy}/{total} konfirmohen aktive tani, "
                        f"plus {infra_reachable}/{len(infra)} komponentë infrastrukture (DB/cache) të arritshëm."
                        f"{unclear_note} {evidence.get('limits', '')}")
            return (f"I directly checked {total} Clisonix services: {healthy}/{total} confirmed active right now, "
                    f"plus {infra_reachable}/{len(infra)} infrastructure components (DB/cache) reachable."
                    f"{unclear_note} {evidence.get('limits', '')}")
        except Exception as exc:
            logger.warning(f"system evidence collection failed: {exc}")
            return None

    return None

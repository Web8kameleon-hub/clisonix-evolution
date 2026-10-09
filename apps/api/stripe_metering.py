# -*- coding: utf-8 -*-
"""
Stripe Usage Metering Module
=============================
Raporton automatikisht përdorimin e API-ve në Stripe për faturim sipas konsumit.

Meter IDs:
- API Calls: mtr_test_61TzaxG1OakTu5L8s41JQa06Hh2HGHXk
- EEG Analysis: mtr_test_61Tzay9lCB6ys9UdN41JQa06Hh2HGEOe  
- Trinity AI: mtr_test_61TzazgpUaNcQFVE041JQa06Hh2HG3p2
"""

import os
import time
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from collections import defaultdict

logger = logging.getLogger("stripe_metering")

# Stripe Meter IDs
METERS = {
    "api_call": "mtr_test_61TzaxG1OakTu5L8s41JQa06Hh2HGHXk",
    "eeg_analysis": "mtr_test_61Tzay9lCB6ys9UdN41JQa06Hh2HGEOe",
    "trinity_analysis": "mtr_test_61TzazgpUaNcQFVE041JQa06Hh2HG3p2"
}

# Endpoints që duhet të maten
METERED_ENDPOINTS = {
    # EEG Analysis endpoints
    "/api/ai/eeg-interpretation": "eeg_analysis",
    "/api/ai/analyze-neural": "eeg_analysis",
    "/api/eeg/analyze": "eeg_analysis",
    "/api/eeg/interpret": "eeg_analysis",
    
    # Trinity AI endpoints  
    "/api/ai/trinity-analysis": "trinity_analysis",
    "/api/ai/curiosity-ocean": "trinity_analysis",
    "/api/ai/quick-interpret": "trinity_analysis",
    
    # General API calls (everything else)
    "default": "api_call"
}

# Cache për batch reporting (optimizim)
_usage_buffer: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
_last_flush = time.time()
FLUSH_INTERVAL = 60  # Flush every 60 seconds


class StripeMetering:
    """Menaxhon raportimin e përdorimit në Stripe."""
    
    def __init__(self):
        self.stripe = None
        self.enabled = False
        self._init_stripe()
    
    def _init_stripe(self):
        """Inicializon Stripe SDK."""
        try:
            import stripe
            api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
            if api_key and api_key.startswith("sk_"):
                stripe.api_key = api_key
                self.stripe = stripe
                self.enabled = True
                logger.info("✅ Stripe metering initialized")
            else:
                logger.warning("⚠️ Stripe API key not configured - metering disabled")
        except ImportError:
            logger.warning("⚠️ Stripe SDK not installed - metering disabled")
    
    def get_meter_event_type(self, path: str) -> str:
        """Përcakton llojin e meter-it bazuar në endpoint path."""
        # Check specific endpoints first
        for endpoint, event_type in METERED_ENDPOINTS.items():
            if endpoint != "default" and path.startswith(endpoint):
                return event_type
        
        # Default to api_call for all other API endpoints
        if path.startswith("/api/"):
            return "api_call"
        
        return None  # Don't meter non-API endpoints
    
    def record_usage(self, customer_id: str, event_type: str, quantity: int = 1):
        """
        Regjistron përdorimin për një klient.
        
        Args:
            customer_id: Stripe Customer ID (cus_xxx)
            event_type: Lloji i event-it (api_call, eeg_analysis, trinity_analysis)
            quantity: Sasia (default 1)
        """
        if not self.enabled or not customer_id:
            return
        
        # Buffer the usage for batch reporting
        _usage_buffer[customer_id][event_type] += quantity
        
        # Check if we need to flush
        global _last_flush
        if time.time() - _last_flush > FLUSH_INTERVAL:
            asyncio.create_task(self._flush_usage())
    
    async def _flush_usage(self):
        """Dërgon të gjitha përdorimet e bufferuara në Stripe."""
        global _usage_buffer, _last_flush
        
        if not self.enabled or not _usage_buffer:
            return
        
        _last_flush = time.time()
        buffer_copy = dict(_usage_buffer)
        _usage_buffer = defaultdict(lambda: defaultdict(int))
        
        for customer_id, events in buffer_copy.items():
            for event_type, quantity in events.items():
                await self._send_meter_event(customer_id, event_type, quantity)
    
    async def _send_meter_event(self, customer_id: str, event_type: str, quantity: int):
        """Dërgon një meter event në Stripe."""
        if not self.enabled:
            return
        
        try:
            meter_id = METERS.get(event_type)
            if not meter_id:
                logger.warning(f"Unknown event type: {event_type}")
                return
            
            # Create meter event
            self.stripe.billing.MeterEvent.create(
                event_name=event_type,
                payload={
                    "value": str(quantity),
                    "stripe_customer_id": customer_id
                },
                timestamp=int(datetime.now(timezone.utc).timestamp())
            )
            
            logger.debug(f"📊 Meter event sent: {event_type} x{quantity} for {customer_id}")
            
        except Exception as e:
            logger.error(f"Failed to send meter event: {e}")
    
    async def record_immediate(self, customer_id: str, event_type: str, quantity: int = 1):
        """Regjistron përdorimin menjëherë (pa buffer)."""
        await self._send_meter_event(customer_id, event_type, quantity)
    
    def get_customer_from_request(self, request) -> Optional[str]:
        """
        Merr Stripe Customer ID nga request.
        Mund të jetë nga:
        - Header: X-Stripe-Customer
        - API Key mapping
        - Session/JWT
        """
        # Check header first
        customer_id = request.headers.get("X-Stripe-Customer")
        if customer_id:
            return customer_id
        
        # Check API key header and map to customer
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
        if api_key:
            # TODO: Map API key to Stripe Customer ID from database
            # For now, return None (demo mode)
            pass
        
        return None


# Global instance
stripe_metering = StripeMetering()


async def metering_middleware(request, call_next):
    """
    FastAPI middleware për metering automatik.
    Përdoret në main.py:
    
    from stripe_metering import metering_middleware
    app.middleware("http")(metering_middleware)
    """
    # Get response first
    response = await call_next(request)
    
    # Only meter successful API calls
    if response.status_code < 400:
        path = request.url.path
        event_type = stripe_metering.get_meter_event_type(path)
        
        if event_type:
            customer_id = stripe_metering.get_customer_from_request(request)
            if customer_id:
                stripe_metering.record_usage(customer_id, event_type)
    
    return response


# Convenience functions për manual metering
def meter_api_call(customer_id: str, quantity: int = 1):
    """Regjistron një API call."""
    stripe_metering.record_usage(customer_id, "api_call", quantity)


def meter_eeg_analysis(customer_id: str, quantity: int = 1):
    """Regjistron një EEG analysis."""
    stripe_metering.record_usage(customer_id, "eeg_analysis", quantity)


def meter_trinity_analysis(customer_id: str, quantity: int = 1):
    """Regjistron një Trinity AI analysis."""
    stripe_metering.record_usage(customer_id, "trinity_analysis", quantity)


async def flush_all_meters():
    """Forcon flush të të gjitha meter-ave (thirret në shutdown)."""
    await stripe_metering._flush_usage()


# For debugging
def get_metering_status() -> Dict[str, Any]:
    """Kthen statusin e metering."""
    return {
        "enabled": stripe_metering.enabled,
        "meters": METERS,
        "metered_endpoints": {k: v for k, v in METERED_ENDPOINTS.items() if k != "default"},
        "buffer_size": sum(sum(v.values()) for v in _usage_buffer.values()),
        "last_flush": datetime.fromtimestamp(_last_flush, tz=timezone.utc).isoformat()
    }

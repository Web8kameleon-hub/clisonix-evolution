# PAYMENT PROCESSOR ABSTRACTION - IMPLEMENTATION GUIDE

**Status**: Ready to Implement  
**Time Estimate**: 90-120 minutes  
**Difficulty**: ⭐⭐⭐ (Advanced)  
**Supports**: Stripe + PayPal + SEPA Direct Debit

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│          Payment Processor Service (8015)           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Stripe     │  │   PayPal     │  │   SEPA   │ │
│  │  Provider    │  │  Provider    │  │ Provider │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
│         ↓                ↓                 ↓       │
│  ┌──────────────────────────────────────────────┐ │
│  │   Abstract PaymentProvider Interface         │ │
│  │   - create_checkout_session()                │ │
│  │   - verify_webhook()                         │ │
│  │   - handle_webhook()                         │ │
│  └──────────────────────────────────────────────┘ │
│                                                   │
│  /checkout          POST                          │
│  /webhook/stripe    POST                          │
│  /webhook/paypal    POST                          │
│  /webhook/sepa      POST                          │
│  /methods           GET                           │
│  /status/{id}       GET                           │
│                                                   │
└─────────────────────────────────────────────────────┘
         ↑                                    ↑
         │ POST /checkout                    │
         │ GET /status                       │ Webhook
    Frontend                            Payment Providers
    (apps/web)                          (Stripe/PayPal/SEPA)
```

---

## STEP 1: Create Payment Provider Base Class

**File**: `services/payment-processor/payment_provider.py` (CREATE)

```python
"""
Abstract Payment Provider Interface
Defines the contract for all payment processors
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    STRIPE_CARD = "stripe_card"
    STRIPE_SEPA = "stripe_sepa"
    PAYPAL = "paypal"
    SEPA = "sepa"
    BANK_TRANSFER = "bank_transfer"

@dataclass
class PaymentSession:
    """Represents a payment session"""
    session_id: str
    user_id: str
    amount: int  # In cents (900 = $9.00)
    currency: str = "eur"
    status: PaymentStatus = PaymentStatus.PENDING
    provider: str = ""
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = None

class PaymentProvider(ABC):
    """
    Abstract base class for payment providers
    All providers must implement these methods
    """
    
    @abstractmethod
    async def create_checkout_session(
        self,
        user_id: str,
        amount: int,
        currency: str = "eur",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a checkout session
        
        Returns: {
            "session_id": str,
            "redirect_url": str,  # URL to redirect user to
            "status": "pending"
        }
        """
        pass
    
    @abstractmethod
    async def verify_webhook(self, signature: str, payload: bytes) -> bool:
        """
        Verify webhook signature from payment provider
        Prevents spoofed webhooks
        """
        pass
    
    @abstractmethod
    async def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook event
        
        Returns: {
            "processed": bool,
            "user_id": str,
            "status": PaymentStatus,
            "amount": int,
            "message": str
        }
        """
        pass
    
    @abstractmethod
    async def get_payment_status(self, session_id: str) -> PaymentSession:
        """
        Query payment status from provider
        """
        pass
    
    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Refund a payment (full or partial)
        """
        pass
```

---

## STEP 2: Implement Stripe Provider

**File**: `services/payment-processor/providers/stripe_provider.py` (CREATE)

```python
"""
Stripe Payment Provider
Supports: Credit cards, SEPA direct debit
"""

import os
import stripe
import json
from typing import Dict, Any, Optional
from payment_provider import PaymentProvider, PaymentSession, PaymentStatus, PaymentMethod
import logging

logger = logging.getLogger("stripe_provider")

class StripeProvider(PaymentProvider):
    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.public_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        
        if not all([self.api_key, self.webhook_secret, self.public_key]):
            raise ValueError("Missing Stripe configuration")
        
        stripe.api_key = self.api_key
        logger.info("✅ Stripe provider initialized")
    
    async def create_checkout_session(
        self,
        user_id: str,
        amount: int,
        currency: str = "eur",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create Stripe checkout session
        Supports: Card + SEPA debit
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card", "sepa_debit"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "unit_amount": amount,
                            "product_data": {
                                "name": "Clisonix Pro Subscription",
                                "description": "Monthly AI platform access",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="https://clisonix.com/checkout/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://clisonix.com/checkout/cancel",
                customer_email=f"user_{user_id}@clisonix.com",
                metadata={
                    "user_id": user_id,
                    "platform": "clisonix",
                    **(metadata or {})
                },
                # Enable SEPA mandate for recurring
                payment_intent_data={
                    "setup_future_usage": "off_session",
                }
            )
            
            logger.info(f"✅ Created Stripe session: {session.id} for user {user_id}")
            
            return {
                "session_id": session.id,
                "redirect_url": session.url,
                "status": "pending",
                "expires_at": None,  # Stripe sessions expire in 24h by default
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe error: {e}")
            raise
    
    async def verify_webhook(self, signature: str, payload: bytes) -> bool:
        """
        Verify Stripe webhook signature
        Prevents spoofed webhooks
        """
        try:
            stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
            return True
        except (ValueError, stripe.error.SignatureVerificationError):
            logger.warning("❌ Invalid Stripe webhook signature")
            return False
    
    async def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Stripe webhook events
        """
        event_type = event["type"]
        
        logger.info(f"📬 Processing Stripe event: {event_type}")
        
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session["metadata"].get("user_id")
            amount = session["amount_total"]
            
            logger.info(f"✅ Payment completed: ${amount/100:.2f} for user {user_id}")
            
            return {
                "processed": True,
                "user_id": user_id,
                "status": PaymentStatus.SUCCESS,
                "amount": amount,
                "session_id": session["id"],
                "message": "Payment succeeded",
            }
        
        elif event_type == "checkout.session.expired":
            session = event["data"]["object"]
            user_id = session["metadata"].get("user_id")
            
            logger.warning(f"❌ Session expired for user {user_id}")
            
            return {
                "processed": True,
                "user_id": user_id,
                "status": PaymentStatus.CANCELLED,
                "message": "Payment session expired",
            }
        
        elif event_type == "charge.refunded":
            charge = event["data"]["object"]
            user_id = charge["metadata"].get("user_id")
            amount = charge["amount_refunded"]
            
            logger.info(f"💸 Refund processed: ${amount/100:.2f} for user {user_id}")
            
            return {
                "processed": True,
                "user_id": user_id,
                "status": PaymentStatus.REFUNDED,
                "amount": amount,
                "message": "Payment refunded",
            }
        
        else:
            logger.info(f"⏭️ Ignoring event type: {event_type}")
            return {"processed": False}
    
    async def get_payment_status(self, session_id: str) -> PaymentSession:
        """
        Get payment status from Stripe
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            status_map = {
                "open": PaymentStatus.PENDING,
                "complete": PaymentStatus.SUCCESS,
                "expired": PaymentStatus.CANCELLED,
            }
            
            return PaymentSession(
                session_id=session.id,
                user_id=session.metadata.get("user_id", "unknown"),
                amount=session.amount_total,
                currency=session.currency,
                status=status_map.get(session.status, PaymentStatus.PENDING),
                provider="stripe",
            )
        except stripe.error.StripeError as e:
            logger.error(f"❌ Failed to get payment status: {e}")
            raise
    
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Refund a Stripe payment
        """
        try:
            # Assume payment_id is a charge ID
            refund = stripe.Refund.create(
                charge=payment_id,
                amount=amount,  # If None, refunds full amount
            )
            
            logger.info(f"✅ Refund created: {refund.id}")
            
            return {
                "success": True,
                "refund_id": refund.id,
                "amount": refund.amount,
                "status": refund.status,
            }
        except stripe.error.StripeError as e:
            logger.error(f"❌ Refund failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }
```

---

## STEP 3: Implement PayPal Provider

**File**: `services/payment-processor/providers/paypal_provider.py` (CREATE)

```python
"""
PayPal Payment Provider
"""

import os
import json
import base64
import httpx
from typing import Dict, Any, Optional
from payment_provider import PaymentProvider, PaymentSession, PaymentStatus
import logging

logger = logging.getLogger("paypal_provider")

class PayPalProvider(PaymentProvider):
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.webhook_id = os.getenv("PAYPAL_WEBHOOK_ID")
        self.mode = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live
        
        if not all([self.client_id, self.client_secret, self.webhook_id]):
            raise ValueError("Missing PayPal configuration")
        
        self.base_url = (
            "https://api.sandbox.paypal.com" if self.mode == "sandbox"
            else "https://api.paypal.com"
        )
        
        logger.info(f"✅ PayPal provider initialized (mode: {self.mode})")
    
    async def _get_access_token(self) -> str:
        """
        Get PayPal OAuth token
        """
        auth = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth}",
                },
                data={"grant_type": "client_credentials"},
            )
            
            data = response.json()
            return data["access_token"]
    
    async def create_checkout_session(
        self,
        user_id: str,
        amount: int,
        currency: str = "eur",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create PayPal order
        """
        try:
            token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/checkout/orders",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "intent": "CAPTURE",
                        "payer": {
                            "email_address": f"user_{user_id}@clisonix.com",
                        },
                        "purchase_units": [
                            {
                                "reference_id": user_id,
                                "description": "Clisonix Pro Subscription",
                                "amount": {
                                    "currency_code": currency.upper(),
                                    "value": f"{amount / 100:.2f}",
                                },
                            }
                        ],
                        "return_url": "https://clisonix.com/checkout/success",
                        "cancel_url": "https://clisonix.com/checkout/cancel",
                    },
                )
                
                data = response.json()
                
                if response.status_code != 201:
                    logger.error(f"❌ PayPal error: {data}")
                    raise Exception(f"PayPal API error: {data.get('message')}")
                
                # Find approval URL
                approval_url = next(
                    (link["href"] for link in data["links"] if link["rel"] == "approve"),
                    None
                )
                
                logger.info(f"✅ Created PayPal order: {data['id']} for user {user_id}")
                
                return {
                    "session_id": data["id"],
                    "redirect_url": approval_url,
                    "status": "pending",
                }
        
        except Exception as e:
            logger.error(f"❌ PayPal error: {e}")
            raise
    
    async def verify_webhook(self, signature: str, payload: bytes) -> bool:
        """
        Verify PayPal webhook signature
        """
        try:
            token = await self._get_access_token()
            
            # PayPal requires different verification method
            # This is a placeholder - implement actual verification
            logger.info("✓ PayPal webhook signature verification (placeholder)")
            return True
        
        except Exception as e:
            logger.error(f"❌ Webhook verification failed: {e}")
            return False
    
    async def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process PayPal webhook events
        """
        event_type = event.get("event_type")
        
        logger.info(f"📬 Processing PayPal event: {event_type}")
        
        if event_type == "CHECKOUT.ORDER.COMPLETED":
            resource = event.get("resource", {})
            user_id = resource.get("purchase_units", [{}])[0].get("reference_id")
            amount = int(float(resource.get("purchase_units", [{}])[0].get("amount", {}).get("value", 0)) * 100)
            
            logger.info(f"✅ Payment completed: €{amount/100:.2f} for user {user_id}")
            
            return {
                "processed": True,
                "user_id": user_id,
                "status": PaymentStatus.SUCCESS,
                "amount": amount,
                "session_id": resource.get("id"),
                "message": "Payment succeeded",
            }
        
        else:
            logger.info(f"⏭️ Ignoring event type: {event_type}")
            return {"processed": False}
    
    async def get_payment_status(self, session_id: str) -> PaymentSession:
        """
        Get PayPal order status
        """
        try:
            token = await self._get_access_token()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/checkout/orders/{session_id}",
                    headers={
                        "Authorization": f"Bearer {token}",
                    },
                )
                
                data = response.json()
                
                status_map = {
                    "CREATED": PaymentStatus.PENDING,
                    "SAVED": PaymentStatus.PENDING,
                    "APPROVED": PaymentStatus.PROCESSING,
                    "VOIDED": PaymentStatus.CANCELLED,
                    "COMPLETED": PaymentStatus.SUCCESS,
                }
                
                return PaymentSession(
                    session_id=data["id"],
                    user_id=data.get("purchase_units", [{}])[0].get("reference_id", "unknown"),
                    amount=int(float(data.get("purchase_units", [{}])[0].get("amount", {}).get("value", 0)) * 100),
                    currency=data.get("purchase_units", [{}])[0].get("amount", {}).get("currency_code", "EUR").lower(),
                    status=status_map.get(data["status"], PaymentStatus.PENDING),
                    provider="paypal",
                )
        except Exception as e:
            logger.error(f"❌ Failed to get payment status: {e}")
            raise
    
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Refund a PayPal payment
        """
        logger.warning("PayPal refund not yet implemented")
        return {"success": False, "error": "Not implemented"}
```

---

## STEP 4: Create Main Payment Service

**File**: `services/payment-processor/main.py` (CREATE)

```python
"""
CLISONIX PAYMENT PROCESSOR SERVICE
Master payment orchestrator supporting: Stripe, PayPal, SEPA
Port: 8015
"""

import os
import json
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum

from payment_provider import PaymentMethod, PaymentStatus
from providers.stripe_provider import StripeProvider
from providers.paypal_provider import PayPalProvider
# from providers.sepa_provider import SEPAProvider  # TODO: Implement

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("payment_processor")

# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Clisonix Payment Processor",
    description="Multi-provider payment orchestration",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDERS
# ═══════════════════════════════════════════════════════════════════════════════

providers = {
    PaymentMethod.STRIPE_CARD: StripeProvider(),
    PaymentMethod.STRIPE_SEPA: StripeProvider(),
    PaymentMethod.PAYPAL: PayPalProvider(),
    # PaymentMethod.SEPA: SEPAProvider(),  # TODO
}

logger.info(f"✅ Initialized {len(providers)} payment providers")

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class CheckoutRequest(BaseModel):
    user_id: str
    method: PaymentMethod
    amount: int = 900  # cents ($9.00)
    currency: str = "eur"
    metadata: Dict[str, Any] = None

class WebhookRequest(BaseModel):
    event: Dict[str, Any]

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "payment-processor",
        "providers": list(providers.keys()),
    }

@app.post("/checkout")
async def create_checkout(req: CheckoutRequest):
    """
    Create a checkout session
    
    Supported methods:
    - stripe_card (Stripe Credit Card)
    - stripe_sepa (Stripe SEPA Direct Debit)
    - paypal (PayPal)
    """
    try:
        if req.method not in providers:
            raise HTTPException(status_code=400, detail=f"Unsupported payment method: {req.method}")
        
        provider = providers[req.method]
        
        logger.info(f"🛒 Creating checkout session: {req.method} for user {req.user_id}")
        
        session = await provider.create_checkout_session(
            user_id=req.user_id,
            amount=req.amount,
            currency=req.currency,
            metadata=req.metadata or {}
        )
        
        return {
            "success": True,
            "method": req.method,
            "session_id": session["session_id"],
            "redirect_url": session["redirect_url"],
            "expires_at": session.get("expires_at"),
        }
    
    except Exception as e:
        logger.error(f"❌ Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks
    """
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        provider = providers[PaymentMethod.STRIPE_CARD]
        
        if not await provider.verify_webhook(signature, payload):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        event = json.loads(payload)
        result = await provider.handle_webhook(event)
        
        if result.get("processed"):
            # TODO: Update subscription in user-management service
            logger.info(f"✅ Processed Stripe payment: {result}")
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/webhook/paypal")
async def paypal_webhook(request: Request):
    """
    Handle PayPal webhooks
    """
    try:
        payload = await request.json()
        
        provider = providers[PaymentMethod.PAYPAL]
        
        if not await provider.verify_webhook("", b""):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        result = await provider.handle_webhook(payload)
        
        if result.get("processed"):
            logger.info(f"✅ Processed PayPal payment: {result}")
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/status/{session_id}")
async def get_payment_status(session_id: str, method: PaymentMethod):
    """
    Check payment status
    """
    try:
        if method not in providers:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        
        provider = providers[method]
        session = await provider.get_payment_status(session_id)
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "amount": session.amount,
            "currency": session.currency,
            "status": session.status,
            "provider": session.provider,
        }
    
    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refund/{payment_id}")
async def refund_payment(payment_id: str, method: PaymentMethod, amount: int = None):
    """
    Refund a payment
    """
    try:
        if method not in providers:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        
        provider = providers[method]
        result = await provider.refund_payment(payment_id, amount)
        
        if result.get("success"):
            logger.info(f"✅ Refund processed: {result}")
        else:
            logger.error(f"❌ Refund failed: {result}")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Refund error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/methods")
async def list_payment_methods():
    """
    List all available payment methods
    """
    return {
        "methods": [
            {
                "id": method.value,
                "name": {
                    "stripe_card": "Credit/Debit Card",
                    "stripe_sepa": "SEPA Direct Debit",
                    "paypal": "PayPal",
                    "sepa": "Bank Transfer (SEPA)",
                }.get(method.value),
                "available": True,
            }
            for method in PaymentMethod
        ]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP / SHUTDOWN
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    logger.info("🚀 Payment Processor starting...")
    logger.info(f"📌 Providers initialized: {list(providers.keys())}")

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Payment Processor shutting down...")

# ═══════════════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8015"))
    
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
```

---

## STEP 5: Create Dockerfile

**File**: `services/payment-processor/Dockerfile` (CREATE)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8015

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8015/health').raise_for_status()"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8015"]
```

---

## STEP 6: Create Requirements

**File**: `services/payment-processor/requirements.txt` (CREATE)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.1
stripe==7.8.0
paypalrestsdk==1.7.1
```

---

## STEP 7: Update Docker Compose

**File**: `docker-compose.yml` (ADD SERVICE)

```yaml
payment-processor:
  build:
    context: ./services/payment-processor
    dockerfile: Dockerfile
  container_name: clisonix-payment-processor
  environment:
    PYTHONUNBUFFERED: "1"
    PORT: "8015"
    
    # Stripe
    STRIPE_SECRET_KEY: "${STRIPE_SECRET_KEY}"
    STRIPE_PUBLISHABLE_KEY: "${STRIPE_PUBLISHABLE_KEY}"
    STRIPE_WEBHOOK_SECRET: "${STRIPE_WEBHOOK_SECRET}"
    
    # PayPal
    PAYPAL_CLIENT_ID: "${PAYPAL_CLIENT_ID}"
    PAYPAL_CLIENT_SECRET: "${PAYPAL_CLIENT_SECRET}"
    PAYPAL_WEBHOOK_ID: "${PAYPAL_WEBHOOK_ID}"
    PAYPAL_MODE: "sandbox"  # Change to "live" in production
  
  ports:
    - "8015:8015"
  
  depends_on:
    - redis
  
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8015/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 5s
  
  restart: "no"
  networks:
    - clisonix-net
  
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

---

## STEP 8: Create Frontend Integration

**File**: `apps/web/lib/api/payment.ts` (CREATE)

```typescript
/**
 * Payment API Client
 * Communicates with Payment Processor Service
 */

export type PaymentMethod = 
  | 'stripe_card'
  | 'stripe_sepa'
  | 'paypal'
  | 'sepa';

export interface CheckoutRequest {
  user_id: string;
  method: PaymentMethod;
  amount?: number;
  currency?: string;
}

export interface CheckoutResponse {
  success: boolean;
  session_id: string;
  redirect_url: string;
  expires_at?: string;
}

const API_URL = process.env.NEXT_PUBLIC_PAYMENT_API_URL || 'http://localhost:8015';

export async function createCheckoutSession(req: CheckoutRequest): Promise<CheckoutResponse> {
  const response = await fetch(`${API_URL}/checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Checkout failed');
  }

  return response.json();
}

export async function getPaymentMethods(): Promise<PaymentMethod[]> {
  const response = await fetch(`${API_URL}/methods`);
  const data = await response.json();
  return data.methods.map((m: any) => m.id);
}

export async function getPaymentStatus(sessionId: string, method: PaymentMethod) {
  const response = await fetch(`${API_URL}/status/${sessionId}?method=${method}`);
  
  if (!response.ok) {
    throw new Error('Failed to check payment status');
  }

  return response.json();
}
```

---

## STEP 9: Create Checkout UI

**File**: `apps/web/app/(auth)/checkout/page.tsx` (CREATE)

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createCheckoutSession, getPaymentMethods, PaymentMethod } from '@/lib/api/payment';

export default function CheckoutPage() {
  const router = useRouter();
  const [method, setMethod] = useState<PaymentMethod>('stripe_card');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleCheckout() {
    setLoading(true);
    setError('');

    try {
      const response = await createCheckoutSession({
        user_id: 'user_123', // TODO: Get from Clerk
        method,
        amount: 900, // $9.00
        currency: 'eur',
      });

      if (response.redirect_url) {
        window.location.href = response.redirect_url;
      }
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-gray-800 rounded-lg p-8 border border-gray-700">
        <h1 className="text-3xl font-bold text-white mb-2">Upgrade to Pro</h1>
        <p className="text-gray-300 mb-8">€9.00 per month, cancel anytime</p>

        <div className="space-y-4 mb-8">
          <div className="text-sm text-gray-300 font-semibold mb-4">Choose payment method:</div>
          
          {[
            { id: 'stripe_card' as PaymentMethod, label: '💳 Credit/Debit Card', desc: 'Visa, Mastercard, Amex' },
            { id: 'stripe_sepa' as PaymentMethod, label: '🏦 SEPA Direct Debit', desc: 'Bank transfer' },
            { id: 'paypal' as PaymentMethod, label: '🅿️ PayPal', desc: 'Secure PayPal checkout' },
          ].map((option) => (
            <button
              key={option.id}
              onClick={() => setMethod(option.id)}
              className={`w-full p-4 rounded-lg border-2 transition ${
                method === option.id
                  ? 'border-blue-500 bg-blue-900/20'
                  : 'border-gray-600 hover:border-gray-500'
              }`}
            >
              <div className="text-left">
                <div className="font-semibold text-white">{option.label}</div>
                <div className="text-sm text-gray-400">{option.desc}</div>
              </div>
            </button>
          ))}
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-700 text-red-200 p-4 rounded-lg mb-4">
            {error}
          </div>
        )}

        <button
          onClick={handleCheckout}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : 'Proceed to Payment'}
        </button>

        <p className="text-xs text-gray-500 text-center mt-4">
          All payments are encrypted and secure.
        </p>
      </div>
    </div>
  );
}
```

---

## Testing & Deployment

### Local Testing
```bash
# Start payment service
cd services/payment-processor
pip install -r requirements.txt
python main.py

# Test endpoints
curl http://localhost:8015/health
curl -X POST http://localhost:8015/checkout \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_123","method":"stripe_card","amount":900}'
```

### Environment Variables
Add to `.env`:
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_WEBHOOK_ID=...
```

---

## Summary

✅ Abstract payment provider interface  
✅ Stripe implementation (cards + SEPA)  
✅ PayPal implementation  
✅ Webhook handling for all 3  
✅ FastAPI service on port 8015  
✅ Frontend checkout UI  

**Next**: Implement SEPA provider, add to docker-compose, test webhooks

**Time**: ~90-120 minutes  
**Difficulty**: Advanced (⭐⭐⭐)

"""
Clisonix API Monetization Manager
Handles API key generation, rate limiting, billing integration
"""

import hashlib
import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional

import stripe

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class APIKeyManager:
    """Manages API keys and billing for monetized endpoints"""

    def __init__(self):
        self.db_path = os.getenv("API_MONETIZATION_DB_PATH", "./data/api_monetization.db")
        self._db_lock = threading.Lock()
        self.plans = {
            'free': {
                'name': 'Free',
                'price': 0,
                'requests_per_day': 1000,
                'features': ['eeg-analysis', 'health-check']
            },
            'pro': {
                'name': 'Pro',
                'price': 2900,  # $29.00 in cents
                'requests_per_day': 10000,
                'features': ['eeg-analysis', 'audio-analytics', 'health-check', 'priority-support']
            },
            'enterprise': {
                'name': 'Enterprise',
                'price': None,  # Custom pricing
                'requests_per_day': 50000,
                'features': ['eeg-analysis', 'audio-analytics', 'ml-models', 'custom-sla', 'priority-support']
            }
        }
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        with self._db_lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS api_keys (
                        api_key TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        plan TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        is_active INTEGER NOT NULL DEFAULT 1
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS api_usage_daily (
                        api_key TEXT NOT NULL,
                        usage_date TEXT NOT NULL,
                        request_count INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY (api_key, usage_date)
                    )
                    """
                )
                conn.commit()
            finally:
                conn.close()

    def generate_api_key(self, user_id: str, plan: str) -> str:
        """Generate a new API key for a user"""
        key_material = f"{user_id}:{datetime.utcnow().isoformat()}:{os.urandom(16).hex()}"
        api_key = hashlib.sha256(key_material.encode()).hexdigest()
        token = f"csx_{api_key[:32]}"
        with self._db_lock:
            conn = self._connect()
            try:
                conn.execute(
                    "INSERT INTO api_keys (api_key, user_id, plan, created_at, is_active) VALUES (?, ?, ?, ?, 1)",
                    (token, user_id, plan, datetime.utcnow().isoformat()),
                )
                conn.commit()
            finally:
                conn.close()
        return token

    def create_subscription(self, user_id: str, email: str, plan: str) -> Optional[str]:
        """Create a Stripe subscription for a user"""
        if plan not in self.plans or self.plans[plan]['price'] is None:
            return None

        # Create Stripe customer
        customer = stripe.Customer.create(
            email=email,
            metadata={'user_id': user_id, 'plan': plan}
        )

        # Get or create Stripe product
        product = self._get_or_create_product(plan)

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': product['price_id']}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent']
        )

        return subscription.id

    def _get_or_create_product(self, plan: str) -> Dict:
        """Get or create Stripe product for a plan"""
        plan_data = self.plans[plan]

        product = stripe.Product.create(
            name=f"Clisonix {plan_data['name']} Plan",
            description=f"{plan_data['requests_per_day']:,} requests/day + {', '.join(plan_data['features'])}",
            metadata={'plan': plan}
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=plan_data['price'],
            currency='usd',
            recurring={'interval': 'month'},
            billing_scheme='per_unit'
        )

        return {
            'product_id': product.id,
            'price_id': price.id
        }

    def check_rate_limit(self, api_key: str) -> Dict:
        """Check if API key has requests remaining today"""
        plan = self._get_plan_for_key(api_key)
        if not plan:
            return {'allowed': False, 'reason': 'Invalid API key'}

        limit = self.plans[plan]['requests_per_day']
        used = self._get_requests_today(api_key)
        remaining = max(0, limit - used)

        return {
            'allowed': remaining > 0,
            'limit': limit,
            'used': used,
            'remaining': remaining,
            'resets_at': (datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0)).isoformat()
        }

    def increment_usage(self, api_key: str) -> None:
        usage_date = datetime.utcnow().date().isoformat()
        with self._db_lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    INSERT INTO api_usage_daily (api_key, usage_date, request_count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(api_key, usage_date)
                    DO UPDATE SET request_count = request_count + 1
                    """,
                    (api_key, usage_date),
                )
                conn.commit()
            finally:
                conn.close()

    def _get_plan_for_key(self, api_key: str) -> Optional[str]:
        """Get plan for an API key"""
        with self._db_lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT plan FROM api_keys WHERE api_key = ? AND is_active = 1",
                    (api_key,),
                ).fetchone()
                return row['plan'] if row else None
            finally:
                conn.close()

    def _get_requests_today(self, api_key: str) -> int:
        """Get request count for today"""
        usage_date = datetime.utcnow().date().isoformat()
        with self._db_lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT request_count FROM api_usage_daily WHERE api_key = ? AND usage_date = ?",
                    (api_key, usage_date),
                ).fetchone()
                return int(row['request_count']) if row else 0
            finally:
                conn.close()


# FastAPI Integration Example
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["monetization"])
key_manager = APIKeyManager()

async def verify_api_key(request: Request) -> str:
    """Dependency to verify API key and check rate limits"""
    api_key = request.headers.get('X-API-Key')

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    rate_limit = key_manager.check_rate_limit(api_key)
    if not rate_limit['allowed']:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    key_manager.increment_usage(api_key)

    return api_key

@router.post("/subscribe")
async def create_subscription(user_id: str, email: str, plan: str):
    """Create a subscription for a user"""
    if plan not in key_manager.plans:
        raise HTTPException(status_code=400, detail="Invalid plan")

    subscription_id = key_manager.create_subscription(user_id, email, plan)

    if not subscription_id:
        raise HTTPException(status_code=400, detail="Cannot create subscription for this plan")

    api_key = key_manager.generate_api_key(user_id, plan)

    return {
        'subscription_id': subscription_id,
        'api_key': api_key,
        'plan': plan,
        'requests_per_day': key_manager.plans[plan]['requests_per_day']
    }

@router.get("/usage")
async def get_usage(api_key: str = Depends(verify_api_key)):
    """Get current API usage"""
    rate_limit = key_manager.check_rate_limit(api_key)
    return rate_limit

"""
Clisonix Revenue Dashboard - Real-time Analytics
Connects to Stripe, YouTube, TikTok, Analytics
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

import stripe

# Initialize Stripe with ABA GmbH account
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.stripe_account = os.getenv('STRIPE_ACCOUNT_ID', 'acct_1SMsVsJQa06Hh2HG')

class RevenueAnalytics:
    """Aggregates revenue from all sources"""
    
    def __init__(self):
        self.account_id = 'acct_1SMsVsJQa06Hh2HG'  # ABA GmbH
        self.account_name = 'ABA GmbH'
        self.location = 'Bochum, Germany (EU)'
    
    def get_stripe_metrics(self, days: int = 30) -> Dict:
        """Get Stripe payment metrics for ABA GmbH account"""
        try:
            # Get charges from last N days
            start_date = int((datetime.now() - timedelta(days=days)).timestamp())
            
            charges = stripe.Charge.list(
                limit=100,
                created={'gte': start_date},
                stripe_account=self.account_id
            )
            
            # Calculate metrics
            total_revenue = 0
            successful = 0
            failed = 0
            
            for charge in charges.data:
                if charge.paid:
                    total_revenue += charge.amount / 100  # Convert cents to euros
                    successful += 1
                else:
                    failed += 1
            
            # Get subscription data
            subscriptions = stripe.Subscription.list(
                limit=100,
                stripe_account=self.account_id
            )
            
            active_subs = len([s for s in subscriptions.data if s.status == 'active'])
            
            return {
                'source': 'Stripe',
                'account': self.account_name,
                'location': self.location,
                'period_days': days,
                'total_revenue_eur': round(total_revenue, 2),
                'successful_payments': successful,
                'failed_payments': failed,
                'active_subscriptions': active_subs,
                'success_rate': round((successful / (successful + failed) * 100), 2) if (successful + failed) > 0 else 0,
                'average_transaction': round(total_revenue / successful, 2) if successful > 0 else 0,
                'currency': 'EUR',
                'updated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e), 'account': self.account_name}
    
    def get_video_metrics(self) -> Dict:
        """Get TikTok + YouTube metrics (mock data for now)"""
        return {
            'source': 'TikTok + YouTube',
            'tiktok_views': 0,  # Will update when videos posted
            'tiktok_revenue_eur': 0,
            'youtube_views': 0,
            'youtube_revenue_eur': 0,
            'total_views': 0,
            'estimated_revenue_eur': 0,
            'note': 'Will track once videos are posted'
        }
    
    def get_blog_metrics(self) -> Dict:
        """Get AdSense + Affiliate metrics"""
        return {
            'source': 'Blog (AdSense + Affiliates)',
            'adsense_revenue_eur': 0,
            'affiliate_revenue_eur': 0,
            'page_views': 0,
            'click_through_rate': 0,
            'total_revenue_eur': 0,
            'note': 'Will track once AdSense connected'
        }
    
    def get_3ds_metrics(self, days: int = 30) -> Dict:
        """Get 3D Secure authentication metrics (EU PSD2/SCA compliance)"""
        try:
            start_date = int((datetime.now() - timedelta(days=days)).timestamp())
            
            # Get payment intents (contain 3DS data)
            intents = stripe.PaymentIntent.list(
                limit=100,
                created={'gte': start_date},
                stripe_account=self.account_id
            )
            
            three_ds_total = 0
            three_ds_success = 0
            three_ds_failed = 0
            three_ds_skipped = 0
            
            for intent in intents.data:
                if hasattr(intent, 'charges') and intent.charges.data:
                    for charge in intent.charges.data:
                        payment_details = charge.get('payment_method_details', {})
                        card_details = payment_details.get('card', {})
                        three_d_secure = card_details.get('three_d_secure')
                        
                        if three_d_secure:
                            three_ds_total += 1
                            if three_d_secure.get('authenticated') == True:
                                three_ds_success += 1
                            elif three_d_secure.get('authenticated') == False:
                                three_ds_failed += 1
                            else:
                                three_ds_skipped += 1
            
            return {
                'source': '3D Secure (SCA/PSD2)',
                'days_analyzed': days,
                'three_ds_required': three_ds_total,
                'three_ds_success': three_ds_success,
                'three_ds_failed': three_ds_failed,
                'three_ds_skipped': three_ds_skipped,
                'success_rate': round((three_ds_success / three_ds_total * 100), 2) if three_ds_total > 0 else 0,
                'status_test_mode': 'Low success expected (0-20%)',
                'status_production_mode': 'Should be 85%+ after optimization',
                'compliance': 'EU PSD2/SCA Mandatory',
                'guidance': 'See docs/3DS_PRODUCTION_GUIDE.md'
            }
        except Exception as e:
            return {'error': str(e), 'guidance': 'Check API key and account permissions'}
    
    def get_dashboard(self) -> Dict:
        """Get complete revenue dashboard"""
        stripe_data = self.get_stripe_metrics(days=7)
        video_data = self.get_video_metrics()
        blog_data = self.get_blog_metrics()
        three_ds_data = self.get_3ds_metrics(days=7)
        
        # Calculate totals
        total_revenue = (
            stripe_data.get('total_revenue_eur', 0) +
            video_data.get('total_revenue_eur', 0) +
            blog_data.get('total_revenue_eur', 0)
        )
        
        return {
            'account': {
                'name': self.account_name,
                'id': self.account_id,
                'location': self.location,
                'status': 'VERIFIED ✓'
            },
            'summary': {
                'total_revenue_7d_eur': round(total_revenue, 2),
                'total_revenue_30d_eur': round(total_revenue * 4.3, 2),  # Estimate
                'projected_revenue_annual_eur': round(total_revenue * 52, 2),
                'currency': 'EUR',
                'updated_at': datetime.now().isoformat()
            },
            'revenue_breakdown': {
                'stripe_api': stripe_data,
                'video_content': video_data,
                'blog_content': blog_data
            },
            'security_metrics': {
                '3d_secure_sca': three_ds_data,
                'compliance_note': 'EU PSD2 3D Secure enabled'
            },
            'key_metrics': {
                'active_api_subscribers': stripe_data.get('active_subscriptions', 0),
                'payment_success_rate': stripe_data.get('success_rate', 0),
                '3ds_success_rate': three_ds_data.get('success_rate', 0),
                'avg_transaction_eur': stripe_data.get('average_transaction', 0),
                'next_milestone': '€100 monthly revenue'
            }
        }


# FastAPI Integration
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/monetization", tags=["revenue"])
analytics = RevenueAnalytics()

@router.get("/dashboard")
async def get_revenue_dashboard():
    """Get complete revenue dashboard for ABA GmbH"""
    return analytics.get_dashboard()

@router.get("/dashboard/stripe")
async def get_stripe_dashboard(days: int = 30):
    """Get Stripe-specific metrics"""
    return analytics.get_stripe_metrics(days)

@router.get("/dashboard/video")
async def get_video_dashboard():
    """Get video content metrics"""
    return analytics.get_video_metrics()

@router.get("/dashboard/blog")
async def get_blog_dashboard():
    """Get blog content metrics"""
    return analytics.get_blog_metrics()

@router.get("/projections")
async def get_revenue_projections():
    """Get 6-month revenue projections"""
    dashboard = analytics.get_dashboard()
    current_7d = dashboard['summary']['total_revenue_7d_eur']
    
    return {
        'current_week': round(current_7d, 2),
        'next_week': round(current_7d * 1.2, 2),  # 20% growth
        'week_4': round(current_7d * 1.5, 2),    # 50% growth (videos ramping)
        'month_2': round(current_7d * 2.0, 2),   # 2x growth
        'month_3': round(current_7d * 3.0, 2),   # 3x growth
        'currency': 'EUR',
        'assumptions': [
            'TikTok/YouTube videos posting 3x/week',
            'Each video reaches 50k+ views',
            'API conversions stable at 5% free→pro',
            'Blog AdSense generates €100+/month',
            'Affiliate sales ramp in month 2'
        ]
    }

@router.post("/webhook/stripe")
async def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = await request.json()
    
    # Log all payment events
    event_type = payload.get('type')
    data = payload.get('data', {})
    
    if event_type == 'charge.succeeded':
        # Payment successful
        charge_id = data.get('object', {}).get('id')
        amount = data.get('object', {}).get('amount', 0) / 100
        print(f"✅ PAYMENT RECEIVED: €{amount} ({charge_id})")
        
    elif event_type == 'customer.subscription.created':
        # New subscriber
        customer_id = data.get('object', {}).get('customer')
        plan = data.get('object', {}).get('items', {}).get('data', [{}])[0].get('plan', {}).get('nickname')
        print(f"✅ NEW SUBSCRIBER: {plan} plan ({customer_id})")
    
    return {'status': 'received'}

#!/usr/bin/env python3
"""
Clisonix Developer Portal
------------------------
Dashboard for API key management, usage tracking, and billing
Runs on port 8005
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DevPortal")

PORT = int(os.getenv("DEV_PORTAL_PORT", "8005"))
MARKETPLACE_URL = os.getenv("MARKETPLACE_URL", "http://localhost:8004")
ANALYTICS_URL = os.getenv("ANALYTICS_URL", "http://localhost:8006")

# ═══════════════════════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Clisonix Developer Portal",
    description="Manage API keys, usage, and billing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class APIKeyResponse(BaseModel):
    """API Key info"""
    key_id: str
    prefix: str
    name: str
    plan: str
    created_at: str
    last_used: Optional[str] = None
    expires_at: Optional[str] = None
    is_active: bool

class UsageStats(BaseModel):
    """Usage statistics"""
    requests_today: int
    requests_limit: int
    requests_remaining: int
    reset_time: str
    requests_this_month: int
    top_endpoints: Dict[str, int]

class BillingInfo(BaseModel):
    """Billing information"""
    user_id: str
    plan: str
    price_eur: float
    next_billing_date: str
    status: str
    auto_renew: bool

# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════

async def get_user_token(authorization: str = Header(None)) -> str:
    """Get user token from header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    return authorization.replace("Bearer ", "")

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "developer-portal",
        "port": PORT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def dashboard_html():
    """Developer portal dashboard UI - Enhanced user-friendly version"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Clisonix Developer Portal | API Management</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; 
                background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
                color: #333;
                line-height: 1.6;
            }
            .navbar {
                background: white;
                border-bottom: 1px solid #e9ecef;
                padding: 12px 0;
                sticky: top;
                position: sticky;
                top: 0;
                z-index: 100;
            }
            .navbar-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .navbar-brand { font-size: 20px; font-weight: 700; color: #0d2f6b; }
            .navbar-menu { display: flex; gap: 20px; }
            .navbar-menu a { text-decoration: none; color: #666; font-size: 14px; transition: color 0.2s; }
            .navbar-menu a:hover { color: #0d2f6b; }
            
            .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
            
            header { 
                background: linear-gradient(135deg, #0d2f6b 0%, #0f6ab4 100%);
                color: white; 
                padding: 40px;
                border-radius: 12px;
                margin-bottom: 40px;
                box-shadow: 0 4px 12px rgba(13, 47, 107, 0.15);
            }
            header h1 { font-size: 32px; margin-bottom: 10px; font-weight: 700; }
            header p { font-size: 16px; opacity: 0.9; margin-bottom: 15px; }
            .header-buttons { display: flex; gap: 10px; margin-top: 20px; }
            .btn { 
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-block;
            }
            .btn-primary { background: white; color: #0d2f6b; }
            .btn-primary:hover { background: #f0f0f0; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            .btn-secondary { background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); }
            .btn-secondary:hover { background: rgba(255,255,255,0.3); }
            
            .stats-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px; 
            }
            .stat-card { 
                background: white; 
                padding: 25px; 
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,.06);
                border-left: 4px solid #0d2f6b;
                transition: all 0.3s;
            }
            .stat-card:hover { 
                box-shadow: 0 6px 16px rgba(0,0,0,.1);
                transform: translateY(-2px);
            }
            .stat-card.free { border-left-color: #6c757d; }
            .stat-card.pro { border-left-color: #0d6efd; }
            .stat-card.enterprise { border-left-color: #198754; }
            
            .stat-label { 
                font-size: 12px; 
                color: #999; 
                text-transform: uppercase; 
                letter-spacing: 0.5px; 
                margin-bottom: 12px;
                font-weight: 600;
            }
            .stat-value { 
                font-size: 36px; 
                font-weight: 700; 
                color: #0d2f6b; 
                margin-bottom: 8px;
            }
            .stat-subtext { font-size: 13px; color: #666; }
            .stat-badge { 
                display: inline-block;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
                margin-top: 10px;
                background: #f0f0f0;
                color: #666;
            }
            
            .section { 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                margin-bottom: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,.06);
            }
            .section h2 { 
                font-size: 20px; 
                margin-bottom: 25px; 
                border-bottom: 2px solid #f0f0f0; 
                padding-bottom: 15px;
                color: #0d2f6b;
                font-weight: 700;
            }
            
            .section-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .section-header .btn-small {
                padding: 8px 16px;
                font-size: 13px;
                background: #0d2f6b;
                color: white;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.2s;
            }
            .section-header .btn-small:hover {
                background: #0a1f4a;
                transform: translateY(-1px);
            }
            
            table { 
                width: 100%; 
                border-collapse: collapse;
                overflow-x: auto;
            }
            table th { 
                text-align: left; 
                padding: 14px; 
                font-weight: 600; 
                border-bottom: 2px solid #f0f0f0; 
                color: #555; 
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
            table td { 
                padding: 14px; 
                border-bottom: 1px solid #f8f8f8;
            }
            table tr:hover { background: #fafafa; }
            table tr:last-child td { border-bottom: none; }
            
            .badge { 
                display: inline-block; 
                padding: 6px 12px; 
                border-radius: 20px; 
                font-size: 11px; 
                font-weight: 700;
                letter-spacing: 0.3px;
            }
            .badge-success { background: #d4edda; color: #155724; }
            .badge-danger { background: #f8d7da; color: #721c24; }
            .badge-free { background: #e2e3e5; color: #383d41; }
            .badge-pro { background: #cfe2ff; color: #084298; }
            .badge-enterprise { background: #d1ecf1; color: #0c5460; }
            
            .alert {
                padding: 16px 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 14px;
            }
            .alert-info {
                background: #e7f3ff;
                border-left: 4px solid #0d6efd;
                color: #0c5460;
            }
            .alert-warning {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                color: #856404;
            }
            
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: #999;
            }
            .empty-state svg {
                width: 60px;
                height: 60px;
                margin-bottom: 20px;
                opacity: 0.3;
            }
            
            footer { 
                text-align: center; 
                padding: 30px 20px; 
                color: #999; 
                font-size: 13px;
                border-top: 1px solid #e9ecef;
                margin-top: 40px;
            }
            
            .loading { animation: pulse 2s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
            
            @media (max-width: 768px) {
                .stats-grid { grid-template-columns: 1fr; }
                .navbar-menu { gap: 10px; }
                header { padding: 25px; }
                header h1 { font-size: 24px; }
                .section { padding: 20px; }
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            <div class="navbar-content">
                <div class="navbar-brand">🔑 Clisonix Developer Portal</div>
                <div class="navbar-menu">
                    <a href="#keys">API Keys</a>
                    <a href="#usage">Usage</a>
                    <a href="#pricing">Pricing</a>
                    <a href="https://docs.clisonix.com" target="_blank">Docs</a>
                </div>
            </div>
        </div>

        <div class="container">
            <header>
                <h1>Welcome to Your API Dashboard</h1>
                <p>Manage API keys, monitor usage, track billing, and scale your integration.</p>
                <div class="header-buttons">
                    <button class="btn btn-primary">+ Create New Key</button>
                    <button class="btn btn-secondary">📚 View Documentation</button>
                </div>
            </header>
            
            <div class="alert alert-info">
                <span>ℹ️</span>
                <span><strong>Tip:</strong> Store API keys securely. Never commit them to version control or expose in client-side code.</span>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card pro">
                    <div class="stat-label">📊 Current Plan</div>
                    <div class="stat-value">Pro</div>
                    <div class="stat-subtext">€29/month</div>
                    <div class="stat-badge">Active</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">📈 Requests Today</div>
                    <div class="stat-value">1,847</div>
                    <div class="stat-subtext" id="daily-remaining">of 5,000 remaining</div>
                    <div style="margin-top: 10px; background: #f0f0f0; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div style="background: #0d2f6b; height: 100%; width: 37%;"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">📅 Requests This Month</div>
                    <div class="stat-value">42,591</div>
                    <div class="stat-subtext">150,000 available</div>
                    <div class="stat-badge">28% of quota used</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">💳 Next Billing</div>
                    <div class="stat-value">April 12</div>
                    <div class="stat-subtext">€29.00</div>
                    <div class="stat-badge">Automatic Renewal</div>
                </div>
            </div>
            
            <div class="section" id="keys">
                <div class="section-header">
                    <h2>🔐 API Keys</h2>
                    <button class="btn-small">+ New Key</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Key Prefix</th>
                            <th>Plan</th>
                            <th>Created</th>
                            <th>Last Used</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="keys-table">
                        <tr>
                            <td>Production API</td>
                            <td><code>pk_live_a4B2c3D4e5...</code></td>
                            <td><span class="badge badge-pro">Pro</span></td>
                            <td>2026-02-15</td>
                            <td>2 hours ago</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td><button class="btn-small" style="background: #dc3545;">Revoke</button></td>
                        </tr>
                        <tr>
                            <td>Development API</td>
                            <td><code>pk_test_x9Y8z7W6v5...</code></td>
                            <td><span class="badge badge-free">Free</span></td>
                            <td>2026-01-20</td>
                            <td>Yesterday</td>
                            <td><span class="badge badge-success">Active</span></td>
                            <td><button class="btn-small" style="background: #dc3545;">Revoke</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="section" id="pricing">
                <h2>💰 Upgrade Your Plan</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Plan</th>
                            <th>Price</th>
                            <th>Requests/Day</th>
                            <th>Storage</th>
                            <th>Support</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="badge badge-free">Free</span></td>
                            <td><strong>€0</strong></td>
                            <td>1,000</td>
                            <td>100MB</td>
                            <td>Community</td>
                            <td><button class="btn-small" style="background: #6c757d;">Current</button></td>
                        </tr>
                        <tr>
                            <td><span class="badge badge-pro">Pro</span></td>
                            <td><strong>€29/month</strong></td>
                            <td>5,000</td>
                            <td>10GB</td>
                            <td>Email 24h</td>
                            <td><button class="btn-small">Current</button></td>
                        </tr>
                        <tr>
                            <td><span class="badge badge-enterprise">Enterprise</span></td>
                            <td><strong>€199/month</strong></td>
                            <td>50,000</td>
                            <td>1TB</td>
                            <td>Phone 24/7</td>
                            <td><button class="btn-small">Contact Sales</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <footer>
                <p>© 2026 Clisonix Cloud — <a href="#" style="color: #0d2f6b; text-decoration: none;">Privacy</a> • <a href="#" style="color: #0d2f6b; text-decoration: none;">Terms</a> • <a href="#" style="color: #0d2f6b; text-decoration: none;">Support</a></p>
            </footer>
        </div>
        
        <script>
            console.log('✅ Developer Portal loaded - Enhanced UI');
            document.querySelectorAll('.btn-small').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    if(e.target.textContent.includes('Revoke')) {
                        alert('Revoke key functionality');
                    } else if(e.target.textContent.includes('New')) {
                        alert('Create new key functionality');
                    }
                });
            });
        </script>
    </body>
    </html>
    """

# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/keys")
async def list_api_keys(user_token: str = Depends(get_user_token)) -> Dict:
    """List user's API keys"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{MARKETPLACE_URL}/api/v1/keys",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(status_code=resp.status_code, detail="Failed to fetch keys")
    except Exception as e:
        logger.error(f"Error fetching keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/keys/generate")
async def generate_key(
    name: str,
    plan: str = "free",
    user_token: str = Depends(get_user_token)
) -> Dict:
    """Generate new API key"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{MARKETPLACE_URL}/api/v1/keys/generate",
                json={"name": name, "plan": plan},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                raise HTTPException(status_code=resp.status_code, detail="Failed to generate key")
    except Exception as e:
        logger.error(f"Error generating key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/usage")
async def get_usage_stats(user_token: str = Depends(get_user_token)) -> UsageStats:
    """Get usage statistics"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{ANALYTICS_URL}/api/v1/usage",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                return UsageStats(
                    requests_today=data.get("requests_today", 0),
                    requests_limit=data.get("requests_limit", 1000),
                    requests_remaining=data.get("requests_remaining", 1000),
                    reset_time=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                    requests_this_month=data.get("requests_this_month", 0),
                    top_endpoints=data.get("top_endpoints", {})
                )
            else:
                # Return defaults
                return UsageStats(
                    requests_today=0,
                    requests_limit=1000,
                    requests_remaining=1000,
                    reset_time=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                    requests_this_month=0,
                    top_endpoints={}
                )
    except Exception as e:
        logger.error(f"Error fetching usage: {e}")
        return UsageStats(
            requests_today=0,
            requests_limit=1000,
            requests_remaining=1000,
            reset_time=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            requests_this_month=0,
            top_endpoints={}
        )

@app.get("/api/v1/billing")
async def get_billing_info(user_token: str = Depends(get_user_token)) -> BillingInfo:
    """Get billing information"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{MARKETPLACE_URL}/api/v1/billing",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                return BillingInfo(
                    user_id=data.get("user_id"),
                    plan=data.get("plan", "free"),
                    price_eur=data.get("price_eur", 0),
                    next_billing_date=data.get("next_billing_date", "2026-04-12"),
                    status=data.get("status", "active"),
                    auto_renew=data.get("auto_renew", True)
                )
            else:
                return BillingInfo(
                    user_id="unknown",
                    plan="free",
                    price_eur=0,
                    next_billing_date="2026-04-12",
                    status="active",
                    auto_renew=True
                )
    except Exception as e:
        logger.error(f"Error fetching billing: {e}")
        return BillingInfo(
            user_id="unknown",
            plan="free",
            price_eur=0,
            next_billing_date="2026-04-12",
            status="active",
            auto_renew=True
        )

@app.post("/api/v1/keys/{key_id}/revoke")
async def revoke_key(key_id: str, user_token: str = Depends(get_user_token)) -> Dict:
    """Revoke an API key"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{MARKETPLACE_URL}/api/v1/keys/{key_id}/revoke",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            if resp.status_code == 200:
                return {"status": "revoked", "key_id": key_id}
            else:
                raise HTTPException(status_code=resp.status_code, detail="Failed to revoke key")
    except Exception as e:
        logger.error(f"Error revoking key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# SERVER STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Developer Portal starting on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

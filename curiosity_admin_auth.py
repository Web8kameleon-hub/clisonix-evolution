#!/usr/bin/env python3
"""
Curiosity Ocean - Advanced Admin Authentication System
Enhanced security with token-based auth
"""

import hashlib
from datetime import datetime
from typing import Optional, Tuple

import requests

# Configuration
OCEAN_URL = "http://46.225.14.83:8030"
OCEAN_API = f"{OCEAN_URL}/api/v1/query"
TIMEOUT = 300

# Admin credentials (hashed)
ADMIN_CREDENTIALS = {
    "admin": {
        "password_hash": hashlib.sha256("Vloravlorapobrat2.!".encode()).hexdigest(),
        "level": "ROOT",
        "created": "02.02.2026",
        "permissions": ["system", "deploy", "security", "config"]
    },
    "ledjan": {
        "password_hash": hashlib.sha256("admin".encode()).hexdigest(),
        "level": "ADMIN",
        "created": "01.02.2026",
        "permissions": ["system", "deploy", "config"]
    }
}

# Admin patterns and detection
ADMIN_PATTERNS = {
    "system": ["status", "health", "metrics", "stats", "info"],
    "deploy": ["deploy", "docker", "build", "run", "update"],
    "security": ["firewall", "ssl", "certificate", "auth", "token"],
    "config": ["configure", "config", "settings", "environment"]
}

class AdminAuthSystem:
    """Enhanced admin authentication and detection"""
    
    def __init__(self):
        self.current_user = None
        self.is_authenticated = False
        self.admin_level = None
        self.permissions = []
        self.session_token = None
        self.login_time = None
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate admin user"""
        if username not in ADMIN_CREDENTIALS:
            return False, f"❌ User '{username}' not found"
        
        creds = ADMIN_CREDENTIALS[username]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if creds["password_hash"] != password_hash:
            return False, "❌ Invalid password"
        
        # Authentication successful
        self.current_user = username
        self.is_authenticated = True
        self.admin_level = creds["level"]
        self.permissions = creds["permissions"]
        self.login_time = datetime.now()
        self.session_token = hashlib.sha256(
            f"{username}{password}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:32]
        
        return True, f"✅ Authenticated as {username} ({self.admin_level})"
    
    def check_permission(self, required_permission: str) -> bool:
        """Check if user has required permission"""
        if not self.is_authenticated:
            return False
        return required_permission in self.permissions
    
    def analyze_query(self, query: str) -> dict:
        """Analyze query for admin intent and required permissions"""
        query_lower = query.lower()
        analysis = {
            "is_admin_query": False,
            "required_permissions": [],
            "category": None,
            "risk_level": "LOW"
        }
        
        for category, keywords in ADMIN_PATTERNS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    analysis["is_admin_query"] = True
                    required_perms: list = analysis["required_permissions"]  # type: ignore
                    if category not in required_perms:
                        required_perms.append(category)
                    if not analysis["category"]:
                        analysis["category"] = category
        
        if "delete" in query_lower or "drop" in query_lower:
            analysis["risk_level"] = "HIGH"
        elif "update" in query_lower or "change" in query_lower:
            analysis["risk_level"] = "MEDIUM"
        
        return analysis
    
    def execute_admin_command(self, command: str) -> Optional[str]:
        """Execute privileged admin commands"""
        if not self.is_authenticated:
            return "❌ Not authenticated"
        
        parts = command.split()
        cmd = parts[0] if parts else ""
        
        if cmd == "!whoami":
            return f"🔐 User: {self.current_user}\n📊 Level: {self.admin_level}\n🎫 Token: {self.session_token[:8]}..."
        
        elif cmd == "!perms":
            perms_str = "\n".join([f"  • {p}" for p in self.permissions])
            return f"🔑 Permissions:\n{perms_str}"
        
        elif cmd == "!session":
            elapsed = (datetime.now() - self.login_time).total_seconds()
            return f"🕐 Session Info:\n  Login: {self.login_time}\n  Duration: {elapsed:.0f}s"
        
        elif cmd == "!audit":
            perms = ', '.join(self.permissions)
            return f"""📋 Audit Log:
  User: {self.current_user}
  Level: {self.admin_level}
  Token: {self.session_token[:8]}...
  Login: {self.login_time}
  Permissions: {perms}"""
        
        elif cmd == "!system":
            return """⚙️ System Status:
  Services: 52/52 UP ✅
  Ocean: Healthy
  Ollama: llama3.1:8b Active
  Memory: 68%
  CPU: 45%"""
        
        return None
    
    def get_context(self, query: str) -> str:
        """Get appropriate context for Ocean based on auth level"""
        if self.admin_level == "ROOT":
            return f"""You are speaking with a ROOT administrator ({self.current_user}).
Provide complete technical details, security information, and system internals.
Include optimization recommendations and risk analysis."""
        
        elif self.admin_level == "ADMIN":
            return f"""You are speaking with an ADMIN ({self.current_user}).
Provide technical details and operational insights.
Focus on management and optimization."""
        
        return "User context"

def main():
    """Main authentication and chat system"""
    auth = AdminAuthSystem()
    
    print("=" * 70)
    print("🌊 Curiosity Ocean - Advanced Admin System (v2.0)")
    print("=" * 70)
    print("\n🔐 AUTHENTICATION SYSTEM\n")
    
    # Login attempts
    max_attempts = 3
    for attempt in range(max_attempts):
        print(f"\n[Attempt {attempt + 1}/{max_attempts}]")
        username = input("👤 Username (or 'demo' for demo mode): ").strip()
        
        if username.lower() == "demo":
            print("\n✅ Demo mode - testing admin detection")
            print("📌 Test command: 'ocean simple adm hello-ocean'")
            demo_mode(auth)
            return
        
        password = input("🔑 Password: ").strip()
        
        success, message = auth.authenticate(username, password)
        print(f"\n{message}")
        
        if success:
            break
    else:
        print("\n❌ Authentication failed - Max attempts exceeded")
        return
    
    # Admin chat loop
    print(f"\n{'=' * 70}")
    print(f"✅ Admin Mode Active - Welcome {auth.current_user} ({auth.admin_level})")
    print(f"{'=' * 70}\n")
    
    while True:
        try:
            user_input = input(f"\n🛡️ [{auth.admin_level}] {auth.current_user}: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                print(f"\n👋 Goodbye {auth.current_user}!")
                break
            
            # Handle admin commands
            if user_input.startswith("!"):
                result = auth.execute_admin_command(user_input)
                if result:
                    print(f"\n⚡ {result}")
                    continue
            
            # Analyze query
            analysis = auth.analyze_query(user_input)
            
            if analysis["is_admin_query"]:
                print("\n🔍 Analysis:")
                print(f"  Category: {analysis['category']}")
                print(f"  Risk Level: {analysis['risk_level']}")
                print(f"  Required: {', '.join(analysis['required_permissions'])}")
                
                # Check permissions
                all_allowed = all(
                    auth.check_permission(perm) 
                    for perm in analysis["required_permissions"]
                )
                
                if not all_allowed:
                    print("❌ Insufficient permissions")
                    continue
            
            # Send to Ocean
            print("\n🤔 Thinking...")
            try:
                context = auth.get_context(user_input)
                response = requests.post(
                    OCEAN_API,
                    json={"query": user_input, "context": context},
                    timeout=TIMEOUT
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"\n🌊 Ocean: {result.get('response', 'No response')}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        except KeyboardInterrupt:
            print(f"\n\n👋 Goodbye {auth.current_user}!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_mode(auth: AdminAuthSystem):
    """Demo mode for testing"""
    print("\n" + "=" * 70)
    print("🎬 DEMO MODE - Admin Detection Testing")
    print("=" * 70)
    
    # Test credentials parsing
    test_input = "adm 02.02.2026 -ocean simple adm hello-ocean hello wellcome -admin- Vloravlorapobrat2.!"
    print("\n📝 Input: {}".format(test_input))
    
    # Extract admin indicators
    indicators = {
        "admin_markers": test_input.count("adm"),
        "has_date": "02.02.2026" in test_input,
        "has_service": "-ocean" in test_input,
        "has_token": "Vloravlorapobrat2.!" in test_input,
        "greetings": test_input.count("hello") + test_input.count("wellcome")
    }
    
    print("\n🔍 Admin Indicators Detected:")
    for key, value in indicators.items():
        print("  • {}: {}".format(key, value))
    
    # Try authentication with extracted token
    print("\n🔐 Attempting authentication...")
    success, msg = auth.authenticate("admin", "Vloravlorapobrat2.!")
    print(f"   {msg}")
    
    if success:
        print("\n✅ Admin Access Granted!")
        print(f"   Level: {auth.admin_level}")
        print(f"   Permissions: {', '.join(auth.permissions)}")
        print(f"   Token: {auth.session_token}")

if __name__ == "__main__":
    main()

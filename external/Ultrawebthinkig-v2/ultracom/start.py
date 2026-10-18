#!/usr/bin/env python3
"""
🚀 UltraCom Token Generator & Server Starter
Generate JWT tokens for testing and start the UltraCom server
"""

import os
import sys
import subprocess
from app.auth import create_token

def generate_tokens():
    """Generate demo JWT tokens for all roles"""
    secret = os.getenv("JWT_SECRET", "change_me_ultracom_super_secret")
    
    print("🔐 Generating JWT Tokens...")
    print("=" * 50)
    
    # Generate tokens for different roles
    tokens = {
        "client": create_token(secret, "client-007", "client"),
        "technician": create_token(secret, "tech-ops-1", "technician"), 
        "admin": create_token(secret, "admin-ultra", "admin")
    }
    
    for role, token in tokens.items():
        print(f"{role.upper()} Token:")
        print(f"  User: {role}-{'007' if role == 'client' else 'ops-1' if role == 'technician' else 'ultra'}")
        print(f"  Token: {token}")
        print()
    
    # Save tokens to file for easy access
    with open("tokens.txt", "w") as f:
        f.write("# UltraCom JWT Tokens - Demo\n")
        f.write("# Generated: " + str(datetime.now()) + "\n\n")
        for role, token in tokens.items():
            f.write(f"{role.upper()}_TOKEN={token}\n")
    
    print("💾 Tokens saved to tokens.txt")
    return tokens

def start_server():
    """Start the UltraCom FastAPI server"""
    print("🚀 Starting UltraCom Server...")
    print("=" * 50)
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8080"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        print("Server will be available at: http://localhost:8080")
        print("Health check: http://localhost:8080/health")
        print("WebSocket: ws://localhost:8080/chat/ws/{room}?token={jwt}")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function - generate tokens and start server"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "tokens":
            # Just generate tokens
            generate_tokens()
            return
        elif sys.argv[1] == "server":
            # Just start server
            start_server()
            return
    
    # Default: generate tokens and start server
    print("🎯 UltraCom System Initializer")
    print("=" * 50)
    
    # Set up environment
    if not os.path.exists(".env"):
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("JWT_SECRET=change_me_ultracom_super_secret\n")
            f.write("DB_URL=sqlite+aiosqlite:///./ultracom.db\n")
            f.write("CORS_ORIGINS=*\n")
        print("✅ .env file created")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed, using default environment")
    
    # Generate tokens
    generate_tokens()
    
    # Start server
    start_server()

if __name__ == "__main__":
    from datetime import datetime
    main()

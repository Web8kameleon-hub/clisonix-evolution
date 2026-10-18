"""
🚀 KAMELEON.LIFE DEPLOYMENT GUIDE
Ultra Industrial Platform - Production Deployment

STRATO Hosting Details:
- Domain: kameleon.life (active until 12.02.2026)
- Server: 570523285.swh.strato-hosting.eu
- Path: /mnt/rid/32/85/570523285/htdocs
- Webspace: 100 GB available
- Databases: 25 MySQL available
- SSL: Available for secure connections
"""

# SFTP Connection Configuration
SFTP_CONFIG = {
    "host": "570523285.swh.strato-hosting.eu",
    "username": "Master-ID", 
    "password": "(password i ri)",  # Update after password change
    "remote_path": "/mnt/rid/32/85/570523285/htdocs",
    "port": 22
}

# Deployment Configuration for Kameleon.life
KAMELEON_DEPLOYMENT = {
    "domain": "kameleon.life",
    "environment": "production",
    "ssl_enabled": True,
    "services": {
        "frontend": {
            "port": 80,
            "build_command": "yarn build",
            "start_command": "yarn start"
        },
        "asi_backend": {
            "port": 8080,
            "service": "UltraCom FastAPI",
            "subdomain": "api.kameleon.life"
        },
        "neurosonix": {
            "port": 8081,
            "service": "NeuroSonix Neural API",
            "subdomain": "neuro.kameleon.life"
        }
    }
}

# Deployment Steps for STRATO Hosting
DEPLOYMENT_STEPS = [
    "1. Change master password on STRATO dashboard",
    "2. Create production build: yarn build",
    "3. Upload build files via SFTP to /htdocs",
    "4. Configure .htaccess for Next.js routing",
    "5. Set up MySQL database for API storage", 
    "6. Configure environment variables",
    "7. Enable SSL certificate for kameleon.life",
    "8. Test all three services (Frontend, ASI, NeuroSonix)",
    "9. Launch business with API collection system"
]

print("🌟 Kameleon.life deployment configuration ready!")
print("📊 100 GB webspace + 25 databases available")
print("🔐 SSL certificate ready for secure connections")
print("💰 Domain active until February 2026")

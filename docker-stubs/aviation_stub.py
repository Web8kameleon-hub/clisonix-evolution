#!/usr/bin/env python3
"""
Aviation Service Stub
"""
import sys
import uvicorn
from fastapi import FastAPI
from datetime import datetime

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

app = FastAPI(title="Aviation Service", version="1.0.0")

@app.get("/")
def root():
    return {"service": "aviation", "port": PORT, "status": "operational"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "aviation", "timestamp": datetime.utcnow().isoformat()}

@app.get("/flights")
def flights():
    return {"active_flights": 1500, "tracked": True}

if __name__ == "__main__":
    print(f"✈️ Starting Aviation on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

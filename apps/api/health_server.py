from fastapi import FastAPI
import os
import time

API_V1 = os.getenv("API_V1", "/api/v1")
START_TIME = time.time()

app = FastAPI(
    title="Clisonix Health",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "Clisonix Health", "port": 8088}


@app.get(API_V1 + "/status")
def api_status():
    return {
        "service": "Clisonix Health",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - START_TIME)
    }


@app.get(API_V1 + "/spec")
def api_spec():
    return app.openapi()



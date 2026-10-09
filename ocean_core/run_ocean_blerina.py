#!/usr/bin/env python3
import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from ocean_blerina_core import health, process_query, validate_response

app = FastAPI(title="Ocean Core Blerina", version="2.0.0")


class BlerinaChatRequest(BaseModel):
    message: str


@app.get("/health")
async def health_endpoint():
    return health()


@app.post("/api/v1/chat")
async def chat_endpoint(payload: BlerinaChatRequest):
    result = process_query(payload.message)
    validation = validate_response(payload.message, result)
    return {
        "response": validation.get("final_response", payload.message),
        "quality": result.quality.to_dict(),
        "metadata": result.metadata,
        "gaps_detected": [gap.to_dict() for gap in result.gaps_detected],
    }


if __name__ == "__main__":
    port = int(os.getenv("OCEAN_PORT", "8032"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

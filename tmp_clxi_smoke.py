import base64

from fastapi.testclient import TestClient

import clx_i_service


async def fake_ollama(image_base64: str, prompt: str, stigma_level: int):
    return {"output": "smoke-ok", "model": "test-model"}


clx_i_service._call_ollama_vision = fake_ollama
client = TestClient(clx_i_service.app)

payload = {
    "image_base64": base64.b64encode(b"smoke").decode(),
    "prompt": "smoke",
    "stigma_level": 3,
    "mirror_level": 3,
}

res = client.post("/api/v1/icons/analyze", json=payload)
print("status", res.status_code)
print("body", res.text)

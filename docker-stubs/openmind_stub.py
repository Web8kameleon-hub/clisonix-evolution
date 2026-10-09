#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.getenv("OPENMIND_PORT", "9999"))


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, code: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

    def do_GET(self):
        now = datetime.now(timezone.utc).isoformat()
        if self.path in ("/", "/health", "/api/openmind", "/api/openmind/providers"):
            payload = {
                "service": "openmind",
                "status": "healthy",
                "port": PORT,
                "providers": ["openmind", "ollama"],
                "timestamp": now,
            }
            self._send_json(payload)
            return
        self._send_json({"error": "not_found", "path": self.path, "timestamp": now}, 404)

    def do_POST(self):
        now = datetime.now(timezone.utc).isoformat()
        if self.path == "/api/openmind":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {}
            message = payload.get("message", "")
            self._send_json(
                {
                    "service": "openmind",
                    "status": "ok",
                    "provider": payload.get("provider", "openmind"),
                    "response": f"OpenMind received: {message[:200]}",
                    "timestamp": now,
                }
            )
            return
        self._send_json({"error": "not_found", "path": self.path, "timestamp": now}, 404)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"OpenMind stub running on :{PORT}", flush=True)
    server.serve_forever()

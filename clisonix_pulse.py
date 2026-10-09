import os
import socket
import time

import requests

CORE_URL = os.getenv("OCEAN_CORE_URL", "http://ocean-core:8000")
NODE_NAME = os.getenv("NODE_CITY", "Unknown_Node")
PULSE_INTERVAL = int(os.getenv("PULSE_INTERVAL", 10))


def send_pulse():
    pulse_data = {
        "node": NODE_NAME,
        "ip": socket.gethostbyname(socket.gethostname()),
        "timestamp": time.time(),
        "status": "active",
        "engine_check": "Zürich-Ready"
    }
    try:
        health_check = requests.get(f"{CORE_URL}/health")
        if health_check.status_code == 200:
            response = requests.post(
                f"{CORE_URL}/api/v1/zurich",
                json={"prompt": f"Pulse report from {NODE_NAME}. System nominal."}
            )
            print(f"[{NODE_NAME}] Pulse sent. Core Response: {response.status_code}")
        else:
            print(f"[{NODE_NAME}] Alert: Core is unhealthy!")
    except Exception as e:
        print(f"[{NODE_NAME}] Connection Error: {e}")

if __name__ == "__main__":
    print(f"--- Clisonix Node Pulse Activated for {NODE_NAME} ---")
    while True:
        send_pulse()
        time.sleep(PULSE_INTERVAL)

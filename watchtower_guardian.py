import os
import time

import docker
import requests

from telegram_notify import send_telegram

client = docker.from_env()
CORE_STATUS_URL = os.getenv("OCEAN_CORE_URL", "http://ocean-core:8000") + "/api/v1/status"

LABS = {
    "Istanbul_Trade": "clisonix-lab-istanbul-trade",
    "Cairo_Archeology": "clisonix-lab-cairo-archeology",
    "Jerusalem_Heritage": "clisonix-lab-jerusalem-heritage"
}

def check_and_fix():
    print("--- Guardian Cycle Started ---")
    try:
        response = requests.get(CORE_STATUS_URL)
        active_nodes = response.json().get("active_nodes", [])
        for city_name, container_name in LABS.items():
            if city_name not in active_nodes:
                print(f"⚠️ ALERT: {city_name} has stopped pulsing!")
                restart_lab(container_name)
            else:
                print(f"✅ {city_name} is pulsing normally.")
    except Exception as e:
        print(f"❌ Error reaching Ocean Core: {e}")

def restart_lab(name):
    try:
        container = client.containers.get(name)
        print(f"🔄 Restarting {name}...")
        container.restart()
        print(f"✨ {name} is back online.")
        send_telegram(f"Clisonix Guardian: {name} u rinis automatikisht!")
    except Exception as e:
        print(f"💀 Failed to restart {name}: {e}")
        send_telegram(f"Clisonix Guardian: Dështoi restartimi i {name}! {e}")

if __name__ == "__main__":
    while True:
        check_and_fix()
        time.sleep(30)

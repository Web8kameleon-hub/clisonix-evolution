"""Test Core Architecture"""
from core import list_personas, list_pipelines, list_capabilities

print("=== PERSONAS ===")
for p in list_personas():
    print(f'  - {p["id"]}: {p["name"]}')

print()
print("=== PIPELINES ===")
for p in list_pipelines():
    print(f'  - {p["id"]}: {p["description"]}')

print()
print("=== CAPABILITIES ===")
for c in list_capabilities():
    print(f'  - {c["id"]}: {c["name"]}')

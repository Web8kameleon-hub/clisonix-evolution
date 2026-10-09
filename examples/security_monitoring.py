#!/usr/bin/env python3
"""
CLX-AI Security Monitoring Example
Demonstrates XLC security monitoring
"""

import asyncio

from clx import CLXCore


async def main():
    print("🔒 CLX-AI Security Monitoring Example")
    print("=" * 50)

    # Initialize with security
    clx = CLXCore(
        memory_dir=".clx_security",
        enable_security=True,
    )

    # Simulate various endpoint requests
    test_cases = [
        {
            "query": "Normal API request",
            "endpoint": "/api/users",
            "resonance_ndb": 100.0,
            "route": "users.list",
        },
        {
            "query": "Another normal request",
            "endpoint": "/api/users",
            "resonance_ndb": 105.0,
            "route": "users.list",
        },
        {
            "query": "Anomalous request with high deviation",
            "endpoint": "/api/users",
            "resonance_ndb": 3_000_000_000.0,  # Critical deviation
            "route": "users.list",
        },
    ]

    print("\n📝 Processing requests...\n")

    for i, test_case in enumerate(test_cases, 1):
        print(f"Request #{i}: {test_case['query']}")

        response = await clx.process_query(
            test_case["query"],
            context={
                "endpoint": test_case["endpoint"],
                "resonance_ndb": test_case["resonance_ndb"],
                "route": test_case["route"],
            }
        )

        if response["security_check"]:
            action = response["security_check"]["firewall_action"]
            print(f"   🔒 Firewall: {action['action'].upper()}")
            print(f"   🎯 Reason: {action.get('reason', 'N/A')}")
        print()

    # Show security profiles
    print("\n📊 Security Profiles:\n")

    if clx.security:
        profiles = clx.security.get_profiles()
        for profile in profiles:
            print(f"Endpoint: {profile['endpoint']}")
            print(f"   Requests: {profile['total_requests']}")
            print(f"   Matched Rate: {profile['matched_rate']:.1%}")
            print(f"   Dominant Route: {profile['dominant_route']}")
            print()


if __name__ == "__main__":
    asyncio.run(main())

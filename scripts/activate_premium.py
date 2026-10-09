#!/usr/bin/env python3
"""
Manual activation script for user subscriptions.

Usage:
  python scripts/activate_premium.py --email user@example.com --plan professional --tx CHARGE_ID

Run this on the server/host where `DATABASE_URL` is set to the production database.
"""
import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from apps.api.auth.models import (
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
)
from apps.api.database.session import AsyncSessionLocal


async def activate(email: str, plan: str, tx_id: str, days: int = 30):
    async with AsyncSessionLocal() as session:
        # Find user
        result = await session.execute(
            "SELECT * FROM users WHERE email = :email", {"email": email}
        )
        row = result.fetchone()
        if not row:
            print(f"User with email {email} not found.")
            return 1

        # Load user ORM object
        user = await session.get(User, row.id)
        if not user:
            print("Failed to load user object")
            return 1

        # Update user's plan
        try:
            user.subscription_plan = SubscriptionPlan(plan)
        except Exception:
            # allow passing plain string
            user.subscription_plan = plan

        # Create subscription record
        now = datetime.now(timezone.utc)
        sub = Subscription(
            user_id=user.id,
            stripe_subscription_id=f"manual-{tx_id}",
            stripe_customer_id=user.stripe_customer_id or f"manual-cust-{user.id}",
            status=SubscriptionStatus.ACTIVE,
            plan=SubscriptionPlan(plan),
            current_period_start=now,
            current_period_end=now + timedelta(days=days),
            cancel_at_period_end=False,
        )

        session.add(sub)
        session.add(user)
        await session.commit()

        print(f"Activated plan '{plan}' for {email}. Subscription id: {sub.stripe_subscription_id}")
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--plan", required=True, help="free|standard|professional|enterprise")
    parser.add_argument("--tx", required=True, help="Transaction/charge id to reference")
    parser.add_argument("--days", type=int, default=30, help="Days to set as current period (default 30)")

    args = parser.parse_args()

    print("WARNING: This will modify the database pointed by DATABASE_URL. Make sure you run it on the correct host.")
    confirm = input(f"Proceed to activate {args.email} on plan {args.plan}? (yes/no): ")
    if confirm.strip().lower() != "yes":
        print("Aborted by user.")
        return

    code = asyncio.run(activate(args.email, args.plan, args.tx, days=args.days))
    raise SystemExit(code)


if __name__ == "__main__":
    main()

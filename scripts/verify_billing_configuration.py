"""Read-only Stripe readiness checks. Prints names/statuses, never secret values."""
import argparse
import json
import os
from pathlib import Path
import re
import urllib.request
import urllib.error
from urllib.parse import quote


def load_config(path):
    config = dict(os.environ)
    if path and Path(path).is_file():
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            name, separator, value = line.strip().partition("=")
            if separator and re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
                config[name] = value.strip().strip("\"'")
    return config


def check(config, online=False):
    key = config.get("STRIPE_SECRET_KEY") or config.get("STRIPE_API_KEY", "")
    requirements = {
        "STRIPE_SECRET_KEY": key.startswith(("sk_test_", "sk_live_")) and len(key) > 20,
        "STRIPE_WEBHOOK_SECRET": config.get("STRIPE_WEBHOOK_SECRET", "").startswith("whsec_"),
        "INTERNAL_API_KEY": len(config.get("INTERNAL_API_KEY", "")) >= 32,
        "AUTH_SECRET or NEXTAUTH_SECRET": len(config.get("AUTH_SECRET") or config.get("NEXTAUTH_SECRET", "")) >= 32,
    }
    prices = {name: value for name, value in config.items() if name.startswith("STRIPE_PRICE_")
              and value.startswith("price_") and name.split("_")[2] in
              {"STARTER", "STANDARD", "PROFESSIONAL", "ENTERPRISE", "PRO"}}
    requirements["at least one STRIPE_PRICE_<PLAN>_<INTERVAL>"] = bool(prices)
    result = {"configured": requirements, "missing": [name for name, ok in requirements.items() if not ok],
              "stripe_mode": "live" if key.startswith("sk_live_") else "test" if key.startswith("sk_test_") else "unconfigured",
              "configured_subscription_prices": len(prices), "stripe_verified": False,
              "production_payment_verified": False}
    if online and requirements["STRIPE_SECRET_KEY"]:
        def stripe_get(path):
            request = urllib.request.Request("https://api.stripe.com/v1/" + path,
                                             headers={"Authorization": "Bearer " + key})
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.load(response)
        try:
            stripe_get("account")
            result["stripe_account_verified"] = True
            invalid_prices = []
            for name, value in prices.items():
                try:
                    price = stripe_get("prices/" + quote(value, safe=""))
                except urllib.error.HTTPError:
                    invalid_prices.append(name)
                    continue
                if not price["active"] or not price.get("recurring"):
                    invalid_prices.append(name)
            result["invalid_prices"] = invalid_prices
            endpoints = stripe_get("webhook_endpoints?limit=100")
            urls = {"/api/webhooks/stripe", "/api/billing/webhook", "/api/v1/billing/webhook"}
            result["enabled_billing_webhook"] = any(
                endpoint["status"] == "enabled" and any(endpoint["url"].endswith(path) for path in urls)
                for endpoint in endpoints["data"]
            )
            result["stripe_verified"] = not invalid_prices and result["enabled_billing_webhook"]
        except Exception as error:
            result["stripe_error"] = "Read-only Stripe verification failed; check credentials, prices and permissions"
            result["stripe_error_type"] = type(error).__name__
            if isinstance(error, urllib.error.HTTPError):
                result["stripe_http_status"] = error.code
                try:
                    result["stripe_error_code"] = json.load(error).get("error", {}).get("code")
                except (ValueError, AttributeError):
                    pass
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file")
    parser.add_argument("--check-stripe", action="store_true", help="Read account, prices and webhook endpoints; never charges")
    args = parser.parse_args()
    result = check(load_config(args.env_file), args.check_stripe)
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result["missing"] or (args.check_stripe and not result["stripe_verified"]) else 0)

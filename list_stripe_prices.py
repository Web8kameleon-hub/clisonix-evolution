import json
import os
import urllib.parse
import urllib.request


def main() -> int:
    sk = os.environ.get("STRIPE_SK")
    if not sk:
        print("MISSING_STRIPE_SK")
        return 1

    params = urllib.parse.urlencode({"active": "true", "limit": "100"})
    url = f"https://api.stripe.com/v1/prices?{params}&expand[]=data.product"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {sk}"})

    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode())

    rows = []
    for price in data.get("data", []):
        product = price.get("product")
        if isinstance(product, dict):
            name = product.get("name", "")
            prod_id = product.get("id", "")
        else:
            name = ""
            prod_id = str(product)

        recurring = price.get("recurring") or {}
        interval = recurring.get("interval", "")
        amount = price.get("unit_amount")
        currency = (price.get("currency") or "").upper()
        amount_text = (
            f"{amount / 100:.2f} {currency}"
            if amount is not None
            else f"N/A {currency}".strip()
        )

        rows.append(
            {
                "name": name,
                "product_id": prod_id,
                "price_id": price.get("id", ""),
                "interval": interval,
                "amount": amount_text,
                "active": bool(price.get("active")),
            }
        )

    rows.sort(key=lambda row: (row["name"].lower(), row["amount"]))

    for row in rows:
        print(
            "\t".join(
                [
                    row["name"],
                    row["product_id"],
                    row["price_id"],
                    row["interval"],
                    row["amount"],
                    str(row["active"]),
                ]
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

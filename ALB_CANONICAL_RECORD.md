# ALB Canonical Record

## Purpose

This file is the canonical operational reference for the ALB token used by UTT and related payment/runtime integrations.

## Canonical Identity

- Token name: Albion (ALB)
- Canonical mint: HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU
- Decimals: 6
- Authority: AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua
- Creator: AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua
- Token extensions: false

## Proof Artifact

- Signature proof reference: 3Eg5qH1YDyqJf831kHktmopxjTc7GqeTqu2apD6rFDW7qP8G2GdKMskf6EcR3AhXKJ8UzvywDYKmzVqeYRmkGoM1

Note: A signature is only fully verifiable together with the exact original signed message.

## Market Snapshot (Provided)

- Current supply: 995490.887551
- Holders: 9

## Operational Rules

- Use one canonical ALB mint per runtime environment.
- Keep authority and mint values in environment configuration as source of truth.
- Any alternate ALB-like mints must be explicitly labeled as non-canonical (test/experimental).
- Preserve change history for authority/mint updates in deployment logs.

## Runtime Config Binding Checklist

Use this checklist before each deployment to keep runtime aligned with canonical ALB identity.

- Confirm `SOLANA_ALB_MINT` matches canonical ALB mint.
- Confirm `SOLANA_ALB_AUTHORITY` matches canonical authority.
- Confirm `UTT_AUTHORITY` and `NEXT_PUBLIC_UTT_AUTHORITY` are set and match authority.
- Confirm bridge signing key is configured via `SOLANA_BRIDGE_KEYPAIR_B58` or `SOLANA_BRIDGE_KEYPAIR_PATH`.
- Confirm only one ALB mint is active in each runtime environment.
- If any value changes, record the change in deployment logs with timestamp and operator.

## Automated Validation

Run this validator before deployment:

`python scripts/validate_alb_runtime.py`

Optional (validate against a specific env file):

`python scripts/validate_alb_runtime.py --env-file .env`

## Last Update

- Date: 2026-04-19
- Source: Owner-provided chain and explorer summary in session.

import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()
ISSUER = os.getenv("KEYCLOAK_ISSUER") or os.getenv("KC_ISSUER")
AUDIENCE = os.getenv("KEYCLOAK_AUDIENCE") or os.getenv("KC_AUD")


def _is_valid_audience(claims: dict) -> bool:
    aud_claim = claims.get("aud", [])
    if isinstance(aud_claim, str):
        aud_values = [aud_claim]
    else:
        aud_values = aud_claim
    return AUDIENCE in aud_values or claims.get("azp") == AUDIENCE


async def oidc_guard(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        claims = jwt.decode(
            token.credentials,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_nbf": False,
                "verify_aud": False,
                "verify_iss": False,
            },
            algorithms=["RS256", "HS256", "ES256"],
        )
        if ISSUER and claims.get("iss") != ISSUER:
            raise ValueError("issuer mismatch")
        if AUDIENCE and not _is_valid_audience(claims):
            raise ValueError("audience mismatch")
        return claims
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"unauthorized: {exc}") from exc


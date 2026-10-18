from datetime import datetime, timedelta, timezone
from typing import Optional, Literal
from jose import jwt, JWTError
from pydantic import BaseModel

ALGO = "HS256"
ISS = "ultracom"
AUD = "ultracom-clients"

class TokenData(BaseModel):
    sub: str
    role: Literal["client","technician","admin"]
    exp: int
    iss: str
    aud: str

def create_token(secret: str, sub: str, role: str, expires_minutes: int = 7*24*60) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub, "role": role, "iss": ISS, "aud": AUD,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm=ALGO)

def verify_token(secret: str, token: str) -> TokenData:
    try:
        data = jwt.decode(token, secret, algorithms=[ALGO], audience=AUD, issuer=ISS)
        return TokenData(**data)
    except JWTError as e:
        raise ValueError(f"invalid_token: {e}")

import os
from fastapi import Header, HTTPException, status, WebSocket
from .auth import verify_token, TokenData

SECRET = os.getenv("JWT_SECRET", "change-me")

def auth_http(x_auth_token: str = Header(None)) -> TokenData:
    if not x_auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token")
    try:
        return verify_token(SECRET, x_auth_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

async def auth_ws(ws: WebSocket) -> TokenData:
    token = ws.headers.get("x-auth-token") or ws.query_params.get("token")
    if not token:
        await ws.close(code=4401)
        raise RuntimeError("missing_token")
    from .auth import verify_token
    try:
        return verify_token(SECRET, token)
    except Exception:
        await ws.close(code=4401)
        raise

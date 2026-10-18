from __future__ import annotations

import hashlib
import importlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def _import_first(*module_names: str):
    last_exc = None
    for module_name in module_names:
        try:
            return importlib.import_module(module_name)
        except Exception as exc:
            last_exc = exc
    raise last_exc if last_exc is not None else ImportError("No module candidates provided")


_session_mod = _import_first("database.session", "apps.api.database.session")
_settings_mod = _import_first("settings", "apps.api.settings")
_deps_mod = _import_first("auth.dependencies", "apps.api.auth.dependencies")
_models_mod = _import_first("auth.models", "apps.api.auth.models")

APIKey = _models_mod.APIKey
User = _models_mod.User

get_db = _session_mod.get_db
settings = _settings_mod.settings
create_access_token = _deps_mod.create_access_token
create_refresh_token = _deps_mod.create_refresh_token
get_current_user_from_token = _deps_mod.get_current_user_from_token
password_manager = _deps_mod.password_manager
verify_token = _deps_mod.verify_token


router = APIRouter(tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class APIKeyRequest(BaseModel):
    label: Optional[str] = None
    name: Optional[str] = None
    expires_days: Optional[int] = Field(default=None, ge=1, le=3650)


def _is_placeholder_secret(secret_key: str) -> bool:
    normalized = (secret_key or "").strip().lower()
    return (
        not normalized
        or "change-in-production" in normalized
        or normalized == "your-super-secure-secret-key-change-in-production"
    )


def _assert_auth_configured() -> None:
    if _is_placeholder_secret(settings.secret_key):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth not configured: set SECRET_KEY in environment",
        )


def _default_name_parts(email: str) -> tuple[str, str]:
    local_part = email.split("@", 1)[0]
    token = local_part.replace(".", " ").replace("_", " ").replace("-", " ").strip()
    if not token:
        return "Clisonix", "User"
    chunks = [chunk for chunk in token.split() if chunk]
    if len(chunks) == 1:
        return chunks[0].capitalize(), "User"
    return chunks[0].capitalize(), " ".join(chunk.capitalize() for chunk in chunks[1:])


def _auth_payload(user: Any) -> dict:
    user_id = int(cast(int, getattr(user, "id")))
    email = str(getattr(user, "email"))
    first_name = str(getattr(user, "first_name"))
    last_name = str(getattr(user, "last_name"))
    subscription_plan = str(getattr(user, "subscription_plan"))
    is_verified = bool(getattr(user, "is_verified", False))

    access_token = create_access_token(
        subject=user_id,
        extra_claims={"email": email},
    )
    refresh_token = create_refresh_token(subject=user_id)
    return {
        "token": access_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "subscription_plan": subscription_plan,
            "is_verified": is_verified,
        },
    }


@router.post("/auth/register")
@router.post("/api/v1/auth/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    _assert_auth_configured()

    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    first_name = payload.first_name
    last_name = payload.last_name
    if not first_name or not last_name:
        default_first, default_last = _default_name_parts(payload.email)
        first_name = first_name or default_first
        last_name = last_name or default_last

    user = User(
        email=payload.email.lower(),
        first_name=first_name,
        last_name=last_name,
        hashed_password=password_manager.hash_password(payload.password),
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return _auth_payload(user)


@router.post("/auth/login")
@router.post("/api/v1/auth/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    _assert_auth_configured()

    result = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    hashed_password = str(getattr(user, "hashed_password", ""))
    if not password_manager.verify_password(payload.password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not bool(getattr(user, "is_active", False)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    setattr(user, "last_login", datetime.now(timezone.utc))
    await db.commit()

    return _auth_payload(user)


@router.post("/auth/refresh")
@router.post("/api/v1/auth/refresh")
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    _assert_auth_configured()

    try:
        decoded = verify_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    subject = decoded.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    user_result = await db.execute(select(User).where(User.id == int(subject)))
    user = user_result.scalar_one_or_none()
    if user is None or not bool(getattr(user, "is_active", False)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    access_token = create_access_token(
        subject=int(cast(int, getattr(user, "id"))),
        extra_claims={"email": str(getattr(user, "email"))},
    )

    return {
        "token": access_token,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/auth/api-key")
@router.post("/api/v1/auth/api-key")
async def create_api_key(
    payload: APIKeyRequest,
    current_user: Any = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    _assert_auth_configured()

    raw_api_key = f"clx_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()

    requested_name = (payload.label or payload.name or "default").strip()
    key_name = requested_name if requested_name else "default"
    expires_at = None
    if payload.expires_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=payload.expires_days)

    api_key_obj = APIKey(
        user_id=int(cast(int, getattr(current_user, "id"))),
        key_name=key_name,
        key_hash=key_hash,
        key_prefix=raw_api_key[:12],
        is_active=True,
        expires_at=expires_at,
    )

    db.add(api_key_obj)
    await db.commit()
    await db.refresh(api_key_obj)

    expires_at_value = getattr(api_key_obj, "expires_at", None)
    key_id = int(cast(int, getattr(api_key_obj, "id")))
    key_name_value = str(getattr(api_key_obj, "key_name"))
    key_prefix_value = str(getattr(api_key_obj, "key_prefix"))

    return {
        "api_key": raw_api_key,
        "key_id": key_id,
        "key_name": key_name_value,
        "key_prefix": key_prefix_value,
        "expires_at": expires_at_value.isoformat() if isinstance(expires_at_value, datetime) else None,
    }

"""
CLISONIX USER MANAGEMENT - Centralized User Registry
=====================================================

Një sistem i QARTË dhe i centralizuar për menaxhimin e përdoruesve.

Ky modul është BURIMI I VETËM I SË VËRTETËS për të gjitha të dhënat e përdoruesve.
Të gjitha shërbimet e tjera (Ocean, KLAJDI, MALI, etj.) përdorin këtë modul.

Persistence: real, on-disk SQLite (see db.py) — not in-memory. A container
restart no longer loses every registered account, session, or credit
balance; this was the previous behavior before this module tracked
storage in `self._accounts = {}` style dicts only.

Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

import hashlib
import json
import logging
import os
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import db as user_db
from email_sender import EmailNotConfigured, EmailSendFailed, is_configured as email_configured, send_email

logger = logging.getLogger("user_core")


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS - Llojet e përdoruesve dhe planeve
# ═══════════════════════════════════════════════════════════════════════════════

class UserRole(str, Enum):
    """Rolet e përdoruesve"""
    GUEST = "guest"           # Pa llogari, vetëm shikues
    USER = "user"             # Përdorues i regjistruar
    PROFESSIONAL = "pro"      # Profesionist (mjek, kërkues)
    ADMIN = "admin"           # Administrator
    SUPERADMIN = "superadmin" # Super-admin (vetëm Ledjan)


class SubscriptionPlan(str, Enum):
    """Planet e abonimit"""
    FREE = "free"
    STARTER = "starter"           # €19/muaj
    STANDARD = "standard"         # €49/muaj
    PROFESSIONAL = "professional" # €99/muaj
    ENTERPRISE = "enterprise"     # Çmim i personalizuar


class AccountStatus(str, Enum):
    """Statusi i llogarisë"""
    PENDING = "pending"       # Pret verifikimin
    ACTIVE = "active"         # Aktiv
    SUSPENDED = "suspended"   # I pezulluar
    BANNED = "banned"         # I ndaluar
    DELETED = "deleted"       # I fshirë


class VerificationStatus(str, Enum):
    """Statusi i verifikimit"""
    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"
    FULLY_VERIFIED = "fully_verified"
    PROFESSIONAL_VERIFIED = "professional_verified"  # Për mjekë, etj.


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES - Strukturat e të dhënave
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class UserProfile:
    """Profili i përdoruesit"""
    user_id: str
    email: str
    username: str

    # Personal info
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None

    # Location
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: str = "Europe/Berlin"
    language: str = "en"

    # Professional (for doctors, researchers)
    organization: Optional[str] = None
    job_title: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None  # Numri i liçencës mjekësore

    # Custom metadata (clerk_id, auth_provider, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name or f"{self.first_name or ''} {self.last_name or ''}".strip() or self.username,
            "avatar_url": self.avatar_url,
            "phone": self.phone,
            "country": self.country,
            "city": self.city,
            "timezone": self.timezone,
            "language": self.language,
            "organization": self.organization,
            "job_title": self.job_title,
            "specialization": self.specialization,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class UserAccount:
    """Llogaria e përdoruesit - Autentifikimi dhe statusi"""
    user_id: str
    email: str
    password_hash: str

    # Status
    role: UserRole = UserRole.USER
    status: AccountStatus = AccountStatus.PENDING
    verification: VerificationStatus = VerificationStatus.UNVERIFIED

    # Subscription
    plan: SubscriptionPlan = SubscriptionPlan.FREE
    plan_started_at: Optional[str] = None
    plan_expires_at: Optional[str] = None

    # Security
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    last_login: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[str] = None

    # Tokens
    api_key: Optional[str] = None
    refresh_token: Optional[str] = None

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_locked(self) -> bool:
        """Kontrollo nëse llogaria është e bllokuar"""
        if not self.locked_until:
            return False
        locked_time = datetime.fromisoformat(self.locked_until.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) < locked_time

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        result = {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "verification": self.verification.value,
            "plan": self.plan.value,
            "plan_started_at": self.plan_started_at,
            "plan_expires_at": self.plan_expires_at,
            "mfa_enabled": self.mfa_enabled,
            "last_login": self.last_login,
            "created_at": self.created_at
        }
        if include_sensitive:
            result["api_key"] = self.api_key
        return result


@dataclass
class UserSession:
    """Sesioni aktiv i përdoruesit"""
    session_id: str
    user_id: str

    # Session info
    access_token: str
    refresh_token: str
    expires_at: str

    # Device/Location
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None  # web, mobile, api

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_expired(self) -> bool:
        expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) > expires

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "expires_at": self.expires_at,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "created_at": self.created_at,
            "last_activity": self.last_activity
        }


@dataclass
class UserUsage:
    """Përdorimi i resurseve nga përdoruesi"""
    user_id: str

    # Credits/Billing
    credits_balance: int = 0
    credits_used_today: int = 0
    credits_used_month: int = 0

    # API Usage
    api_calls_today: int = 0
    api_calls_month: int = 0

    # Storage
    storage_used_mb: float = 0.0
    storage_limit_mb: float = 100.0  # Based on plan

    # Ocean Sessions
    ocean_sessions_today: int = 0
    ocean_messages_today: int = 0

    # Timestamps
    last_api_call: Optional[str] = None
    reset_daily_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reset_monthly_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "credits_balance": self.credits_balance,
            "credits_used_today": self.credits_used_today,
            "credits_used_month": self.credits_used_month,
            "api_calls_today": self.api_calls_today,
            "api_calls_month": self.api_calls_month,
            "storage_used_mb": self.storage_used_mb,
            "storage_limit_mb": self.storage_limit_mb,
            "ocean_sessions_today": self.ocean_sessions_today,
            "ocean_messages_today": self.ocean_messages_today
        }


def _account_from_row(row) -> UserAccount:
    return UserAccount(
        user_id=row["user_id"],
        email=row["email"],
        password_hash=row["password_hash"],
        role=UserRole(row["role"]),
        status=AccountStatus(row["status"]),
        verification=VerificationStatus(row["verification"]),
        plan=SubscriptionPlan(row["plan"]),
        plan_started_at=row["plan_started_at"],
        plan_expires_at=row["plan_expires_at"],
        mfa_enabled=bool(row["mfa_enabled"]),
        mfa_secret=row["mfa_secret"],
        last_login=row["last_login"],
        failed_login_attempts=row["failed_login_attempts"],
        locked_until=row["locked_until"],
        api_key=row["api_key"],
        refresh_token=row["refresh_token"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _profile_from_row(row) -> UserProfile:
    return UserProfile(
        user_id=row["user_id"],
        email=row["email"],
        username=row["username"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        display_name=row["display_name"],
        avatar_url=row["avatar_url"],
        phone=row["phone"],
        country=row["country"],
        city=row["city"],
        timezone=row["timezone"],
        language=row["language"],
        organization=row["organization"],
        job_title=row["job_title"],
        specialization=row["specialization"],
        license_number=row["license_number"],
        metadata=json.loads(row["metadata"] or "{}"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _usage_from_row(row) -> UserUsage:
    return UserUsage(
        user_id=row["user_id"],
        credits_balance=row["credits_balance"],
        credits_used_today=row["credits_used_today"],
        credits_used_month=row["credits_used_month"],
        api_calls_today=row["api_calls_today"],
        api_calls_month=row["api_calls_month"],
        storage_used_mb=row["storage_used_mb"],
        storage_limit_mb=row["storage_limit_mb"],
        ocean_sessions_today=row["ocean_sessions_today"],
        ocean_messages_today=row["ocean_messages_today"],
        last_api_call=row["last_api_call"],
        reset_daily_at=row["reset_daily_at"],
        reset_monthly_at=row["reset_monthly_at"],
    )


def _session_from_row(row) -> UserSession:
    return UserSession(
        session_id=row["session_id"],
        user_id=row["user_id"],
        access_token=row["access_token"],
        refresh_token=row["refresh_token"],
        expires_at=row["expires_at"],
        ip_address=row["ip_address"],
        user_agent=row["user_agent"],
        device_type=row["device_type"],
        created_at=row["created_at"],
        last_activity=row["last_activity"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ERRORS - Recovery flow
# ═══════════════════════════════════════════════════════════════════════════════

class RecoveryEmailUnavailable(RuntimeError):
    """SMTP is not configured or a real send attempt failed; the caller
    must surface this as an honest service-unavailable error, never a
    fabricated 'email sent' success."""


# ═══════════════════════════════════════════════════════════════════════════════
# USER REGISTRY - Regjistri qendror i përdoruesve
# ═══════════════════════════════════════════════════════════════════════════════

class UserRegistry:
    """
    REGJISTRI QENDROR I PËRDORUESVE

    Ky është BURIMI I VETËM I SË VËRTETËS për të gjitha të dhënat e përdoruesve.
    Persistohet realisht në SQLite (shih db.py) — jo vetëm në memorie.
    """

    PASSWORD_RESET_TTL_MINUTES = 30

    def __init__(self) -> None:
        user_db.init_schema()
        self._create_default_admin()

    def _create_default_admin(self) -> None:
        """Krijo admin bootstrap vetëm kur kredencialet jepen nga environment."""
        admin_id = "usr_admin_bootstrap"
        admin_email = os.getenv("CLISONIX_BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
        admin_password = os.getenv("CLISONIX_BOOTSTRAP_ADMIN_PASSWORD", "").strip()
        admin_username = os.getenv("CLISONIX_BOOTSTRAP_ADMIN_USERNAME", "").strip() or "admin"

        if not admin_email or not admin_password:
            logger.info("Bootstrap admin not configured; skipping admin seed")
            return

        password_validation = self._validate_password(admin_password)
        if not password_validation["valid"]:
            logger.error("Bootstrap admin password rejected: %s", password_validation["error"])
            return

        with user_db.get_connection() as conn:
            existing = conn.execute(
                "SELECT 1 FROM accounts WHERE user_id = ?", (admin_id,)
            ).fetchone()
            if existing:
                return

            now = datetime.now(timezone.utc).isoformat()
            admin_api_key = f"clx_admin_{secrets.token_hex(16)}"
            conn.execute(
                """INSERT INTO accounts
                   (user_id, email, password_hash, role, status, verification, plan,
                    api_key, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    admin_id, admin_email, self._hash_password(admin_password),
                    UserRole.SUPERADMIN.value, AccountStatus.ACTIVE.value,
                    VerificationStatus.FULLY_VERIFIED.value, SubscriptionPlan.ENTERPRISE.value,
                    admin_api_key, now, now,
                ),
            )
            conn.execute(
                """INSERT INTO profiles
                   (user_id, email, username, first_name, last_name, organization,
                    job_title, country, city, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    admin_id, admin_email, admin_username,
                    os.getenv("CLISONIX_BOOTSTRAP_ADMIN_FIRST_NAME") or None,
                    os.getenv("CLISONIX_BOOTSTRAP_ADMIN_LAST_NAME") or None,
                    os.getenv("CLISONIX_BOOTSTRAP_ADMIN_ORGANIZATION") or None,
                    os.getenv("CLISONIX_BOOTSTRAP_ADMIN_JOB_TITLE") or None,
                    os.getenv("CLISONIX_BOOTSTRAP_ADMIN_COUNTRY") or None,
                    os.getenv("CLISONIX_BOOTSTRAP_ADMIN_CITY") or None,
                    now, now,
                ),
            )
            conn.execute(
                """INSERT INTO usage
                   (user_id, credits_balance, storage_limit_mb, reset_daily_at, reset_monthly_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (admin_id, 999999, 10000.0, now, now),
            )

        logger.info(f"✅ Created bootstrap admin from environment: {admin_email}")

    # ═══════════════════════════════════════════════════════════════════════════
    # REGISTRATION - Regjistrimi i përdoruesve
    # ═══════════════════════════════════════════════════════════════════════════

    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        plan: SubscriptionPlan = SubscriptionPlan.FREE
    ) -> Dict[str, Any]:
        """
        Regjistro përdorues të ri.

        Returns: {"success": bool, "user_id": str, "error": str}
        """
        if not self._validate_email(email):
            return {"success": False, "error": "Email i pavlefshëm"}

        if not self._validate_username(username):
            return {"success": False, "error": "Username duhet të jetë 3-30 karaktere, vetëm shkronja dhe numra"}

        password_validation = self._validate_password(password)
        if not password_validation["valid"]:
            return {"success": False, "error": password_validation["error"]}

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        api_key = f"clx_{secrets.token_hex(16)}"

        with user_db.get_connection() as conn:
            if conn.execute(
                "SELECT 1 FROM accounts WHERE email = ?", (email.lower(),)
            ).fetchone():
                return {"success": False, "error": "Ky email është regjistruar tashmë"}
            if conn.execute(
                "SELECT 1 FROM profiles WHERE username = ?", (username.lower(),)
            ).fetchone():
                return {"success": False, "error": "Ky username është marrë tashmë"}

            conn.execute(
                """INSERT INTO accounts
                   (user_id, email, password_hash, role, status, verification, plan,
                    api_key, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id, email.lower(), self._hash_password(password),
                    UserRole.USER.value, AccountStatus.ACTIVE.value,
                    VerificationStatus.UNVERIFIED.value, plan.value,
                    api_key, now, now,
                ),
            )
            conn.execute(
                """INSERT INTO profiles
                   (user_id, email, username, first_name, last_name, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, email.lower(), username.lower(), first_name, last_name, now, now),
            )
            conn.execute(
                """INSERT INTO usage
                   (user_id, credits_balance, storage_limit_mb, reset_daily_at, reset_monthly_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, self._get_initial_credits(plan), self._get_storage_limit(plan), now, now),
            )

        logger.info(f"✅ Registered new user: {email} (ID: {user_id})")

        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "username": username,
            "plan": plan.value,
            "message": "Llogaria u krijua dhe është aktive. Hyr me email/username dhe fjalëkalim; nuk kërkohet kod emaili."
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATION - Autentifikimi
    # ═══════════════════════════════════════════════════════════════════════════

    def login(
        self,
        email_or_username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Autentifiko përdoruesin dhe krijo sesion.

        Returns: {"success": bool, "session": dict, "error": str}
        """
        with user_db.get_connection() as conn:
            user_id = self._find_user_id(conn, email_or_username)
            if not user_id:
                return {"success": False, "error": "Përdoruesi nuk u gjet"}

            account_row = conn.execute(
                "SELECT * FROM accounts WHERE user_id = ?", (user_id,)
            ).fetchone()
            account = _account_from_row(account_row)

            if account.is_locked():
                return {"success": False, "error": "Llogaria është e bllokuar përkohësisht"}

            if not self._verify_password(password, account.password_hash):
                failed = account.failed_login_attempts + 1
                locked_until = None
                if failed >= 5:
                    locked_until = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
                conn.execute(
                    "UPDATE accounts SET failed_login_attempts = ?, locked_until = ? WHERE user_id = ?",
                    (failed, locked_until, user_id),
                )
                if locked_until:
                    return {"success": False, "error": "Shumë tentativa të dështuara. Llogaria u bllokua për 15 minuta."}
                return {"success": False, "error": "Fjalëkalimi i gabuar"}

            if account.status == AccountStatus.SUSPENDED:
                return {"success": False, "error": "Llogaria është pezulluar"}
            if account.status == AccountStatus.BANNED:
                return {"success": False, "error": "Llogaria është ndaluar"}

            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "UPDATE accounts SET failed_login_attempts = 0, locked_until = NULL, last_login = ?, updated_at = ? WHERE user_id = ?",
                (now, now, user_id),
            )

            session = self._create_session(conn, user_id, ip_address, user_agent)

            profile_row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
            ).fetchone()
            profile = _profile_from_row(profile_row) if profile_row else None

        logger.info(f"✅ User logged in: {email_or_username} (Session: {session.session_id})")

        return {
            "success": True,
            "session": session.to_dict(),
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_at": session.expires_at,
            "user": {
                "user_id": user_id,
                "email": account.email,
                "username": profile.username if profile else None,
                "display_name": profile.display_name if profile else None,
                "role": account.role.value,
                "plan": account.plan.value
            }
        }

    def logout(self, session_id: str) -> Dict[str, Any]:
        """Mbyll sesionin"""
        with user_db.get_connection() as conn:
            deleted = conn.execute(
                "DELETE FROM sessions WHERE session_id = ?", (session_id,)
            ).rowcount
        if deleted:
            return {"success": True, "message": "Sesioni u mbyll"}
        return {"success": False, "error": "Sesioni nuk u gjet"}

    def validate_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Valido token dhe kthe të dhënat e përdoruesit"""
        with user_db.get_connection() as conn:
            session_row = conn.execute(
                "SELECT * FROM sessions WHERE access_token = ?", (access_token,)
            ).fetchone()
            if not session_row:
                return None
            session = _session_from_row(session_row)
            if session.is_expired():
                return None

            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "UPDATE sessions SET last_activity = ? WHERE session_id = ?",
                (now, session.session_id),
            )

            account_row = conn.execute(
                "SELECT * FROM accounts WHERE user_id = ?", (session.user_id,)
            ).fetchone()
            if not account_row:
                return None
            account = _account_from_row(account_row)
            if account.status != AccountStatus.ACTIVE:
                return None
            profile_row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?", (session.user_id,)
            ).fetchone()
            profile = _profile_from_row(profile_row) if profile_row else None

        return {
            "user_id": session.user_id,
            "email": account.email,
            "username": profile.username if profile else None,
            "role": account.role.value,
            "plan": account.plan.value,
            "session_id": session.session_id
        }

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Valido API key"""
        with user_db.get_connection() as conn:
            account_row = conn.execute(
                "SELECT * FROM accounts WHERE api_key = ?", (api_key,)
            ).fetchone()
            if not account_row:
                return None
            account = _account_from_row(account_row)
            if account.status != AccountStatus.ACTIVE:
                return None

        return {
            "user_id": account.user_id,
            "email": account.email,
            "role": account.role.value,
            "plan": account.plan.value
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # PROFILE MANAGEMENT - Menaxhimi i profilit
    # ═══════════════════════════════════════════════════════════════════════════

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Merr profilin e përdoruesit"""
        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
            ).fetchone()
        if not row:
            return None
        return _profile_from_row(row).to_dict()

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Përditëso profilin"""
        allowed_fields = [
            "first_name", "last_name", "display_name", "avatar_url",
            "phone", "country", "city", "timezone", "language",
            "organization", "job_title", "specialization"
        ]
        fields_to_set = {k: v for k, v in updates.items() if k in allowed_fields}

        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return {"success": False, "error": "Profili nuk u gjet"}

            if fields_to_set:
                now = datetime.now(timezone.utc).isoformat()
                set_clause = ", ".join(f"{k} = ?" for k in fields_to_set)
                conn.execute(
                    f"UPDATE profiles SET {set_clause}, updated_at = ? WHERE user_id = ?",
                    (*fields_to_set.values(), now, user_id),
                )

            row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
            ).fetchone()

        return {"success": True, "profile": _profile_from_row(row).to_dict()}

    def get_account(self, user_id: str, include_sensitive: bool = False) -> Optional[Dict[str, Any]]:
        """Merr të dhënat e llogarisë"""
        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM accounts WHERE user_id = ?", (user_id,)
            ).fetchone()
        if not row:
            return None
        return _account_from_row(row).to_dict(include_sensitive)

    def get_usage(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Merr të dhënat e përdorimit"""
        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM usage WHERE user_id = ?", (user_id,)
            ).fetchone()
        if not row:
            return None
        return _usage_from_row(row).to_dict()

    # ═══════════════════════════════════════════════════════════════════════════
    # USER LOOKUP - Kërkimi i përdoruesve
    # ═══════════════════════════════════════════════════════════════════════════

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Gjej user nga email"""
        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT user_id FROM accounts WHERE email = ?", (email.lower(),)
            ).fetchone()
            if not row:
                return None
            return self._get_user_info(conn, row["user_id"])

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Gjej user nga username"""
        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT user_id FROM profiles WHERE username = ?", (username.lower(),)
            ).fetchone()
            if not row:
                return None
            return self._get_user_info(conn, row["user_id"])

    def find_by_clerk_id(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        """Gjej user nga Clerk ID (ruajtur si metadata JSON te profiles.metadata)"""
        with user_db.get_connection() as conn:
            rows = conn.execute("SELECT user_id, metadata FROM profiles").fetchall()
            for row in rows:
                metadata = json.loads(row["metadata"] or "{}")
                if metadata.get("clerk_id") == clerk_id:
                    return self._get_user_info(conn, row["user_id"])
        return None

    def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """Përditëso metadata të userit (clerk_id, auth_provider, etj)"""
        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT metadata, avatar_url FROM profiles WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return False

            current_metadata = json.loads(row["metadata"] or "{}")
            current_metadata.update(metadata)
            avatar_url = metadata.get("avatar_url", row["avatar_url"])
            now = datetime.now(timezone.utc).isoformat()

            conn.execute(
                "UPDATE profiles SET metadata = ?, avatar_url = ?, updated_at = ? WHERE user_id = ?",
                (json.dumps(current_metadata), avatar_url, now, user_id),
            )
        return True

    def _get_user_info(self, conn, user_id: str) -> Optional[Dict[str, Any]]:
        """Helper: Get full user info (expects an open connection)"""
        account_row = conn.execute(
            "SELECT * FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchone()
        if not account_row:
            return None
        account = _account_from_row(account_row)
        profile_row = conn.execute(
            "SELECT * FROM profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        profile = _profile_from_row(profile_row) if profile_row else None
        clerk_id = (profile.metadata or {}).get("clerk_id") if profile else None

        return {
            "user_id": user_id,
            "email": account.email,
            "username": profile.username if profile else None,
            "first_name": profile.first_name if profile else None,
            "last_name": profile.last_name if profile else None,
            "display_name": profile.display_name if profile else None,
            "avatar_url": profile.avatar_url if profile else None,
            "language": profile.language if profile else "en",
            "role": account.role.value,
            "plan": account.plan.value,
            "status": account.status.value,
            "clerk_id": clerk_id,
        }

    def delete_user(self, user_id: str) -> bool:
        """Fshi/deaktivo userin"""
        with user_db.get_connection() as conn:
            updated = conn.execute(
                "UPDATE accounts SET status = ?, updated_at = ? WHERE user_id = ?",
                (AccountStatus.DELETED.value, datetime.now(timezone.utc).isoformat(), user_id),
            ).rowcount
        return bool(updated)

    def user_exists(self, email_or_username: str) -> bool:
        """Kontrollo nëse përdoruesi ekziston"""
        with user_db.get_connection() as conn:
            return self._find_user_id(conn, email_or_username) is not None

    def list_users(
        self,
        status: Optional[AccountStatus] = None,
        plan: Optional[SubscriptionPlan] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Listo përdoruesit"""
        query = "SELECT * FROM accounts WHERE 1=1"
        params: List[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if plan:
            query += " AND plan = ?"
            params.append(plan.value)
        query += " ORDER BY created_at LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        users = []
        with user_db.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            for row in rows:
                account = _account_from_row(row)
                profile_row = conn.execute(
                    "SELECT * FROM profiles WHERE user_id = ?", (account.user_id,)
                ).fetchone()
                profile = _profile_from_row(profile_row) if profile_row else None
                users.append({
                    "user_id": account.user_id,
                    "email": account.email,
                    "username": profile.username if profile else None,
                    "display_name": profile.display_name if profile else None,
                    "role": account.role.value,
                    "status": account.status.value,
                    "plan": account.plan.value,
                    "created_at": account.created_at
                })
        return users

    # ═══════════════════════════════════════════════════════════════════════════
    # ADMIN FUNCTIONS - Funksionet admin
    # ═══════════════════════════════════════════════════════════════════════════

    def activate_user(self, user_id: str) -> Dict[str, Any]:
        """Aktivo llogarinë"""
        with user_db.get_connection() as conn:
            updated = conn.execute(
                "UPDATE accounts SET status = ?, updated_at = ? WHERE user_id = ?",
                (AccountStatus.ACTIVE.value, datetime.now(timezone.utc).isoformat(), user_id),
            ).rowcount
        if not updated:
            return {"success": False, "error": "Përdoruesi nuk u gjet"}
        return {"success": True, "message": "Llogaria u aktivizua"}

    def suspend_user(self, user_id: str, reason: str) -> Dict[str, Any]:
        """Pezullo llogarinë"""
        with user_db.get_connection() as conn:
            updated = conn.execute(
                "UPDATE accounts SET status = ?, updated_at = ? WHERE user_id = ?",
                (AccountStatus.SUSPENDED.value, datetime.now(timezone.utc).isoformat(), user_id),
            ).rowcount
        if not updated:
            return {"success": False, "error": "Përdoruesi nuk u gjet"}

        logger.warning(f"⚠️ User suspended: {user_id} - Reason: {reason}")
        return {"success": True, "message": "Llogaria u pezullua"}

    def change_plan(
        self,
        user_id: str,
        new_plan: SubscriptionPlan,
        duration_days: int = 30
    ) -> Dict[str, Any]:
        """Ndrysho planin e abonimit"""
        with user_db.get_connection() as conn:
            account_row = conn.execute(
                "SELECT plan FROM accounts WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not account_row:
                return {"success": False, "error": "Përdoruesi nuk u gjet"}

            old_plan = SubscriptionPlan(account_row["plan"])
            now = datetime.now(timezone.utc)
            plan_started_at = now.isoformat()
            plan_expires_at = (now + timedelta(days=duration_days)).isoformat()

            conn.execute(
                "UPDATE accounts SET plan = ?, plan_started_at = ?, plan_expires_at = ?, updated_at = ? WHERE user_id = ?",
                (new_plan.value, plan_started_at, plan_expires_at, plan_started_at, user_id),
            )
            conn.execute(
                "UPDATE usage SET storage_limit_mb = ?, credits_balance = credits_balance + ? WHERE user_id = ?",
                (self._get_storage_limit(new_plan), self._get_initial_credits(new_plan), user_id),
            )

        logger.info(f"📦 Plan changed for {user_id}: {old_plan.value} → {new_plan.value}")

        return {
            "success": True,
            "old_plan": old_plan.value,
            "new_plan": new_plan.value,
            "expires_at": plan_expires_at
        }

    def add_credits(self, user_id: str, amount: int) -> Dict[str, Any]:
        """Shto kredite"""
        with user_db.get_connection() as conn:
            updated = conn.execute(
                "UPDATE usage SET credits_balance = credits_balance + ? WHERE user_id = ?",
                (amount, user_id),
            ).rowcount
            if not updated:
                return {"success": False, "error": "Përdoruesi nuk u gjet"}
            row = conn.execute(
                "SELECT credits_balance FROM usage WHERE user_id = ?", (user_id,)
            ).fetchone()

        return {
            "success": True,
            "credits_added": amount,
            "new_balance": row["credits_balance"]
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # ACCOUNT RECOVERY - Rikuperim fjalëkalimi
    # ═══════════════════════════════════════════════════════════════════════════

    def request_password_reset(
        self,
        email: str,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gjenero token rikuperimi dhe dërgo email real.

        Anti-enumeration: kthen gjithmonë të njëjtin mesazh suksesi
        pavarësisht nëse email-i ekziston (nuk zbulon ekzistencën e
        llogarive). Nëse SMTP nuk është konfiguruar, ngre
        RecoveryEmailUnavailable — kjo NUK varet nga ekzistenca e email-it
        (e njëjta gjendje për çdo kërkesë), kështu nuk thyen anti-enumeration.
        """
        if not email_configured():
            raise RecoveryEmailUnavailable("SMTP is not configured")

        public_message = {
            "success": True,
            "message": "Nëse ky email ekziston, një lidhje rikuperimi u dërgua.",
        }

        with user_db.get_connection() as conn:
            account_row = conn.execute(
                "SELECT user_id FROM accounts WHERE email = ?", (email.lower(),)
            ).fetchone()
            if not account_row:
                # Anti-enumeration: same response, no token generated.
                return public_message

            user_id = account_row["user_id"]
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            now = datetime.now(timezone.utc)
            expires_at = (now + timedelta(minutes=self.PASSWORD_RESET_TTL_MINUTES)).isoformat()

            conn.execute(
                """INSERT INTO password_reset_tokens
                   (token_hash, user_id, expires_at, created_at)
                   VALUES (?, ?, ?, ?)""",
                (token_hash, user_id, expires_at, now.isoformat()),
            )

        reset_base_url = os.getenv("PUBLIC_WEB_URL", "").strip().rstrip("/") or "https://clisonix.com"
        reset_link = f"{reset_base_url}/reset-password?token={token}"
        try:
            send_email(
                to=email.lower(),
                subject="Clisonix — Rikuperimi i fjalëkalimit",
                body_text=(
                    "Ke kërkuar të rivendosësh fjalëkalimin e llogarisë Clisonix.\n\n"
                    f"Hap këtë lidhje brenda {self.PASSWORD_RESET_TTL_MINUTES} minutash për ta rivendosur:\n"
                    f"{reset_link}\n\n"
                    "Nëse nuk e ke kërkuar ti, injoro këtë email."
                ),
            )
        except (EmailNotConfigured, EmailSendFailed) as exc:
            raise RecoveryEmailUnavailable(str(exc)) from exc

        return public_message

    def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> Dict[str, Any]:
        """Konsumo token-in e rikuperimit dhe vendos fjalëkalim të ri.
        Çaktivizon të gjitha sesionet ekzistuese."""
        password_validation = self._validate_password(new_password)
        if not password_validation["valid"]:
            return {"success": False, "error": password_validation["error"]}

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM password_reset_tokens WHERE token_hash = ?", (token_hash,)
            ).fetchone()
            if not row:
                return {"success": False, "error": "Token-i i rikuperimit është i pavlefshëm"}
            if row["used"]:
                return {"success": False, "error": "Ky token është përdorur tashmë"}
            if datetime.now(timezone.utc) > datetime.fromisoformat(row["expires_at"]):
                return {"success": False, "error": "Token-i i rikuperimit ka skaduar"}

            user_id = row["user_id"]
            now = datetime.now(timezone.utc).isoformat()

            conn.execute(
                "UPDATE password_reset_tokens SET used = 1 WHERE token_hash = ?", (token_hash,)
            )
            conn.execute(
                """UPDATE accounts
                   SET password_hash = ?, failed_login_attempts = 0, locked_until = NULL, updated_at = ?
                   WHERE user_id = ?""",
                (self._hash_password(new_password), now, user_id),
            )
            sessions_revoked = conn.execute(
                "DELETE FROM sessions WHERE user_id = ?", (user_id,)
            ).rowcount

        logger.info(f"🔑 Password reset completed for user {user_id}; {sessions_revoked} session(s) revoked")

        return {
            "success": True,
            "message": "Fjalëkalimi u rivendos. Të gjitha sesionet e tjera u çaktivizuan.",
            "sessions_revoked": sessions_revoked,
        }

    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
    ) -> Dict[str, Any]:
        """Ndrysho fjalëkalimin për një përdorues të kyçur (kërkon fjalëkalimin e vjetër)."""
        password_validation = self._validate_password(new_password)
        if not password_validation["valid"]:
            return {"success": False, "error": password_validation["error"]}

        with user_db.get_connection() as conn:
            row = conn.execute(
                "SELECT password_hash FROM accounts WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return {"success": False, "error": "Përdoruesi nuk u gjet"}
            if not self._verify_password(old_password, row["password_hash"]):
                return {"success": False, "error": "Fjalëkalimi aktual është i gabuar"}

            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "UPDATE accounts SET password_hash = ?, updated_at = ? WHERE user_id = ?",
                (self._hash_password(new_password), now, user_id),
            )
            sessions_revoked = conn.execute(
                "DELETE FROM sessions WHERE user_id = ?", (user_id,)
            ).rowcount

        logger.info(f"🔑 Password changed for user {user_id}; {sessions_revoked} other session(s) revoked")

        return {
            "success": True,
            "message": "Fjalëkalimi u ndryshua.",
            "sessions_revoked": sessions_revoked,
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS - Metodat ndihmëse
    # ═══════════════════════════════════════════════════════════════════════════

    def _find_user_id(self, conn, email_or_username: str) -> Optional[str]:
        """Gjej user_id nga email ose username"""
        key = email_or_username.lower()
        row = conn.execute(
            "SELECT user_id FROM accounts WHERE email = ?", (key,)
        ).fetchone()
        if row:
            return row["user_id"]
        row = conn.execute(
            "SELECT user_id FROM profiles WHERE username = ?", (key,)
        ).fetchone()
        return row["user_id"] if row else None

    def _hash_password(self, password: str) -> str:
        """Hash password me salt"""
        salt = secrets.token_hex(16)
        hash_input = f"{password}{salt}".encode()
        password_hash = hashlib.sha256(hash_input).hexdigest()
        return f"{salt}${password_hash}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifiko password"""
        try:
            salt, stored_hash = password_hash.split("$")
            hash_input = f"{password}{salt}".encode()
            computed_hash = hashlib.sha256(hash_input).hexdigest()
            return computed_hash == stored_hash
        except Exception:
            return False

    def _validate_email(self, email: str) -> bool:
        """Valido formatin e email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_username(self, username: str) -> bool:
        """Valido username"""
        import re
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))

    def _validate_password(self, password: str) -> Dict[str, Any]:
        """Valido fjalëkalimin"""
        if len(password) < 8:
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën 8 karaktere"}
        if not any(c.isupper() for c in password):
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën një shkronjë të madhe"}
        if not any(c.islower() for c in password):
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën një shkronjë të vogël"}
        if not any(c.isdigit() for c in password):
            return {"valid": False, "error": "Fjalëkalimi duhet të ketë të paktën një numër"}
        return {"valid": True}

    def _create_session(
        self,
        conn,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """Krijo sesion të ri (expects an open connection)"""
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        access_token = f"at_{secrets.token_hex(32)}"
        refresh_token = f"rt_{secrets.token_hex(32)}"
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        now = datetime.now(timezone.utc).isoformat()
        device_type = self._detect_device_type(user_agent) if user_agent else "unknown"

        conn.execute(
            """INSERT INTO sessions
               (session_id, user_id, access_token, refresh_token, expires_at,
                ip_address, user_agent, device_type, created_at, last_activity)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, user_id, access_token, refresh_token, expires_at,
             ip_address, user_agent, device_type, now, now),
        )

        return UserSession(
            session_id=session_id,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            created_at=now,
            last_activity=now,
        )

    def _detect_device_type(self, user_agent: str) -> str:
        """Detekto llojin e pajisjes"""
        ua = user_agent.lower()
        if "mobile" in ua or "android" in ua or "iphone" in ua:
            return "mobile"
        if "tablet" in ua or "ipad" in ua:
            return "tablet"
        return "web"

    def _get_initial_credits(self, plan: SubscriptionPlan) -> int:
        """Kreditet fillestare sipas planit"""
        credits_map = {
            SubscriptionPlan.FREE: 100,
            SubscriptionPlan.STARTER: 1000,
            SubscriptionPlan.STANDARD: 5000,
            SubscriptionPlan.PROFESSIONAL: 20000,
            SubscriptionPlan.ENTERPRISE: 100000
        }
        return credits_map.get(plan, 100)

    @staticmethod
    def _get_storage_limit(plan: SubscriptionPlan) -> float:
        """Limiti i ruajtjes sipas planit (MB)"""
        storage_map = {
            SubscriptionPlan.FREE: 100.0,
            SubscriptionPlan.STARTER: 1000.0,
            SubscriptionPlan.STANDARD: 5000.0,
            SubscriptionPlan.PROFESSIONAL: 20000.0,
            SubscriptionPlan.ENTERPRISE: 100000.0
        }
        return storage_map.get(plan, 100.0)

    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat"""
        with user_db.get_connection() as conn:
            total_users = conn.execute("SELECT COUNT(*) AS c FROM accounts").fetchone()["c"]
            active_users = conn.execute(
                "SELECT COUNT(*) AS c FROM accounts WHERE status = ?", (AccountStatus.ACTIVE.value,)
            ).fetchone()["c"]
            active_sessions = conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone()["c"]
            profiles_count = conn.execute("SELECT COUNT(*) AS c FROM profiles").fetchone()["c"]

        return {
            "total_users": total_users,
            "active_users": active_users,
            "active_sessions": active_sessions,
            "accounts_count": total_users,
            "profiles_count": profiles_count,
            "sessions_count": active_sessions,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON - Instanca globale
# ═══════════════════════════════════════════════════════════════════════════════

_registry: Optional[UserRegistry] = None


def get_user_registry() -> UserRegistry:
    """Merr ose krijo regjistrin e përdoruesve"""
    global _registry
    if _registry is None:
        _registry = UserRegistry()
    return _registry

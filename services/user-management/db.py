"""
CLISONIX USER MANAGEMENT - SQLite persistence layer
=====================================================

Real, on-disk persistence for user_core.py's UserRegistry. Replaces the
previous in-memory-only dict storage: every container restart used to
silently lose every registered account, session and credit balance.

Uses the Python standard library `sqlite3` module only — no new
third-party dependency is introduced. A short-lived connection is opened
per call (WAL journal mode allows safe concurrent readers/writers for a
service at this scale) rather than holding one long-lived connection
across threads, which keeps this correct under FastAPI's threadpool
execution of synchronous endpoint code without extra locking.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator
from contextlib import contextmanager


def get_db_path() -> Path:
    """Resolve the SQLite file path from CLISONIX_USER_DB (real, operator
    configurable), defaulting to ./data/users.db so a fresh checkout still
    works out of the box in development."""
    raw_path = os.getenv("CLISONIX_USER_DB", "").strip() or "./data/users.db"
    path = Path(raw_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Open a short-lived connection with row access by column name and
    foreign keys enforced. Committed/closed automatically on exit."""
    conn = sqlite3.connect(get_db_path(), timeout=30.0)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    user_id               TEXT PRIMARY KEY,
    email                 TEXT NOT NULL UNIQUE,
    password_hash         TEXT NOT NULL,
    role                  TEXT NOT NULL,
    status                TEXT NOT NULL,
    verification          TEXT NOT NULL,
    plan                  TEXT NOT NULL,
    plan_started_at       TEXT,
    plan_expires_at       TEXT,
    mfa_enabled           INTEGER NOT NULL DEFAULT 0,
    mfa_secret            TEXT,
    last_login            TEXT,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until          TEXT,
    api_key               TEXT UNIQUE,
    refresh_token         TEXT,
    clerk_id              TEXT UNIQUE,
    created_at            TEXT NOT NULL,
    updated_at            TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id        TEXT PRIMARY KEY REFERENCES accounts(user_id) ON DELETE CASCADE,
    email          TEXT NOT NULL,
    username       TEXT NOT NULL UNIQUE,
    first_name     TEXT,
    last_name      TEXT,
    display_name   TEXT,
    avatar_url     TEXT,
    phone          TEXT,
    country        TEXT,
    city           TEXT,
    timezone       TEXT NOT NULL DEFAULT 'Europe/Berlin',
    language       TEXT NOT NULL DEFAULT 'en',
    organization   TEXT,
    job_title      TEXT,
    specialization TEXT,
    license_number TEXT,
    metadata       TEXT NOT NULL DEFAULT '{}',
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id     TEXT PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES accounts(user_id) ON DELETE CASCADE,
    access_token   TEXT NOT NULL UNIQUE,
    refresh_token  TEXT NOT NULL,
    expires_at     TEXT NOT NULL,
    ip_address     TEXT,
    user_agent     TEXT,
    device_type    TEXT,
    created_at     TEXT NOT NULL,
    last_activity  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usage (
    user_id              TEXT PRIMARY KEY REFERENCES accounts(user_id) ON DELETE CASCADE,
    credits_balance      INTEGER NOT NULL DEFAULT 0,
    credits_used_today   INTEGER NOT NULL DEFAULT 0,
    credits_used_month   INTEGER NOT NULL DEFAULT 0,
    api_calls_today      INTEGER NOT NULL DEFAULT 0,
    api_calls_month      INTEGER NOT NULL DEFAULT 0,
    storage_used_mb      REAL NOT NULL DEFAULT 0,
    storage_limit_mb     REAL NOT NULL DEFAULT 100,
    ocean_sessions_today INTEGER NOT NULL DEFAULT 0,
    ocean_messages_today INTEGER NOT NULL DEFAULT 0,
    last_api_call        TEXT,
    reset_daily_at       TEXT NOT NULL,
    reset_monthly_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_hash  TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES accounts(user_id) ON DELETE CASCADE,
    expires_at  TEXT NOT NULL,
    used        INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_user ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_expires ON password_reset_tokens(expires_at);
"""


def init_schema() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)

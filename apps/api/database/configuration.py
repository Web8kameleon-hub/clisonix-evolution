"""Explicit storage selection. SQLite by default; PostgreSQL is opt-in."""
import os
from pathlib import Path

from sqlalchemy.engine import make_url


def database_url(raw: str | None = None, *, asynchronous: bool = False):
    raw = os.getenv("API_DATABASE_URL") or raw or os.getenv("DATABASE_URL")
    if not raw:
        path = Path(os.getenv("API_SQLITE_PATH", "./data/platform.db")).resolve()
        raw = f"sqlite:///{path.as_posix()}"
    url = make_url(raw)
    if url.get_backend_name() == "sqlite":
        if url.database and url.database != ":memory:":
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)
        return url.set(drivername="sqlite+aiosqlite" if asynchronous else "sqlite")
    if url.get_backend_name() in ("postgresql", "postgres"):
        return url.set(drivername="postgresql+asyncpg" if asynchronous else "postgresql+psycopg")
    raise ValueError("Supported API storage backends: SQLite, PostgreSQL")


def engine_options(url, *, asynchronous: bool = False):
    if url.get_backend_name() == "sqlite":
        return {"connect_args": {"check_same_thread": False, "timeout": 30}}
    options = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", "2")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "0")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "10")),
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }
    if asynchronous:
        options["connect_args"] = {"server_settings": {"application_name": "Clisonix-api"}}
    return options

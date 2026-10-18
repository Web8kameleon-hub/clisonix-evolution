import asyncio
from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

ROOT = next((p for p in Path(__file__).resolve().parents if (p / "apps" / "api").is_dir()), Path("/app"))
sys.path.insert(0, str(ROOT / "apps" / "api" if (ROOT / "apps" / "api").is_dir() else ROOT))
from database.configuration import database_url, engine_options


def test_sqlite_is_durable_default_without_postgres(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("API_DATABASE_URL", raising=False)
    monkeypatch.setenv("API_SQLITE_PATH", str(tmp_path / "platform.db"))
    url = database_url()
    engine = create_engine(url, **engine_options(url))
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE proof (id INTEGER PRIMARY KEY, value TEXT NOT NULL)"))
        conn.execute(text("INSERT INTO proof VALUES (1, 'durable')"))
    engine.dispose()

    async def verify():
        async_url = database_url(asynchronous=True)
        engine = create_async_engine(async_url, **engine_options(async_url, asynchronous=True))
        async with engine.connect() as conn:
            assert (await conn.execute(text("SELECT value FROM proof"))).scalar_one() == "durable"
        await engine.dispose()
    asyncio.run(verify())


def test_explicit_postgres_uses_correct_drivers_and_small_pool(monkeypatch):
    monkeypatch.setenv("API_DATABASE_URL", "postgresql://user:pass@host/database")
    monkeypatch.delenv("DB_POOL_SIZE", raising=False)
    monkeypatch.delenv("DB_MAX_OVERFLOW", raising=False)
    sync = database_url()
    asynchronous = database_url(asynchronous=True)
    assert sync.drivername == "postgresql+psycopg"
    assert asynchronous.drivername == "postgresql+asyncpg"
    assert engine_options(sync)["pool_size"] == 2
    assert engine_options(sync)["max_overflow"] == 0
    assert "server_settings" in engine_options(asynchronous, asynchronous=True)["connect_args"]


def test_unsupported_database_fails_instead_of_silently_changing_storage(monkeypatch):
    monkeypatch.setenv("API_DATABASE_URL", "otherdb://host/db")
    with pytest.raises(ValueError):
        database_url()

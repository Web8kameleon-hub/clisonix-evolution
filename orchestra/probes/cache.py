"""
orchestra.probes.cache
=======================
Probes the Redis cache instance used across Clisonix services.

Checks
------
  - PING roundtrip
  - Memory usage (warning if > CACHE_WARN_MB)
  - Keyspace hit-rate (warning if < CACHE_MIN_HITRATE %)
  - Connected clients
  - RDB / AOF persistence status
  - Uptime

Env vars
--------
  REDIS_URL            redis://host:port  (default: redis://localhost:6379)
  CACHE_WARN_MB        int                 (default: 256)
  CACHE_MIN_HITRATE    float 0-100         (default: 60)
"""
from __future__ import annotations

import os
import socket
import time
from typing import Any, Dict, Optional

from orchestra.models import ProbeResult, SignalStatus

_REDIS_URL    = os.getenv("REDIS_URL", "redis://localhost:6379")
_WARN_MB      = float(os.getenv("CACHE_WARN_MB", "256"))
_MIN_HITRATE  = float(os.getenv("CACHE_MIN_HITRATE", "60"))


def _parse_url(url: str):
    """Parse redis://host:port/db into (host, port)."""
    url = url.replace("redis://", "").split("/")[0]
    host, _, port = url.partition(":")
    return host or "localhost", int(port or 6379)


def _redis_command(sock: socket.socket, cmd: str) -> str:
    """Send a raw Redis inline command and read one response line."""
    sock.sendall((cmd + "\r\n").encode())
    response = b""
    while not response.endswith(b"\r\n"):
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    return response.decode(errors="ignore").strip()


def _redis_info(host: str, port: int, timeout: int = 5) -> Optional[Dict[str, str]]:
    """Return parsed INFO dict from Redis."""
    with socket.create_connection((host, port), timeout=timeout) as s:
        # PING
        pong = _redis_command(s, "PING")
        if "+PONG" not in pong:
            raise RuntimeError(f"PING failed: {pong!r}")
        # INFO all
        s.sendall(b"INFO all\r\n")
        raw = b""
        # read until we get the bulk string terminator
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            raw += chunk
            if raw.endswith(b"\r\n") or b"\r\n\r\n" in raw:
                # keep reading a bit to get the full INFO dump
                try:
                    s.settimeout(0.2)
                    while True:
                        extra = s.recv(65536)
                        if not extra:
                            break
                        raw += extra
                except Exception:
                    pass
                break

    info: Dict[str, str] = {}
    for line in raw.decode(errors="ignore").splitlines():
        if ":" in line and not line.startswith("#"):
            k, _, v = line.partition(":")
            info[k.strip()] = v.strip()
    return info


def run() -> ProbeResult:
    start = time.monotonic()
    details: Dict[str, Any] = {"redis_url": _REDIS_URL}
    warnings: list[str] = []
    errors:   list[str] = []

    try:
        host, port = _parse_url(_REDIS_URL)
        details["host"] = host
        details["port"] = port

        info = _redis_info(host, port)
        if not info:
            raise RuntimeError("Empty INFO response from Redis")

        # ── key metrics ───────────────────────────────────────────────────────
        version  = info.get("redis_version", "?")
        uptime_s = int(info.get("uptime_in_seconds", 0))
        clients  = int(info.get("connected_clients", 0))
        used_mem = int(info.get("used_memory", 0))
        used_mb  = used_mem / (1024 * 1024)

        hits   = int(info.get("keyspace_hits",   0))
        misses = int(info.get("keyspace_misses", 0))
        total  = hits + misses
        hitrate = (hits / total * 100) if total > 0 else 0.0

        rdb_last_save = info.get("rdb_last_bgsave_status", "?")
        aof_enabled   = info.get("aof_enabled", "0") == "1"

        details.update({
            "version":          version,
            "uptime_seconds":   uptime_s,
            "connected_clients": clients,
            "used_memory_mb":   round(used_mb, 2),
            "keyspace_hits":    hits,
            "keyspace_misses":  misses,
            "hit_rate_pct":     round(hitrate, 1),
            "rdb_status":       rdb_last_save,
            "aof_enabled":      aof_enabled,
        })

        # ── gates ─────────────────────────────────────────────────────────────
        if used_mb > _WARN_MB:
            warnings.append(f"Redis memory {used_mb:.1f} MB > threshold {_WARN_MB} MB")

        if total > 100 and hitrate < _MIN_HITRATE:
            warnings.append(f"Cache hit-rate {hitrate:.1f}% < threshold {_MIN_HITRATE}%")

        if rdb_last_save not in ("ok", "?"):
            warnings.append(f"RDB last bgsave status: {rdb_last_save}")

        # ── result ────────────────────────────────────────────────────────────
        if errors:
            status  = SignalStatus.ERROR
            message = "; ".join(errors)
        elif warnings:
            status  = SignalStatus.WARNING
            message = "; ".join(warnings)
        else:
            status  = SignalStatus.OK
            message = (
                f"Redis {version} OK — "
                f"{used_mb:.1f} MB used, "
                f"hit-rate {hitrate:.1f}%, "
                f"{clients} clients"
            )

    except ConnectionRefusedError:
        status  = SignalStatus.ERROR
        message = f"Redis unreachable at {_REDIS_URL} (connection refused)"
    except Exception as exc:
        status  = SignalStatus.ERROR
        message = f"cache probe failed: {exc}"

    return ProbeResult(
        domain     = "cache",
        status     = status,
        message    = message,
        details    = details,
        latency_ms = (time.monotonic() - start) * 1000,
    )

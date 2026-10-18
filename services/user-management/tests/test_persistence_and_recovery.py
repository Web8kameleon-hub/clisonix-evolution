"""Real functional tests for the user-management service's persistence and
account-recovery behavior. No mocks: exercises the actual SQLite-backed
UserRegistry and a real (hand-rolled, stdlib-only) SMTP server end to end.

Run with: pytest services/user-management/tests/test_persistence_and_recovery.py -v
"""
from __future__ import annotations

import email as email_lib
import os
import socket
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def registry_factory(tmp_path, monkeypatch):
    """Returns a factory that builds a fresh UserRegistry pointed at the
    same on-disk SQLite file, so tests can simulate a container restart by
    just calling the factory again."""
    db_path = tmp_path / "test_users.db"
    monkeypatch.setenv("CLISONIX_USER_DB", str(db_path))
    monkeypatch.delenv("SMTP_HOST", raising=False)

    import user_core
    import importlib
    importlib.reload(user_core)

    def factory():
        return user_core.UserRegistry()

    return factory, user_core


class _MinimalSMTPServer:
    """Hand-rolled, stdlib-socket-only SMTP server for tests. smtpd/asyncore
    were removed from the standard library in Python 3.12+, so this
    implements just enough of the protocol (EHLO/MAIL/RCPT/DATA/QUIT) for
    smtplib to complete a real send."""

    def __init__(self) -> None:
        self.captured: list[str] = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(("127.0.0.1", 0))
        self._socket.listen(1)
        self.port = self._socket.getsockname()[1]
        self._thread = threading.Thread(target=self._serve_once, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def join(self, timeout: float = 3.0) -> None:
        self._thread.join(timeout=timeout)

    def close(self) -> None:
        self._socket.close()

    def _serve_once(self) -> None:
        self._socket.settimeout(5.0)
        try:
            conn, _ = self._socket.accept()
        except OSError:
            return
        with conn:
            conn.sendall(b"220 test.local ESMTP\r\n")
            data_lines: list[bytes] = []
            in_data = False
            buffer = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    return
                buffer += chunk
                while b"\r\n" in buffer:
                    line, buffer = buffer.split(b"\r\n", 1)
                    if in_data:
                        if line == b".":
                            in_data = False
                            self.captured.append(b"\r\n".join(data_lines).decode("utf-8", errors="replace"))
                            conn.sendall(b"250 OK\r\n")
                        else:
                            data_lines.append(line)
                        continue
                    verb = line.decode("utf-8", errors="replace").split()[0].upper() if line else ""
                    if verb == "DATA":
                        conn.sendall(b"354 End with <CRLF>.<CRLF>\r\n")
                        in_data = True
                        data_lines = []
                    elif verb == "QUIT":
                        conn.sendall(b"221 Bye\r\n")
                        return
                    else:
                        conn.sendall(b"250 OK\r\n")


def _extract_reset_token(raw_message: str) -> str | None:
    """Decode the captured SMTP DATA exactly as a real email client would
    (quoted-printable/MIME decoding), then pull the token out of the reset
    link. The real message body contains Albanian diacritics, so Python's
    email encoder picks quoted-printable, which soft-wraps long lines —
    naive raw-line scanning would incorrectly split the token."""
    parsed = email_lib.message_from_string(raw_message)
    decoded_body = parsed.get_payload(decode=True).decode("utf-8")
    for line in decoded_body.splitlines():
        if "token=" in line:
            return line.split("token=")[-1].strip()
    return None


def test_user_data_persists_across_simulated_restart(registry_factory):
    factory, _user_core = registry_factory

    reg = factory()
    result = reg.register_user(
        email="persist-test@example.com",
        username="persisttest",
        password="StrongPass123",
    )
    assert result["success"]

    login1 = reg.login("persist-test@example.com", "StrongPass123")
    assert login1["success"]

    # Simulate a full process/container restart: brand new UserRegistry
    # instance pointed at the same on-disk SQLite file.
    reg2 = factory()
    login2 = reg2.login("persist-test@example.com", "StrongPass123")
    assert login2["success"], "user data must survive a container restart"
    assert reg2.get_stats()["total_users"] >= 1

    bad_login = reg2.login("persist-test@example.com", "WrongPassword999")
    assert not bad_login["success"]


def test_password_reset_without_smtp_fails_honestly(registry_factory):
    factory, user_core = registry_factory
    reg = factory()
    reg.register_user(email="nosmtp@example.com", username="nosmtpuser", password="StrongPass123")

    with pytest.raises(user_core.RecoveryEmailUnavailable):
        reg.request_password_reset("nosmtp@example.com")


def test_password_reset_full_flow_via_real_smtp(registry_factory, monkeypatch):
    factory, _user_core = registry_factory
    reg = factory()
    reg.register_user(email="reset-flow@example.com", username="resetflowuser", password="StrongPass123")

    smtp_server = _MinimalSMTPServer()
    monkeypatch.setenv("SMTP_HOST", "127.0.0.1")
    monkeypatch.setenv("SMTP_PORT", str(smtp_server.port))
    monkeypatch.setenv("SMTP_FROM", "noreply@clisonix.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")
    smtp_server.start()

    try:
        reset_request = reg.request_password_reset("reset-flow@example.com")
        assert reset_request["success"]

        smtp_server.join()
        assert len(smtp_server.captured) == 1, "a real email must have been sent via SMTP"

        token = _extract_reset_token(smtp_server.captured[0])
        assert token, "reset token must be extractable from the real emailed message"

        reset_result = reg.reset_password(token, "NewStrongPass456")
        assert reset_result["success"]

        assert not reg.login("reset-flow@example.com", "StrongPass123")["success"]
        assert reg.login("reset-flow@example.com", "NewStrongPass456")["success"]

        # Token cannot be reused.
        reuse_result = reg.reset_password(token, "AnotherPass789")
        assert not reuse_result["success"]
    finally:
        smtp_server.close()


def test_password_reset_anti_enumeration(registry_factory, monkeypatch):
    """A request for a non-existent email must return the same success
    message as a real one, without generating a token or attempting to
    send anything."""
    factory, _user_core = registry_factory
    reg = factory()

    smtp_server = _MinimalSMTPServer()
    monkeypatch.setenv("SMTP_HOST", "127.0.0.1")
    monkeypatch.setenv("SMTP_PORT", str(smtp_server.port))
    monkeypatch.setenv("SMTP_FROM", "noreply@clisonix.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")
    smtp_server.start()

    try:
        result = reg.request_password_reset("no-such-user@example.com")
        assert result["success"]
    finally:
        smtp_server.close()


def test_change_password_requires_current_password(registry_factory):
    factory, _user_core = registry_factory
    reg = factory()
    result = reg.register_user(email="change-pw@example.com", username="changepwuser", password="StrongPass123")
    user_id = result["user_id"]

    wrong_old = reg.change_password(user_id, "WrongOldPassword", "Irrelevant123")
    assert not wrong_old["success"]

    changed = reg.change_password(user_id, "StrongPass123", "YetAnotherPass999")
    assert changed["success"]

    assert reg.login("change-pw@example.com", "YetAnotherPass999")["success"]
    assert not reg.login("change-pw@example.com", "StrongPass123")["success"]

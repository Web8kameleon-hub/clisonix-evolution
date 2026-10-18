"""
CLISONIX USER MANAGEMENT - Real SMTP email delivery
=====================================================

Sends real transactional email (password reset links) via stdlib
smtplib. Per NO_FAKE_DATA_POLICY.md this module never pretends an email
was sent when it wasn't: if SMTP is not configured via environment
variables, EmailNotConfigured is raised so the caller can return an
honest 503 instead of a fabricated "email sent" success response.

No credential is ever hardcoded; all SMTP settings come from the
environment (os.environ), per the repo's NO HARDCODED KEYS rule.
"""
from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("user_core.email")


class EmailNotConfigured(RuntimeError):
    """Raised when SMTP_HOST is not set — there is no real email
    transport available, so no send should ever be attempted or faked."""


class EmailSendFailed(RuntimeError):
    """Raised when a real SMTP send attempt failed (auth, connection,
    etc.). Carries the real underlying error for logging."""


def is_configured() -> bool:
    return bool(os.getenv("SMTP_HOST", "").strip())


def send_email(*, to: str, subject: str, body_text: str) -> None:
    """Send a real plaintext email via SMTP. Raises EmailNotConfigured if
    no SMTP_HOST is set, or EmailSendFailed if the real send attempt
    failed. Never returns successfully without a real SMTP transaction."""
    host = os.getenv("SMTP_HOST", "").strip()
    if not host:
        raise EmailNotConfigured("SMTP_HOST is not configured")

    port = int(os.getenv("SMTP_PORT", "587").strip() or "587")
    username = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("SMTP_FROM", "").strip() or username
    use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower() not in ("false", "0", "no")

    if not sender:
        raise EmailNotConfigured("SMTP_FROM (or SMTP_USER) is not configured")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to
    message.set_content(body_text)

    try:
        with smtplib.SMTP(host, port, timeout=15) as client:
            if use_tls:
                client.starttls()
            if username and password:
                client.login(username, password)
            client.send_message(message)
    except Exception as exc:  # noqa: BLE001 - real transport failure, surfaced to caller
        logger.error("SMTP send to %s failed: %s", to, exc)
        raise EmailSendFailed(str(exc)) from exc

    logger.info("Password reset email sent to %s via %s:%s", to, host, port)

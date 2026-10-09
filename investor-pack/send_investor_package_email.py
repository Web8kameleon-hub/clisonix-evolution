import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = ROOT / "investor-pack" / "publisher_boardgrade_report.json"
DEFAULT_ATTACHMENT = ROOT / "investor-pack" / "CLISONIX_Board_Grade_Investor_Memo_EN_SQ_DE.docx"


def _load_report() -> dict:
    if not REPORT_FILE.exists():
        return {}
    try:
        return json.loads(REPORT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _resolve_attachment(report: dict) -> Path:
    env_attachment = os.getenv("INVESTOR_ATTACHMENT_PATH", "").strip()
    if env_attachment:
        return (ROOT / env_attachment).resolve() if not Path(env_attachment).is_absolute() else Path(env_attachment)

    output_markdown = str(report.get("output_markdown") or "").strip()
    if output_markdown:
        md_path = (ROOT / output_markdown).resolve() if not Path(output_markdown).is_absolute() else Path(output_markdown)
        if md_path.exists():
            return md_path

    return DEFAULT_ATTACHMENT


def send_investor_email() -> Path:
    report = _load_report()
    attachment_path = _resolve_attachment(report)
    if not attachment_path.exists():
        raise FileNotFoundError(f"Attachment not found: {attachment_path}")

    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587").strip())
    user = (
        os.getenv("SMTP_USER", "").strip()
        or os.getenv("SMTP_USERNAME", "").strip()
    )
    password = (
        os.getenv("SMTP_PASS", "").strip()
        or os.getenv("SMTP_PASSWORD", "").strip()
    )

    if not user or not password:
        raise RuntimeError("Missing SMTP_USER/SMTP_PASS in environment")

    from_addr = os.getenv("REPORT_FROM", user).strip()
    to_addr = os.getenv("REPORT_TO", "").strip()
    if not to_addr:
        raise RuntimeError("Missing REPORT_TO in environment")

    subject = os.getenv("INVESTOR_EMAIL_SUBJECT", "Clisonix Investor Package")
    body = os.getenv(
        "INVESTOR_EMAIL_BODY",
        "Pershendetje,\n\nBashkengjitur keni paketen e investitorit te gjeneruar nga Ocean Mission.\n\nFaleminderit.",
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    data = attachment_path.read_bytes()
    subtype = "octet-stream"
    if attachment_path.suffix.lower() == ".pdf":
        subtype = "pdf"
    elif attachment_path.suffix.lower() == ".docx":
        subtype = "vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif attachment_path.suffix.lower() == ".md":
        subtype = "markdown"

    msg.add_attachment(data, maintype="application", subtype=subtype, filename=attachment_path.name)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(user, password)
        server.send_message(msg)

    return attachment_path


if __name__ == "__main__":
    sent_path = send_investor_email()
    print(json.dumps({"ok": True, "attachment": str(sent_path)}, ensure_ascii=False))

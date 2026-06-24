"""Gmail API tool (Manual 28.2). Mock by default ($0, no key).

Live mode needs a Google OAuth refresh token plus client id/secret. The manual
names them ``GOOGLE_CLIENT_ID`` / ``GOOGLE_CLIENT_SECRET``; the shipped
``.env.example`` historically used ``GMAIL_CLIENT_ID`` / ``GMAIL_CLIENT_SECRET``
— both spellings are accepted here so either env wiring works.
"""

import base64
import os

from tools import is_live


def _client_id() -> str:
    return os.environ.get("GOOGLE_CLIENT_ID") or os.environ.get("GMAIL_CLIENT_ID", "")


def _client_secret() -> str:
    return os.environ.get("GOOGLE_CLIENT_SECRET") or os.environ.get("GMAIL_CLIENT_SECRET", "")


def _get_gmail_service():  # pragma: no cover - needs live credentials
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        client_id=_client_id(),
        client_secret=_client_secret(),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/gmail.modify"],
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def get_recent_emails(max_results: int = 10) -> dict:
    if is_live("GOOGLE_REFRESH_TOKEN"):  # pragma: no cover - needs credentials
        service = _get_gmail_service()
        results = service.users().messages().list(
            userId="me", maxResults=max_results, labelIds=["INBOX"]
        ).execute()
        emails = []
        for msg in results.get("messages", []):
            detail = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata"
            ).execute()
            headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
            emails.append({"from": headers.get("From", ""), "subject": headers.get("Subject", "")})
        return {"emails": emails, "count": len(emails)}

    sample = [
        {"from": "Lahari <lahari@edvisingu.ca>", "subject": "MailerLite sequence ready for QA"},
        {"from": "Whop <noreply@whop.com>", "subject": "New member: Priya Patel joined Premium"},
        {"from": "campaign@drddurham.ca", "subject": "Volunteer signup — Pickering ward 2"},
    ][:max_results]
    return {"mock": True, "emails": sample, "count": len(sample)}


def send_email(to: str, subject: str, body: str) -> dict:
    if is_live("GOOGLE_REFRESH_TOKEN"):  # pragma: no cover - needs credentials
        from email.mime.text import MIMEText

        service = _get_gmail_service()
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"status": "sent", "id": sent.get("id"), "to": to}

    return {"mock": True, "status": "sent", "to": to, "subject": subject,
            "id": f"mock_msg_{abs(hash(subject)) % 100000}",
            "note": "Mock Gmail send. Set GOOGLE_REFRESH_TOKEN + ARCH_BACKEND=live to send for real."}

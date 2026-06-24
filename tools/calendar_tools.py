"""Google Calendar API tool (Manual 28.3). Mock by default ($0, no key)."""

import os
from datetime import datetime, timedelta, timezone

from tools import is_live
from tools.gmail_tools import _client_id, _client_secret


def _get_calendar_service():  # pragma: no cover - needs live credentials
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        client_id=_client_id(),
        client_secret=_client_secret(),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)


def get_todays_events() -> dict:
    if is_live("GOOGLE_REFRESH_TOKEN"):  # pragma: no cover - needs credentials
        service = _get_calendar_service()
        now = datetime.now(timezone.utc).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        events = service.events().list(
            calendarId="primary", timeMin=now, timeMax=end,
            singleEvents=True, orderBy="startTime",
        ).execute()
        items = events.get("items", [])
        return {"events": items, "count": len(items)}

    sample = [
        {"summary": "Content review with Lahari", "start": "09:30", "end": "10:00"},
        {"summary": "hermes-campaign weekly approval", "start": "13:00", "end": "13:30"},
        {"summary": "CrediVersity cohort kickoff", "start": "16:00", "end": "17:00"},
    ]
    return {"mock": True, "events": sample, "count": len(sample)}


def create_event(title: str, start: str, end: str, description: str = "") -> dict:
    if is_live("GOOGLE_REFRESH_TOKEN"):  # pragma: no cover - needs credentials
        service = _get_calendar_service()
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start, "timeZone": "America/Toronto"},
            "end": {"dateTime": end, "timeZone": "America/Toronto"},
        }
        created = service.events().insert(calendarId="primary", body=event).execute()
        return {"status": "created", "id": created.get("id"), "html_link": created.get("htmlLink")}

    return {"mock": True, "status": "created", "title": title, "start": start, "end": end,
            "id": f"mock_evt_{abs(hash(title + start)) % 100000}", "timezone": "America/Toronto",
            "note": "Mock Calendar event. Set GOOGLE_REFRESH_TOKEN + ARCH_BACKEND=live to create for real."}

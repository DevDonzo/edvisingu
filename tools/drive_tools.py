"""Google Drive API tool (Manual 28.5). Mock by default ($0, no key)."""

import os

from tools import is_live
from tools.gmail_tools import _client_id, _client_secret


def _get_drive_service():  # pragma: no cover - needs live credentials
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        client_id=_client_id(),
        client_secret=_client_secret(),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def list_recent_files(max_results: int = 20) -> dict:
    if is_live("GOOGLE_REFRESH_TOKEN"):  # pragma: no cover - needs credentials
        service = _get_drive_service()
        results = service.files().list(
            pageSize=max_results, orderBy="modifiedTime desc",
            fields="files(id, name, mimeType, modifiedTime)",
        ).execute()
        files = results.get("files", [])
        return {"files": files, "count": len(files)}

    sample = [
        {"id": "mock_1", "name": "DrDDurham — Week 14 content.docx", "mimeType": "application/vnd.google-apps.document"},
        {"id": "mock_2", "name": "EdVisingU MRR tracker.xlsx", "mimeType": "application/vnd.google-apps.spreadsheet"},
        {"id": "mock_3", "name": "CrediVersity cohort roster.csv", "mimeType": "text/csv"},
    ][:max_results]
    return {"mock": True, "files": sample, "count": len(sample)}


def search_files(query: str) -> dict:
    if is_live("GOOGLE_REFRESH_TOKEN"):  # pragma: no cover - needs credentials
        service = _get_drive_service()
        results = service.files().list(
            q=f"fullText contains '{query}'", fields="files(id, name, mimeType)",
        ).execute()
        files = results.get("files", [])
        return {"query": query, "files": files, "count": len(files)}

    sample = [
        {"id": f"mock_{abs(hash(query)) % 1000}", "name": f"{query} — notes.docx",
         "mimeType": "application/vnd.google-apps.document"},
    ]
    return {"mock": True, "query": query, "files": sample, "count": len(sample)}

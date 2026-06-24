"""Tool 4 — n8n workflow trigger. Mock by default (Manual 23.4)."""

import os

from tools import is_live


def trigger_workflow(webhook_id: str, payload: dict) -> dict:
    if is_live():  # n8n has no API key; live mode + reachable n8n only
        import httpx  # pragma: no cover - needs running n8n

        n8n = os.environ.get("N8N_BASE_URL", "http://n8n:5678")
        try:
            r = httpx.post(f"{n8n}/webhook/{webhook_id}", json=payload, timeout=30)
            return {"status": r.status_code, "response": r.text}
        except Exception as exc:  # pragma: no cover
            return {"status": 0, "error": str(exc)}
    return {"mock": True, "status": 200, "webhook": webhook_id, "payload": payload,
            "response": "Mock n8n execution queued."}


def trigger_content_pipeline(topic: str, platform: str) -> dict:
    return trigger_workflow("content-pipeline", {"topic": topic, "platform": platform})


def trigger_email_send(to: str, subject: str, body: str) -> dict:
    return trigger_workflow("gmail-send", {"to": to, "subject": subject, "body": body})

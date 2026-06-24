"""Tool 5 — Notion API. Mock by default (Manual 23.5)."""

import os

from tools import is_live


def create_notion_page(parent_id: str, title: str, content: str) -> dict:
    if is_live("NOTION_TOKEN"):  # pragma: no cover - needs token
        from notion_client import Client

        notion = Client(auth=os.environ["NOTION_TOKEN"])
        p = notion.pages.create(
            parent={"page_id": parent_id},
            properties={"title": {"title": [{"text": {"content": title}}]}},
            children=[{
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]},
            }],
        )
        return {"page_id": p["id"], "url": p["url"]}
    return {"mock": True, "page_id": f"mock_page_{abs(hash(title)) % 100000}",
            "url": f"https://notion.so/mock-{abs(hash(title)) % 100000}", "title": title}


def append_to_database(db_id: str, properties: dict) -> dict:
    if is_live("NOTION_TOKEN"):  # pragma: no cover - needs token
        from notion_client import Client

        notion = Client(auth=os.environ["NOTION_TOKEN"])
        p = notion.pages.create(parent={"database_id": db_id}, properties=properties)
        return {"page_id": p["id"]}
    return {"mock": True, "page_id": f"mock_row_{abs(hash(str(properties))) % 100000}", "db_id": db_id}

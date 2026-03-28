"""
ELYX Email MCP Server
Gmail integration: send, draft, search, read, mark as read, archive.
"""

import os
import json
import base64
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

mcp = FastMCP("elyx-email-mcp")

# --- Gmail client (lazy init) ---

_gmail = None


def _get_gmail():
    global _gmail
    if _gmail is not None:
        return _gmail

    creds_path = Path(os.environ.get("GMAIL_CREDENTIALS_PATH", "gmail_credentials.json")).resolve()
    token_path = creds_path.parent / "gmail_token.json"

    if not token_path.exists():
        raise RuntimeError(f"Gmail token not found at {token_path}. Authenticate first.")

    token_data = json.loads(token_path.read_text())
    creds = Credentials.from_authorized_user_info(token_data)
    _gmail = build("gmail", "v1", credentials=creds)
    return _gmail


def _make_message(to: str, subject: str, body: str, is_html: bool = False) -> str:
    mime_type = "text/html" if is_html else "text/plain"
    raw = "\n".join([
        f"To: {to}",
        f"Subject: {subject}",
        "MIME-Version: 1.0",
        f"Content-Type: {mime_type}; charset=utf-8",
        "",
        body,
    ])
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


# --- Tools ---


@mcp.tool()
def send_email(to: str, subject: str, body: str, is_html: bool = False) -> str:
    """Send an email via Gmail."""
    gmail = _get_gmail()
    resp = gmail.users().messages().send(
        userId="me", body={"raw": _make_message(to, subject, body, is_html)}
    ).execute()
    return json.dumps({"success": True, "message_id": resp["id"], "to": to})


@mcp.tool()
def draft_email(to: str, subject: str, body: str, is_html: bool = False) -> str:
    """Create a Gmail draft (does not send)."""
    gmail = _get_gmail()
    resp = gmail.users().drafts().create(
        userId="me", body={"message": {"raw": _make_message(to, subject, body, is_html)}}
    ).execute()
    return json.dumps({"success": True, "draft_id": resp["id"], "to": to})


@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> str:
    """Search Gmail for emails matching a query."""
    gmail = _get_gmail()
    resp = gmail.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = resp.get("messages", [])

    results = []
    for msg in messages:
        full = gmail.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()
        headers = {h["name"]: h["value"] for h in full["payload"]["headers"]}
        results.append({
            "id": msg["id"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
        })
    return json.dumps({"count": len(results), "emails": results})


@mcp.tool()
def read_email(email_id: str) -> str:
    """Read the full content of an email by its ID."""
    gmail = _get_gmail()
    msg = gmail.users().messages().get(userId="me", id=email_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

    body = ""
    payload = msg["payload"]
    if payload.get("body", {}).get("data"):
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    elif payload.get("parts"):
        for part in payload["parts"]:
            if part.get("body", {}).get("data"):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                break

    return json.dumps({
        "id": msg["id"],
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "body": body,
    })


@mcp.tool()
def mark_as_read(email_ids: list[str]) -> str:
    """Mark one or more emails as read."""
    gmail = _get_gmail()
    for eid in email_ids:
        gmail.users().messages().modify(
            userId="me", id=eid, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
    return json.dumps({"success": True, "marked": len(email_ids)})


@mcp.tool()
def archive_email(email_ids: list[str]) -> str:
    """Archive one or more emails (remove from Inbox)."""
    gmail = _get_gmail()
    for eid in email_ids:
        gmail.users().messages().modify(
            userId="me", id=eid, body={"removeLabelIds": ["INBOX"]}
        ).execute()
    return json.dumps({"success": True, "archived": len(email_ids)})


if __name__ == "__main__":
    mcp.run(transport="stdio")

"""
ELYX WhatsApp MCP Server
WhatsApp Web automation: send messages, read chats, check urgent messages.
"""

import os
import json
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

mcp = FastMCP("elyx-whatsapp-mcp")

HEADLESS = os.environ.get("BROWSER_HEADLESS", "true").lower() == "true"
CHROME_DIR = os.environ.get("CHROME_USER_DATA_DIR", "")
VAULT_PATH = Path(os.environ.get("VAULT_PATH", "obsidian_vault"))
DEFAULT_KEYWORDS = os.environ.get(
    "WHATSAPP_KEYWORDS", "urgent,asap,invoice,payment,help,emergency,critical,important"
).split(",")


def _launch_browser():
    pw = sync_playwright().start()
    if CHROME_DIR:
        ctx = pw.chromium.launch_persistent_context(CHROME_DIR, headless=HEADLESS)
    else:
        browser = pw.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context()
    return pw, ctx


def _open_whatsapp(ctx):
    page = ctx.new_page()
    page.goto("https://web.whatsapp.com", timeout=60000)
    page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
    return page


# --- Tools ---


@mcp.tool()
def send_message(contact: str, message: str) -> str:
    """Send a WhatsApp message to a contact (name or phone number)."""
    pw, ctx = _launch_browser()
    try:
        page = _open_whatsapp(ctx)
        search = page.locator('[data-testid="chat-list-search"]')
        search.click()
        search.fill(contact)
        page.wait_for_timeout(2000)

        # Click first matching chat
        page.locator(f'span[title*="{contact}"]').first.click(timeout=10000)
        page.wait_for_timeout(1000)

        # Type and send
        msg_box = page.locator('[data-testid="conversation-compose-box-input"]')
        msg_box.fill(message)
        page.locator('[data-testid="send"]').click()
        page.wait_for_timeout(2000)

        return json.dumps({"success": True, "contact": contact, "message_length": len(message)})
    finally:
        ctx.close()
        pw.stop()


@mcp.tool()
def send_bulk_message(contacts: list[str], message: str) -> str:
    """Schedule a bulk WhatsApp message. Creates an approval file (HITL)."""
    ts = datetime.now().isoformat()
    filename = f"WHATSAPP_BULK_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    approval_path = VAULT_PATH / "Pending_Approval" / filename
    approval_path.parent.mkdir(parents=True, exist_ok=True)

    md = f"""---
type: whatsapp_bulk
contacts: {len(contacts)}
created: {ts}
status: pending
---

## Message
{message}

## Recipients
{chr(10).join(f'- {c}' for c in contacts)}

## To Approve
Move this file to the Approved/ folder.
"""
    approval_path.write_text(md, encoding="utf-8")
    return json.dumps({"success": True, "approval_file": str(approval_path), "contacts": len(contacts)})


@mcp.tool()
def get_recent_chats(unread_only: bool = True, limit: int = 20) -> str:
    """Get recent WhatsApp chats."""
    pw, ctx = _launch_browser()
    try:
        page = _open_whatsapp(ctx)
        selector = '[aria-label*="unread"]' if unread_only else '[data-testid="cell-frame-container"]'
        elements = page.query_selector_all(selector)

        chats = []
        for el in elements[:limit]:
            text = el.inner_text()
            chats.append({"preview": text[:200]})

        return json.dumps({"count": len(chats), "chats": chats})
    finally:
        ctx.close()
        pw.stop()


@mcp.tool()
def mark_as_read(contact: str) -> str:
    """Mark a WhatsApp chat as read by opening it."""
    pw, ctx = _launch_browser()
    try:
        page = _open_whatsapp(ctx)
        search = page.locator('[data-testid="chat-list-search"]')
        search.click()
        search.fill(contact)
        page.wait_for_timeout(2000)
        page.locator(f'span[title*="{contact}"]').first.click(timeout=10000)
        page.wait_for_timeout(2000)
        return json.dumps({"success": True, "contact": contact})
    finally:
        ctx.close()
        pw.stop()


@mcp.tool()
def check_urgent_messages(keywords: list[str] | None = None) -> str:
    """Check for urgent WhatsApp messages matching keywords."""
    kw_list = keywords or DEFAULT_KEYWORDS
    pw, ctx = _launch_browser()
    try:
        page = _open_whatsapp(ctx)
        unread = page.query_selector_all('[aria-label*="unread"]')
        urgent = []
        for el in unread:
            text = el.inner_text().lower()
            matched = [k for k in kw_list if k.strip().lower() in text]
            if matched:
                urgent.append({"preview": text[:200], "matched_keywords": matched})

        return json.dumps({"count": len(urgent), "urgent_messages": urgent})
    finally:
        ctx.close()
        pw.stop()


if __name__ == "__main__":
    mcp.run(transport="stdio")

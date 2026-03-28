"""
ELYX Social Media MCP Server
LinkedIn, Facebook, Twitter/X, Instagram posting via Playwright browser automation.
"""

import os
import json
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

mcp = FastMCP("elyx-social-mcp")

HEADLESS = os.environ.get("BROWSER_HEADLESS", "true").lower() == "true"
CHROME_DIR = os.environ.get("CHROME_USER_DATA_DIR", "")
VAULT_PATH = Path(os.environ.get("VAULT_PATH", "obsidian_vault"))


def _launch_browser():
    pw = sync_playwright().start()
    if CHROME_DIR:
        ctx = pw.chromium.launch_persistent_context(CHROME_DIR, headless=HEADLESS)
    else:
        browser = pw.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context()
    return pw, ctx


# --- Tools ---


@mcp.tool()
def linkedin_post(content: str) -> str:
    """Create a LinkedIn post (max 3000 chars)."""
    pw, ctx = _launch_browser()
    try:
        page = ctx.new_page()
        page.goto("https://www.linkedin.com/feed/", wait_until="networkidle", timeout=30000)
        page.click('[role="button"]:has-text("Start a post")', timeout=10000)
        page.wait_for_selector('[role="textbox"]', timeout=10000)
        page.fill('[role="textbox"]', content[:3000])
        page.click('button:has-text("Post")', timeout=10000)
        page.wait_for_timeout(3000)
        return json.dumps({"success": True, "platform": "linkedin", "chars": len(content)})
    finally:
        ctx.close()
        pw.stop()


@mcp.tool()
def facebook_post(content: str) -> str:
    """Create a Facebook post."""
    pw, ctx = _launch_browser()
    try:
        page = ctx.new_page()
        page.goto("https://www.facebook.com/", wait_until="networkidle", timeout=30000)
        page.click('[aria-label="Create a post"]', timeout=10000)
        page.wait_for_selector('[role="textbox"]', timeout=10000)
        page.fill('[role="textbox"]', content)
        page.click('[aria-label="Post"]', timeout=10000)
        page.wait_for_timeout(3000)
        return json.dumps({"success": True, "platform": "facebook"})
    finally:
        ctx.close()
        pw.stop()


@mcp.tool()
def twitter_post(content: str) -> str:
    """Create a tweet on Twitter/X (max 280 chars)."""
    pw, ctx = _launch_browser()
    try:
        page = ctx.new_page()
        page.goto("https://x.com/compose/post", wait_until="networkidle", timeout=30000)
        page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
        page.fill('[data-testid="tweetTextarea_0"]', content[:280])
        page.click('[data-testid="tweetButton"]', timeout=10000)
        page.wait_for_timeout(3000)
        return json.dumps({"success": True, "platform": "twitter", "chars": len(content[:280])})
    finally:
        ctx.close()
        pw.stop()


@mcp.tool()
def instagram_post(content: str, image_url: str = "") -> str:
    """Create an Instagram post (requires image_url for full post)."""
    pw, ctx = _launch_browser()
    try:
        page = ctx.new_page()
        page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        return json.dumps({
            "success": False,
            "platform": "instagram",
            "note": "Instagram web posting requires image upload. Use the mobile app or Graph API for full support.",
        })
    finally:
        ctx.close()
        pw.stop()


@mcp.tool()
def schedule_social_post(content: str, platforms: list[str], scheduled_time: str = "") -> str:
    """Schedule a post for multiple platforms. Creates an approval file in the vault."""
    ts = datetime.now().isoformat()
    filename = f"SOCIAL_POST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    approval_path = VAULT_PATH / "Pending_Approval" / filename
    approval_path.parent.mkdir(parents=True, exist_ok=True)

    md = f"""---
type: social_post
platforms: {', '.join(platforms)}
scheduled_time: {scheduled_time or 'immediate'}
created: {ts}
status: pending
---

## Content
{content}

## Platforms
{chr(10).join(f'- {p}' for p in platforms)}

## To Approve
Move this file to the Approved/ folder.
"""
    approval_path.write_text(md, encoding="utf-8")
    return json.dumps({"success": True, "approval_file": str(approval_path), "platforms": platforms})


if __name__ == "__main__":
    mcp.run(transport="stdio")

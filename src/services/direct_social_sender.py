#!/usr/bin/env python3
"""
Direct Social Media Sender
Sends messages and posts via existing browser sessions (no MCP, no asyncio conflicts)

Usage:
    python src/services/direct_social_sender.py linkedin "Hello from ELYX"
    python src/services/direct_social_sender.py facebook "Test message"
    python src/services/direct_social_sender.py twitter "Test tweet"
    python src/services/direct_social_sender.py instagram "Test caption" [image_path]
    python src/services/direct_social_sender.py linkedin-post "Feed post content"
    python src/services/direct_social_sender.py twitter-post "Tweet content"
    python src/services/direct_social_sender.py facebook-post "Feed post content"
"""

import sys
import time
import logging
from pathlib import Path

logger = logging.getLogger("DirectSocialSender")

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    PLAYWRIGHT_AVAILABLE = False


def _launch_browser(session_path: str, headless: bool = False):
    """Launch a persistent browser context with anti-detection flags"""
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    browser = p.chromium.launch_persistent_context(
        session_path,
        headless=headless,
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    return p, browser, page


def _check_login(page, login_indicator: str, platform: str) -> bool:
    """Check if logged in by looking for an indicator element"""
    try:
        page.wait_for_selector(login_indicator, timeout=10000)
        return True
    except Exception:
        if "login" in page.url.lower() or "accounts" in page.url.lower():
            logger.error(f"Not logged in to {platform}. Run: python setup_sessions.py {platform.lower()}")
            return False
        return False


def send_linkedin_message(message: str, recipient: str = None, session_path: str = None):
    """Send LinkedIn feed post using existing session"""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    session_path = session_path or "sessions/linkedin_session"

    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return {"success": False, "error": "Not logged in. Run: python setup_sessions.py linkedin"}

        # Click "Start a post" button
        start_post = page.query_selector('button.share-box-feed-entry__trigger, button[aria-label*="Start a post"]')
        if not start_post:
            # Try alternative selector
            start_post = page.query_selector('[data-test-id="share-box-feed-entry__trigger"]')
        if not start_post:
            return {"success": False, "error": "Could not find 'Start a post' button on LinkedIn"}

        start_post.click()
        time.sleep(2)

        # Fill the post editor
        editor = page.wait_for_selector('.ql-editor[contenteditable="true"], div[role="textbox"][contenteditable="true"]', timeout=10000)
        editor.click()
        page.keyboard.type(message, delay=30)
        time.sleep(1)

        # Click Post button
        post_btn = page.query_selector('button.share-actions__primary-action, button[aria-label="Post"]')
        if not post_btn:
            post_btn = page.query_selector('button:has-text("Post")')
        if post_btn:
            post_btn.click()
            time.sleep(3)
            return {"success": True, "message": "LinkedIn post published successfully", "platform": "linkedin"}
        else:
            return {"success": False, "error": "Could not find Post button"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if p:
            try:
                browser.close()
                p.stop()
            except Exception:
                pass


def send_facebook_message(message: str, recipient: str = None, session_path: str = None):
    """Post to Facebook feed using existing session"""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    session_path = session_path or "sessions/facebook_session"

    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.facebook.com/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return {"success": False, "error": "Not logged in. Run: python setup_sessions.py facebook"}

        # Click "What's on your mind?" to open post composer
        create_post = page.query_selector('[aria-label="Create a post"], [data-testid="create_post"], span:has-text("What\'s on your mind")')
        if not create_post:
            # Try clicking the status update area
            create_post = page.query_selector('[role="button"]:has-text("What\'s on your mind")')
        if not create_post:
            return {"success": False, "error": "Could not find post creation area on Facebook"}

        create_post.click()
        time.sleep(2)

        # Fill the post content
        post_input = page.wait_for_selector('[contenteditable="true"][role="textbox"], div[data-testid="post-message-input"]', timeout=10000)
        post_input.click()
        page.keyboard.type(message, delay=30)
        time.sleep(1)

        # Click Post button
        post_btn = page.query_selector('div[aria-label="Post"][role="button"], button[data-testid="react-composer-post-button"]')
        if not post_btn:
            post_btn = page.query_selector('[aria-label="Post"]')
        if post_btn:
            post_btn.click()
            time.sleep(3)
            return {"success": True, "message": "Facebook post published successfully", "platform": "facebook"}
        else:
            return {"success": False, "error": "Could not find Post button"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if p:
            try:
                browser.close()
                p.stop()
            except Exception:
                pass


def send_twitter_dm(message: str, username: str = None, session_path: str = None):
    """Post a tweet using existing session"""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    session_path = session_path or "sessions/twitter_session"

    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://x.com/home", timeout=60000)
        time.sleep(3)

        # Check login
        try:
            page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=10000)
        except Exception:
            if "login" in page.url.lower():
                return {"success": False, "error": "Not logged in. Run: python setup_sessions.py twitter"}

        # Click tweet compose box
        tweet_box = page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
        tweet_box.click()
        time.sleep(1)

        # Type the tweet (280 char limit)
        content = message[:280] if len(message) > 280 else message
        page.keyboard.type(content, delay=30)
        time.sleep(1)

        # Click Post button
        post_btn = page.wait_for_selector('[data-testid="tweetButton"], [data-testid="tweetButtonInline"]', timeout=10000)
        post_btn.click()
        time.sleep(3)

        return {"success": True, "message": "Tweet posted successfully", "platform": "twitter"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if p:
            try:
                browser.close()
                p.stop()
            except Exception:
                pass


def send_instagram_dm(message: str, image_path: str = None, session_path: str = None):
    """Post to Instagram feed (requires image) using existing session"""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    session_path = session_path or "sessions/instagram_session"

    if not image_path or not Path(image_path).exists():
        return {"success": False, "error": f"Instagram requires an image. Provide a valid image_path. Got: {image_path}"}

    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.instagram.com/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower() or "accounts" in page.url.lower():
            return {"success": False, "error": "Not logged in. Run: python setup_sessions.py instagram"}

        # Click Create / New Post button
        create_btn = page.query_selector('svg[aria-label="New post"], [aria-label="New post"]')
        if not create_btn:
            create_btn = page.query_selector('a[href="/create/style/"]')
        if not create_btn:
            # Try the + icon in nav
            nav_items = page.query_selector_all('svg[aria-label]')
            for item in nav_items:
                label = item.get_attribute('aria-label') or ''
                if 'new' in label.lower() or 'create' in label.lower():
                    create_btn = item
                    break

        if not create_btn:
            return {"success": False, "error": "Could not find Create/New Post button on Instagram"}

        create_btn.click()
        time.sleep(2)

        # Upload image via file input
        file_input = page.wait_for_selector('input[type="file"]', timeout=10000)
        file_input.set_input_files(image_path)
        time.sleep(3)

        # Click Next (crop step)
        next_btn = page.query_selector('button:has-text("Next"), div[role="button"]:has-text("Next")')
        if next_btn:
            next_btn.click()
            time.sleep(2)

        # Click Next again (filter step)
        next_btn = page.query_selector('button:has-text("Next"), div[role="button"]:has-text("Next")')
        if next_btn:
            next_btn.click()
            time.sleep(2)

        # Add caption
        caption_input = page.query_selector('textarea[aria-label*="caption"], textarea[aria-label*="Write"]')
        if caption_input:
            caption_input.click()
            # Instagram caption limit: 2200 chars
            caption = message[:2200] if len(message) > 2200 else message
            page.keyboard.type(caption, delay=20)
            time.sleep(1)

        # Click Share
        share_btn = page.query_selector('button:has-text("Share"), div[role="button"]:has-text("Share")')
        if share_btn:
            share_btn.click()
            time.sleep(5)
            return {"success": True, "message": "Instagram post published successfully", "platform": "instagram"}
        else:
            return {"success": False, "error": "Could not find Share button"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if p:
            try:
                browser.close()
                p.stop()
            except Exception:
                pass


def send_gmail_via_browser(to: str, subject: str, body: str, session_path: str = None):
    """
    Send an email by opening Gmail in the browser, composing, and clicking Send.
    Uses sessions/gmail_session (log in once via browser when prompted).
    No MCP or Gmail API required.
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    session_path = session_path or "sessions/gmail_session"
    Path(session_path).mkdir(parents=True, exist_ok=True)

    p = None
    try:
        p, browser, page = _launch_browser(session_path, headless=False)
        page.goto("https://mail.google.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        if "accounts.google" in page.url or "login" in page.url.lower():
            logger.warning("Gmail not logged in. Browser opened — log in to Gmail, then run again.")
            return {"success": False, "error": "Not logged in to Gmail. Open browser and log in to Gmail once."}

        # Click Compose (role or text)
        compose = page.get_by_role("button", name="Compose").first
        try:
            compose.wait_for(state="visible", timeout=15000)
            compose.click()
        except Exception:
            compose = page.get_by_text("Compose", exact=True).first
            compose.wait_for(state="visible", timeout=5000)
            compose.click()
        time.sleep(2)

        # To
        to_field = page.get_by_role("combobox", name="To").or_(page.locator('input[aria-label*="To"], input[name="to"]')).first
        to_field.wait_for(state="visible", timeout=10000)
        to_field.fill(to)
        time.sleep(0.5)

        # Subject (optional placeholder "Subject" or "Add a subject")
        subj_sel = page.get_by_role("textbox", name="Subject").or_(
            page.locator('input[aria-label*="Subject"], input[name="subject"]')
        ).first
        try:
            subj_sel.wait_for(state="visible", timeout=5000)
            subj_sel.fill(subject)
        except Exception:
            pass
        time.sleep(0.5)

        # Body (contenteditable or role=textbox)
        body_el = page.locator('div[aria-label*="Message"], div[contenteditable="true"]').first
        try:
            body_el.wait_for(state="visible", timeout=5000)
            body_el.click()
            page.keyboard.type(body, delay=20)
        except Exception:
            body_el = page.get_by_role("textbox").last
            body_el.fill(body)
        time.sleep(1)

        # Send
        send_btn = page.get_by_role("button", name="Send").first
        try:
            send_btn.wait_for(state="visible", timeout=5000)
            send_btn.click()
        except Exception:
            send_btn = page.get_by_text("Send", exact=True).first
            send_btn.click()
        time.sleep(2)

        return {"success": True, "message": "Email sent via Gmail (browser)", "platform": "gmail"}
    except Exception as e:
        logger.exception("Gmail browser send failed")
        return {"success": False, "error": str(e)}
    finally:
        if p:
            try:
                browser.close()
                p.stop()
            except Exception:
                pass


def verify_session(platform: str, session_path: str = None):
    """Verify a platform session is still logged in without posting"""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    platforms = {
        "linkedin": {"url": "https://www.linkedin.com/feed/", "session": "sessions/linkedin_session", "check": "login"},
        "facebook": {"url": "https://www.facebook.com/", "session": "sessions/facebook_session", "check": "login"},
        "twitter": {"url": "https://x.com/home", "session": "sessions/twitter_session", "check": "login"},
        "instagram": {"url": "https://www.instagram.com/", "session": "sessions/instagram_session", "check": "login"},
    }

    if platform not in platforms:
        return {"success": False, "error": f"Unknown platform: {platform}"}

    config = platforms[platform]
    session = session_path or config["session"]

    p = None
    try:
        p, browser, page = _launch_browser(session)
        page.goto(config["url"], timeout=60000)
        time.sleep(3)

        if config["check"] in page.url.lower():
            return {"success": False, "error": f"Not logged in to {platform}. Run: python setup_sessions.py {platform}"}

        return {"success": True, "message": f"{platform.title()} session is active and valid"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if p:
            try:
                browser.close()
                p.stop()
            except Exception:
                pass


def main():
    if len(sys.argv) < 3:
        print("Usage: python direct_social_sender.py <platform> <message> [image_path]")
        print("Platforms: linkedin, facebook, twitter, instagram")
        print("Commands: linkedin-post, twitter-post, facebook-post, instagram (needs image)")
        print("Session:  verify-linkedin, verify-facebook, verify-twitter, verify-instagram")
        sys.exit(1)

    platform = sys.argv[1].lower()
    message = sys.argv[2]
    image_path = sys.argv[3] if len(sys.argv) > 3 else None

    # Handle verify commands
    if platform.startswith("verify-"):
        plat = platform.replace("verify-", "")
        result = verify_session(plat)
        if result.get("success"):
            print(f"[OK] {plat.title()}: {result.get('message')}")
        else:
            print(f"[FAIL] {plat.title()}: {result.get('error')}")
        sys.exit(0 if result.get("success") else 1)

    print(f"Sending to {platform}: {message[:80]}...")

    if platform in ("linkedin", "linkedin-post"):
        result = send_linkedin_message(message)
    elif platform in ("facebook", "facebook-post"):
        result = send_facebook_message(message)
    elif platform in ("twitter", "twitter-post"):
        result = send_twitter_dm(message)
    elif platform == "instagram":
        result = send_instagram_dm(message, image_path=image_path)
    else:
        print(f"Unknown platform: {platform}")
        sys.exit(1)

    if result.get("success"):
        print(f"[OK] {platform.title()}: {result.get('message')}")
    else:
        print(f"[FAIL] {platform.title()}: {result.get('error')}")

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

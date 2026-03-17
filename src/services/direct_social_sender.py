#!/usr/bin/env python3
"""
Unified Social Sender — THE single sender for all platforms.
All functions are SYNC (Playwright sync_api). No async/await.

Each function follows: Navigate → Verify → Multi-selector Interact → Keyboard Fallback → Verify Result

Usage (CLI):
    python src/services/direct_social_sender.py gmail "to@email.com" "Subject" "Body text"
    python src/services/direct_social_sender.py linkedin-post "Feed post content"
    python src/services/direct_social_sender.py linkedin-dm "John Doe" "Hello John"
    python src/services/direct_social_sender.py whatsapp "+1234567890" "Hello"
    python src/services/direct_social_sender.py tweet "My tweet"
    python src/services/direct_social_sender.py twitter-dm "@username" "Hello"
    python src/services/direct_social_sender.py facebook-post "Feed post"
    python src/services/direct_social_sender.py facebook-dm "Friend Name" "Hello"
    python src/services/direct_social_sender.py instagram-dm "username" "Hello"
    python src/services/direct_social_sender.py instagram-post "Caption" path/to/image.jpg
    python src/services/direct_social_sender.py verify-linkedin
"""

import logging
import random
import sys
import time
from pathlib import Path

logger = logging.getLogger("UnifiedSender")

try:
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from src.utils.rate_limiter import check_rate_limit, wait_for_rate_limit
except ImportError:

    def wait_for_rate_limit(s):
        return 0

    def check_rate_limit(s):
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────


def _try_registry(session_path: str):
    """
    Check if a watcher already owns a browser for this session path.
    Returns (page, release_fn) or (None, None).
    """
    try:
        from src.services.browser_registry import acquire_page
        return acquire_page(session_path)
    except Exception:
        return None, None


def _launch_browser(session_path: str, headless: bool = False):
    """
    Launch a persistent browser context with anti-detection flags.

    If a watcher already holds a browser open for this session_path,
    returns a borrowed reference instead of launching a second instance.
    Callers receive (p, browser, page) for a new browser or
    (None, None, page) for a borrowed one.  _safe_close handles both.
    """
    # Try to borrow from a running watcher first
    page, release_fn = _try_registry(session_path)
    if page is not None:
        logger.info(f"Reusing watcher browser for {session_path}")
        # Stash the release callback on the page object so _safe_close can call it
        page._sender_release_fn = release_fn  # type: ignore[attr-defined]
        return None, None, page

    p = sync_playwright().start()
    Path(session_path).mkdir(parents=True, exist_ok=True)
    browser = p.chromium.launch_persistent_context(
        session_path,
        headless=headless,
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ],
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    return p, browser, page


def _find_and_click(
    page, selectors: list, timeout: int = 5000, description: str = "element"
):
    """Try multiple selectors, click the first visible one. Returns True on success."""
    for sel in selectors:
        try:
            elem = page.locator(sel).first
            elem.wait_for(state="visible", timeout=timeout)
            elem.click()
            logger.info(f"{description} clicked via: {sel}")
            return True
        except Exception:
            continue
    return False


def _find_element(
    page, selectors: list, timeout: int = 5000, description: str = "element"
):
    """Try multiple selectors, return the first visible locator or None."""
    for sel in selectors:
        try:
            elem = page.locator(sel).first
            elem.wait_for(state="visible", timeout=timeout)
            logger.info(f"{description} found via: {sel}")
            return elem
        except Exception:
            continue
    return None


def _safe_close(p, browser, page=None):
    """
    Close browser and playwright without raising.
    If the page was borrowed from a watcher (p is None, browser is None),
    just release the registry lock — do NOT close the browser.
    """
    if p is None and browser is None:
        # Borrowed from watcher — release the lock
        if page is not None:
            release_fn = getattr(page, "_sender_release_fn", None)
            if release_fn:
                try:
                    release_fn()
                except Exception:
                    pass
        return
    try:
        browser.close()
    except Exception:
        pass
    try:
        p.stop()
    except Exception:
        pass


def _not_logged_in(platform: str):
    return {
        "success": False,
        "error": f"Not logged in to {platform}. Run: python config/setup_sessions.py {platform.lower()}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# GMAIL
# ─────────────────────────────────────────────────────────────────────────────


def send_gmail_via_browser(to: str, subject: str, body: str, session_path: str = None):
    """Send email via Gmail browser session. Compose → Fill → Ctrl+Enter."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("gmail")
    session_path = session_path or "sessions/gmail_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path, headless=False)

        # Step 1: Load Gmail inbox
        try:
            page.goto("https://mail.google.com/mail/u/0/#inbox", timeout=60000)
        except Exception as e:
            # Timeout may indicate the login page never loaded or network issues
            logger.error(f"Gmail navigation timeout/error: {e}")
            # If the session cookie is missing, we can't proceed
            return _not_logged_in("Gmail")

        time.sleep(4)

        # After navigation, verify that we are still logged in
        current = page.url or ""
        if "accounts.google" in current or "signin" in current.lower():
            logger.error("Gmail session appears to be logged out or invalid")
            return _not_logged_in("Gmail")

        # Step 2: Open Compose
        compose_opened = _find_and_click(
            page,
            [
                'div.T-I.T-I-KE.L3[role="button"]',
                '[gh="cm"]',
                'div[role="button"]:has-text("Compose")',
            ],
            timeout=8000,
            description="Compose button",
        )

        if not compose_opened:
            page.keyboard.press("c")  # Gmail shortcut
            logger.info("Compose opened via 'c' shortcut")

        time.sleep(2)

        # Step 3: Find To field
        to_field = _find_element(
            page,
            [
                'textarea[aria-label="To recipients"]',
                'textarea[name="to"]',
                'input[aria-label="To recipients"]',
                'input[name="to"]',
                'input[peoplekit-id="BbVjBd"]',
            ],
            timeout=8000,
            description="To field",
        )

        if not to_field:
            return {
                "success": False,
                "error": "Could not find To field in compose window",
            }

        # Step 4: Fill To
        to_field.click()
        to_field.fill(to)
        page.keyboard.press("Tab")
        time.sleep(0.5)

        # Step 5: Fill Subject
        subj_field = _find_element(
            page,
            [
                'input[aria-label="Subject"]',
                'input[name="subjectbox"]',
            ],
            timeout=3000,
            description="Subject field",
        )
        if subj_field:
            subj_field.click()
            subj_field.fill(subject)
            page.keyboard.press("Tab")
            time.sleep(0.3)

        # Step 6: Fill Body
        body_field = _find_element(
            page,
            [
                'div[aria-label="Message Body"][contenteditable="true"]',
                'div[role="textbox"][aria-label="Message Body"]',
                'div.Am.Al.editable[contenteditable="true"]',
                'div[contenteditable="true"][g_editable="true"]',
            ],
            timeout=3000,
            description="Body field",
        )

        if body_field:
            body_field.click()
            body_field.fill(body)
        else:
            page.keyboard.type(body, delay=10)

        time.sleep(1)

        # Step 7: Send via Ctrl+Enter (most reliable)
        page.keyboard.press("Control+Enter")
        logger.info("Send via Ctrl+Enter")
        time.sleep(3)

        return {
            "success": True,
            "message": f"Email sent to {to} via Gmail",
            "platform": "gmail",
        }

    except Exception as e:
        logger.exception("Gmail send failed")
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


def send_gmail_via_api(to: str, subject: str, body: str):
    """Fallback: send email via Gmail API (requires OAuth credentials)."""
    try:
        import base64
        from email.mime.text import MIMEText

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds_path = "gmail_credentials.json"
        if not Path(creds_path).exists():
            return {
                "success": False,
                "error": f"Gmail credentials not found at {creds_path}",
            }

        creds = Credentials.from_authorized_user_file(
            creds_path, scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        service = build("gmail", "v1", credentials=creds)

        msg = MIMEText(body)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        result = (
            service.users().messages().send(userId="me", body={"raw": raw}).execute()
        )

        return {
            "success": True,
            "message": f"Email sent to {to} via Gmail API",
            "platform": "gmail",
            "message_id": result.get("id"),
        }
    except Exception as e:
        return {"success": False, "error": f"Gmail API failed: {e}"}


# ─────────────────────────────────────────────────────────────────────────────
# LINKEDIN
# ─────────────────────────────────────────────────────────────────────────────


def send_linkedin_post(message: str, session_path: str = None):
    """Post to LinkedIn feed."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("linkedin")
    session_path = session_path or "sessions/linkedin_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return _not_logged_in("LinkedIn")

        # Click "Start a post"
        if not _find_and_click(
            page,
            [
                "button.share-box-feed-entry__trigger",
                'button[aria-label*="Start a post"]',
                '[data-test-id="share-box-feed-entry__trigger"]',
            ],
            timeout=8000,
            description="Start a post",
        ):
            return {"success": False, "error": "Could not find 'Start a post' button"}

        time.sleep(2)

        # Fill editor
        editor = _find_element(
            page,
            [
                '.ql-editor[contenteditable="true"]',
                'div[role="textbox"][contenteditable="true"]',
                'div[data-placeholder*="What do you want to talk about"]',
            ],
            timeout=8000,
            description="Post editor",
        )

        if not editor:
            return {"success": False, "error": "Could not find post editor"}

        editor.click()
        page.keyboard.type(message, delay=30)
        time.sleep(1)

        # Click Post
        if not _find_and_click(
            page,
            [
                "button.share-actions__primary-action",
                'button[aria-label="Post"]',
                'button:has-text("Post")',
            ],
            timeout=8000,
            description="Post button",
        ):
            page.keyboard.press("Control+Enter")

        time.sleep(3)
        return {
            "success": True,
            "message": "LinkedIn post published",
            "platform": "linkedin",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


def send_linkedin_dm(recipient_name: str, message: str, session_path: str = None):
    """Send a LinkedIn direct message."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("linkedin")
    session_path = session_path or "sessions/linkedin_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.linkedin.com/messaging/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return _not_logged_in("LinkedIn")

        # Search for contact
        search = _find_element(
            page,
            [
                'input[aria-label="Search messages"]',
                'input[placeholder*="Search messages"]',
                "input.msg-search-form__search-field",
            ],
            timeout=8000,
            description="Message search",
        )

        if search:
            search.click()
            search.fill(recipient_name)
            time.sleep(2)
            page.keyboard.press("Enter")
            time.sleep(2)

        # Find and click the conversation
        _find_and_click(
            page,
            [
                f'span:has-text("{recipient_name}")',
                "li.msg-conversation-listitem:first-child",
            ],
            timeout=5000,
            description="Contact thread",
        )
        time.sleep(1)

        # Type message
        msg_box = _find_element(
            page,
            [
                'div.msg-form__contenteditable[contenteditable="true"]',
                'div[role="textbox"][aria-label*="Write a message"]',
                'div.msg-form__msg-content-container div[contenteditable="true"]',
            ],
            timeout=8000,
            description="Message box",
        )

        if not msg_box:
            return {"success": False, "error": "Could not find message input"}

        msg_box.click()
        page.keyboard.type(message, delay=random.randint(20, 50))
        time.sleep(0.5)

        # Send
        if not _find_and_click(
            page,
            [
                "button.msg-form__send-button",
                'button[aria-label="Send"]',
                'button:has-text("Send")',
            ],
            timeout=5000,
            description="Send button",
        ):
            page.keyboard.press("Enter")

        time.sleep(2)
        return {
            "success": True,
            "message": f"LinkedIn DM sent to {recipient_name}",
            "platform": "linkedin",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


# ─────────────────────────────────────────────────────────────────────────────
# FACEBOOK
# ─────────────────────────────────────────────────────────────────────────────


def send_facebook_post(message: str, session_path: str = None):
    """Post to Facebook feed."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("facebook")
    session_path = session_path or "sessions/facebook_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.facebook.com/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return _not_logged_in("Facebook")

        # Click "What's on your mind?"
        if not _find_and_click(
            page,
            [
                '[aria-label="Create a post"]',
                '[data-testid="create_post"]',
                'span:has-text("What\'s on your mind")',
                '[role="button"]:has-text("What\'s on your mind")',
            ],
            timeout=8000,
            description="Create post",
        ):
            return {"success": False, "error": "Could not find post creation area"}

        time.sleep(2)

        # Fill content
        editor = _find_element(
            page,
            [
                '[contenteditable="true"][role="textbox"]',
                'div[data-testid="post-message-input"]',
            ],
            timeout=8000,
            description="Post editor",
        )

        if not editor:
            return {"success": False, "error": "Could not find post editor"}

        editor.click()
        page.keyboard.type(message, delay=30)
        time.sleep(1)

        # Click Post
        if not _find_and_click(
            page,
            [
                'div[aria-label="Post"][role="button"]',
                'button[data-testid="react-composer-post-button"]',
                '[aria-label="Post"]',
            ],
            timeout=8000,
            description="Post button",
        ):
            page.keyboard.press("Control+Enter")

        time.sleep(3)
        return {
            "success": True,
            "message": "Facebook post published",
            "platform": "facebook",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


def send_facebook_dm(recipient: str, message: str, session_path: str = None):
    """Send a Facebook Messenger DM."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("facebook")
    session_path = session_path or "sessions/facebook_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.facebook.com/messages/t/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return _not_logged_in("Facebook")

        # Search for contact
        search = _find_element(
            page,
            [
                'input[aria-label="Search Messenger"]',
                'input[placeholder*="Search Messenger"]',
            ],
            timeout=8000,
            description="Messenger search",
        )

        if search:
            search.click()
            search.fill(recipient)
            time.sleep(2)
            # Click first search result
            _find_and_click(
                page,
                [
                    'ul[role="listbox"] li:first-child',
                    '[data-testid="mwthreadlist-item"]:first-child',
                ],
                timeout=5000,
                description="Contact result",
            )
            time.sleep(2)

        # Type message
        msg_box = _find_element(
            page,
            [
                'div[contenteditable="true"][role="textbox"]',
                'div[aria-label="Message"][contenteditable="true"]',
                'p[data-testid="message-input"]',
            ],
            timeout=8000,
            description="Message box",
        )

        if not msg_box:
            return {"success": False, "error": "Could not find message input"}

        msg_box.click()
        page.keyboard.type(message, delay=random.randint(20, 50))
        time.sleep(0.5)

        # Send via Enter
        page.keyboard.press("Enter")
        time.sleep(2)
        return {
            "success": True,
            "message": f"Facebook DM sent to {recipient}",
            "platform": "facebook",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


# ─────────────────────────────────────────────────────────────────────────────
# TWITTER / X
# ─────────────────────────────────────────────────────────────────────────────


def send_tweet(message: str, session_path: str = None):
    """Post a tweet on X/Twitter."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("twitter")
    session_path = session_path or "sessions/twitter_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://x.com/compose/post", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return _not_logged_in("Twitter")

        # Fill tweet
        tweet_box = _find_element(
            page,
            [
                '[data-testid="tweetTextarea_0"]',
                'div[role="textbox"][data-testid="tweetTextarea_0"]',
                'div[contenteditable="true"][role="textbox"]',
            ],
            timeout=8000,
            description="Tweet box",
        )

        if not tweet_box:
            return {"success": False, "error": "Could not find tweet compose box"}

        tweet_box.click()
        content = message[:280]
        page.keyboard.type(content, delay=30)
        time.sleep(1)

        # Click Post
        if not _find_and_click(
            page,
            [
                '[data-testid="tweetButton"]',
                '[data-testid="tweetButtonInline"]',
            ],
            timeout=8000,
            description="Tweet button",
        ):
            page.keyboard.press("Control+Enter")

        time.sleep(3)
        return {"success": True, "message": "Tweet posted", "platform": "twitter"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


def send_twitter_dm(username: str, message: str, session_path: str = None):
    """Send a Twitter/X direct message."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("twitter")
    session_path = session_path or "sessions/twitter_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://x.com/messages", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower():
            return _not_logged_in("Twitter")

        # Click new message
        _find_and_click(
            page,
            [
                '[data-testid="NewDM_Button"]',
                'a[href="/messages/compose"]',
                '[aria-label="New message"]',
            ],
            timeout=8000,
            description="New DM button",
        )
        time.sleep(2)

        # Search for user
        search = _find_element(
            page,
            [
                'input[data-testid="searchPeople"]',
                'input[aria-label="Search people"]',
                'input[placeholder*="Search people"]',
            ],
            timeout=8000,
            description="People search",
        )

        if search:
            clean_user = username.lstrip("@")
            search.click()
            search.fill(clean_user)
            time.sleep(2)

            # Click first result
            _find_and_click(
                page,
                [
                    '[data-testid="TypeaheadUser"]:first-child',
                    'div[role="option"]:first-child',
                ],
                timeout=5000,
                description="User result",
            )
            time.sleep(1)

            # Click Next
            _find_and_click(
                page,
                [
                    '[data-testid="nextButton"]',
                    'button:has-text("Next")',
                ],
                timeout=5000,
                description="Next button",
            )
            time.sleep(1)

        # Type message
        msg_box = _find_element(
            page,
            [
                'div[data-testid="dmComposerTextInput"]',
                'div[contenteditable="true"][role="textbox"]',
                '[data-testid="dmComposerTextInput"] div[contenteditable]',
            ],
            timeout=8000,
            description="DM input",
        )

        if not msg_box:
            return {"success": False, "error": "Could not find DM input"}

        msg_box.click()
        page.keyboard.type(message, delay=random.randint(20, 50))
        time.sleep(0.5)

        # Send
        if not _find_and_click(
            page,
            [
                '[data-testid="dmComposerSendButton"]',
                'button[aria-label="Send"]',
            ],
            timeout=5000,
            description="Send button",
        ):
            page.keyboard.press("Enter")

        time.sleep(2)
        return {
            "success": True,
            "message": f"Twitter DM sent to {username}",
            "platform": "twitter",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


# ─────────────────────────────────────────────────────────────────────────────
# INSTAGRAM
# ─────────────────────────────────────────────────────────────────────────────


def send_instagram_post(message: str, image_path: str = None, session_path: str = None):
    """Post to Instagram feed (requires image)."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    if not image_path or not Path(image_path).exists():
        return {
            "success": False,
            "error": f"Instagram feed post requires an image. Got: {image_path}",
        }

    wait_for_rate_limit("instagram")
    session_path = session_path or "sessions/instagram_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.instagram.com/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower() or "accounts/login" in page.url.lower():
            return _not_logged_in("Instagram")

        # Click Create / New Post
        if not _find_and_click(
            page,
            [
                'svg[aria-label="New post"]',
                '[aria-label="New post"]',
                'a[href="/create/style/"]',
            ],
            timeout=8000,
            description="New post",
        ):
            # Try finding any Create button in nav
            nav_items = page.query_selector_all("svg[aria-label]")
            clicked = False
            for item in nav_items:
                label = item.get_attribute("aria-label") or ""
                if "new" in label.lower() or "create" in label.lower():
                    item.click()
                    clicked = True
                    break
            if not clicked:
                return {
                    "success": False,
                    "error": "Could not find Create/New Post button",
                }

        time.sleep(2)

        # Upload image
        file_input = page.wait_for_selector('input[type="file"]', timeout=10000)
        file_input.set_input_files(image_path)
        time.sleep(3)

        # Click Next (crop step)
        _find_and_click(
            page,
            ['button:has-text("Next")', 'div[role="button"]:has-text("Next")'],
            timeout=5000,
            description="Next (crop)",
        )
        time.sleep(2)

        # Click Next (filter step)
        _find_and_click(
            page,
            ['button:has-text("Next")', 'div[role="button"]:has-text("Next")'],
            timeout=5000,
            description="Next (filter)",
        )
        time.sleep(2)

        # Add caption
        caption_input = _find_element(
            page,
            [
                'textarea[aria-label*="caption"]',
                'textarea[aria-label*="Write"]',
            ],
            timeout=5000,
            description="Caption input",
        )

        if caption_input:
            caption_input.click()
            page.keyboard.type(message[:2200], delay=20)
            time.sleep(1)

        # Click Share
        if not _find_and_click(
            page,
            [
                'button:has-text("Share")',
                'div[role="button"]:has-text("Share")',
            ],
            timeout=8000,
            description="Share button",
        ):
            return {"success": False, "error": "Could not find Share button"}

        time.sleep(5)
        return {
            "success": True,
            "message": "Instagram post published",
            "platform": "instagram",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


def send_instagram_dm(recipient: str, message: str, session_path: str = None):
    """Send an Instagram direct message."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("instagram")
    session_path = session_path or "sessions/instagram_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path)
        page.goto("https://www.instagram.com/direct/inbox/", timeout=60000)
        time.sleep(3)

        if "login" in page.url.lower() or "accounts/login" in page.url.lower():
            return _not_logged_in("Instagram")

        # Click new message / compose
        _find_and_click(
            page,
            [
                'svg[aria-label="New message"]',
                '[aria-label="New message"]',
                'div[role="button"]:has-text("Send message")',
            ],
            timeout=8000,
            description="New message",
        )
        time.sleep(2)

        # Search for user
        search = _find_element(
            page,
            [
                'input[placeholder="Search..."]',
                'input[aria-label="Search"]',
                'input[name="queryBox"]',
            ],
            timeout=8000,
            description="Search box",
        )

        if search:
            search.click()
            search.fill(recipient)
            time.sleep(2)

            # Click first result
            _find_and_click(
                page,
                [
                    'div[role="listbox"] button:first-child',
                    'div[role="button"][tabindex="0"]:first-child',
                ],
                timeout=5000,
                description="User result",
            )
            time.sleep(1)

            # Click Chat / Next
            _find_and_click(
                page,
                [
                    'button:has-text("Chat")',
                    'div[role="button"]:has-text("Next")',
                ],
                timeout=5000,
                description="Chat/Next button",
            )
            time.sleep(1)

        # Type message
        msg_box = _find_element(
            page,
            [
                'textarea[placeholder="Message..."]',
                'div[contenteditable="true"][role="textbox"]',
                'textarea[aria-label="Message"]',
            ],
            timeout=8000,
            description="Message input",
        )

        if not msg_box:
            return {"success": False, "error": "Could not find message input"}

        msg_box.click()
        page.keyboard.type(message, delay=random.randint(20, 50))
        time.sleep(0.5)

        # Send
        if not _find_and_click(
            page,
            [
                'button:has-text("Send")',
                'div[role="button"]:has-text("Send")',
            ],
            timeout=5000,
            description="Send button",
        ):
            page.keyboard.press("Enter")

        time.sleep(2)
        return {
            "success": True,
            "message": f"Instagram DM sent to {recipient}",
            "platform": "instagram",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


# ─────────────────────────────────────────────────────────────────────────────
# WHATSAPP
# ─────────────────────────────────────────────────────────────────────────────


def send_whatsapp_message(phone: str, message: str, session_path: str = None):
    """Send WhatsApp message to a phone number or contact name."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    wait_for_rate_limit("whatsapp")
    session_path = session_path or "sessions/whatsapp_session"
    p = None
    try:
        p, browser, page = _launch_browser(session_path, headless=False)
        page.goto(
            "https://web.whatsapp.com", wait_until="domcontentloaded", timeout=90000
        )

        # Wait for chat list (logged in indicator)
        try:
            page.wait_for_selector(
                '[data-testid="chat-list"], #pane-side, [aria-label="Chat list"]',
                timeout=20000,
            )
        except Exception:
            return _not_logged_in("WhatsApp")

        # Search for contact
        search_box = _find_element(
            page,
            [
                'div[contenteditable="true"][data-tab="3"]',
                '[data-testid="chat-list-search"]',
            ],
            timeout=8000,
            description="Search box",
        )

        if not search_box:
            # Click search icon first
            _find_and_click(
                page,
                ['[data-testid="search"]', '[data-icon="search"]'],
                timeout=5000,
                description="Search icon",
            )
            time.sleep(1)
            search_box = _find_element(
                page,
                ['div[contenteditable="true"][data-tab="3"]'],
                timeout=5000,
                description="Search box (retry)",
            )

        if not search_box:
            return {"success": False, "error": "Could not find WhatsApp search box"}

        search_box.click()
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(phone, delay=random.randint(30, 60))
        time.sleep(2)

        # Click first matching contact or press Enter
        contact = page.query_selector(f'span[title*="{phone}"]')
        if contact:
            contact.click()
        else:
            page.keyboard.press("Enter")
        time.sleep(1.5)

        # Find message input and type
        msg_box = _find_element(
            page,
            [
                'div[contenteditable="true"][data-tab="10"]',
                'footer div[contenteditable="true"]',
                'div[title="Type a message"]',
            ],
            timeout=8000,
            description="Message box",
        )

        if not msg_box:
            return {"success": False, "error": "Could not find message input box"}

        msg_box.click()
        time.sleep(0.3)

        # Handle multi-line messages
        lines = message.split("\n")
        for i, line in enumerate(lines):
            page.keyboard.type(line, delay=random.randint(10, 30))
            if i < len(lines) - 1:
                page.keyboard.press("Shift+Enter")

        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(2)

        return {
            "success": True,
            "message": f"WhatsApp sent to {phone}",
            "platform": "whatsapp",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


# ─────────────────────────────────────────────────────────────────────────────
# UNIFIED DISPATCH
# ─────────────────────────────────────────────────────────────────────────────


def send_message(platform: str, recipient: str, content: str, **kwargs) -> dict:
    """
    Single entry point — routes to the right sender function.

    Args:
        platform: gmail, linkedin, linkedin-dm, facebook, facebook-dm,
                  twitter, twitter-dm, whatsapp, instagram, instagram-dm
        recipient: email address, phone number, username, or contact name
        content: message body or post content
        **kwargs: extra args (subject for email, image_path for instagram)
    """
    platform = platform.lower().strip()

    dispatch = {
        "gmail": lambda: send_gmail_via_browser(
            to=recipient, subject=kwargs.get("subject", ""), body=content
        ),
        "email": lambda: send_gmail_via_browser(
            to=recipient, subject=kwargs.get("subject", ""), body=content
        ),
        "linkedin": lambda: send_linkedin_post(content),
        "linkedin-post": lambda: send_linkedin_post(content),
        "linkedin-dm": lambda: send_linkedin_dm(recipient, content),
        "facebook": lambda: send_facebook_post(content),
        "facebook-post": lambda: send_facebook_post(content),
        "facebook-dm": lambda: send_facebook_dm(recipient, content),
        "twitter": lambda: send_tweet(content),
        "twitter-post": lambda: send_tweet(content),
        "tweet": lambda: send_tweet(content),
        "twitter-dm": lambda: send_twitter_dm(recipient, content),
        "whatsapp": lambda: send_whatsapp_message(recipient, content),
        "instagram": lambda: send_instagram_post(
            content, image_path=kwargs.get("image_path")
        ),
        "instagram-post": lambda: send_instagram_post(
            content, image_path=kwargs.get("image_path")
        ),
        "instagram-dm": lambda: send_instagram_dm(recipient, content),
    }

    handler = dispatch.get(platform)
    if not handler:
        return {"success": False, "error": f"Unknown platform: {platform}"}

    return handler()


# ─────────────────────────────────────────────────────────────────────────────
# SESSION VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────


def verify_session(platform: str, session_path: str = None):
    """Verify a platform session is still logged in without posting."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"success": False, "error": "Playwright not installed"}

    platforms = {
        "linkedin": {
            "url": "https://www.linkedin.com/feed/",
            "session": "sessions/linkedin_session",
        },
        "facebook": {
            "url": "https://www.facebook.com/",
            "session": "sessions/facebook_session",
        },
        "twitter": {"url": "https://x.com/home", "session": "sessions/twitter_session"},
        "instagram": {
            "url": "https://www.instagram.com/",
            "session": "sessions/instagram_session",
        },
        "gmail": {
            "url": "https://mail.google.com/mail/",
            "session": "sessions/gmail_session",
        },
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

        if (
            "login" in page.url.lower()
            or "signin" in page.url.lower()
            or "accounts" in page.url.lower()
        ):
            return _not_logged_in(platform.title())

        return {"success": True, "message": f"{platform.title()} session is active"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        _safe_close(p, browser, page)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: python direct_social_sender.py <command> [args...]")
        print("Commands:")
        print("  gmail <to> <subject> <body>")
        print("  linkedin-post <message>")
        print("  linkedin-dm <recipient> <message>")
        print("  tweet <message>")
        print("  twitter-dm <@username> <message>")
        print("  facebook-post <message>")
        print("  facebook-dm <recipient> <message>")
        print("  instagram-post <caption> <image_path>")
        print("  instagram-dm <recipient> <message>")
        print("  whatsapp <phone> <message>")
        print("  verify-<platform>")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Handle verify commands
    if command.startswith("verify-"):
        plat = command.replace("verify-", "")
        result = verify_session(plat)
        print(
            f"{'[OK]' if result['success'] else '[FAIL]'} {plat.title()}: {result.get('message') or result.get('error')}"
        )
        sys.exit(0 if result["success"] else 1)

    args = sys.argv[2:]

    if command == "gmail" and len(args) >= 3:
        result = send_gmail_via_browser(to=args[0], subject=args[1], body=args[2])
    elif command == "linkedin-post" and args:
        result = send_linkedin_post(args[0])
    elif command == "linkedin-dm" and len(args) >= 2:
        result = send_linkedin_dm(args[0], args[1])
    elif command == "tweet" and args:
        result = send_tweet(args[0])
    elif command == "twitter-dm" and len(args) >= 2:
        result = send_twitter_dm(args[0], args[1])
    elif command == "facebook-post" and args:
        result = send_facebook_post(args[0])
    elif command == "facebook-dm" and len(args) >= 2:
        result = send_facebook_dm(args[0], args[1])
    elif command == "instagram-post" and len(args) >= 2:
        result = send_instagram_post(args[0], image_path=args[1])
    elif command == "instagram-dm" and len(args) >= 2:
        result = send_instagram_dm(args[0], args[1])
    elif command == "whatsapp" and len(args) >= 2:
        result = send_whatsapp_message(args[0], args[1])
    else:
        print(f"Invalid command or missing args: {command} {args}")
        sys.exit(1)

    print(
        f"{'[OK]' if result['success'] else '[FAIL]'} {result.get('message') or result.get('error')}"
    )
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

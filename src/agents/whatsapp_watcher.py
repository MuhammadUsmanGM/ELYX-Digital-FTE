import hashlib
from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
from ..base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os


class WhatsAppWatcher(BaseWatcher):
    """
    Monitors WhatsApp Web for urgent messages.
    Keeps a single Playwright browser open across all check cycles
    so the session is never lost and QR scanning only happens once.
    """

    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('WHATSAPP_CHECK_INTERVAL', 60))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/whatsapp_session')
        self.keywords = os.getenv('WHATSAPP_KEYWORDS', 'urgent,asap,invoice,payment,help').split(',')
        self.processed_messages: set = self._load_processed_ids("whatsapp")

        # Persistent browser state — opened once, reused across checks
        self._playwright: Playwright | None = None
        self._browser: BrowserContext | None = None
        self._page: Page | None = None

    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------

    def _open_browser(self):
        """Open the browser once and navigate to WhatsApp Web."""
        self._playwright = sync_playwright().start()
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._browser = self._playwright.chromium.launch_persistent_context(
            str(self.session_path),
            headless=False,          # Must be visible for initial QR scan
            viewport={'width': 1280, 'height': 800},
            args=['--disable-blink-features=AutomationControlled'],
        )
        self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
        self._page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=90000)
        self._ensure_logged_in()

        # Register with shared browser registry so the sender reuses this browser
        try:
            from src.services.browser_registry import register
            register(str(self.session_path), self._playwright, self._browser, self._page)
        except Exception as e:
            self.logger.warning(f"Could not register browser in registry: {e}")

    def _is_whatsapp_logged_in(self, timeout: int = 15000) -> bool:
        """Try multiple selectors to detect if WhatsApp is logged in."""
        selectors = [
            '[data-testid="chat-list"]',
            '#pane-side',
            '[aria-label="Chat list"]',
            '[aria-label="Chats"]',
            'div[data-tab="3"]',
        ]
        try:
            self._page.wait_for_selector(
                ', '.join(selectors), timeout=timeout
            )
            return True
        except Exception:
            return False

    def _ensure_logged_in(self):
        """Block until the chat list is visible (handles first-run QR scan)."""
        if self._is_whatsapp_logged_in(timeout=30000):
            self.logger.info("WhatsApp: already logged in")
            return
        self.logger.info("=" * 60)
        self.logger.info("WHATSAPP NOT LOGGED IN — please scan the QR code")
        self.logger.info("1. Open WhatsApp on your phone")
        self.logger.info("2. Settings > Linked Devices > Link a Device")
        self.logger.info("3. Scan the QR code in the open browser window")
        self.logger.info("Waiting up to 3 minutes …")
        self.logger.info("=" * 60)
        if self._is_whatsapp_logged_in(timeout=180000):
            self.logger.info("WhatsApp login successful — session saved")
            self._page.wait_for_timeout(3000)   # let cookies flush to disk
        else:
            self.logger.error("WhatsApp QR not scanned within 3 minutes — closing browser")
            self._close_browser()
            raise RuntimeError("WhatsApp login timed out")

    def _is_browser_alive(self) -> bool:
        try:
            return self._page is not None and not self._page.is_closed()
        except Exception:
            return False

    def _close_browser(self):
        # Unregister from shared browser registry before closing
        try:
            from src.services.browser_registry import unregister
            unregister(str(self.session_path))
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._playwright = None
        self._browser = None
        self._page = None

    # ------------------------------------------------------------------
    # Watcher interface
    # ------------------------------------------------------------------

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for urgent messages using the persistent browser."""
        messages = []

        try:
            # Open browser on first call (or after a crash)
            if not self._is_browser_alive():
                self._open_browser()

            page = self._page

            # Reload if page somehow navigated away
            if 'web.whatsapp.com' not in page.url:
                page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=90000)
                self._ensure_logged_in()

            # Brief wait for dynamic content to settle
            page.wait_for_timeout(2000)

            # Find unread chats
            unread_chats = page.query_selector_all(
                '[data-icon="muted-unread"], [data-icon="unread-count"], span[aria-label*="unread message"]'
            )
            self.logger.info(f"WhatsApp: found {len(unread_chats)} unread chats")

            for chat in unread_chats[:5]:
                try:
                    chat.click()
                    self.human_delay(1, 2)
                    self.stealth_move_mouse(page)

                    # Extract sender name
                    sender_elem = page.query_selector('header [title]')
                    sender_name = sender_elem.get_attribute('title') if sender_elem else "Unknown Contact"

                    message_elements = page.query_selector_all(
                        '[data-testid="conversation"] [dir="ltr"]'
                    )

                    for msg_elem in message_elements:
                        text = msg_elem.text_content()
                        if not text:
                            continue
                        text_lower = text.lower()

                        if any(kw in text_lower for kw in self.keywords):
                            msg_id = hashlib.sha256(f"{sender_name}_{text}".encode()).hexdigest()[:16]
                            if msg_id not in self.processed_messages:
                                messages.append({
                                    'type': 'whatsapp_urgent',
                                    'sender': sender_name,
                                    'text': text[:500],
                                    'keywords_found': [kw for kw in self.keywords if kw in text_lower],
                                    'timestamp': datetime.now().isoformat(),
                                })
                                self.processed_messages.add(msg_id)
                                self._save_processed_ids("whatsapp", self.processed_messages)

                except Exception as e:
                    self.logger.error(f"WhatsApp: error processing chat: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"WhatsApp watcher error: {e}")
            self._close_browser()   # Will re-open on next cycle

        return messages

    def create_action_file(self, item) -> Path:
        content = f'''---
type: {item['type']}
from: {item['sender']}
platform: WhatsApp
priority: high
status: pending
received: {item["timestamp"]}
keywords: {", ".join(item["keywords_found"])}
---

# URGENT WhatsApp Message

**From**: {item["sender"]}

**Message**: {item["text"]}

**Keywords Found**: {", ".join(item["keywords_found"])}

**Received**: {item["timestamp"]}

## Suggested Actions
- [ ] Respond urgently via WhatsApp to {item["sender"]}
- [ ] Forward to relevant party
- [ ] Archive after processing
'''
        # Create a unique but readable filename
        safe_name = "".join([c if c.isalnum() else "_" for c in item['sender'][:15]])
        filepath = self.needs_action / f'WHATSAPP_{safe_name}_{hashlib.sha256(item["text"].encode()).hexdigest()[:8]}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

    def cleanup(self):
        """Call this when shutting down the orchestrator."""
        self._close_browser()

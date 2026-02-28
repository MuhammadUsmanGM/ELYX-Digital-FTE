from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class FacebookWatcher(BaseWatcher):
    """
    Monitors Facebook Messenger for new messages.
    Keeps a single Playwright browser open across all check cycles.
    Run setup_sessions.py once to log in before starting ELYX.
    """

    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('FACEBOOK_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/facebook_session')
        self.processed_items: set = set()

        self._playwright: Playwright | None = None
        self._browser: BrowserContext | None = None
        self._page: Page | None = None

    def _open_browser(self):
        self._playwright = sync_playwright().start()
        self.session_path.mkdir(parents=True, exist_ok=True)
        self._browser = self._playwright.chromium.launch_persistent_context(
            str(self.session_path),
            headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
            viewport={'width': 1280, 'height': 800},
            args=['--disable-blink-features=AutomationControlled'],
        )
        self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
        self._page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=90000)
        self._ensure_logged_in()

    def _ensure_logged_in(self):
        try:
            self._page.wait_for_selector('[aria-label="Facebook"]', timeout=10000)
            self.logger.info("Facebook: already logged in")
        except Exception:
            self.logger.error(
                "Facebook: not logged in. Run: python setup_sessions.py facebook"
            )
            self._close_browser()
            raise RuntimeError("Facebook session missing — run setup_sessions.py facebook")

    def _is_browser_alive(self) -> bool:
        try:
            return self._page is not None and not self._page.is_closed()
        except Exception:
            return False

    def _close_browser(self):
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

    def check_for_updates(self) -> list:
        updates = []
        try:
            if not self._is_browser_alive():
                self._open_browser()

            page = self._page
            page.goto('https://www.facebook.com/messages/t/', wait_until='domcontentloaded', timeout=90000)
            page.wait_for_timeout(3000)

            unread = page.query_selector_all('[aria-label*="unread"]')
            self.logger.info(f"Facebook: found {len(unread)} unread items")

            for u in unread[:5]:
                text = u.text_content()[:200]
                u_id = hash(text)
                if u_id not in self.processed_items:
                    updates.append({
                        'type': 'facebook_message',
                        'text': text,
                        'timestamp': str(page.evaluate("new Date().toISOString()")),
                    })
                    self.processed_items.add(u_id)

        except Exception as e:
            self.logger.error(f"Facebook watcher error: {e}")
            self._close_browser()

        return updates

    def create_action_file(self, item) -> Path:
        content = f'''---
type: {item['type']}
from: Facebook
priority: medium
status: pending
received: {item["timestamp"]}
---

## New Facebook Message

**Content**: {item["text"]}

**Received**: {item["timestamp"]}

## Suggested Actions
- [ ] Review message
- [ ] Respond if needed
- [ ] Archive if spam
'''
        filepath = self.needs_action / f'FACEBOOK_{hash(item["text"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

    def cleanup(self):
        self._close_browser()

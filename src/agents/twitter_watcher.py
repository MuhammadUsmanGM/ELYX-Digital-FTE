from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class TwitterWatcher(BaseWatcher):
    """
    Monitors Twitter/X for mentions and DMs.
    Keeps a single Playwright browser open across all check cycles.
    Run setup_sessions.py once to log in before starting ELYX.
    """

    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('TWITTER_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/twitter_session')
        self.processed_ids: set = set()

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
        self._page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=90000)
        self._ensure_logged_in()

    def _ensure_logged_in(self):
        try:
            self._page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=10000)
            self.logger.info("Twitter: already logged in")
        except Exception:
            self.logger.error(
                "Twitter: not logged in. Run: python setup_sessions.py twitter"
            )
            self._close_browser()
            raise RuntimeError("Twitter session missing — run setup_sessions.py twitter")

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
            page.goto('https://x.com/notifications', wait_until='domcontentloaded', timeout=90000)
            page.wait_for_timeout(3000)

            notifications = page.query_selector_all('[data-testid="cellInnerDiv"]')
            self.logger.info(f"Twitter: found {len(notifications)} notifications")

            for n in notifications[:5]:
                text = n.inner_text()
                n_id = hash(text)
                if n_id not in self.processed_ids:
                    updates.append({
                        'type': 'twitter_notification',
                        'text': text[:200],
                        'timestamp': str(page.evaluate("new Date().toISOString()")),
                    })
                    self.processed_ids.add(n_id)

        except Exception as e:
            self.logger.error(f"Twitter watcher error: {e}")
            self._close_browser()

        return updates

    def create_action_file(self, item) -> Path:
        content = f'''---
type: {item['type']}
from: Twitter/X
priority: medium
status: pending
received: {item["timestamp"]}
---

## New Twitter Notification

**Content**: {item["text"]}

**Received**: {item["timestamp"]}

## Suggested Actions
- [ ] Review notification
- [ ] Respond if needed
- [ ] Archive if spam
'''
        filepath = self.needs_action / f'TWITTER_{hash(item["text"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

    def cleanup(self):
        self._close_browser()

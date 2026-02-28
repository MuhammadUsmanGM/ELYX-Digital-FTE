from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class LinkedInWatcher(BaseWatcher):
    """
    Monitors LinkedIn for urgent messages.
    Keeps a single Playwright browser open across all check cycles.
    Run setup_sessions.py once to log in before starting ELYX.
    """

    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('LINKEDIN_CHECK_INTERVAL', 3600))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/linkedin_session')
        self.keywords = ['urgent', 'asap', 'meeting', 'proposal', 'opportunity', 'help', 'important']
        self.processed_messages: set = set()

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
        self._page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=90000)
        self._ensure_logged_in()

    def _ensure_logged_in(self):
        try:
            self._page.wait_for_selector('nav.global-nav', timeout=10000)
            self.logger.info("LinkedIn: already logged in")
        except Exception:
            self.logger.error(
                "LinkedIn: not logged in. Run: python setup_sessions.py linkedin"
            )
            self._close_browser()
            raise RuntimeError("LinkedIn session missing — run setup_sessions.py linkedin")

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
        messages = []
        try:
            if not self._is_browser_alive():
                self._open_browser()

            page = self._page
            page.goto('https://www.linkedin.com/messaging/', wait_until='domcontentloaded', timeout=90000)
            page.wait_for_timeout(3000)

            unread_threads = page.query_selector_all('[data-test-id="messaging-thread"]')
            self.logger.info(f"LinkedIn: found {len(unread_threads)} threads")

            for thread in unread_threads[:5]:
                text = thread.text_content()[:200]
                if any(kw in text.lower() for kw in self.keywords):
                    t_id = hash(text)
                    if t_id not in self.processed_messages:
                        messages.append({
                            'type': 'linkedin_message',
                            'text': text,
                            'keywords_found': [kw for kw in self.keywords if kw in text.lower()],
                            'timestamp': str(page.evaluate("new Date().toISOString()")),
                        })
                        self.processed_messages.add(t_id)

        except Exception as e:
            self.logger.error(f"LinkedIn watcher error: {e}")
            self._close_browser()

        return messages

    def create_action_file(self, item) -> Path:
        content = f'''---
type: {item['type']}
from: LinkedIn
priority: high
status: pending
received: {item["timestamp"]}
keywords: {", ".join(item["keywords_found"])}
---

## Urgent LinkedIn Message

**Content**: {item["text"]}

**Keywords Found**: {", ".join(item["keywords_found"])}

**Received**: {item["timestamp"]}

## Suggested Actions
- [ ] Review message
- [ ] Respond professionally
- [ ] Archive after processing
'''
        filepath = self.needs_action / f'LINKEDIN_{hash(item["text"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

    def cleanup(self):
        self._close_browser()

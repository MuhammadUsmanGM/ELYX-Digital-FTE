import re
from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
from ..base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
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
        self.processed_messages: set = self._load_processed_ids("linkedin")

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
        self._page.goto('https://www.linkedin.com/feed/', wait_until='commit', timeout=120000)
        # Wait for redirect to settle so URL/login check sees feed (not login)
        try:
            self._page.wait_for_url(re.compile(r'/feed'), timeout=15000)
        except Exception:
            pass
        self._ensure_logged_in()

    def _ensure_logged_in(self):
        try:
            self._page.wait_for_selector('nav.global-nav', timeout=10000)
            self.logger.info("LinkedIn: already logged in")
            return
        except Exception:
            pass
        # Fallback: if we're on feed URL (not redirected to login), session is valid
        current_url = (self._page.url or "")
        if "/feed/" in current_url and "login" not in current_url:
            self.logger.info("LinkedIn: already logged in (verified via URL)")
            return
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

            # Find threads with unread indicators
            unread_threads = page.query_selector_all('[data-test-id="messaging-thread"]:has([aria-label*="unread"]), [data-test-id="messaging-thread"]:has(.msg-conversation-card__unread-count)')
            
            if not unread_threads:
                # Fallback: check all recent threads if unread selector fails
                unread_threads = page.query_selector_all('[data-test-id="messaging-thread"]')[:3]

            self.logger.info(f"LinkedIn: evaluating {len(unread_threads)} threads")

            for thread in unread_threads:
                try:
                    # Extract sender name from the thread card
                    sender_elem = thread.query_selector('.msg-conversation-card__participant-names')
                    sender_name = sender_elem.inner_text().strip() if sender_elem else "LinkedIn Contact"
                    
                    text = thread.text_content()[:500]
                    text_lower = text.lower()
                    
                    # Process if it contains keywords OR if it's explicitly unread
                    is_urgent = any(kw in text_lower for kw in self.keywords)
                    
                    t_id = hash(f"{sender_name}_{text[:100]}")
                    if t_id not in self.processed_messages:
                        messages.append({
                            'type': 'linkedin_message',
                            'sender': sender_name,
                            'text': text,
                            'is_urgent': is_urgent,
                            'keywords_found': [kw for kw in self.keywords if kw in text_lower],
                            'timestamp': datetime.now().isoformat(),
                        })
                        self.processed_messages.add(t_id)
                        self._save_processed_ids("linkedin", self.processed_messages)

                        # Add stealth interaction: hover over thread
                        thread.hover()
                        self.human_delay(0.5, 1.5)
                except Exception as e:
                    self.logger.error(f"Error processing LinkedIn thread: {e}")

        except Exception as e:
            self.logger.error(f"LinkedIn watcher error: {e}")
            self._close_browser()

        return messages

    def create_action_file(self, item) -> Path:
        priority = "high" if item.get('is_urgent') else "medium"
        content = f'''---
type: {item['type']}
from: "{item['sender']}"
platform: LinkedIn
priority: {priority}
status: pending
received: "{item["timestamp"]}"
keywords: [{", ".join([f'"{kw}"' for kw in item["keywords_found"]])}]
---

# LinkedIn Message from {item["sender"]}

**Priority**: {priority.upper()}
**Received**: {item["timestamp"]}

**Content Preview**: 
{item["text"]}

## Suggested Actions
- [ ] Review full message on LinkedIn
- [ ] Draft a professional response
- [ ] Archive after processing
'''
        # Create a unique filename based on sender
        safe_sender = "".join([c if c.isalnum() else "_" for c in item['sender'][:15]])
        filepath = self.needs_action / f'LINKEDIN_{safe_sender}_{hash(item["text"]) % 10000}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

    def cleanup(self):
        self._close_browser()

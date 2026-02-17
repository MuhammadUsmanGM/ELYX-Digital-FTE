from playwright.sync_api import sync_playwright
from src.agents.base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os

class FacebookWatcher(BaseWatcher):
    """
    Monitors Facebook for messages and notifications using Playwright
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('FACEBOOK_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path.home() / ".facebook_session"
        self.keywords = ['urgent', 'asap', 'business', 'opportunity', 'order', 'client']
        self.processed_items = set()

    def check_for_updates(self) -> list:
        """
        Check Facebook for new unread messages
        """
        updates = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                    viewport={'width': 1280, 'height': 800}
                )
                page = browser.new_page()
                page.goto('https://www.facebook.com/messages/t/')

                # Wait for login or messages
                try:
                    page.wait_for_selector('[aria-label="Chats"]', timeout=10000)
                except:
                    self.logger.warning("Facebook Messages not loaded, authentication may be required")
                    browser.close()
                    return []

                # Find unread/new messages
                # Note: This is a simplified selector, selectors change frequently
                unread_threads = page.query_selector_all('[role="gridcell"] b')
                
                for thread in unread_threads:
                    text = thread.inner_text().lower()
                    if any(kw in text for kw in self.keywords):
                        update_id = hash(text)
                        if update_id not in self.processed_items:
                            updates.append({
                                'type': 'facebook_message',
                                'text': text,
                                'timestamp': datetime.now().isoformat()
                            })
                            self.processed_items.add(update_id)

                browser.close()
        except Exception as e:
            self.logger.error(f"Error in Facebook checking: {e}")
        return updates

    def create_action_file(self, item) -> Path:
        """
        Create an action file in Needs_Action folder
        """
        content = f'''---
type: facebook
from: Facebook Message
priority: high
status: pending
received: {item["timestamp"]}
---

## New Facebook Interaction

**Content**: {item["text"]}

## Suggested Actions
- [ ] Review message content
- [ ] Draft response if business related
- [ ] Archive if non-business
'''
        filepath = self.needs_action / f'FACEBOOK_{hash(item["text"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os

class TwitterWatcher(BaseWatcher):
    """
    Monitors Twitter (X) for mentions and DMs using Playwright
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('TWITTER_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        # Use session_path from parameter, or from .env, or default to sessions/twitter_session
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path(os.getenv('TWITTER_SESSION_PATH', './sessions/twitter_session'))
        self.processed_ids = set()

    def check_for_updates(self) -> list:
        """
        Check Twitter for new notifications or DMs
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
                
                # Check Notifications
                page.goto('https://x.com/notifications')
                try:
                    page.wait_for_selector('[data-testid="cellInnerDiv"]', timeout=10000)
                    notifications = page.query_selector_all('[data-testid="notification"]')
                    for n in notifications[:5]: # Check top 5
                        text = n.inner_text()
                        n_id = hash(text)
                        if n_id not in self.processed_ids:
                            updates.append({
                                'type': 'twitter_notification',
                                'text': text,
                                'timestamp': datetime.now().isoformat()
                            })
                            self.processed_ids.add(n_id)
                except:
                    self.logger.warning("Could not load Twitter notifications")

                browser.close()
        except Exception as e:
            self.logger.error(f"Error in Twitter checking: {e}")
        return updates

    def create_action_file(self, item) -> Path:
        """
        Create an action file in Needs_Action folder
        """
        content = f'''---
type: twitter
from: Twitter (X)
priority: medium
status: pending
received: {item["timestamp"]}
---

## New Twitter Notification

**Content**: {item["text"]}

## Suggested Actions
- [ ] Review mention/activity
- [ ] Determine if engagement is needed
- [ ] Archive if irrelevant
'''
        filepath = self.needs_action / f'TWITTER_{hash(item["text"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

from playwright.sync_api import sync_playwright
from src.agents.base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os

class InstagramWatcher(BaseWatcher):
    """
    Monitors Instagram for DMs and activity using Playwright
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('INSTAGRAM_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path.home() / ".instagram_session"
        self.processed_ids = set()

    def check_for_updates(self) -> list:
        """
        Check Instagram for new activity
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
                page.goto('https://www.instagram.com/direct/inbox/')

                try:
                    page.wait_for_selector('role=main', timeout=10000)
                    # Check for unread indicators
                    unread = page.query_selector_all('[aria-label="Unread"]')
                    for u in unread:
                        text = "Unread message in thread"
                        u_id = hash(u.inner_html())
                        if u_id not in self.processed_ids:
                            updates.append({
                                'type': 'instagram_dm',
                                'text': text,
                                'timestamp': datetime.now().isoformat()
                            })
                            self.processed_ids.add(u_id)
                except:
                    self.logger.warning("Could not load Instagram DM inbox")

                browser.close()
        except Exception as e:
            self.logger.error(f"Error in Instagram checking: {e}")
        return updates

    def create_action_file(self, item) -> Path:
        """
        Create an action file in Needs_Action folder
        """
        content = f'''---
type: instagram
from: Instagram DM
priority: medium
status: pending
received: {item["timestamp"]}
---

## New Instagram Activity

**Summary**: {item["text"]}

## Suggested Actions
- [ ] Log into Instagram to check thread
- [ ] Determine if business related
- [ ] Archive if personal
'''
        filepath = self.needs_action / f'INSTAGRAM_{hash(item["timestamp"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

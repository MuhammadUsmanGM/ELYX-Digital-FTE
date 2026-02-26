from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class InstagramWatcher(BaseWatcher):
    """
    Monitors Instagram for DMs using auto-login
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('INSTAGRAM_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/instagram_session')
        self.username = os.getenv('INSTAGRAM_USERNAME', '')
        self.password = os.getenv('INSTAGRAM_PASSWORD', '')
        self.processed_ids = set()

    def check_for_updates(self) -> list:
        """Check Instagram for DMs"""
        updates = []
        
        if not self.username or not self.password:
            self.logger.warning("Instagram credentials not set")
            return updates

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                    viewport={'width': 1280, 'height': 800}
                )

                page = browser.new_page()
                
                # Go to Instagram login
                page.goto('https://www.instagram.com/accounts/login/', timeout=30000)
                page.wait_for_timeout(3000)
                
                # Check if already logged in
                try:
                    page.wait_for_selector('main', timeout=5000)
                    self.logger.info("Already logged in to Instagram")
                except:
                    # Need to login
                    self.logger.info("Logging in to Instagram...")
                    
                    try:
                        # Wait for login form
                        page.wait_for_selector('input[type="text"]', timeout=10000)
                        
                        # Fill username
                        username_field = page.locator('input[type="text"]').first
                        username_field.fill(self.username)
                        
                        # Fill password
                        password_field = page.locator('input[type="password"]').first
                        password_field.fill(self.password)
                        
                        # Click login
                        login_button = page.locator('button[type="submit"]').first
                        login_button.click()
                        page.wait_for_timeout(5000)
                        
                        self.logger.info("Instagram login successful")
                    except Exception as e:
                        self.logger.error(f"Instagram login failed: {e}")
                        browser.close()
                        return updates
                
                # Check DMs
                try:
                    page.goto('https://www.instagram.com/direct/inbox/', timeout=30000)
                    page.wait_for_timeout(3000)
                    
                    # Get unread indicators
                    unread = page.query_selector_all('[aria-label="Unread"]')
                    
                    for u in unread[:5]:
                        u_id = hash(u.inner_html())
                        
                        if u_id not in self.processed_ids:
                            updates.append({
                                'type': 'instagram_dm',
                                'text': 'Unread message in thread',
                                'timestamp': str(page.evaluate("new Date().toISOString()"))
                            })
                            self.processed_ids.add(u_id)
                
                except Exception as e:
                    self.logger.error(f"Error checking Instagram DMs: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error in Instagram watcher: {e}")
        
        return updates

    def create_action_file(self, item) -> Path:
        """Create action file for Instagram DM"""
        content = f'''---
type: {item['type']}
from: Instagram
priority: medium
status: pending
received: {item["timestamp"]}
---

## New Instagram DM

**Summary**: {item["text"]}

**Received**: {item["timestamp"]}

## Suggested Actions
- [ ] Open Instagram to check thread
- [ ] Respond if business-related
- [ ] Archive if personal/spam
'''
        filepath = self.needs_action / f'INSTAGRAM_{hash(item["text"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

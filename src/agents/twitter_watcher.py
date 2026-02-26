from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class TwitterWatcher(BaseWatcher):
    """
    Monitors Twitter/X for mentions and DMs using auto-login
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('TWITTER_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/twitter_session')
        self.username = os.getenv('TWITTER_USERNAME', '')
        self.password = os.getenv('TWITTER_PASSWORD', '')
        self.processed_ids = set()

    def check_for_updates(self) -> list:
        """Check Twitter for new notifications"""
        updates = []
        
        if not self.username or not self.password:
            self.logger.warning("Twitter credentials not set")
            return updates

        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                    viewport={'width': 1280, 'height': 800}
                )

                page = browser.new_page()
                
                # Go to Twitter login
                page.goto('https://x.com/login', timeout=30000)
                
                # Check if already logged in
                try:
                    page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=5000)
                    self.logger.info("Already logged in to Twitter")
                except:
                    # Need to login
                    self.logger.info("Logging in to Twitter...")
                    
                    # Fill username
                    try:
                        username_field = page.locator('input[autocomplete="username"]').first
                        username_field.fill(self.username)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(3000)
                        
                        # Fill password
                        password_field = page.locator('input[type="password"]').first
                        password_field.fill(self.password)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(5000)
                        
                        self.logger.info("Twitter login successful")
                    except Exception as e:
                        self.logger.error(f"Twitter login failed: {e}")
                        browser.close()
                        return updates
                
                # Check notifications
                try:
                    page.goto('https://x.com/notifications', timeout=30000)
                    page.wait_for_timeout(3000)
                    
                    # Get recent notifications
                    notifications = page.query_selector_all('[data-testid="cellInnerDiv"]')
                    
                    for n in notifications[:5]:
                        text = n.inner_text()
                        n_id = hash(text)
                        
                        if n_id not in self.processed_ids:
                            updates.append({
                                'type': 'twitter_notification',
                                'text': text[:200],
                                'timestamp': str(page.evaluate("new Date().toISOString()"))
                            })
                            self.processed_ids.add(n_id)
                
                except Exception as e:
                    self.logger.error(f"Error checking Twitter notifications: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error in Twitter watcher: {e}")
        
        return updates

    def create_action_file(self, item) -> Path:
        """Create action file for Twitter notification"""
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

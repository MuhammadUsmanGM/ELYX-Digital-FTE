from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class FacebookWatcher(BaseWatcher):
    """
    Monitors Facebook for messages using auto-login
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('FACEBOOK_CHECK_INTERVAL', 7200))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/facebook_session')
        self.username = os.getenv('FACEBOOK_USERNAME', '')
        self.password = os.getenv('FACEBOOK_PASSWORD', '')
        self.processed_items = set()

    def check_for_updates(self) -> list:
        """Check Facebook for messages"""
        updates = []
        
        if not self.username or not self.password:
            self.logger.warning("Facebook credentials not set")
            return updates

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                    viewport={'width': 1280, 'height': 800}
                )

                page = browser.new_page()
                
                # Go to Facebook login
                page.goto('https://www.facebook.com/login', timeout=30000)
                
                # Check if already logged in
                try:
                    page.wait_for_selector('[placeholder="What\'s on your mind?"]', timeout=5000)
                    self.logger.info("Already logged in to Facebook")
                except:
                    # Need to login
                    self.logger.info("Logging in to Facebook...")
                    
                    try:
                        # Fill email
                        email_field = page.locator('input[id="email"]').first
                        email_field.fill(self.username)
                        
                        # Fill password
                        password_field = page.locator('input[id="pass"]').first
                        password_field.fill(self.password)
                        
                        # Click login
                        login_button = page.locator('button[name="login"]').first
                        login_button.click()
                        page.wait_for_timeout(5000)
                        
                        self.logger.info("Facebook login successful")
                    except Exception as e:
                        self.logger.error(f"Facebook login failed: {e}")
                        browser.close()
                        return updates
                
                # Check messages
                try:
                    page.goto('https://www.facebook.com/messages/t/', timeout=30000)
                    page.wait_for_timeout(3000)
                    
                    # Get unread indicators
                    unread = page.query_selector_all('[aria-label*="unread"]')
                    
                    for u in unread[:5]:
                        text = u.text_content()[:200]
                        u_id = hash(text)
                        
                        if u_id not in self.processed_items:
                            updates.append({
                                'type': 'facebook_message',
                                'text': text,
                                'timestamp': str(page.evaluate("new Date().toISOString()"))
                            })
                            self.processed_items.add(u_id)
                
                except Exception as e:
                    self.logger.error(f"Error checking Facebook messages: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error in Facebook watcher: {e}")
        
        return updates

    def create_action_file(self, item) -> Path:
        """Create action file for Facebook message"""
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

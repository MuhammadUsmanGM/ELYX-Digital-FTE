from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
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
        # Use session_path from parameter, or from .env, or default to sessions/facebook_session
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path(os.getenv('FACEBOOK_SESSION_PATH', './sessions/facebook_session'))
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

                # Check if already logged in
                logged_in = False
                try:
                    page.wait_for_selector('[aria-label="Chats"], [aria-label="Search Messenger"]', timeout=10000)
                    logged_in = True
                    self.logger.info("Facebook loaded - already logged in")
                except:
                    self.logger.info("Not logged in to Facebook, attempting login...")

                # If not logged in, try to log in with credentials
                if not logged_in:
                    try:
                        username = os.getenv('FACEBOOK_USERNAME', '')
                        password = os.getenv('FACEBOOK_PASSWORD', '')

                        if not username or not password:
                            self.logger.error("Facebook credentials not set in .env (FACEBOOK_USERNAME / FACEBOOK_PASSWORD)")
                            browser.close()
                            return []

                        # Navigate to login page
                        page.goto('https://www.facebook.com/login')
                        import time
                        time.sleep(2)

                        # Fill in credentials
                        email_input = page.wait_for_selector('#email, [name="email"]', timeout=10000)
                        if email_input:
                            email_input.fill(username)

                        pass_input = page.wait_for_selector('#pass, [name="pass"]', timeout=5000)
                        if pass_input:
                            pass_input.fill(password)

                        # Click login button
                        login_btn = page.query_selector('[name="login"], [data-testid="royal_login_button"], button[type="submit"]')
                        if login_btn:
                            login_btn.click()
                        else:
                            page.keyboard.press('Enter')

                        self.logger.info("Login credentials submitted, waiting for response...")

                        # Wait to see what happens after login
                        time.sleep(5)

                        # Check if we hit a checkpoint/2FA page
                        current_url = page.url
                        if 'checkpoint' in current_url or 'two_step_verification' in current_url:
                            self.logger.warning("=" * 60)
                            self.logger.warning("Facebook requires 2FA / security checkpoint!")
                            self.logger.warning("Please complete the verification in the browser window.")
                            self.logger.warning("Waiting up to 120 seconds...")
                            self.logger.warning("=" * 60)
                            try:
                                page.wait_for_url('**/messages/**', timeout=120000)
                            except:
                                self.logger.warning("Timed out waiting for 2FA completion.")
                                browser.close()
                                return []

                        # Navigate to messages after login
                        page.goto('https://www.facebook.com/messages/t/')
                        page.wait_for_selector('[aria-label="Chats"], [aria-label="Search Messenger"]', timeout=30000)
                        self.logger.info("Facebook login successful! Inbox loaded.")

                    except Exception as login_err:
                        self.logger.error(f"Facebook login failed: {login_err}")
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

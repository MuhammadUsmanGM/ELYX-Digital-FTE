from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class LinkedInWatcher(BaseWatcher):
    """
    Monitors LinkedIn for messages using auto-login
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('LINKEDIN_CHECK_INTERVAL', 3600))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/linkedin_session')
        self.username = os.getenv('LINKEDIN_USERNAME', '')
        self.password = os.getenv('LINKEDIN_PASSWORD', '')
        self.keywords = ['urgent', 'asap', 'meeting', 'proposal', 'opportunity', 'help', 'important']
        self.processed_messages = set()

    def check_for_updates(self) -> list:
        """Check LinkedIn for new messages"""
        messages = []
        
        if not self.username or not self.password:
            self.logger.warning("LinkedIn credentials not set")
            return messages

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                    viewport={'width': 1280, 'height': 800}
                )

                page = browser.new_page()
                
                # Go to LinkedIn login
                page.goto('https://www.linkedin.com/login', timeout=30000)
                
                # Check if already logged in
                try:
                    page.wait_for_selector('[data-test-id="update-create-post-trigger"]', timeout=5000)
                    self.logger.info("Already logged in to LinkedIn")
                except:
                    # Need to login
                    self.logger.info("Logging in to LinkedIn...")
                    
                    try:
                        # Fill username
                        username_field = page.locator('input[id="username"]').first
                        username_field.fill(self.username)
                        
                        # Fill password
                        password_field = page.locator('input[id="password"]').first
                        password_field.fill(self.password)
                        
                        # Click login
                        login_button = page.locator('button[type="submit"]').first
                        login_button.click()
                        page.wait_for_timeout(5000)
                        
                        self.logger.info("LinkedIn login successful")
                    except Exception as e:
                        self.logger.error(f"LinkedIn login failed: {e}")
                        browser.close()
                        return messages
                
                # Check messages
                try:
                    page.goto('https://www.linkedin.com/messaging/', timeout=30000)
                    page.wait_for_timeout(3000)
                    
                    # Get unread threads
                    unread_threads = page.query_selector_all('[data-test-id="messaging-thread"]')
                    
                    for thread in unread_threads[:5]:
                        text = thread.text_content()[:200]
                        
                        # Check for urgent keywords
                        if any(kw in text.lower() for kw in self.keywords):
                            t_id = hash(text)
                            if t_id not in self.processed_messages:
                                messages.append({
                                    'type': 'linkedin_message',
                                    'text': text,
                                    'keywords_found': [kw for kw in self.keywords if kw in text.lower()],
                                    'timestamp': str(page.evaluate("new Date().toISOString()"))
                                })
                                self.processed_messages.add(t_id)
                
                except Exception as e:
                    self.logger.error(f"Error checking LinkedIn messages: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error in LinkedIn watcher: {e}")
        
        return messages

    def create_action_file(self, item) -> Path:
        """Create action file for LinkedIn message"""
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

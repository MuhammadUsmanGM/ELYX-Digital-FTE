from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
import json
from datetime import datetime
import time
import os


class LinkedInWatcher(BaseWatcher):
    """
    Monitors LinkedIn for urgent messages using Playwright
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('LINKEDIN_CHECK_INTERVAL', 3600))
        super().__init__(vault_path, check_interval=interval)
        # Use session_path from parameter, or from .env, or default to sessions/linkedin_session
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path(os.getenv('LINKEDIN_SESSION_PATH', './sessions/linkedin_session'))
        self.keywords = ['urgent', 'asap', 'meeting', 'proposal', 'opportunity', 'help', 'important', 'follow', 'contact']
        self.processed_messages = set()

    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new urgent messages using Chrome profile
        """
        messages = []

        try:
            with sync_playwright() as p:
                # Use Chrome profile from .env (where user is logged in)
                chrome_user_data_dir = os.getenv('CHROME_USER_DATA_DIR', '')
                
                if chrome_user_data_dir:
                    # Launch with user's Chrome profile (already logged in)
                    browser = p.chromium.launch_persistent_context(
                        chrome_user_data_dir,
                        headless=False,  # Always show browser for logged-in profile
                        viewport={'width': 1280, 'height': 800},
                        locale='en-US',
                        channel='chrome',  # Use Chrome, not Chromium
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox'
                        ]
                    )
                else:
                    # Fallback to session-based (not recommended)
                    # Use Chrome profile from .env (where user is logged in)
                chrome_user_data_dir = os.getenv('CHROME_USER_DATA_DIR', '')
                
                if chrome_user_data_dir:
                    # Launch with user's Chrome profile (already logged in)
                    browser = p.chromium.launch_persistent_context(
                        chrome_user_data_dir,
                        headless=False,  # Always show browser for logged-in profile
                        viewport={'width': 1280, 'height': 800},
                        locale='en-US',
                        channel='chrome',  # Use Chrome, not Chromium
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox'
                        ]
                    )
                else:
                    # Fallback to session-based (not recommended)
                    # Use Chrome profile
                chrome_user_data_dir = os.getenv("CHROME_USER_DATA_DIR", "")
                if chrome_user_data_dir:
                    browser = p.chromium.launch_persistent_context(chrome_user_data_dir, headless=False, viewport={"width": 1280, "height": 800}, channel="chrome", args=["--disable-blink-features=AutomationControlled"])
                        headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                        viewport={'width': 1280, 'height': 800},
                        locale='en-US'
                    )
                        headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                        viewport={'width': 1280, 'height': 800},
                        locale='en-US'
                    )

                page = browser.new_page()
                page.goto('https://www.linkedin.com/feed/')

                # Check if already logged in by looking for feed elements
                try:
                    # Try to go to messages page
                    page.goto('https://www.linkedin.com/messaging/')

                    # Wait for messaging interface to load
                    page.wait_for_selector('[data-test-id="messaging-thread"]', timeout=10000)

                    # Find unread message threads
                    unread_threads = page.query_selector_all('[data-test-id="messaging-thread"]:has([aria-label="Unread"])')

                    for thread in unread_threads:
                        try:
                            # Get thread information
                            thread_preview = thread.text_content().lower()

                            # Check if thread contains urgent keywords
                            if any(keyword in thread_preview for keyword in self.keywords):
                                # Get more details about the thread
                                thread_title_elem = thread.query_selector('[data-test-id="thread-title"]')
                                thread_snippet_elem = thread.query_selector('[data-test-id="thread-snippet"]')

                                thread_title = thread_title_elem.text_content() if thread_title_elem else "Unknown"
                                thread_snippet = thread_snippet_elem.text_content() if thread_snippet_elem else thread_preview[:100]

                                # Create a unique ID for this message/thread
                                message_id = hash(thread_title + thread_snippet)

                                # Only process if not already processed
                                if message_id not in self.processed_messages:
                                    messages.append({
                                        'title': thread_title,
                                        'snippet': thread_snippet,
                                        'full_preview': thread_preview,
                                        'timestamp': datetime.now().isoformat(),
                                        'keywords_found': [kw for kw in self.keywords if kw in thread_preview]
                                    })
                                    self.processed_messages.add(message_id)

                        except Exception as e:
                            self.logger.error(f"Error processing LinkedIn thread: {e}")
                            continue

                except Exception as e:
                    self.logger.warning(f"LinkedIn not accessible or not logged in: {e}")
                    # Try to log in if needed
                    self._attempt_login(page)

                browser.close()

        except Exception as e:
            self.logger.error(f"Error in LinkedIn checking: {e}")

        return messages

    def _attempt_login(self, page):
        """
        Attempt to log in to LinkedIn if not already logged in
        """
        try:
            username = os.getenv('LINKEDIN_USERNAME')
            password = os.getenv('LINKEDIN_PASSWORD')

            if not username or not password:
                self.logger.warning("LinkedIn credentials not found in environment variables")
                return False

            # Fill in login form
            page.fill('input#username', username)
            page.fill('input#password', password)

            # Click login button
            page.click('button[type="submit"]')

            # Wait for login to complete
            page.wait_for_url('https://www.linkedin.com/feed/', timeout=10000)

            self.logger.info("Successfully logged in to LinkedIn")
            return True

        except Exception as e:
            self.logger.error(f"Failed to log in to LinkedIn: {e}")
            return False

    def create_action_file(self, message) -> Path:
        """
        Create an action file in Needs_Action folder for the urgent LinkedIn message
        """
        content = f'''---
type: linkedin_message
from: LinkedIn Connection
priority: medium
status: pending
received: {message["timestamp"]}
keywords_found: {", ".join(message["keywords_found"])}
---

## LinkedIn Message

**Title**: {message["title"]}

**Snippet**: {message["snippet"]}

**Received**: {message["timestamp"]}

## Keywords Detected
{", ".join(message["keywords_found"])}

## Suggested Actions
- [ ] Review full message on LinkedIn
- [ ] Respond appropriately based on Company Handbook
- [ ] Follow up if needed
'''

        filepath = self.needs_action / f'LINKEDIN_{hash(message["title"] + message["snippet"])}.md'
        filepath.write_text(content)
        return filepath


def run_linkedin_watcher(vault_path: str, session_path: str = None):
    """
    Convenience function to run the LinkedIn watcher continuously
    """
    watcher = LinkedInWatcher(vault_path, session_path)

    # Log startup
    watcher.logger.info("Starting LinkedIn Watcher...")

    while True:
        try:
            items = watcher.check_for_updates()
            for item in items:
                action_file = watcher.create_action_file(item)
                watcher.logger.info(f'Created action file: {action_file}')
        except Exception as e:
            watcher.logger.error(f'Error in LinkedIn Watcher: {e}')

        time.sleep(watcher.check_interval)
from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
import json
from datetime import datetime
import time
import os

class WhatsAppWatcher(BaseWatcher):
    """
    Monitors WhatsApp for urgent messages using Playwright
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('WHATSAPP_CHECK_INTERVAL', 3600))
        super().__init__(vault_path, check_interval=interval)
        # Use session_path from parameter, or from .env, or default to sessions/whatsapp_session
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path(os.getenv('WHATSAPP_SESSION_PATH', './sessions/whatsapp_session'))
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'critical', 'important']
        self.processed_messages = set()

    def check_for_updates(self) -> list:
        """
        Check WhatsApp Web for new urgent messages
        """
        messages = []

        try:
            with sync_playwright() as p:
                # Launch browser with saved session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                    viewport={'width': 1280, 'height': 800}
                )

                page = browser.new_page()
                page.goto('https://web.whatsapp.com')

                # Wait for WhatsApp to load (check if already logged in)
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=15000)
                    self.logger.info("WhatsApp Web loaded successfully - already logged in")
                except:
                    # Not logged in yet - check if QR code is visible
                    self.logger.info("WhatsApp Web not loaded yet, checking for QR code...")
                    try:
                        # Wait for QR code canvas to appear
                        page.wait_for_selector('canvas, [data-testid="qrcode"]', timeout=15000)
                        self.logger.info("=" * 60)
                        self.logger.info("QR CODE DETECTED! Please scan it with your WhatsApp app.")
                        self.logger.info("Open WhatsApp on your phone -> Linked Devices -> Link a Device")
                        self.logger.info("Waiting up to 120 seconds for you to scan...")
                        self.logger.info("=" * 60)
                        
                        # Now wait for login to complete after QR scan
                        try:
                            page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                            self.logger.info("QR code scanned successfully! WhatsApp is now connected.")
                        except:
                            self.logger.warning("Timed out waiting for QR scan. Please try again.")
                            browser.close()
                            return []
                    except:
                        self.logger.warning("Could not find QR code or chat list. WhatsApp Web may have changed its layout.")
                        browser.close()
                        return []

                # Find unread chats
                unread_chats = page.query_selector_all('[data-icon="muted-unread"]')

                for chat in unread_chats:
                    try:
                        # Click on the chat to see messages
                        chat.click()

                        # Get messages in the chat
                        message_elements = page.query_selector_all('[data-testid="conversation"] [dir="ltr"]')

                        for msg_elem in message_elements:
                            text = msg_elem.text_content().lower()

                            # Check if message contains urgent keywords and hasn't been processed
                            if any(kw in text for kw in self.keywords):
                                message_id = hash(text)  # Simple way to track processed messages
                                if message_id not in self.processed_messages:
                                    messages.append({
                                        'text': text,
                                        'chat': chat,
                                        'full_text': msg_elem.text_content(),
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_messages.add(message_id)

                    except Exception as e:
                        self.logger.error(f"Error processing chat: {e}")
                        continue

                browser.close()

        except Exception as e:
            self.logger.error(f"Error in WhatsApp checking: {e}")

        return messages

    def create_action_file(self, message) -> Path:
        """
        Create an action file in Needs_Action folder for the urgent WhatsApp message
        """
        content = f'''---
type: whatsapp
from: WhatsApp Chat
priority: high
status: pending
received: {message["timestamp"]}
keywords_found: {", ".join([kw for kw in self.keywords if kw in message["text"].lower()])}
---

## Urgent WhatsApp Message

**Message**: {message["full_text"]}

**Received**: {message["timestamp"]}

## Keywords Detected
{", ".join([kw for kw in self.keywords if kw in message["text"].lower()])}

## Suggested Actions
- [ ] Assess urgency level
- [ ] Respond appropriately based on Company Handbook
- [ ] Escalate if needed
'''

        filepath = self.needs_action / f'WHATSAPP_{hash(message["text"])}.md'
        filepath.write_text(content)
        return filepath


def run_whatsapp_watcher(vault_path: str, session_path: str = None):
    """
    Convenience function to run the WhatsApp watcher continuously
    """
    watcher = WhatsAppWatcher(vault_path, session_path)

    # Log startup
    watcher.logger.info("Starting WhatsApp Watcher...")

    while True:
        try:
            items = watcher.check_for_updates()
            for item in items:
                action_file = watcher.create_action_file(item)
                watcher.logger.info(f'Created action file: {action_file}')
        except Exception as e:
            watcher.logger.error(f'Error in WhatsApp Watcher: {e}')

        time.sleep(watcher.check_interval)
from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
import os


class WhatsAppWatcher(BaseWatcher):
    """
    Monitors WhatsApp Web for urgent messages
    Keeps browser open for QR code scanning on first run
    """
    def __init__(self, vault_path: str, session_path: str = None):
        interval = int(os.getenv('WHATSAPP_CHECK_INTERVAL', 60))
        super().__init__(vault_path, check_interval=interval)
        self.session_path = Path(session_path) if session_path else Path('./sessions/whatsapp_session')
        self.keywords = os.getenv('WHATSAPP_KEYWORDS', 'urgent,asap,invoice,payment,help').split(',')
        self.processed_messages = set()
        self.qr_shown = False

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for urgent messages"""
        messages = []

        try:
            with sync_playwright() as p:
                # Launch browser with persistent session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Always show browser for QR code
                    viewport={'width': 1280, 'height': 800},
                    timeout=60000  # 60 second timeout for QR scanning
                )

                page = browser.pages[0]
                page.goto('https://web.whatsapp.com', timeout=60000)
                
                # Wait for chat list or QR code
                try:
                    # Try to find chat list (already logged in)
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                    self.logger.info("WhatsApp already logged in")
                    self.qr_shown = False
                except:
                    # QR code should be showing
                    if not self.qr_shown:
                        self.logger.info("=" * 60)
                        self.logger.info("WHATSAPP NOT LOGGED IN!")
                        self.logger.info("Please scan QR code with your phone:")
                        self.logger.info("1. Open WhatsApp on phone")
                        self.logger.info("2. Settings > Linked Devices")
                        self.logger.info("3. Tap 'Link a Device'")
                        self.logger.info("4. Scan QR code on screen")
                        self.logger.info("=" * 60)
                        self.qr_shown = True
                    
                    # Wait for login (user scans QR)
                    self.logger.info("Waiting for QR scan (60 seconds)...")
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
                        self.logger.info("WhatsApp login successful!")
                        self.qr_shown = False
                    except:
                        self.logger.warning("QR code not scanned within 60 seconds")
                        browser.close()
                        return messages
                
                # Find unread chats with urgent keywords
                try:
                    unread_chats = page.query_selector_all('[data-icon="muted-unread"]')
                    
                    for chat in unread_chats[:5]:
                        try:
                            # Click to open chat
                            chat.click()
                            page.wait_for_timeout(1000)
                            
                            # Get messages
                            message_elements = page.query_selector_all('[data-testid="conversation"] [dir="ltr"]')
                            
                            for msg_elem in message_elements:
                                text = msg_elem.text_content().lower()
                                
                                # Check for urgent keywords
                                if any(kw in text for kw in self.keywords):
                                    msg_id = hash(text)
                                    if msg_id not in self.processed_messages:
                                        messages.append({
                                            'type': 'whatsapp_urgent',
                                            'text': msg_elem.text_content()[:200],
                                            'keywords_found': [kw for kw in self.keywords if kw in text],
                                            'timestamp': str(page.evaluate("new Date().toISOString()"))
                                        })
                                        self.processed_messages.add(msg_id)
                            
                        except Exception as e:
                            self.logger.error(f"Error processing chat: {e}")
                            continue
                
                except Exception as e:
                    self.logger.error(f"Error checking WhatsApp: {e}")
                
                # Keep browser open for next check
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error in WhatsApp watcher: {e}")
        
        return messages

    def create_action_file(self, item) -> Path:
        """Create action file for WhatsApp urgent message"""
        content = f'''---
type: {item['type']}
from: WhatsApp
priority: high
status: pending
received: {item["timestamp"]}
keywords: {", ".join(item["keywords_found"])}
---

# URGENT WhatsApp Message

**Message**: {item["text"]}

**Keywords Found**: {", ".join(item["keywords_found"])}

**Received**: {item["timestamp"]}

## Suggested Actions
- [ ] Respond urgently via WhatsApp
- [ ] Forward to relevant party
- [ ] Archive after processing
'''
        filepath = self.needs_action / f'WHATSAPP_{hash(item["text"])}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

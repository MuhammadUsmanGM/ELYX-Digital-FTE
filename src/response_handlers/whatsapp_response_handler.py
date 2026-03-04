"""
WhatsApp Response Handler
Sends WhatsApp messages via Playwright browser automation (same Chrome profile as watcher).
No Business API needed - uses WhatsApp Web directly.
"""

import asyncio
import time
import os
import random
from typing import Dict, Any, Optional
from pathlib import Path

from .base_handler import BaseResponseHandler, CommunicationChannel, ResponseStatus

try:
    from playwright.async_api import async_playwright
    from playwright._impl._errors import TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class WhatsAppResponseHandler(BaseResponseHandler):
    """
    Response handler for sending WhatsApp messages via Playwright (WhatsApp Web).
    Uses the same persistent Chrome session as the WhatsApp watcher.
    """

    def __init__(self, session_path: Optional[str] = None):
        super().__init__(CommunicationChannel.WHATSAPP)
        self.session_path = Path(
            session_path or os.getenv('WHATSAPP_SESSION_PATH', './sessions/whatsapp_session')
        )
        self.playwright = None
        self.browser = None
        self.page = None
        self.logged_in = False

    async def _ensure_browser(self):
        """Open Playwright with the persistent WhatsApp session."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install chromium")

        if self.playwright is None:
            self.playwright = await async_playwright().start()

        if self.browser is None or not self.browser.is_connected():
            self.session_path.mkdir(parents=True, exist_ok=True)
            self.browser = await self.playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,  # WhatsApp Web needs visible browser for QR on first run
                viewport={'width': 1280, 'height': 800},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-first-run',
                    '--no-default-browser-check',
                ],
            )
            self.page = self.browser.pages[0] if self.browser.pages else await self.browser.new_page()

        # Navigate to WhatsApp Web
        if 'web.whatsapp.com' not in (self.page.url or ''):
            await self.page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=90000)

        # Check if logged in
        self.logged_in = await self._is_logged_in()
        if not self.logged_in:
            self.logger.warning("WhatsApp Web not logged in — QR scan required in the browser window")

    async def _is_logged_in(self, timeout: int = 15000) -> bool:
        """Check if WhatsApp Web is logged in by looking for the chat list."""
        selectors = [
            '[data-testid="chat-list"]',
            '#pane-side',
            '[aria-label="Chat list"]',
            '[aria-label="Chats"]',
            'div[data-tab="3"]',
        ]
        try:
            await self.page.wait_for_selector(', '.join(selectors), timeout=timeout)
            return True
        except Exception:
            return False

    def validate_recipient(self, recipient_identifier: str) -> bool:
        """
        Validate recipient — accepts contact name or phone number.
        WhatsApp Web search works with both.
        """
        if not recipient_identifier or len(recipient_identifier.strip()) < 2:
            return False
        return True

    def format_response(self, content: str, response_format: Optional[str] = None) -> str:
        """Format content for WhatsApp (max 4096 chars)."""
        formatted = content.strip()
        if len(formatted) > 4000:
            self.logger.warning("WhatsApp message truncated to fit character limit")
            formatted = formatted[:4000] + "... [truncated]"
        return formatted

    async def send_response(self, recipient_identifier: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Send a WhatsApp message to a contact or phone number via WhatsApp Web.

        Args:
            recipient_identifier: Contact name or phone number (e.g., "John Doe" or "+923001234567")
            content: Message text to send
        """
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(
                    Exception("WhatsApp Web not logged in. Please scan QR code in the browser."),
                    recipient_identifier,
                    content
                )

            if not self.validate_recipient(recipient_identifier):
                return await self.handle_error(
                    ValueError(f"Invalid recipient: {recipient_identifier}"),
                    recipient_identifier,
                    content
                )

            formatted_content = self.format_response(content)
            success = await self._send_whatsapp_message(recipient_identifier, formatted_content)

            if success:
                self.log_response_attempt(recipient_identifier, content, ResponseStatus.SENT)
                return {
                    "status": ResponseStatus.SENT.value,
                    "recipient": recipient_identifier,
                    "timestamp": time.time(),
                    "provider_message_id": f"wa_msg_{int(time.time())}"
                }
            else:
                return await self.handle_error(
                    Exception(f"Failed to send WhatsApp message to {recipient_identifier}"),
                    recipient_identifier,
                    content
                )

        except Exception as error:
            return await self.handle_error(error, recipient_identifier, content)

    async def _send_whatsapp_message(self, recipient: str, content: str) -> bool:
        """
        Send a message via WhatsApp Web using the search box.

        1. Click the search/new chat box
        2. Type the contact name or phone number
        3. Click on the matched contact
        4. Type the message in the chat input
        5. Press Enter to send
        """
        try:
            page = self.page

            # Step 1: Click on the search box (data-tab="3" is the search/new chat input)
            search_selectors = [
                'div[contenteditable="true"][data-tab="3"]',
                '[data-testid="chat-list-search"]',
                'div[title="Search input textbox"]',
            ]
            search_box = None
            for sel in search_selectors:
                search_box = await page.query_selector(sel)
                if search_box:
                    break

            if not search_box:
                # Try clicking the search icon first
                search_icon = await page.query_selector('[data-testid="search"], [data-icon="search"]')
                if search_icon:
                    await search_icon.click()
                    await page.wait_for_timeout(1000)
                    for sel in search_selectors:
                        search_box = await page.query_selector(sel)
                        if search_box:
                            break

            if not search_box:
                self.logger.error("Could not find WhatsApp search box")
                return False

            # Step 2: Clear and type the contact name/number
            await search_box.click()
            await page.wait_for_timeout(500)
            # Select all and delete to clear any previous search
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await page.wait_for_timeout(300)

            # Type search term with human-like delay
            await page.keyboard.type(recipient, delay=random.randint(30, 80))
            await page.wait_for_timeout(2000)  # Wait for search results

            # Step 3: Click on the first matching contact
            contact_selectors = [
                f'span[title*="{recipient}"]',
                '[data-testid="cell-frame-container"]',
                '#pane-side [role="listitem"]',
                'div._ak8l',  # WhatsApp chat list item
            ]

            clicked = False
            for sel in contact_selectors:
                contact = await page.query_selector(sel)
                if contact:
                    await contact.click()
                    clicked = True
                    break

            if not clicked:
                # Try pressing Enter which selects the first result
                await page.keyboard.press('Enter')
                clicked = True

            await page.wait_for_timeout(1500)

            # Step 4: Find the message input box (data-tab="10" is the message composer)
            msg_selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                '[data-testid="conversation-compose-box-input"]',
                'footer div[contenteditable="true"]',
            ]

            msg_box = None
            for sel in msg_selectors:
                msg_box = await page.query_selector(sel)
                if msg_box:
                    break

            if not msg_box:
                self.logger.error("Could not find WhatsApp message input box")
                return False

            # Step 5: Type the message
            await msg_box.click()
            await page.wait_for_timeout(300)

            # For multi-line messages, use Shift+Enter for newlines
            lines = content.split('\n')
            for i, line in enumerate(lines):
                await page.keyboard.type(line, delay=random.randint(10, 30))
                if i < len(lines) - 1:
                    await page.keyboard.press('Shift+Enter')

            await page.wait_for_timeout(500)

            # Step 6: Press Enter to send
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(1500)

            self.logger.info(f"WhatsApp message sent to {recipient}")
            return True

        except PlaywrightTimeout:
            self.logger.error(f"Timeout sending WhatsApp message to {recipient}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp message: {e}")
            return False

    async def close(self):
        """Close browser and Playwright context."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.browser = None
        self.playwright = None
        self.page = None

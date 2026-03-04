import asyncio
import time
import os
from typing import Dict, Any, Optional
from pathlib import Path

from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError, Error

from .base_handler import BaseResponseHandler, CommunicationChannel, ResponseStatus


class LinkedInResponseHandler(BaseResponseHandler):
    """
    Response handler for sending LinkedIn messages using Playwright automation
    """
    def __init__(self, session_path: Optional[str] = None):
        super().__init__(CommunicationChannel.LINKEDIN)
        self.session_path = Path(session_path or os.getenv('LINKEDIN_SESSION_PATH', './sessions/linkedin_session'))
        self.playwright = None
        self.browser = None
        self.page = None
        self.logged_in = False

    async def _ensure_browser(self):
        """
        Ensure the browser is initialized and ready
        """
        if self.playwright is None:
            self.playwright = await async_playwright().start()

        if self.browser is None or not self.browser.is_connected():
            self.session_path.mkdir(parents=True, exist_ok=True)
            self.browser = await self.playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                args=['--disable-blink-features=AutomationControlled']
            )

            self.page = await self.browser.new_page()

        # Navigate to LinkedIn and check login status
        await self.page.goto('https://www.linkedin.com/feed/')

        # Check if already logged in by looking for feed elements
        try:
            # Wait briefly to see if we're on the feed
            await self.page.wait_for_url('https://www.linkedin.com/feed/', timeout=5000)
            self.logged_in = True
        except TimeoutError:
            # Not logged in, try to log in
            self.logged_in = await self._login()

    async def _login(self) -> bool:
        """
        Login to LinkedIn if not already logged in

        Returns:
            True if login successful, False otherwise
        """
        try:
            username = os.getenv('LINKEDIN_USERNAME')
            password = os.getenv('LINKEDIN_PASSWORD')

            if not username or not password:
                raise ValueError("LinkedIn credentials not found in environment variables")

            # Fill in login form
            await self.page.fill('input#username', username)
            await self.page.fill('input#password', password)

            # Click login button
            await self.page.click('button[type="submit"]')

            # Wait for login to complete
            await self.page.wait_for_url('https://www.linkedin.com/feed/', timeout=10000)

            self.logger.info("Successfully logged in to LinkedIn")
            return True

        except Exception as e:
            self.logger.error(f"Failed to login to LinkedIn: {e}")
            return False

    def validate_recipient(self, recipient_identifier: str) -> bool:
        """
        Validate that the recipient identifier is valid for LinkedIn
        For LinkedIn, this could be a profile URL, member ID, or connection name

        Args:
            recipient_identifier: LinkedIn profile identifier

        Returns:
            True if valid format, False otherwise
        """
        # Basic validation - could be improved with more specific LinkedIn identifier formats
        if not recipient_identifier or len(recipient_identifier.strip()) < 3:
            return False

        # Could add more specific validation for LinkedIn profile URLs or IDs
        return True

    def format_response(self, content: str, response_format: Optional[str] = None) -> str:
        """
        Format the response content appropriately for LinkedIn messages

        Args:
            content: Raw content to format
            response_format: Format type (ignored for LinkedIn)

        Returns:
            Formatted content string
        """
        # LinkedIn messages are typically plain text
        # Limit length to LinkedIn's message limit (around 2000 characters)
        formatted = content.strip()
        if len(formatted) > 1950:  # Leave room for potential prefixes
            self.logger.warning("LinkedIn message content truncated to fit character limit")
            formatted = formatted[:1950] + "... [truncated]"

        return formatted

    async def send_response(self, recipient_identifier: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Send a LinkedIn message response to the specified recipient

        Args:
            recipient_identifier: LinkedIn identifier (profile URL, member ID, etc.)
            content: Content of the response message
            **kwargs: Additional parameters

        Returns:
            Dictionary containing response details and status
        """
        try:
            # Ensure browser is ready
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(
                    Exception("Not logged in to LinkedIn"),
                    recipient_identifier,
                    content
                )

            # Validate recipient
            if not self.validate_recipient(recipient_identifier):
                return await self.handle_error(
                    ValueError(f"Invalid LinkedIn identifier: {recipient_identifier}"),
                    recipient_identifier,
                    content
                )

            # Format the content
            formatted_content = self.format_response(content)

            # Send the message
            message_sent = await self._send_linkedin_message(recipient_identifier, formatted_content)

            if message_sent:
                # Log success
                self.log_response_attempt(recipient_identifier, content, ResponseStatus.SENT)

                return {
                    "status": ResponseStatus.SENT.value,
                    "recipient": recipient_identifier,
                    "timestamp": time.time(),
                    "provider_message_id": f"linkedin_msg_{int(time.time())}"
                }
            else:
                return await self.handle_error(
                    Exception("Failed to send LinkedIn message"),
                    recipient_identifier,
                    content
                )

        except Exception as error:
            return await self.handle_error(error, recipient_identifier, content)

    async def post_to_feed(self, content: str) -> Dict[str, Any]:
        """
        Post an update to the LinkedIn feed
        """
        try:
            await self._ensure_browser()
            
            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to LinkedIn"), "feed", content)
                
            await self.page.goto('https://www.linkedin.com/feed/')
            
            # Click the start a post button
            await self.page.click('button.share-mb__trigger')
            
            # Wait for the post modal and fill content
            await self.page.wait_for_selector('.ql-editor', timeout=5000)
            await self.page.fill('.ql-editor', content)
            
            # Click post button
            await self.page.click('button.share-actions__primary-action')
            
            # Log success
            self.log_response_attempt("feed", content, ResponseStatus.SENT)
            
            return {
                "status": ResponseStatus.SENT.value,
                "recipient": "feed",
                "timestamp": time.time(),
                "provider_message_id": f"linkedin_post_{int(time.time())}"
            }
        except Exception as e:
            return await self.handle_error(e, "feed", content)

    async def _send_linkedin_message(self, recipient_identifier: str, content: str) -> bool:
        """
        Actually send the LinkedIn message using Playwright

        Args:
            recipient_identifier: LinkedIn identifier for the recipient
            content: Content to send

        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            # Navigate to the recipient's profile or messages
            # For now, assuming we're sending via the messages interface
            await self.page.goto('https://www.linkedin.com/messaging/')
            await self.page.wait_for_selector('[data-test-id="messaging-thread"]', timeout=10000)

            # This is a simplified approach - in practice, you'd need to:
            # 1. Find the specific conversation/thread with the recipient
            # 2. Or initiate a new message if no existing thread

            # For now, let's try to send a direct message by navigating to the person's profile
            # and clicking the message button
            if recipient_identifier.startswith('http'):
                # Assume it's a profile URL
                await self.page.goto(recipient_identifier)

                # Look for the "Message" button
                message_button = await self.page.wait_for_selector(
                    'button.pvs-profile-actions__action:has-text("Message")',
                    timeout=5000
                )
                if message_button:
                    await message_button.click()

                    # Wait for the message modal to appear
                    await self.page.wait_for_selector('textarea.msg-form__contenteditable', timeout=5000)

                    # Fill in the message
                    await self.page.fill('textarea.msg-form__contenteditable', content)

                    # Send the message
                    send_button = await self.page.wait_for_selector(
                        'button.msg-form__send-button[disabled=false]',
                        timeout=5000
                    )
                    await send_button.click()

                    # Wait briefly to ensure it was sent
                    await asyncio.sleep(1)

                    return True
            else:
                # If not a URL, we might need to search for the person first
                # This is a simplified implementation
                self.logger.warning(f"Sending LinkedIn message to non-URL identifier: {recipient_identifier}")
                # In a full implementation, you'd search for the user first
                return False

        except TimeoutError:
            self.logger.error("Timeout while trying to send LinkedIn message")
            return False
        except Exception as e:
            self.logger.error(f"Error sending LinkedIn message: {e}")
            return False

    async def close(self):
        """
        Close the browser and Playwright context
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
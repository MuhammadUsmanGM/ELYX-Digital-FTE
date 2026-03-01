"""
Facebook Response Handler
Handles sending messages via Facebook Messenger and posting to Facebook feed
Uses Playwright automation for browser-based interactions
"""

import asyncio
import time
import os
from typing import Dict, Any, Optional
from pathlib import Path

from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError

from .base_handler import BaseResponseHandler, CommunicationChannel, ResponseStatus


class FacebookResponseHandler(BaseResponseHandler):
    """
    Response handler for Facebook Messenger and Feed posts using Playwright automation
    """
    
    def __init__(self, session_path: Optional[str] = None):
        super().__init__(CommunicationChannel.FACEBOOK)
        self.session_path = Path(session_path or os.getenv('FACEBOOK_SESSION_PATH', './sessions/facebook_session'))
        self.playwright = None
        self.browser = None
        self.page = None
        self.logged_in = False

    async def _ensure_browser(self):
        """Ensure the browser is initialized and ready"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()

        if self.browser is None or not self.browser.is_connected():
            self.session_path.parent.mkdir(parents=True, exist_ok=True)
            self.browser = await self.playwright.chromium.launch_persistent_context(
                str(self.session_path.parent),
                headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                args=['--disable-blink-features=AutomationControlled']
            )
            self.page = await self.browser.new_page()

        # Navigate to Facebook and check login status
        await self.page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=60000)
        
        try:
            await self.page.wait_for_selector('[aria-label="Facebook"]', timeout=10000)
            self.logged_in = True
        except TimeoutError:
            self.logged_in = await self._login()

    async def _login(self) -> bool:
        """Login to Facebook if not already logged in"""
        try:
            username = os.getenv('FACEBOOK_USERNAME')
            password = os.getenv('FACEBOOK_PASSWORD')

            if not username or not password:
                raise ValueError("Facebook credentials not found. Please run setup_sessions.py facebook")

            # Fill in login form
            await self.page.fill('input#email', username)
            await self.page.fill('input#pass', password)
            await self.page.click('button[type="submit"]')

            # Wait for login to complete
            await self.page.wait_for_selector('[aria-label="Facebook"]', timeout=30000)
            
            self.logger.info("Successfully logged in to Facebook")
            return True

        except Exception as e:
            self.logger.error(f"Failed to login to Facebook: {e}")
            return False

    def validate_recipient(self, recipient_identifier: str) -> bool:
        """Validate Facebook recipient (profile URL, name, or ID)"""
        if not recipient_identifier or len(recipient_identifier.strip()) < 2:
            return False
        return True

    def format_response(self, content: str, response_format: Optional[str] = None) -> str:
        """Format content for Facebook (plain text, max 63206 chars for posts)"""
        formatted = content.strip()
        # Facebook Messenger limit is much higher, but keep it reasonable
        if len(formatted) > 5000:
            self.logger.warning("Facebook message content truncated")
            formatted = formatted[:5000] + "... [truncated]"
        return formatted

    async def send_response(self, recipient_identifier: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send a Facebook Messenger message"""
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(
                    Exception("Not logged in to Facebook"),
                    recipient_identifier,
                    content
                )

            if not self.validate_recipient(recipient_identifier):
                return await self.handle_error(
                    ValueError(f"Invalid Facebook identifier: {recipient_identifier}"),
                    recipient_identifier,
                    content
                )

            formatted_content = self.format_response(content)
            message_sent = await self._send_facebook_message(recipient_identifier, formatted_content)

            if message_sent:
                self.log_response_attempt(recipient_identifier, content, ResponseStatus.SENT)
                return {
                    "status": ResponseStatus.SENT.value,
                    "recipient": recipient_identifier,
                    "timestamp": time.time(),
                    "provider_message_id": f"fb_msg_{int(time.time())}"
                }
            else:
                return await self.handle_error(
                    Exception("Failed to send Facebook message"),
                    recipient_identifier,
                    content
                )

        except Exception as error:
            return await self.handle_error(error, recipient_identifier, content)

    async def _send_facebook_message(self, recipient_identifier: str, content: str) -> bool:
        """Send a message via Facebook Messenger"""
        try:
            # Navigate to Messenger
            await self.page.goto('https://www.facebook.com/messages/t/', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # If recipient is a URL, navigate directly
            if recipient_identifier.startswith('http'):
                await self.page.goto(recipient_identifier, wait_until='domcontentloaded', timeout=30000)
            else:
                # Search for the contact
                search_box = await self.page.wait_for_selector('input[aria-label="Search Messenger"]', timeout=10000)
                await search_box.fill(recipient_identifier)
                await self.page.wait_for_timeout(2000)
                
                # Click on the first result
                first_result = await self.page.query_selector('[role="link"]')
                if first_result:
                    await first_result.click()
                    await self.page.wait_for_timeout(2000)

            # Find and fill the message input
            message_input = await self.page.wait_for_selector(
                '[contenteditable="true"][data-testid="conversation-item-message-composer"]',
                timeout=10000
            )
            await message_input.fill(content)
            await self.page.wait_for_timeout(500)

            # Click send button
            send_button = await self.page.query_selector('button[aria-label="Send"]')
            if send_button:
                await send_button.click()
                await self.page.wait_for_timeout(1000)
                return True

            # Alternative: press Enter to send
            await message_input.press('Enter')
            await self.page.wait_for_timeout(1000)
            return True

        except TimeoutError:
            self.logger.error("Timeout while sending Facebook message")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Facebook message: {e}")
            return False

    async def post_to_feed(self, content: str, privacy: str = 'friends') -> Dict[str, Any]:
        """
        Post an update to the Facebook feed
        
        Args:
            content: Content to post
            privacy: Privacy setting ('public', 'friends', 'only_me')
        """
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Facebook"), "feed", content)

            # Navigate to home feed
            await self.page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Click on "What's on your mind?" box
            create_post = await self.page.wait_for_selector(
                '[data-testid="create_post"]',
                timeout=10000
            )
            await create_post.click()
            await self.page.wait_for_timeout(2000)

            # Find the post text area and fill content
            post_input = await self.page.wait_for_selector(
                '[data-testid="empty_message_input"]',
                timeout=10000
            )
            await post_input.fill(content)
            await self.page.wait_for_timeout(1000)

            # Set privacy if needed
            if privacy != 'friends':
                try:
                    privacy_button = await self.page.query_selector('[data-testid="privacy-selector"]')
                    if privacy_button:
                        await privacy_button.click()
                        await self.page.wait_for_timeout(1000)
                        
                        privacy_option = await self.page.query_selector(f'[data-testid="{privacy}"]')
                        if privacy_option:
                            await privacy_option.click()
                            await self.page.wait_for_timeout(1000)
                except Exception as e:
                    self.logger.warning(f"Could not set privacy: {e}")

            # Click Post button
            post_button = await self.page.wait_for_selector(
                'button[data-testid="react-composer-post-button"]',
                timeout=10000
            )
            await post_button.click()
            await self.page.wait_for_timeout(3000)

            self.log_response_attempt("feed", content, ResponseStatus.SENT)
            return {
                "status": ResponseStatus.SENT.value,
                "recipient": "feed",
                "timestamp": time.time(),
                "provider_message_id": f"fb_post_{int(time.time())}"
            }

        except Exception as e:
            return await self.handle_error(e, "feed", content)

    async def post_to_group(self, group_id: str, content: str) -> Dict[str, Any]:
        """Post to a Facebook group"""
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Facebook"), f"group:{group_id}", content)

            # Navigate to group
            group_url = f'https://www.facebook.com/groups/{group_id}'
            await self.page.goto(group_url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Find create post area
            create_post = await self.page.query_selector('[data-testid="create_post"]')
            if create_post:
                await create_post.click()
                await self.page.wait_for_timeout(2000)

                # Fill content
                post_input = await self.page.wait_for_selector('[data-testid="empty_message_input"]', timeout=10000)
                await post_input.fill(content)
                await self.page.wait_for_timeout(1000)

                # Post
                post_button = await self.page.query_selector('button[data-testid="react-composer-post-button"]')
                if post_button:
                    await post_button.click()
                    await self.page.wait_for_timeout(3000)

                    self.log_response_attempt(f"group:{group_id}", content, ResponseStatus.SENT)
                    return {
                        "status": ResponseStatus.SENT.value,
                        "recipient": f"group:{group_id}",
                        "timestamp": time.time(),
                        "provider_message_id": f"fb_group_post_{int(time.time())}"
                    }

            return await self.handle_error(
                Exception("Could not find post creation area in group"),
                f"group:{group_id}",
                content
            )

        except Exception as e:
            return await self.handle_error(e, f"group:{group_id}", content)

    async def close(self):
        """Close browser and Playwright context"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

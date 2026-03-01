"""
Instagram Response Handler
Handles sending DMs and posting to Instagram feed/stories
Uses Playwright automation for browser-based interactions
"""

import asyncio
import time
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError

from .base_handler import BaseResponseHandler, CommunicationChannel, ResponseStatus


class InstagramResponseHandler(BaseResponseHandler):
    """
    Response handler for Instagram DMs and Posts using Playwright automation
    """
    
    def __init__(self, session_path: Optional[str] = None):
        super().__init__(CommunicationChannel.INSTAGRAM)
        self.session_path = Path(session_path or os.getenv('INSTAGRAM_SESSION_PATH', './sessions/instagram_session'))
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

        # Navigate to Instagram and check login status
        await self.page.goto('https://www.instagram.com/', wait_until='domcontentloaded', timeout=60000)
        await self.page.wait_for_timeout(3000)
        
        try:
            # Check for feed or profile elements that indicate logged in state
            await self.page.wait_for_selector('a[href="/direct/inbox/"]', timeout=10000)
            self.logged_in = True
        except TimeoutError:
            self.logged_in = await self._login()

    async def _login(self) -> bool:
        """Login to Instagram if not already logged in"""
        try:
            username = os.getenv('INSTAGRAM_USERNAME')
            password = os.getenv('INSTAGRAM_PASSWORD')

            if not username or not password:
                raise ValueError("Instagram credentials not found. Please run setup_sessions.py instagram")

            # Fill in login form
            await self.page.wait_for_selector('input[aria-label="Phone number, username, or email"]', timeout=10000)
            await self.page.fill('input[aria-label="Phone number, username, or email"]', username)
            await self.page.fill('input[aria-label="Password"]', password)
            
            # Click Log In
            await self.page.click('button[type="submit"]')
            
            # Wait for login to complete - look for feed or profile
            await self.page.wait_for_selector('a[href="/direct/inbox/"]', timeout=30000)
            
            # Handle "Save Login Info" dialog if it appears
            try:
                await self.page.wait_for_selector('button:has-text("Save")', timeout=3000)
                save_button = await self.page.query_selector('button:has-text("Save")')
                if save_button:
                    await save_button.click()
                    await self.page.wait_for_timeout(1000)
            except TimeoutError:
                pass  # Dialog didn't appear

            # Handle "Turn on Notifications" dialog if it appears
            try:
                await self.page.wait_for_selector('button:has-text("Not Now")', timeout=3000)
                not_now_button = await self.page.query_selector('button:has-text("Not Now")')
                if not_now_button:
                    await not_now_button.click()
                    await self.page.wait_for_timeout(1000)
            except TimeoutError:
                pass  # Dialog didn't appear

            self.logger.info("Successfully logged in to Instagram")
            return True

        except Exception as e:
            self.logger.error(f"Failed to login to Instagram: {e}")
            return False

    def validate_recipient(self, recipient_identifier: str) -> bool:
        """Validate Instagram recipient (@username)"""
        if not recipient_identifier or len(recipient_identifier.strip()) < 2:
            return False
        return True

    def format_response(self, content: str, response_format: Optional[str] = None) -> str:
        """Format content for Instagram DMs"""
        formatted = content.strip()
        # Instagram DM limit is 1000 characters
        if len(formatted) > 950:
            self.logger.warning("Instagram DM content truncated")
            formatted = formatted[:950] + "... [truncated]"
        return formatted

    async def send_response(self, recipient_identifier: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send an Instagram Direct Message"""
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(
                    Exception("Not logged in to Instagram"),
                    recipient_identifier,
                    content
                )

            if not self.validate_recipient(recipient_identifier):
                return await self.handle_error(
                    ValueError(f"Invalid Instagram identifier: {recipient_identifier}"),
                    recipient_identifier,
                    content
                )

            formatted_content = self.format_response(content)
            message_sent = await self._send_instagram_dm(recipient_identifier, formatted_content)

            if message_sent:
                self.log_response_attempt(recipient_identifier, content, ResponseStatus.SENT)
                return {
                    "status": ResponseStatus.SENT.value,
                    "recipient": recipient_identifier,
                    "timestamp": time.time(),
                    "provider_message_id": f"ig_dm_{int(time.time())}"
                }
            else:
                return await self.handle_error(
                    Exception("Failed to send Instagram DM"),
                    recipient_identifier,
                    content
                )

        except Exception as error:
            return await self.handle_error(error, recipient_identifier, content)

    async def _send_instagram_dm(self, recipient_identifier: str, content: str) -> bool:
        """Send a Direct Message via Instagram"""
        try:
            # Navigate to Direct Messages
            await self.page.goto('https://www.instagram.com/direct/inbox/', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Click on "New message" or "+" button
            try:
                new_message_btn = await self.page.wait_for_selector('button:has-text("New message"), svg[aria-label*="message"]', timeout=10000)
                await new_message_btn.click()
                await self.page.wait_for_timeout(2000)
            except TimeoutError:
                # Alternative: look for compose button
                compose_btn = await self.page.query_selector('[aria-label="Send message"]')
                if compose_btn:
                    await compose_btn.click()
                    await self.page.wait_for_timeout(2000)

            # Search for user (remove @ if present)
            search_name = recipient_identifier.lstrip('@')
            search_input = await self.page.wait_for_selector('input[placeholder*="Search"]', timeout=10000)
            await search_input.fill(search_name)
            await self.page.wait_for_timeout(2000)

            # Click on first result
            first_result = await self.page.query_selector('[role="button"][tabindex="0"]')
            if first_result:
                await first_result.click()
                await self.page.wait_for_timeout(1000)

            # Click "Chat" button to start conversation
            chat_button = await self.page.query_selector('button:has-text("Chat"), button:has-text("Send")')
            if chat_button:
                await chat_button.click()
                await self.page.wait_for_timeout(2000)

            # Find message input and send
            message_input = await self.page.wait_for_selector(
                'textarea[aria-label*="Message"]',
                timeout=10000
            )
            if message_input:
                await message_input.fill(content)
                await self.page.wait_for_timeout(500)
                
                # Click send button
                send_button = await self.page.query_selector('button:has-text("Send"), [aria-label="Send"]')
                if send_button:
                    await send_button.click()
                    await self.page.wait_for_timeout(1000)
                    return True

            return False

        except TimeoutError:
            self.logger.error("Timeout while sending Instagram DM")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Instagram DM: {e}")
            return False

    async def post_to_feed(self, caption: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a photo/video to Instagram feed
        
        Args:
            caption: Caption for the post
            image_path: Path to image/video file (optional, will use placeholder if not provided)
        """
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Instagram"), "feed", caption)

            # Navigate to home
            await self.page.goto('https://www.instagram.com/', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Click on "+" (Create) button in nav
            create_button = await self.page.wait_for_selector(
                'svg[aria-label="New post"], [aria-label*="Create"]',
                timeout=10000
            )
            await create_button.click()
            await self.page.wait_for_timeout(2000)

            # Handle file upload if image_path provided
            if image_path and os.path.exists(image_path):
                file_input = await self.page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await self.page.wait_for_timeout(3000)
            else:
                # For demo purposes, we'll note that an image is required
                self.logger.warning("No image provided for Instagram post. Upload manually or provide image_path.")
                return await self.handle_error(
                    Exception("Image path required for Instagram post"),
                    "feed",
                    caption
                )

            # Click "Next"
            next_button = await self.page.query_selector('button:has-text("Next")')
            if next_button:
                await next_button.click()
                await self.page.wait_for_timeout(2000)

            # Add caption
            caption_input = await self.page.query_selector('textarea[aria-label*="caption"]')
            if caption_input:
                await caption_input.fill(caption)
                await self.page.wait_for_timeout(500)

            # Add hashtags if not already in caption
            if '#' not in caption:
                # Could add default hashtags here
                pass

            # Click "Share" to post
            share_button = await self.page.query_selector('button:has-text("Share")')
            if share_button:
                await share_button.click()
                await self.page.wait_for_timeout(3000)

                self.log_response_attempt("feed", caption, ResponseStatus.SENT)
                return {
                    "status": ResponseStatus.SENT.value,
                    "recipient": "feed",
                    "timestamp": time.time(),
                    "provider_message_id": f"ig_post_{int(time.time())}"
                }

            return await self.handle_error(
                Exception("Could not complete Instagram post"),
                "feed",
                caption
            )

        except Exception as e:
            return await self.handle_error(e, "feed", caption)

    async def post_story(self, content: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Post to Instagram Story
        
        Args:
            content: Text overlay for the story
            image_path: Path to image/video file
        """
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Instagram"), "story", content)

            # Navigate to story creation
            await self.page.goto('https://www.instagram.com/', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Click on "Your story" or "+" for story
            try:
                story_button = await self.page.wait_for_selector(
                    '[aria-label*="story"], [aria-label*="Your story"]',
                    timeout=10000
                )
                await story_button.click()
                await self.page.wait_for_timeout(2000)
            except TimeoutError:
                # Alternative: use create button and select story
                create_button = await self.page.query_selector('svg[aria-label="New post"]')
                if create_button:
                    await create_button.click()
                    await self.page.wait_for_timeout(1000)
                    
                    # Select "Story" option
                    story_option = await self.page.query_selector('[aria-label="Story"]')
                    if story_option:
                        await story_option.click()
                        await self.page.wait_for_timeout(2000)

            # Handle file upload
            if image_path and os.path.exists(image_path):
                file_input = await self.page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await self.page.wait_for_timeout(3000)
            else:
                self.logger.warning("No image provided for Instagram story.")
                return await self.handle_error(
                    Exception("Image path required for Instagram story"),
                    "story",
                    content
                )

            # Add text overlay if content provided
            if content:
                try:
                    # Tap to add text
                    await self.page.click('div[role="button"]:has-text("Aa")')
                    await self.page.wait_for_timeout(1000)
                    
                    # Fill text
                    text_input = await self.page.query_selector('textarea, input[placeholder*="text"]')
                    if text_input:
                        await text_input.fill(content)
                        await self.page.wait_for_timeout(500)
                except Exception as e:
                    self.logger.warning(f"Could not add text to story: {e}")

            # Click "Your Story" or "Share" to post
            share_button = await self.page.query_selector('button:has-text("Your Story"), button:has-text("Share")')
            if share_button:
                await share_button.click()
                await self.page.wait_for_timeout(3000)

                self.log_response_attempt("story", content, ResponseStatus.SENT)
                return {
                    "status": ResponseStatus.SENT.value,
                    "recipient": "story",
                    "timestamp": time.time(),
                    "provider_message_id": f"ig_story_{int(time.time())}"
                }

            return await self.handle_error(
                Exception("Could not complete Instagram story post"),
                "story",
                content
            )

        except Exception as e:
            return await self.handle_error(e, "story", content)

    async def follow_user(self, username: str) -> Dict[str, Any]:
        """Follow a user on Instagram"""
        try:
            await self._ensure_browser()
            
            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Instagram"), "follow", username)

            # Navigate to user profile
            profile_url = f'https://www.instagram.com/{username.lstrip("@")}/'
            await self.page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Click Follow button
            follow_button = await self.page.query_selector('button:has-text("Follow")')
            if follow_button:
                await follow_button.click()
                await self.page.wait_for_timeout(1000)
                return {
                    "status": ResponseStatus.SENT.value,
                    "action": "follow",
                    "username": username,
                    "timestamp": time.time()
                }

            return await self.handle_error(Exception("Follow button not found"), "follow", username)

        except Exception as e:
            return await self.handle_error(e, "follow", username)

    async def like_post(self, post_url: str) -> Dict[str, Any]:
        """Like an Instagram post"""
        try:
            await self._ensure_browser()
            
            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Instagram"), "like", post_url)

            await self.page.goto(post_url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(2000)

            # Click heart icon
            like_button = await self.page.query_selector('[aria-label="Like"], svg[aria-label*="Like"]')
            if like_button:
                await like_button.click()
                await self.page.wait_for_timeout(1000)
                return {
                    "status": ResponseStatus.SENT.value,
                    "action": "like",
                    "timestamp": time.time()
                }

            return await self.handle_error(Exception("Like button not found"), "like", post_url)

        except Exception as e:
            return await self.handle_error(e, "like", post_url)

    async def close(self):
        """Close browser and Playwright context"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

"""
Twitter/X Response Handler
Handles sending DMs and posting tweets via Twitter/X
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


class TwitterResponseHandler(BaseResponseHandler):
    """
    Response handler for Twitter/X DMs and Tweets using Playwright automation
    """
    
    def __init__(self, session_path: Optional[str] = None):
        super().__init__(CommunicationChannel.TWITTER)
        self.session_path = Path(session_path or os.getenv('TWITTER_SESSION_PATH', './sessions/twitter_session'))
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

        # Navigate to Twitter/X and check login status
        await self.page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=60000)
        
        try:
            # Check for home timeline or profile button
            await self.page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=10000)
            self.logged_in = True
        except TimeoutError:
            self.logged_in = await self._login()

    async def _login(self) -> bool:
        """Login to Twitter/X if not already logged in"""
        try:
            username = os.getenv('TWITTER_USERNAME')
            password = os.getenv('TWITTER_PASSWORD')
            email = os.getenv('TWITTER_EMAIL')  # May be required for 2FA

            if not username or not password:
                raise ValueError("Twitter credentials not found. Please run setup_sessions.py twitter")

            # Navigate to login page
            await self.page.goto('https://x.com/login', wait_until='domcontentloaded', timeout=30000)
            await self.page.wait_for_timeout(2000)

            # Fill username/phone/email
            username_field = await self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            await username_field.fill(username)
            await self.page.wait_for_timeout(500)
            
            # Click Next
            next_button = await self.page.query_selector('div[role="button"]:has-text("Next")')
            if next_button:
                await next_button.click()
                await self.page.wait_for_timeout(2000)

            # Fill password
            password_field = await self.page.wait_for_selector('input[type="password"]', timeout=10000)
            await password_field.fill(password)
            await self.page.wait_for_timeout(500)

            # Click Log In
            login_button = await self.page.query_selector('div[role="button"]:has-text("Log in")')
            if login_button:
                await login_button.click()
                await self.page.wait_for_timeout(3000)

            # Handle email verification if prompted
            if email:
                try:
                    await self.page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=5000)
                    email_field = await self.page.query_selector('input[data-testid="ocfEnterTextTextInput"]')
                    if email_field:
                        await email_field.fill(email)
                        await self.page.wait_for_timeout(500)
                        submit_button = await self.page.query_selector('div[role="button"]:has-text("Submit")')
                        if submit_button:
                            await submit_button.click()
                            await self.page.wait_for_timeout(2000)
                except TimeoutError:
                    pass  # Email verification not required

            # Wait for login to complete
            await self.page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=30000)
            
            self.logger.info("Successfully logged in to Twitter/X")
            return True

        except Exception as e:
            self.logger.error(f"Failed to login to Twitter/X: {e}")
            return False

    def validate_recipient(self, recipient_identifier: str) -> bool:
        """Validate Twitter recipient (@username or profile URL)"""
        if not recipient_identifier or len(recipient_identifier.strip()) < 2:
            return False
        return True

    def format_response(self, content: str, response_format: Optional[str] = None) -> str:
        """Format content for Twitter (280 char limit for tweets, 10000 for DMs)"""
        formatted = content.strip()
        # For DMs we have more room, but keep it concise
        if len(formatted) > 9000:
            self.logger.warning("Twitter DM content truncated")
            formatted = formatted[:9000] + "... [truncated]"
        return formatted

    async def send_response(self, recipient_identifier: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send a Twitter/X Direct Message"""
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(
                    Exception("Not logged in to Twitter/X"),
                    recipient_identifier,
                    content
                )

            if not self.validate_recipient(recipient_identifier):
                return await self.handle_error(
                    ValueError(f"Invalid Twitter identifier: {recipient_identifier}"),
                    recipient_identifier,
                    content
                )

            formatted_content = self.format_response(content)
            message_sent = await self._send_twitter_dm(recipient_identifier, formatted_content)

            if message_sent:
                self.log_response_attempt(recipient_identifier, content, ResponseStatus.SENT)
                return {
                    "status": ResponseStatus.SENT.value,
                    "recipient": recipient_identifier,
                    "timestamp": time.time(),
                    "provider_message_id": f"twitter_dm_{int(time.time())}"
                }
            else:
                return await self.handle_error(
                    Exception("Failed to send Twitter DM"),
                    recipient_identifier,
                    content
                )

        except Exception as error:
            return await self.handle_error(error, recipient_identifier, content)

    async def _send_twitter_dm(self, recipient_identifier: str, content: str) -> bool:
        """Send a Direct Message via Twitter/X"""
        try:
            # Navigate to Messages
            await self.page.goto('https://x.com/messages', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # If recipient starts with @, remove it for search
            search_name = recipient_identifier.lstrip('@')

            # Look for existing conversation or start new one
            # Try to find the contact in recent conversations first
            try:
                conversation_link = await self.page.query_selector(f'[data-testid="Conversation"] a[href*="{search_name}"]')
                if conversation_link:
                    await conversation_link.click()
                    await self.page.wait_for_timeout(2000)
                else:
                    # Start new message
                    new_message_btn = await self.page.query_selector('[data-testid="DMDrawer"]')
                    if new_message_btn:
                        await new_message_btn.click()
                        await self.page.wait_for_timeout(2000)
                    
                    # Search for user
                    search_input = await self.page.wait_for_selector('input[placeholder*="Search"]', timeout=10000)
                    await search_input.fill(search_name)
                    await self.page.wait_for_timeout(2000)
                    
                    # Click on first result
                    first_result = await self.page.query_selector('[role="group"][aria-label*="Profile"]')
                    if first_result:
                        await first_result.click()
                        await self.page.wait_for_timeout(2000)
            except Exception as e:
                self.logger.warning(f"Could not find conversation, trying direct approach: {e}")

            # Find message input and send
            message_input = await self.page.wait_for_selector(
                '[data-testid="DMDrawer"] [data-testid="conversationComposer"]',
                timeout=10000
            )
            if message_input:
                await message_input.fill(content)
                await self.page.wait_for_timeout(500)
                
                # Click send button (SVG icon)
                send_button = await self.page.query_selector(
                    '[data-testid="DMDrawer"] button[data-testid="appBarClose"]'
                )
                if send_button:
                    await send_button.click()
                    await self.page.wait_for_timeout(1000)
                    return True

            # Alternative: press Enter
            await message_input.press('Enter')
            await self.page.wait_for_timeout(1000)
            return True

        except TimeoutError:
            self.logger.error("Timeout while sending Twitter DM")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Twitter DM: {e}")
            return False

    async def post_tweet(self, content: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a tweet to Twitter/X
        
        Args:
            content: Tweet content (280 characters max for standard tweets)
            reply_to: Tweet ID to reply to (optional)
        """
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Twitter/X"), "tweet", content)

            # Check character limit
            if len(content) > 280:
                self.logger.warning(f"Tweet content exceeds 280 characters ({len(content)} chars)")
                # Twitter Blue allows longer tweets, but we'll truncate for safety
                content = content[:280] + "... [truncated]"

            # Navigate to home
            await self.page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Click on "What is happening?!" box
            tweet_box = await self.page.wait_for_selector(
                '[data-testid="tweetTextarea_0"]',
                timeout=10000
            )
            await tweet_box.click()
            await self.page.wait_for_timeout(1000)

            # Fill tweet content
            await tweet_box.fill(content)
            await self.page.wait_for_timeout(1000)

            # Click Post button
            post_button = await self.page.wait_for_selector(
                '[data-testid="tweetButton"]',
                timeout=10000
            )
            await post_button.click()
            await self.page.wait_for_timeout(3000)

            self.log_response_attempt("tweet", content, ResponseStatus.SENT)
            return {
                "status": ResponseStatus.SENT.value,
                "recipient": "tweet",
                "timestamp": time.time(),
                "provider_message_id": f"twitter_tweet_{int(time.time())}"
            }

        except Exception as e:
            return await self.handle_error(e, "tweet", content)

    async def post_thread(self, tweets: list) -> Dict[str, Any]:
        """
        Post a thread of tweets
        
        Args:
            tweets: List of tweet contents
        """
        try:
            await self._ensure_browser()

            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Twitter/X"), "thread", str(tweets))

            if not tweets or len(tweets) == 0:
                return await self.handle_error(
                    ValueError("No tweets provided for thread"),
                    "thread",
                    str(tweets)
                )

            # Navigate to home
            await self.page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(3000)

            # Click tweet box
            tweet_box = await self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
            await tweet_box.click()
            await self.page.wait_for_timeout(1000)

            # Fill first tweet
            await tweet_box.fill(tweets[0])
            await self.page.wait_for_timeout(1000)

            # Add additional tweets to thread
            for i, tweet_content in enumerate(tweets[1:], 1):
                try:
                    # Click "Add" button to add another tweet
                    add_button = await self.page.query_selector('[data-testid="addTweet"]')
                    if add_button:
                        await add_button.click()
                        await self.page.wait_for_timeout(1000)
                        
                        # Find the new tweet textarea and fill it
                        textareas = await self.page.query_selector_all('[data-testid="tweetTextarea_0"]')
                        if len(textareas) > i:
                            await textareas[i].fill(tweet_content)
                            await self.page.wait_for_timeout(500)
                except Exception as e:
                    self.logger.warning(f"Could not add tweet {i} to thread: {e}")

            # Click Post button
            post_button = await self.page.wait_for_selector('[data-testid="tweetButton"]', timeout=10000)
            await post_button.click()
            await self.page.wait_for_timeout(3000)

            self.log_response_attempt("thread", f"{len(tweets)} tweets", ResponseStatus.SENT)
            return {
                "status": ResponseStatus.SENT.value,
                "recipient": "thread",
                "timestamp": time.time(),
                "provider_message_id": f"twitter_thread_{int(time.time())}",
                "tweet_count": len(tweets)
            }

        except Exception as e:
            return await self.handle_error(e, "thread", str(tweets))

    async def like_tweet(self, tweet_url: str) -> Dict[str, Any]:
        """Like a tweet"""
        try:
            await self._ensure_browser()
            
            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Twitter/X"), "like", tweet_url)

            await self.page.goto(tweet_url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(2000)

            like_button = await self.page.query_selector('[data-testid="like"]')
            if like_button:
                await like_button.click()
                await self.page.wait_for_timeout(1000)
                return {
                    "status": ResponseStatus.SENT.value,
                    "action": "like",
                    "timestamp": time.time()
                }

            return await self.handle_error(Exception("Like button not found"), "like", tweet_url)

        except Exception as e:
            return await self.handle_error(e, "like", tweet_url)

    async def retweet(self, tweet_url: str) -> Dict[str, Any]:
        """Retweet a tweet"""
        try:
            await self._ensure_browser()
            
            if not self.logged_in:
                return await self.handle_error(Exception("Not logged in to Twitter/X"), "retweet", tweet_url)

            await self.page.goto(tweet_url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(2000)

            retweet_button = await self.page.query_selector('[data-testid="retweet"]')
            if retweet_button:
                await retweet_button.click()
                await self.page.wait_for_timeout(1000)
                
                # Confirm retweet
                confirm_button = await self.page.query_selector('[data-testid="retweetConfirm"]')
                if confirm_button:
                    await confirm_button.click()
                    await self.page.wait_for_timeout(1000)
                    return {
                        "status": ResponseStatus.SENT.value,
                        "action": "retweet",
                        "timestamp": time.time()
                    }

            return await self.handle_error(Exception("Retweet button not found"), "retweet", tweet_url)

        except Exception as e:
            return await self.handle_error(e, "retweet", tweet_url)

    async def close(self):
        """Close browser and Playwright context"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

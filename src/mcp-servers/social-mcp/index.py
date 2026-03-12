#!/usr/bin/env python3
"""
Universal Social Media MCP Server
Provides social media posting capabilities via JSON-RPC 2.0 protocol

Supports: LinkedIn, Twitter, Facebook, Instagram

Works with any AI agent: Claude, Qwen, Gemini, Codex

Usage:
    python src/mcp-servers/social-mcp/index.py
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Playwright for browser automation
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Install with: pip install playwright", file=sys.stderr)


class SocialMediaMCPServer:
    """Social Media MCP Server implementation"""
    
    def __init__(self, headless: bool = True, chrome_user_data: str = None):
        """
        Initialize Social Media MCP Server
        
        Args:
            headless: Run browser in headless mode
            chrome_user_data: Chrome user data directory for saved sessions
        """
        self.headless = headless
        self.chrome_user_data = chrome_user_data or os.getenv('CHROME_USER_DATA_DIR')
        self.browser = None
        self.page = None
        self._playwright = None
        
        if not PLAYWRIGHT_AVAILABLE:
            print("Warning: Playwright not available.", file=sys.stderr)
    
    def _ensure_browser(self):
        """Ensure browser is open"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        if self.browser is None:
            self._playwright = sync_playwright().start()
            
            if self.chrome_user_data and os.path.exists(self.chrome_user_data):
                self.browser = self._playwright.chromium.launch_persistent_context(
                    self.chrome_user_data,
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
            else:
                self.browser = self._playwright.chromium.launch(headless=self.headless)
            
            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        
        return True
    
    def post_to_linkedin(self, content: str, image_url: str = None) -> Dict[str, Any]:
        """Post to LinkedIn"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        try:
            self._ensure_browser()
            
            # Navigate to LinkedIn
            self.page.goto('https://www.linkedin.com/feed', timeout=60000)
            
            # Wait for post creation box
            try:
                self.page.wait_for_selector('div[role="textbox"]', timeout=15000)
            except PlaywrightTimeout:
                return {
                    "success": False,
                    "error": "NOT_LOGGED_IN",
                    "message": "Please log in to LinkedIn first"
                }
            
            # Click on post creation
            start_post = self.page.locator('button:has-text("Start a post")')
            if start_post.count() > 0:
                start_post.first.click()

            # Type content
            textbox = self.page.locator('div[role="textbox"]')
            if textbox.count() > 0:
                textbox.first.fill(content)

                # Add image if provided
                if image_url:
                    # Click media icon and add image
                    media_btn = self.page.locator('button[aria-label*="photo"]')
                    if media_btn.count() > 0:
                        media_btn.first.click()
                        # Would need file upload handling here

                # Click post button
                post_btn = self.page.locator('button:has-text("Post")')
                if post_btn.count() > 0:
                    post_btn.first.click()
                    
                    return {
                        "success": True,
                        "platform": "linkedin",
                        "content": content[:100] + "..." if len(content) > 100 else content,
                        "timestamp": datetime.now().isoformat(),
                        "status": "posted"
                    }
            
            return {
                "success": False,
                "error": "POST_FAILED",
                "message": "Could not complete post"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "LINKEDIN_ERROR",
                "message": str(e)
            }
    
    def post_to_twitter(self, content: str, media_urls: list = None) -> Dict[str, Any]:
        """Post to Twitter/X"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        try:
            self._ensure_browser()
            
            # Navigate to Twitter
            self.page.goto('https://twitter.com/home', timeout=60000)
            
            # Wait for tweet box
            try:
                self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
            except PlaywrightTimeout:
                return {
                    "success": False,
                    "error": "NOT_LOGGED_IN",
                    "message": "Please log in to Twitter first"
                }
            
            # Type tweet
            textarea = self.page.locator('[data-testid="tweetTextarea_0"]')
            if textarea.count() > 0:
                textarea.first.fill(content)

                # Add media if provided
                if media_urls:
                    # Click media upload button
                    media_btn = self.page.locator('[data-testid="addImageButton"]')
                    if media_btn.count() > 0:
                        media_btn.first.click()

                # Click tweet button
                tweet_btn = self.page.locator('[data-testid="tweetButton"]')
                if tweet_btn.count() > 0:
                    tweet_btn.first.click()
                    
                    return {
                        "success": True,
                        "platform": "twitter",
                        "content": content[:100] + "..." if len(content) > 100 else content,
                        "timestamp": datetime.now().isoformat(),
                        "status": "tweeted"
                    }
            
            return {
                "success": False,
                "error": "TWEET_FAILED",
                "message": "Could not complete tweet"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "TWITTER_ERROR",
                "message": str(e)
            }
    
    def post_to_facebook(self, content: str, image_url: str = None) -> Dict[str, Any]:
        """Post to Facebook"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        try:
            self._ensure_browser()
            
            # Navigate to Facebook
            self.page.goto('https://www.facebook.com', timeout=60000)
            
            # Wait for post creation
            try:
                self.page.wait_for_selector('[placeholder="What\'s on your mind?"]', timeout=15000)
            except PlaywrightTimeout:
                return {
                    "success": False,
                    "error": "NOT_LOGGED_IN",
                    "message": "Please log in to Facebook first"
                }
            
            # Click on post creation
            post_input = self.page.locator('[placeholder="What\'s on your mind?"]')
            if post_input.count() > 0:
                post_input.first.click()
                post_input.first.fill(content)

                # Click post button
                post_btn = self.page.locator('button:has-text("Post")')
                if post_btn.count() > 0:
                    post_btn.first.click()
                    
                    return {
                        "success": True,
                        "platform": "facebook",
                        "content": content[:100] + "..." if len(content) > 100 else content,
                        "timestamp": datetime.now().isoformat(),
                        "status": "posted"
                    }
            
            return {
                "success": False,
                "error": "POST_FAILED",
                "message": "Could not complete post"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "FACEBOOK_ERROR",
                "message": str(e)
            }
    
    def post_to_instagram(self, caption: str, image_path: str) -> Dict[str, Any]:
        """Post to Instagram"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        try:
            self._ensure_browser()
            
            # Navigate to Instagram
            self.page.goto('https://www.instagram.com', timeout=60000)
            
            # Wait for feed
            try:
                self.page.wait_for_selector('article', timeout=15000)
            except PlaywrightTimeout:
                return {
                    "success": False,
                    "error": "NOT_LOGGED_IN",
                    "message": "Please log in to Instagram first"
                }
            
            # Click new post
            new_post_btn = self.page.locator('svg[aria-label="New post"]')
            if new_post_btn.count() > 0:
                new_post_btn.first.click()
                
                # Upload image (would need file input handling)
                # For now, just return info
                return {
                    "success": True,
                    "platform": "instagram",
                    "caption": caption[:100] + "..." if len(caption) > 100 else caption,
                    "image": image_path,
                    "timestamp": datetime.now().isoformat(),
                    "status": "draft",
                    "message": "Manual image upload required"
                }
            
            return {
                "success": False,
                "error": "POST_FAILED",
                "message": "Could not create post"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "INSTAGRAM_ERROR",
                "message": str(e)
            }
    
    def schedule_post(self, platform: str, content: str, scheduled_time: str) -> Dict[str, Any]:
        """Schedule a post for later"""
        # Simplified - would need database integration for real scheduling
        return {
            "success": True,
            "platform": platform,
            "content": content[:100],
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "message": "Post scheduled (requires background service for actual posting)"
        }
    
    def get_tools(self) -> Dict[str, Any]:
        """Get available tools"""
        return {
            "tools": [
                {
                    "name": "social.linkedin.post",
                    "description": "Post to LinkedIn",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Post content"},
                            "imageUrl": {"type": "string", "description": "Image URL (optional)"}
                        },
                        "required": ["content"]
                    }
                },
                {
                    "name": "social.twitter.post",
                    "description": "Post to Twitter/X",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Tweet content"},
                            "mediaUrls": {"type": "array", "items": {"type": "string"}, "description": "Media URLs"}
                        },
                        "required": ["content"]
                    }
                },
                {
                    "name": "social.facebook.post",
                    "description": "Post to Facebook",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Post content"},
                            "imageUrl": {"type": "string", "description": "Image URL (optional)"}
                        },
                        "required": ["content"]
                    }
                },
                {
                    "name": "social.instagram.post",
                    "description": "Post to Instagram",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "caption": {"type": "string", "description": "Post caption"},
                            "imagePath": {"type": "string", "description": "Path to image file"}
                        },
                        "required": ["caption", "imagePath"]
                    }
                },
                {
                    "name": "social.schedule",
                    "description": "Schedule a post",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string", "description": "Platform (linkedin, twitter, facebook, instagram)"},
                            "content": {"type": "string", "description": "Post content"},
                            "scheduledTime": {"type": "string", "description": "ISO 8601 datetime"}
                        },
                        "required": ["platform", "content", "scheduledTime"]
                    }
                }
            ]
        }
    
    def close(self):
        """Close browser connection"""
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()


# JSON-RPC Server Handler

def handle_request(server: SocialMediaMCPServer, request: Dict) -> Dict:
    """Handle JSON-RPC request"""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    try:
        if method == 'tools.list':
            result = server.get_tools()
        elif method == 'social.linkedin.post':
            result = server.post_to_linkedin(
                content=params.get('content'),
                image_url=params.get('imageUrl')
            )
        elif method == 'social.twitter.post':
            result = server.post_to_twitter(
                content=params.get('content'),
                media_urls=params.get('mediaUrls')
            )
        elif method == 'social.facebook.post':
            result = server.post_to_facebook(
                content=params.get('content'),
                image_url=params.get('imageUrl')
            )
        elif method == 'social.instagram.post':
            result = server.post_to_instagram(
                caption=params.get('caption'),
                image_path=params.get('imagePath')
            )
        elif method == 'social.schedule':
            result = server.schedule_post(
                platform=params.get('platform'),
                content=params.get('content'),
                scheduled_time=params.get('scheduledTime')
            )
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }


def main():
    """Main entry point"""
    print("Starting Social Media MCP Server (Python)...", file=sys.stderr)
    
    # Initialize server
    server = SocialMediaMCPServer()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("Warning: Playwright not available.", file=sys.stderr)
    else:
        print("Social Media MCP Server ready", file=sys.stderr)
    
    # Process stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(server, request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {e}"
                }
            }
            print(json.dumps(error_response), flush=True)
    
    # Cleanup
    server.close()


if __name__ == "__main__":
    main()

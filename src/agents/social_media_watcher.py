"""
Unified Social Media Watcher
Monitors all social media platforms using shared Chrome profile
- Twitter/X
- LinkedIn  
- Facebook
- Instagram
- WhatsApp

All platforms use the same Chrome profile - login once, ELYX reuses session!
"""

import hashlib
from playwright.sync_api import sync_playwright
from ..base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os
import time


class SocialMediaWatcher(BaseWatcher):
    """
    Monitors multiple social media platforms using shared Chrome profile.
    Keeps a single Playwright browser open across all check cycles.
    """

    def __init__(self, vault_path: str, platform: str = 'all'):
        """
        Initialize social media watcher

        Args:
            vault_path: Path to Obsidian vault
            platform: Which platform to monitor ('twitter', 'linkedin', 'facebook', 'instagram', 'whatsapp', or 'all')
        """
        super().__init__(vault_path, check_interval=60, use_chrome_profile=True)
        self.platform = platform

        # Persistent browser context (reused across check cycles)
        self._playwright = None
        self._browser = None
        self._page = None

        # Platform-specific configurations (must be set before _load_all_platform_ids)
        self.platform_configs = {
            'twitter': {
                'url': 'https://x.com/notifications',
                'env_prefix': 'TWITTER',
                'check_interval': int(os.getenv('TWITTER_CHECK_INTERVAL', 7200))
            },
            'linkedin': {
                'url': 'https://www.linkedin.com/messaging/',
                'env_prefix': 'LINKEDIN',
                'check_interval': int(os.getenv('LINKEDIN_CHECK_INTERVAL', 3600))
            },
            'facebook': {
                'url': 'https://www.facebook.com/messages/t/',
                'env_prefix': 'FACEBOOK',
                'check_interval': int(os.getenv('FACEBOOK_CHECK_INTERVAL', 7200))
            },
            'instagram': {
                'url': 'https://www.instagram.com/direct/inbox/',
                'env_prefix': 'INSTAGRAM',
                'check_interval': int(os.getenv('INSTAGRAM_CHECK_INTERVAL', 7200))
            },
            'whatsapp': {
                'url': 'https://web.whatsapp.com',
                'env_prefix': 'WHATSAPP',
                'check_interval': int(os.getenv('WHATSAPP_CHECK_INTERVAL', 60)),
                'keywords': os.getenv('WHATSAPP_KEYWORDS', 'urgent,asap,invoice,payment,help').split(',')
            }
        }

        # Now safe to call — platform_configs is set
        self.processed_items = self._load_all_platform_ids()

    def _load_all_platform_ids(self) -> dict:
        """Load processed IDs for all platforms from disk"""
        result = {}
        for platform in self.platform_configs:
            ids = self._load_processed_ids(f"social_{platform}")
            result[platform] = ids
        return result

    def _persist_platform_ids(self, platform: str):
        """Save processed IDs for a specific platform to disk"""
        ids = self.processed_items.get(platform, set())
        self._save_processed_ids(f"social_{platform}", ids)

    def check_platform(self, platform: str, page) -> list:
        """
        Check a specific platform for new activity
        
        Args:
            platform: Platform name
            page: Playwright page object
            
        Returns:
            List of new items
        """
        updates = []
        
        try:
            if platform == 'twitter':
                updates = self._check_twitter(page)
            elif platform == 'linkedin':
                updates = self._check_linkedin(page)
            elif platform == 'facebook':
                updates = self._check_facebook(page)
            elif platform == 'instagram':
                updates = self._check_instagram(page)
            elif platform == 'whatsapp':
                updates = self._check_whatsapp(page)
        except Exception as e:
            self.logger.error(f"Error checking {platform}: {e}")
        
        return updates
    
    def _check_twitter(self, page) -> list:
        """Check Twitter for notifications and DMs"""
        updates = []
        
        try:
            page.goto('https://x.com/notifications', timeout=30000)
            page.wait_for_selector('[data-testid="cellInnerDiv"]', timeout=10000)
            
            # Get recent notifications
            notifications = page.query_selector_all('[data-testid="notification"]')
            
            for n in notifications[:5]:
                text = n.inner_text()
                n_id = hashlib.sha256(text.encode()).hexdigest()[:16]

                if n_id not in self.processed_items.get('twitter', set()):
                    updates.append({
                        'platform': 'twitter',
                        'type': 'notification',
                        'text': text[:200],
                        'timestamp': datetime.now().isoformat()
                    })
                    self.processed_items.setdefault('twitter', set()).add(n_id)
                    self._persist_platform_ids('twitter')
        except Exception as e:
            self.logger.warning(f"Twitter check failed: {e}")
        
        return updates
    
    def _check_linkedin(self, page) -> list:
        """Check LinkedIn for messages"""
        updates = []
        
        try:
            page.goto('https://www.linkedin.com/messaging/', timeout=30000)
            page.wait_for_selector('[data-test-id="messaging-thread"]', timeout=10000)
            
            # Find unread threads
            unread_threads = page.query_selector_all('[data-test-id="messaging-thread"]:has([aria-label="Unread"])')
            
            for thread in unread_threads[:5]:
                text = thread.text_content()[:200]
                t_id = hashlib.sha256(text.encode()).hexdigest()[:16]

                if t_id not in self.processed_items.get('linkedin', set()):
                    updates.append({
                        'platform': 'linkedin',
                        'type': 'message',
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.processed_items.setdefault('linkedin', set()).add(t_id)
                    self._persist_platform_ids('linkedin')
        except Exception as e:
            self.logger.warning(f"LinkedIn check failed: {e}")
        
        return updates
    
    def _check_facebook(self, page) -> list:
        """Check Facebook Messenger for messages"""
        updates = []
        
        try:
            page.goto('https://www.facebook.com/messages/t/', timeout=30000)
            page.wait_for_selector('[aria-label="Chats"], [aria-label="Search Messenger"]', timeout=10000)
            
            # Look for unread message indicators
            unread = page.query_selector_all('[aria-label*="unread"], [data-visually-hidden*="unread"]')
            
            for u in unread[:5]:
                text = u.text_content()[:200]
                u_id = hashlib.sha256(text.encode()).hexdigest()[:16]

                if u_id not in self.processed_items.get('facebook', set()):
                    updates.append({
                        'platform': 'facebook',
                        'type': 'message',
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.processed_items.setdefault('facebook', set()).add(u_id)
                    self._persist_platform_ids('facebook')
        except Exception as e:
            self.logger.warning(f"Facebook check failed: {e}")
        
        return updates
    
    def _check_instagram(self, page) -> list:
        """Check Instagram DMs"""
        updates = []
        
        try:
            page.goto('https://www.instagram.com/direct/inbox/', timeout=30000)
            page.wait_for_selector('role=main', timeout=10000)
            
            # Check for unread indicators
            unread = page.query_selector_all('[aria-label="Unread"]')
            
            for u in unread[:5]:
                text = "Unread message in thread"
                u_id = hashlib.sha256(u.inner_html().encode()).hexdigest()[:16]

                if u_id not in self.processed_items.get('instagram', set()):
                    updates.append({
                        'platform': 'instagram',
                        'type': 'dm',
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    })
                    self.processed_items.setdefault('instagram', set()).add(u_id)
                    self._persist_platform_ids('instagram')
        except Exception as e:
            self.logger.warning(f"Instagram check failed: {e}")
        
        return updates
    
    def _check_whatsapp(self, page) -> list:
        """Check WhatsApp for urgent messages"""
        updates = []
        keywords = self.platform_configs['whatsapp'].get('keywords', [])
        
        try:
            page.goto('https://web.whatsapp.com', timeout=30000)
            page.wait_for_selector('[data-testid="chat-list"]', timeout=15000)
            
            # Find unread chats
            unread_chats = page.query_selector_all('[data-icon="muted-unread"]')
            
            for chat in unread_chats[:5]:
                try:
                    chat.click()
                    message_elements = page.query_selector_all('[data-testid="conversation"] [dir="ltr"]')
                    
                    for msg_elem in message_elements:
                        text = msg_elem.text_content().lower()
                        
                        # Check for urgent keywords
                        if any(kw in text for kw in keywords):
                            msg_id = hashlib.sha256(text.encode()).hexdigest()[:16]
                            if msg_id not in self.processed_items.get('whatsapp', set()):
                                updates.append({
                                    'platform': 'whatsapp',
                                    'type': 'urgent_message',
                                    'text': msg_elem.text_content()[:200],
                                    'keywords_found': [kw for kw in keywords if kw in text],
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.processed_items.setdefault('whatsapp', set()).add(msg_id)
                                self._persist_platform_ids('whatsapp')
                except Exception as e:
                    self.logger.error(f"Error processing WhatsApp chat: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"WhatsApp check failed: {e}")
        
        return updates
    
    def _open_browser(self):
        """Open a persistent browser context (reused across check cycles)."""
        self._playwright = sync_playwright().start()
        browser_args = self.get_browser_args()
        self._browser = self._playwright.chromium.launch_persistent_context(**browser_args)
        self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()

    def _is_browser_alive(self) -> bool:
        """Check if the persistent browser is still usable."""
        try:
            return self._page is not None and not self._page.is_closed()
        except Exception:
            return False

    def _close_browser(self):
        """Close the persistent browser and Playwright instance."""
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._playwright = None
        self._browser = None
        self._page = None

    def cleanup(self):
        """Clean up browser resources."""
        self._close_browser()

    def check_for_updates(self) -> list:
        """
        Check all configured platforms for updates.
        Reuses a single persistent browser across cycles.
        """
        all_updates = []

        try:
            if not self._is_browser_alive():
                self._open_browser()

            page = self._page

            # Check each platform
            platforms_to_check = [self.platform] if self.platform != 'all' else self.platform_configs.keys()

            for platform in platforms_to_check:
                if platform in self.platform_configs:
                    self.logger.info(f"Checking {platform}...")
                    updates = self.check_platform(platform, page)
                    all_updates.extend(updates)
                    self.logger.info(f"Found {len(updates)} new {platform} items")

        except Exception as e:
            self.logger.error(f"Error in social media checking: {e}")
            self._close_browser()

        return all_updates
    
    def create_action_file(self, item) -> Path:
        """
        Create an action file in Needs_Action folder
        """
        platform = item['platform']
        item_type = item['type']
        
        content = f'''---
type: {platform}_{item_type}
platform: {platform}
priority: {"high" if item_type == "urgent_message" else "medium"}
status: pending
received: {item["timestamp"]}
{f'keywords: {", ".join(item["keywords_found"])}' if 'keywords_found' in item else ''}
---

## New {platform.title()} Activity

**Type**: {item_type.replace('_', ' ').title()}

**Content**: {item["text"]}

**Received**: {item["timestamp"]}

## Suggested Actions
- [ ] Review {platform} activity
- [ ] Determine if response is needed
- [ ] Respond appropriately based on Company Handbook
- [ ] Archive if spam/irrelevant
'''
        
        filepath = self.needs_action / f'{platform.upper()}_{hashlib.sha256(item["text"].encode()).hexdigest()[:8]}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath


def run_social_media_watcher(vault_path: str, platform: str = 'all'):
    """
    Convenience function to run the social media watcher.
    Delegates to BaseWatcher.run() for retry logic, error recovery,
    status reporting, and Chrome health-checks (#50).
    """
    watcher = SocialMediaWatcher(vault_path, platform)
    watcher.logger.info(f"Starting Social Media Watcher (platform: {platform})")
    watcher.logger.info(f"Chrome Profile: {watcher.chrome_user_data_dir}")
    try:
        watcher.run()
    finally:
        watcher.cleanup()

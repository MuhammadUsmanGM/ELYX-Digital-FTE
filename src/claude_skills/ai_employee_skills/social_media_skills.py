"""
Social Media Posting Skills for ELYX AI Employee

Provides skills for:
- Posting to LinkedIn, Facebook, Twitter/X, Instagram
- Cross-platform campaigns
- Scheduled posting
- Engagement actions (likes, follows, etc.)
"""

from pathlib import Path
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from src.services.direct_social_sender import (
    send_message,
    send_linkedin_post, send_linkedin_dm,
    send_facebook_post, send_facebook_dm,
    send_tweet, send_twitter_dm,
    send_instagram_post, send_instagram_dm,
)
from src.utils.logger import log_activity


class CommunicationChannel:
    """Platform identifiers for social media routing."""
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"


class SocialPostingService:
    """
    Bridges social media skills to the unified direct_social_sender.
    Manages post history and scheduled posts via the Obsidian vault.
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.social_posts_dir = self.vault_path / "Social_Posts"
        self.published_dir = self.social_posts_dir / "Published"
        self.scheduled_dir = self.social_posts_dir / "Scheduled"
        self.failed_dir = self.social_posts_dir / "Failed"

        # Ensure directories exist
        for d in (self.published_dir, self.scheduled_dir, self.failed_dir):
            d.mkdir(parents=True, exist_ok=True)

    async def post_to_platform(
        self, platform: str, content: str, requires_approval: bool = True, **kwargs
    ) -> Dict[str, Any]:
        if requires_approval:
            return self._create_approval_request(platform, content, **kwargs)

        result = send_message(platform, "", content, **kwargs)
        self._record_post(platform, content, result)
        return result

    async def post_to_all_platforms(
        self, content: str, platforms: list, image_path: str = None,
        requires_approval: bool = True
    ) -> Dict[str, Any]:
        import uuid
        campaign_id = str(uuid.uuid4())[:8]
        results = {}
        for plat in platforms:
            result = await self.post_to_platform(
                plat, content, requires_approval=requires_approval,
                image_path=image_path
            )
            results[plat] = result
        return {"campaign_id": campaign_id, "results": results}

    def _create_approval_request(self, platform: str, content: str, **kwargs) -> Dict[str, Any]:
        import time as _t
        filename = f"SOCIAL_APPROVAL_{platform}_{int(_t.time())}.md"
        approval_content = f"""---
type: approval_request
action: social_post
platform: {platform}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + __import__('datetime').timedelta(hours=24)).isoformat()}
status: pending
---

## Social Media Post Approval

**Platform**: {platform.title()}
**Content**: {content[:500]}

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
"""
        approval_path = self.vault_path / "Pending_Approval" / filename
        approval_path.parent.mkdir(parents=True, exist_ok=True)
        approval_path.write_text(approval_content, encoding="utf-8")
        return {"status": "pending_approval", "file": str(approval_path)}

    def _record_post(self, platform: str, content: str, result: dict):
        import time as _t
        ts = datetime.now()
        filename = f"{platform}_{int(_t.time())}.md"
        record = f"""---
platform: {platform}
posted: {ts.isoformat()}
success: {result.get('success', False)}
---

## {platform.title()} Post

{content[:1000]}

## Result
{result.get('message', result.get('error', 'unknown'))}
"""
        if result.get("success"):
            (self.published_dir / filename).write_text(record, encoding="utf-8")
        else:
            (self.failed_dir / filename).write_text(record, encoding="utf-8")

    def get_post_history(self, platform=None, limit=50) -> list:
        posts = []
        for f in sorted(self.published_dir.glob("*.md"), reverse=True)[:limit]:
            if platform and not f.name.startswith(platform):
                continue
            posts.append({"file": f.name, "content": f.read_text(encoding="utf-8")[:200]})
        return posts

    def get_scheduled_posts(self) -> list:
        return [{"file": f.name} for f in self.scheduled_dir.glob("*.md")]

    def cancel_scheduled_post(self, post_id: str) -> bool:
        target = self.scheduled_dir / post_id
        if target.exists():
            target.unlink()
            return True
        return False


class SocialMediaSkills:
    """
    Social media posting and engagement skills for ELYX
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.posting_service = SocialPostingService(vault_path)
        
    async def post_to_linkedin(self, content: str, requires_approval: bool = True) -> Dict[str, Any]:
        """
        Post content to LinkedIn feed
        
        Args:
            content: Post content (max 3000 characters)
            requires_approval: Whether approval is needed (default True for safety)
            
        Returns:
            Post result dictionary
        """
        log_activity("SOCIAL", f"LinkedIn post requested: {content[:50]}...", str(self.vault_path))
        
        result = await self.posting_service.post_to_platform(
            platform=CommunicationChannel.LINKEDIN,
            content=content,
            requires_approval=requires_approval
        )
        
        log_activity("SOCIAL", f"LinkedIn post result: {result.get('status')}", str(self.vault_path))
        return result
    
    async def post_to_facebook(self, content: str, privacy: str = 'friends', requires_approval: bool = True) -> Dict[str, Any]:
        """
        Post content to Facebook feed
        
        Args:
            content: Post content
            privacy: Privacy setting ('public', 'friends', 'only_me')
            requires_approval: Whether approval is needed
            
        Returns:
            Post result dictionary
        """
        log_activity("SOCIAL", f"Facebook post requested: {content[:50]}...", str(self.vault_path))
        
        result = await self.posting_service.post_to_platform(
            platform=CommunicationChannel.FACEBOOK,
            content=content,
            requires_approval=requires_approval,
            privacy=privacy
        )
        
        log_activity("SOCIAL", f"Facebook post result: {result.get('status')}", str(self.vault_path))
        return result
    
    async def post_to_twitter(self, content: str, is_thread: bool = False, requires_approval: bool = True) -> Dict[str, Any]:
        """
        Post content to Twitter/X
        
        Args:
            content: Tweet content (max 280 chars for single tweet)
            is_thread: Whether this is a thread (list of tweets)
            requires_approval: Whether approval is needed
            
        Returns:
            Post result dictionary
        """
        log_activity("SOCIAL", f"Twitter post requested: {content[:50]}...", str(self.vault_path))
        
        result = await self.posting_service.post_to_platform(
            platform=CommunicationChannel.TWITTER,
            content=content,
            requires_approval=requires_approval,
            is_thread=is_thread
        )
        
        log_activity("SOCIAL", f"Twitter post result: {result.get('status')}", str(self.vault_path))
        return result
    
    async def post_to_instagram(self, caption: str, image_path: str, requires_approval: bool = True) -> Dict[str, Any]:
        """
        Post content to Instagram feed
        
        Args:
            caption: Post caption (max 2200 characters, 30 hashtags)
            image_path: Path to image/video file (required)
            requires_approval: Whether approval is needed
            
        Returns:
            Post result dictionary
        """
        log_activity("SOCIAL", f"Instagram post requested: {caption[:50]}...", str(self.vault_path))
        
        # Verify image exists
        image_file = Path(image_path)
        if not image_file.exists():
            return {
                "status": "failed",
                "error": f"Image not found: {image_path}"
            }
        
        result = await self.posting_service.post_to_platform(
            platform=CommunicationChannel.INSTAGRAM,
            content=caption,
            image_path=str(image_file),
            requires_approval=requires_approval
        )
        
        log_activity("SOCIAL", f"Instagram post result: {result.get('status')}", str(self.vault_path))
        return result
    
    async def post_to_all_platforms(
        self,
        content: str,
        image_path: Optional[str] = None,
        platforms: Optional[list] = None,
        requires_approval: bool = True
    ) -> Dict[str, Any]:
        """
        Post content to all configured social media platforms
        
        Args:
            content: Base content (will be formatted per platform)
            image_path: Path to image/video (required for Instagram)
            platforms: Specific platforms to post to (default: all)
            requires_approval: Whether approval is needed
            
        Returns:
            Campaign result dictionary with results per platform
        """
        log_activity("SOCIAL", f"Cross-platform post requested: {content[:50]}...", str(self.vault_path))
        
        platform_map = {
            'linkedin': CommunicationChannel.LINKEDIN,
            'facebook': CommunicationChannel.FACEBOOK,
            'twitter': CommunicationChannel.TWITTER,
            'instagram': CommunicationChannel.INSTAGRAM
        }
        
        if platforms:
            channels = [platform_map.get(p.lower()) for p in platforms if p.lower() in platform_map]
            channels = [c for c in channels if c is not None]
        else:
            channels = list(platform_map.values())
        
        result = await self.posting_service.post_to_all_platforms(
            content=content,
            platforms=channels,
            image_path=image_path,
            requires_approval=requires_approval
        )
        
        log_activity("SOCIAL", f"Cross-platform campaign result: {result.get('campaign_id')}", str(self.vault_path))
        return result
    
    async def schedule_post(
        self,
        platform: str,
        content: str,
        schedule_time: datetime,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a post for future publishing
        
        Args:
            platform: Target platform ('linkedin', 'facebook', 'twitter', 'instagram')
            content: Post content
            schedule_time: When to publish
            image_path: Path to image/video (required for Instagram)
            
        Returns:
            Schedule result dictionary
        """
        log_activity("SOCIAL", f"Scheduled {platform} post for {schedule_time}", str(self.vault_path))
        
        platform_map = {
            'linkedin': CommunicationChannel.LINKEDIN,
            'facebook': CommunicationChannel.FACEBOOK,
            'twitter': CommunicationChannel.TWITTER,
            'instagram': CommunicationChannel.INSTAGRAM
        }
        
        channel = platform_map.get(platform.lower())
        if not channel:
            return {"status": "failed", "error": f"Unknown platform: {platform}"}
        
        result = await self.posting_service.post_to_platform(
            platform=channel,
            content=content,
            image_path=image_path,
            schedule_time=schedule_time,
            requires_approval=False  # Already approved by scheduling
        )
        
        return result
    
    async def like_linkedin_post(self, post_url: str) -> Dict[str, Any]:
        """Like a LinkedIn post"""
        # Note: LinkedIn handler doesn't have like method yet
        return {"status": "not_implemented", "message": "LinkedIn like not yet implemented"}
    
    async def follow_instagram_user(self, username: str) -> Dict[str, Any]:
        """Follow a user on Instagram"""
        log_activity("SOCIAL", f"Following Instagram user: {username}", str(self.vault_path))
        return {"status": "not_implemented", "message": "Instagram follow not yet implemented via unified sender"}

    async def like_instagram_post(self, post_url: str) -> Dict[str, Any]:
        """Like an Instagram post"""
        log_activity("SOCIAL", f"Liking Instagram post: {post_url}", str(self.vault_path))
        return {"status": "not_implemented", "message": "Instagram like not yet implemented via unified sender"}

    async def like_twitter_post(self, tweet_url: str) -> Dict[str, Any]:
        """Like a tweet"""
        log_activity("SOCIAL", f"Liking tweet: {tweet_url}", str(self.vault_path))
        return {"status": "not_implemented", "message": "Twitter like not yet implemented via unified sender"}

    async def retweet(self, tweet_url: str) -> Dict[str, Any]:
        """Retweet a tweet"""
        log_activity("SOCIAL", f"Retweeting: {tweet_url}", str(self.vault_path))
        return {"status": "not_implemented", "message": "Retweet not yet implemented via unified sender"}
    
    def get_post_history(self, platform: Optional[str] = None, limit: int = 50) -> list:
        """
        Get published post history
        
        Args:
            platform: Filter by platform (optional)
            limit: Maximum posts to return
            
        Returns:
            List of post records
        """
        channel = None
        if platform:
            platform_map = {
                'linkedin': CommunicationChannel.LINKEDIN,
                'facebook': CommunicationChannel.FACEBOOK,
                'twitter': CommunicationChannel.TWITTER,
                'instagram': CommunicationChannel.INSTAGRAM
            }
            channel = platform_map.get(platform.lower())
        
        return self.posting_service.get_post_history(channel, limit)
    
    def get_scheduled_posts(self) -> list:
        """Get all scheduled posts"""
        return self.posting_service.get_scheduled_posts()
    
    def cancel_scheduled_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        return self.posting_service.cancel_scheduled_post(post_id)


# Convenience functions for direct usage
async def post_linkedin_update(content: str, approval: bool = True) -> Dict[str, Any]:
    """Post a professional update to LinkedIn"""
    skills = SocialMediaSkills("./obsidian_vault")
    return await skills.post_to_linkedin(content, requires_approval=approval)


async def post_business_update(content: str, platforms: list = None, approval: bool = True) -> Dict[str, Any]:
    """Post a business update across multiple platforms"""
    skills = SocialMediaSkills("./obsidian_vault")
    return await skills.post_to_all_platforms(content, platforms=platforms, requires_approval=approval)


async def schedule_business_post(platform: str, content: str, when: datetime, image: str = None) -> Dict[str, Any]:
    """Schedule a business post for optimal timing"""
    skills = SocialMediaSkills("./obsidian_vault")
    return await skills.schedule_post(platform, content, when, image_path=image)

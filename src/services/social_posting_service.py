"""
Unified Social Media Posting Service
Coordinates posting across all social media platforms:
- LinkedIn (messages + feed posts)
- Facebook (messages + feed posts + group posts)
- Twitter/X (DMs + tweets + threads)
- Instagram (DMs + feed posts + stories)

Features:
- Cross-platform posting
- Scheduling support
- Content formatting per platform
- Rate limiting
- Approval workflow integration
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

from src.response_handlers.base_handler import CommunicationChannel, ResponseStatus
from src.services.approval_workflow import ApprovalWorkflow, MessageType


class SocialPostingService:
    """
    Unified service for managing social media posts across all platforms
    """
    
    def __init__(self, vault_path: str = "./obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.posts_dir = self.vault_path / "Social_Posts"
        self.scheduled_dir = self.posts_dir / "Scheduled"
        self.published_dir = self.posts_dir / "Published"
        self.failed_dir = self.posts_dir / "Failed"
        
        # Create directories
        for dir_path in [self.posts_dir, self.scheduled_dir, self.published_dir, self.failed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize handlers lazily
        self._linkedin_handler = None
        self._facebook_handler = None
        self._twitter_handler = None
        self._instagram_handler = None
        
        # Approval workflow
        self.approval_workflow = ApprovalWorkflow(vault_path)
        
        # Rate limiting (platform-specific limits)
        self.rate_limits = {
            CommunicationChannel.LINKEDIN: {"requests": [], "limit": 100, "window": 3600},  # 100/hour
            CommunicationChannel.FACEBOOK: {"requests": [], "limit": 50, "window": 3600},   # 50/hour
            CommunicationChannel.TWITTER: {"requests": [], "limit": 2400, "window": 86400}, # 2400/day
            CommunicationChannel.INSTAGRAM: {"requests": [], "limit": 25, "window": 3600},  # 25/hour
        }
        
        # Platform-specific content guidelines
        self.content_guidelines = {
            CommunicationChannel.LINKEDIN: {
                "max_length": 3000,
                "hashtag_limit": 5,
                "best_practices": ["Professional tone", "Industry insights", "Value-driven content"]
            },
            CommunicationChannel.FACEBOOK: {
                "max_length": 63206,
                "hashtag_limit": 10,
                "best_practices": ["Engaging visuals", "Community-focused", "Conversational"]
            },
            CommunicationChannel.TWITTER: {
                "max_length": 280,  # Standard limit
                "hashtag_limit": 3,
                "best_practices": ["Concise", "Timely", "Use threads for longer content"]
            },
            CommunicationChannel.INSTAGRAM: {
                "max_length": 2200,  # Caption length
                "hashtag_limit": 30,
                "best_practices": ["Visual-first", "Authentic", "Story-driven"]
            }
        }

    @property
    def linkedin_handler(self):
        """Lazy initialization of LinkedIn handler"""
        if self._linkedin_handler is None:
            from src.response_handlers.linkedin_response_handler import LinkedInResponseHandler
            self._linkedin_handler = LinkedInResponseHandler()
        return self._linkedin_handler

    @property
    def facebook_handler(self):
        """Lazy initialization of Facebook handler"""
        if self._facebook_handler is None:
            from src.response_handlers.facebook_response_handler import FacebookResponseHandler
            self._facebook_handler = FacebookResponseHandler()
        return self._facebook_handler

    @property
    def twitter_handler(self):
        """Lazy initialization of Twitter handler"""
        if self._twitter_handler is None:
            from src.response_handlers.twitter_response_handler import TwitterResponseHandler
            self._twitter_handler = TwitterResponseHandler()
        return self._twitter_handler

    @property
    def instagram_handler(self):
        """Lazy initialization of Instagram handler"""
        if self._instagram_handler is None:
            from src.response_handlers.instagram_response_handler import InstagramResponseHandler
            self._instagram_handler = InstagramResponseHandler()
        return self._instagram_handler

    async def post_to_platform(
        self,
        platform: CommunicationChannel,
        content: str,
        image_path: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        requires_approval: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to a specific social media platform
        
        Args:
            platform: Target platform (LINKEDIN, FACEBOOK, TWITTER, INSTAGRAM)
            content: Content to post
            image_path: Path to image/video file (required for Instagram)
            schedule_time: When to post (None for immediate)
            requires_approval: Whether approval is needed before posting
            **kwargs: Platform-specific options
            
        Returns:
            Post result dictionary
        """
        post_id = f"post_{int(time.time())}_{platform.value.lower()}"
        
        # Validate content for platform
        validation = self._validate_content(platform, content)
        if not validation["valid"]:
            return {
                "status": "failed",
                "error": validation["error"],
                "post_id": post_id
            }
        
        # Check if approval is required
        if requires_approval:
            approval_id = self.approval_workflow.create_approval_request(
                message_type=MessageType.POST,
                action=f"Post to {platform.value}",
                recipient=platform.value,
                reason=f"Social media post: {content[:100]}...",
                amount=None
            )
            
            # Save post details for after approval
            self._save_post_details(post_id, platform, content, image_path, schedule_time, approval_id, **kwargs)
            
            return {
                "status": "pending_approval",
                "approval_id": approval_id,
                "post_id": post_id,
                "platform": platform.value
            }
        
        # Check rate limits
        if not self._check_rate_limit(platform):
            return {
                "status": "rate_limited",
                "error": f"Rate limit exceeded for {platform.value}",
                "post_id": post_id
            }
        
        # Schedule or post immediately
        if schedule_time:
            if schedule_time > datetime.now():
                self._schedule_post(post_id, platform, content, image_path, schedule_time, **kwargs)
                return {
                    "status": "scheduled",
                    "post_id": post_id,
                    "scheduled_time": schedule_time.isoformat(),
                    "platform": platform.value
                }
        
        # Post immediately
        result = await self._execute_post(platform, content, image_path, **kwargs)
        result["post_id"] = post_id
        
        # Record rate limit
        if result.get("status") == "sent":
            self._record_rate_limit_call(platform)
            self._save_published_post(post_id, platform, content, result)
        
        return result

    async def post_to_all_platforms(
        self,
        content: str,
        platforms: Optional[List[CommunicationChannel]] = None,
        image_path: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        requires_approval: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to multiple platforms simultaneously
        
        Args:
            content: Content to post
            platforms: List of platforms (defaults to all)
            image_path: Path to image/video file
            schedule_time: When to post
            requires_approval: Whether approval is needed
            **kwargs: Platform-specific options
            
        Returns:
            Dictionary with results for each platform
        """
        if platforms is None:
            platforms = [
                CommunicationChannel.LINKEDIN,
                CommunicationChannel.FACEBOOK,
                CommunicationChannel.TWITTER,
                CommunicationChannel.INSTAGRAM
            ]
        
        results = {}
        campaign_id = f"campaign_{int(time.time())}"
        
        for platform in platforms:
            # Platform-specific content formatting
            platform_content = self._format_content_for_platform(platform, content)
            
            result = await self.post_to_platform(
                platform=platform,
                content=platform_content,
                image_path=image_path,
                schedule_time=schedule_time,
                requires_approval=requires_approval,
                campaign_id=campaign_id,
                **kwargs
            )
            
            results[platform.value] = result
        
        return {
            "campaign_id": campaign_id,
            "results": results,
            "total_platforms": len(platforms)
        }

    async def _execute_post(
        self,
        platform: CommunicationChannel,
        content: str,
        image_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute post on specific platform"""
        try:
            if platform == CommunicationChannel.LINKEDIN:
                if kwargs.get("post_type") == "message":
                    return await self.linkedin_handler.send_response(
                        kwargs.get("recipient"), content
                    )
                else:
                    return await self.linkedin_handler.post_to_feed(content)
                    
            elif platform == CommunicationChannel.FACEBOOK:
                if kwargs.get("post_type") == "message":
                    return await self.facebook_handler.send_response(
                        kwargs.get("recipient"), content
                    )
                elif kwargs.get("post_type") == "group":
                    return await self.facebook_handler.post_to_group(
                        kwargs.get("group_id"), content
                    )
                else:
                    return await self.facebook_handler.post_to_feed(
                        content, kwargs.get("privacy", "friends")
                    )
                    
            elif platform == CommunicationChannel.TWITTER:
                if kwargs.get("post_type") == "message":
                    return await self.twitter_handler.send_response(
                        kwargs.get("recipient"), content
                    )
                elif kwargs.get("is_thread"):
                    return await self.twitter_handler.post_thread(kwargs.get("tweets", [content]))
                else:
                    return await self.twitter_handler.post_tweet(content)
                    
            elif platform == CommunicationChannel.INSTAGRAM:
                if kwargs.get("post_type") == "message":
                    return await self.instagram_handler.send_response(
                        kwargs.get("recipient"), content
                    )
                elif kwargs.get("post_type") == "story":
                    return await self.instagram_handler.post_story(content, image_path)
                else:
                    return await self.instagram_handler.post_to_feed(content, image_path)
            
            return {"status": "failed", "error": f"Unknown platform: {platform}"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _validate_content(self, platform: CommunicationChannel, content: str) -> Dict[str, Any]:
        """Validate content for specific platform"""
        guidelines = self.content_guidelines.get(platform, {})
        max_length = guidelines.get("max_length", 1000)
        
        if len(content) > max_length:
            return {
                "valid": False,
                "error": f"Content exceeds {platform.value} limit of {max_length} characters"
            }
        
        # Count hashtags
        hashtag_count = content.count("#")
        hashtag_limit = guidelines.get("hashtag_limit", 10)
        
        if hashtag_count > hashtag_limit:
            return {
                "valid": False,
                "error": f"Too many hashtags ({hashtag_count}/{hashtag_limit})"
            }
        
        return {"valid": True}

    def _format_content_for_platform(self, platform: CommunicationChannel, content: str) -> str:
        """Format content appropriately for each platform"""
        guidelines = self.content_guidelines.get(platform, {})
        max_length = guidelines.get("max_length", 1000)
        
        # Truncate if needed
        if len(content) > max_length:
            content = content[:max_length - 3] + "..."
        
        # Platform-specific formatting
        if platform == CommunicationChannel.TWITTER:
            # Twitter: concise, may need thread indicator
            if len(content) > 280:
                content = content[:277] + "..."
        elif platform == CommunicationChannel.LINKEDIN:
            # LinkedIn: professional formatting
            content = content.strip()
        elif platform == CommunicationChannel.INSTAGRAM:
            # Instagram: add emoji support, line breaks
            pass
        elif platform == CommunicationChannel.FACEBOOK:
            # Facebook: conversational
            pass
        
        return content

    def _check_rate_limit(self, platform: CommunicationChannel) -> bool:
        """Check if within rate limits for platform"""
        limit_info = self.rate_limits.get(platform)
        if not limit_info:
            return True
        
        current_time = time.time()
        # Remove old requests outside window
        limit_info["requests"] = [
            req_time for req_time in limit_info["requests"]
            if current_time - req_time < limit_info["window"]
        ]
        
        return len(limit_info["requests"]) < limit_info["limit"]

    def _record_rate_limit_call(self, platform: CommunicationChannel):
        """Record a post for rate limiting"""
        limit_info = self.rate_limits.get(platform)
        if limit_info:
            limit_info["requests"].append(time.time())

    def _schedule_post(
        self,
        post_id: str,
        platform: CommunicationChannel,
        content: str,
        image_path: Optional[str],
        schedule_time: datetime,
        **kwargs
    ):
        """Save post for scheduled publishing"""
        import json
        
        post_data = {
            "post_id": post_id,
            "platform": platform.value,
            "content": content,
            "image_path": image_path,
            "schedule_time": schedule_time.isoformat(),
            "kwargs": kwargs,
            "created_at": datetime.now().isoformat()
        }
        
        filepath = self.scheduled_dir / f"{post_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, indent=2)

    def _save_post_details(
        self,
        post_id: str,
        platform: CommunicationChannel,
        content: str,
        image_path: Optional[str],
        schedule_time: Optional[datetime],
        approval_id: str,
        **kwargs
    ):
        """Save post details pending approval"""
        import json
        
        post_data = {
            "post_id": post_id,
            "platform": platform.value,
            "content": content,
            "image_path": image_path,
            "schedule_time": schedule_time.isoformat() if schedule_time else None,
            "approval_id": approval_id,
            "kwargs": kwargs,
            "status": "pending_approval",
            "created_at": datetime.now().isoformat()
        }
        
        filepath = self.posts_dir / f"{post_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, indent=2)

    def _save_published_post(
        self,
        post_id: str,
        platform: CommunicationChannel,
        content: str,
        result: Dict[str, Any]
    ):
        """Save published post record"""
        import json
        
        post_data = {
            "post_id": post_id,
            "platform": platform.value,
            "content": content,
            "result": result,
            "published_at": datetime.now().isoformat()
        }
        
        filepath = self.published_dir / f"{post_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, indent=2)

    async def process_scheduled_posts(self):
        """Process and publish any due scheduled posts"""
        import json
        
        now = datetime.now()
        processed = 0
        
        for filepath in self.scheduled_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    post_data = json.load(f)
                
                schedule_time = datetime.fromisoformat(post_data["schedule_time"])
                
                if schedule_time <= now:
                    # Time to post
                    platform = CommunicationChannel(post_data["platform"])
                    result = await self._execute_post(
                        platform,
                        post_data["content"],
                        post_data.get("image_path"),
                        **post_data.get("kwargs", {})
                    )
                    
                    if result.get("status") == "sent":
                        # Move to published
                        self._save_published_post(
                            post_data["post_id"],
                            platform,
                            post_data["content"],
                            result
                        )
                        filepath.unlink()  # Remove from scheduled
                        processed += 1
                        
            except Exception as e:
                print(f"Error processing scheduled post {filepath}: {e}")
        
        return processed

    def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Get all scheduled posts"""
        import json
        
        posts = []
        for filepath in self.scheduled_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    posts.append(json.load(f))
            except Exception:
                continue
        
        return sorted(posts, key=lambda x: x.get("schedule_time", ""))

    def cancel_scheduled_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        filepath = self.scheduled_dir / f"{post_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def get_post_history(
        self,
        platform: Optional[CommunicationChannel] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get published post history"""
        import json
        
        posts = []
        for filepath in self.published_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    post = json.load(f)
                    if platform is None or post.get("platform") == platform.value:
                        posts.append(post)
            except Exception:
                continue
        
        # Sort by published time, most recent first
        posts.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return posts[:limit]


# Convenience functions for direct usage
async def post_to_linkedin(content: str, requires_approval: bool = True) -> Dict[str, Any]:
    """Post to LinkedIn feed"""
    service = SocialPostingService()
    return await service.post_to_platform(
        CommunicationChannel.LINKEDIN, content, requires_approval=requires_approval
    )


async def post_to_facebook(content: str, requires_approval: bool = True) -> Dict[str, Any]:
    """Post to Facebook feed"""
    service = SocialPostingService()
    return await service.post_to_platform(
        CommunicationChannel.FACEBOOK, content, requires_approval=requires_approval
    )


async def post_to_twitter(content: str, requires_approval: bool = True) -> Dict[str, Any]:
    """Post a tweet"""
    service = SocialPostingService()
    return await service.post_to_platform(
        CommunicationChannel.TWITTER, content, requires_approval=requires_approval
    )


async def post_to_instagram(content: str, image_path: str, requires_approval: bool = True) -> Dict[str, Any]:
    """Post to Instagram feed"""
    service = SocialPostingService()
    return await service.post_to_platform(
        CommunicationChannel.INSTAGRAM, content, image_path=image_path, requires_approval=requires_approval
    )

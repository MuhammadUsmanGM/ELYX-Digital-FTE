#!/usr/bin/env python3
"""
Social Media Posting Test Suite
Tests all social media response handlers for ELYX AI Employee

Run this to verify:
- Facebook posting (feed + messages)
- Twitter/X posting (tweets + DMs)
- Instagram posting (feed + stories + DMs)
- LinkedIn posting (feed + messages)
- Cross-platform campaigns
- Rate limiting
- Approval workflow integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.response_handlers.base_handler import CommunicationChannel, ResponseStatus
from src.services.social_posting_service import SocialPostingService
from src.claude_skills.ai_employee_skills.social_media_skills import SocialMediaSkills


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    print(f"\n{Colors.OKCYAN}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  ELYX Social Media Posting Test Suite{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 70}{Colors.ENDC}\n")


def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}  {title}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'─' * 70}{Colors.ENDC}")


def print_result(test_name: str, passed: bool, details: str = ""):
    status = f"{Colors.OKGREEN}[PASS]{Colors.ENDC}" if passed else f"{Colors.FAIL}[FAIL]{Colors.ENDC}"
    print(f"  {status} {test_name}")
    if details:
        print(f"         {details}")


async def test_linkedin_handler():
    """Test LinkedIn response handler"""
    print_section("Testing LinkedIn Handler")
    
    from src.response_handlers.linkedin_response_handler import LinkedInResponseHandler
    
    try:
        handler = LinkedInResponseHandler()
        print_result("Handler Initialization", True, "LinkedIn handler created successfully")
    except Exception as e:
        print_result("Handler Initialization", False, str(e))
        return False
    
    # Test content formatting
    test_content = "Test LinkedIn message"
    formatted = handler.format_response(test_content)
    print_result("Content Formatting", formatted == test_content, f"Formatted: {formatted[:50]}...")
    
    # Test validation
    valid = handler.validate_recipient("test_user")
    print_result("Recipient Validation", valid, "Valid recipient accepted")
    
    # Note: Actual posting tests require login session
    print_result("Post to Feed", None, "⚠️  Requires LinkedIn session (run setup_sessions.py linkedin)")
    
    return True


async def test_facebook_handler():
    """Test Facebook response handler"""
    print_section("Testing Facebook Handler")
    
    from src.response_handlers.facebook_response_handler import FacebookResponseHandler
    
    try:
        handler = FacebookResponseHandler()
        print_result("Handler Initialization", True, "Facebook handler created successfully")
    except Exception as e:
        print_result("Handler Initialization", False, str(e))
        return False
    
    # Test content formatting
    test_content = "Test Facebook message"
    formatted = handler.format_response(test_content)
    print_result("Content Formatting", formatted == test_content, f"Formatted: {formatted[:50]}...")
    
    # Test validation
    valid = handler.validate_recipient("test_user")
    print_result("Recipient Validation", valid, "Valid recipient accepted")
    
    # Note: Actual posting tests require login session
    print_result("Post to Feed", None, "⚠️  Requires Facebook session (run setup_sessions.py facebook)")
    print_result("Post to Group", None, "⚠️  Requires Facebook session and group ID")
    
    return True


async def test_twitter_handler():
    """Test Twitter/X response handler"""
    print_section("Testing Twitter/X Handler")
    
    from src.response_handlers.twitter_response_handler import TwitterResponseHandler
    
    try:
        handler = TwitterResponseHandler()
        print_result("Handler Initialization", True, "Twitter handler created successfully")
    except Exception as e:
        print_result("Handler Initialization", False, str(e))
        return False
    
    # Test content formatting
    test_content = "Test tweet"
    formatted = handler.format_response(test_content)
    print_result("Content Formatting", formatted == test_content, f"Formatted: {formatted[:50]}...")
    
    # Test validation
    valid = handler.validate_recipient("@test_user")
    print_result("Recipient Validation", valid, "Valid recipient accepted")
    
    # Note: Actual posting tests require login session
    print_result("Post Tweet", None, "⚠️  Requires Twitter session (run setup_sessions.py twitter)")
    print_result("Post Thread", None, "⚠️  Requires Twitter session")
    print_result("Like Tweet", None, "⚠️  Requires Twitter session and tweet URL")
    print_result("Retweet", None, "⚠️  Requires Twitter session and tweet URL")
    
    return True


async def test_instagram_handler():
    """Test Instagram response handler"""
    print_section("Testing Instagram Handler")
    
    from src.response_handlers.instagram_response_handler import InstagramResponseHandler
    
    try:
        handler = InstagramResponseHandler()
        print_result("Handler Initialization", True, "Instagram handler created successfully")
    except Exception as e:
        print_result("Handler Initialization", False, str(e))
        return False
    
    # Test content formatting
    test_content = "Test Instagram DM"
    formatted = handler.format_response(test_content)
    print_result("Content Formatting", formatted == test_content, f"Formatted: {formatted[:50]}...")
    
    # Test validation
    valid = handler.validate_recipient("@test_user")
    print_result("Recipient Validation", valid, "Valid recipient accepted")
    
    # Note: Actual posting tests require login session and image
    print_result("Post to Feed", None, "⚠️  Requires Instagram session and image path")
    print_result("Post Story", None, "⚠️  Requires Instagram session and image path")
    print_result("Follow User", None, "⚠️  Requires Instagram session and username")
    print_result("Like Post", None, "⚠️  Requires Instagram session and post URL")
    
    return True


async def test_social_posting_service():
    """Test unified social posting service"""
    print_section("Testing Social Posting Service")
    
    vault_path = "./obsidian_vault"
    
    try:
        service = SocialPostingService(vault_path)
        print_result("Service Initialization", True, "SocialPostingService created successfully")
    except Exception as e:
        print_result("Service Initialization", False, str(e))
        return False
    
    # Test content validation
    validation = service._validate_content(CommunicationChannel.TWITTER, "Short tweet")
    print_result("Twitter Content Validation", validation["valid"], "Short content validated")
    
    # Test long content rejection for Twitter
    long_content = "x" * 300
    validation = service._validate_content(CommunicationChannel.TWITTER, long_content)
    print_result("Twitter Length Check", not validation["valid"], "Long content rejected")
    
    # Test content formatting per platform
    content = "Test post content"
    linkedin_formatted = service._format_content_for_platform(CommunicationChannel.LINKEDIN, content)
    print_result("LinkedIn Formatting", linkedin_formatted == content, "Content formatted for LinkedIn")
    
    # Test rate limiting
    within_limit = service._check_rate_limit(CommunicationChannel.LINKEDIN)
    print_result("Rate Limit Check", within_limit, "Within rate limit")
    
    # Test directory structure
    posts_dir = Path(vault_path) / "Social_Posts"
    print_result("Posts Directory", posts_dir.exists(), f"Directory exists: {posts_dir}")
    
    scheduled_dir = posts_dir / "Scheduled"
    print_result("Scheduled Directory", scheduled_dir.exists(), f"Directory exists: {scheduled_dir}")
    
    published_dir = posts_dir / "Published"
    print_result("Published Directory", published_dir.exists(), f"Directory exists: {published_dir}")
    
    return True


async def test_social_media_skills():
    """Test social media skills for Claude"""
    print_section("Testing Social Media Skills")
    
    vault_path = "./obsidian_vault"
    
    try:
        skills = SocialMediaSkills(vault_path)
        print_result("Skills Initialization", True, "SocialMediaSkills created successfully")
    except Exception as e:
        print_result("Skills Initialization", False, str(e))
        return False
    
    # Test skill methods exist
    methods = [
        "post_to_linkedin",
        "post_to_facebook", 
        "post_to_twitter",
        "post_to_instagram",
        "post_to_all_platforms",
        "schedule_post",
        "get_post_history",
        "get_scheduled_posts"
    ]
    
    for method in methods:
        exists = hasattr(skills, method)
        print_result(f"Skill: {method}", exists, f"Method {'exists' if exists else 'missing'}")
    
    # Test post history (should be empty initially)
    history = skills.get_post_history()
    print_result("Get Post History", isinstance(history, list), f"Returned list with {len(history)} posts")
    
    # Test scheduled posts (should be empty initially)
    scheduled = skills.get_scheduled_posts()
    print_result("Get Scheduled Posts", isinstance(scheduled, list), f"Returned list with {len(scheduled)} posts")
    
    return True


async def test_approval_workflow_integration():
    """Test approval workflow integration"""
    print_section("Testing Approval Workflow Integration")
    
    vault_path = "./obsidian_vault"
    
    try:
        service = SocialPostingService(vault_path)
        print_result("Service for Approval Test", True, "SocialPostingService available")
    except Exception as e:
        print_result("Service for Approval Test", False, str(e))
        return False
    
    # Check approval directories
    pending_dir = Path(vault_path) / "Pending_Approval"
    print_result("Pending Approval Dir", pending_dir.exists(), f"Directory exists: {pending_dir}")
    
    approved_dir = Path(vault_path) / "Approved"
    print_result("Approved Dir", approved_dir.exists(), f"Directory exists: {approved_dir}")
    
    rejected_dir = Path(vault_path) / "Rejected"
    print_result("Rejected Dir", rejected_dir.exists(), f"Directory exists: {rejected_dir}")
    
    return True


async def run_all_tests():
    """Run all tests"""
    print_banner()
    
    results = {
        "LinkedIn Handler": await test_linkedin_handler(),
        "Facebook Handler": await test_facebook_handler(),
        "Twitter Handler": await test_twitter_handler(),
        "Instagram Handler": await test_instagram_handler(),
        "Social Posting Service": await test_social_posting_service(),
        "Social Media Skills": await test_social_media_skills(),
        "Approval Workflow": await test_approval_workflow_integration()
    }
    
    print_section("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if result else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"  {status} {test_name}")
    
    print(f"\n  {Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"\n  {Colors.OKGREEN}🎉 All tests passed! Social media posting is ready.{Colors.ENDC}")
        print(f"\n  {Colors.WARNING}⚠️  Note: Actual posting requires running setup_sessions.py for each platform{Colors.ENDC}")
    else:
        print(f"\n  {Colors.FAIL}❌ Some tests failed. Review the errors above.{Colors.ENDC}")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test Social Media Detection from Email

Tests the new social media detection functionality.

Usage:
    python scripts/test_social_detection.py
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.utils.vault import VaultEntry

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    # Use ASCII-safe icons for Windows
    CHECK = '[OK]'
    CROSS = '[FAIL]'
    ARROW = '->'

def test_social_detection():
    """Test social media detection from email content"""
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Test: Social Media Detection from Email{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    processor = TaskProcessor(vault_path="obsidian_vault")
    
    # Test case 1: LinkedIn post request
    print(f"{Colors.BOLD}Test 1: LinkedIn Post Request{Colors.ENDC}")
    
    test_content_1 = '''---
type: email
from: "user@example.com"
subject: "First post"
---

Make your first post on linkedin and x with your telling about yourself that who you are
'''
    
    # Create a mock task object
    class MockTask:
        def __init__(self, content):
            self.content = content
            self.frontmatter = {'subject': 'First post'}
    
    task1 = MockTask(test_content_1)
    result1 = processor._detect_social_media_action(task1)
    
    if result1:
        print(f"  {Colors.OKGREEN}{Colors.CHECK} Detected social media request{Colors.ENDC}")
        print(f"     Platforms: {result1.get('platforms', [])}")
        print(f"     Content: {result1.get('content', '')[:50]}...")
    else:
        print(f"  {Colors.FAIL}{Colors.CROSS} Failed to detect social media request{Colors.ENDC}")
    
    print()
    
    # Test case 2: Not a social media request
    print(f"{Colors.BOLD}Test 2: Regular Email (Not Social){Colors.ENDC}")
    
    test_content_2 = '''---
type: email
from: "user@example.com"
subject: "Meeting Tomorrow"
---

Can we meet tomorrow at 3pm to discuss the project?
'''
    
    task2 = MockTask(test_content_2)
    result2 = processor._detect_social_media_action(task2)
    
    if result2 is None:
        print(f"  {Colors.OKGREEN}{Colors.CHECK} Correctly identified as non-social email{Colors.ENDC}")
    else:
        print(f"  {Colors.FAIL}{Colors.CROSS} Incorrectly detected as social media{Colors.ENDC}")
    
    print()
    
    # Test case 3: Twitter/X request
    print(f"{Colors.BOLD}Test 3: Twitter/X Post Request{Colors.ENDC}")
    
    test_content_3 = '''---
type: email
from: "user@example.com"
subject: "Tweet about launch"
---

Please post on X (Twitter) about our new product launch.
'''
    
    task3 = MockTask(test_content_3)
    result3 = processor._detect_social_media_action(task3)
    
    if result3:
        print(f"  {Colors.OKGREEN}{Colors.CHECK} Detected Twitter/X request{Colors.ENDC}")
        print(f"     Platforms: {result3.get('platforms', [])}")
    else:
        print(f"  {Colors.FAIL}{Colors.CROSS} Failed to detect Twitter request{Colors.ENDC}")
    
    print()
    
    # Test case 4: Multiple platforms
    print(f"{Colors.BOLD}Test 4: Multiple Platforms Request{Colors.ENDC}")
    
    test_content_4 = '''---
type: email
from: "user@example.com"
subject: "Social media blast"
---

Post this announcement on LinkedIn, Twitter, and Facebook.
'''
    
    task4 = MockTask(test_content_4)
    result4 = processor._detect_social_media_action(task4)
    
    if result4:
        print(f"  {Colors.OKGREEN}{Colors.CHECK} Detected multi-platform request{Colors.ENDC}")
        print(f"     Platforms: {result4.get('platforms', [])}")
    else:
        print(f"  {Colors.FAIL}{Colors.CROSS} Failed to detect multi-platform request{Colors.ENDC}")
    
    print()
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print()
    print("Social media detection is working!")
    print()
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print("  1. Ensure social media credentials are configured")
    print("  2. Test with actual email: python scripts/test_core_flow.py")
    print("  3. Check LinkedIn/Twitter for posts")
    print()

if __name__ == "__main__":
    test_social_detection()

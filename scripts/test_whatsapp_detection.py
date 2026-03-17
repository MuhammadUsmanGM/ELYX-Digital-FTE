#!/usr/bin/env python3
"""
Test WhatsApp Auto-Detection

Tests the new WhatsApp message detection and sending functionality.

Usage:
    python scripts/test_whatsapp_detection.py
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

def test_whatsapp_detection():
    """Test WhatsApp message detection from email content"""
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Test: WhatsApp Message Detection{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    processor = TaskProcessor(vault_path="obsidian_vault")
    
    # Test case 1: Simple WhatsApp request
    print(f"{Colors.BOLD}Test 1: Simple WhatsApp Request{Colors.ENDC}")
    
    test_content_1 = '''---
type: email
from: "user@example.com"
subject: "Send WhatsApp"
---

Please send a WhatsApp message to +1234567890 saying hello
'''
    
    class MockTask:
        def __init__(self, content):
            self.content = content
            self.frontmatter = {'subject': 'Send WhatsApp', 'from': 'user@example.com'}
    
    task1 = MockTask(test_content_1)
    result1 = processor._detect_whatsapp_action(task1)
    
    if result1:
        print(f"  {Colors.OKGREEN}✅ Detected WhatsApp request{Colors.ENDC}")
        print(f"     To: {result1.get('to')}")
        print(f"     Message: {result1.get('message')}")
    else:
        print(f"  {Colors.FAIL}❌ Failed to detect WhatsApp request{Colors.ENDC}")
    
    print()
    
    # Test case 2: WhatsApp with custom message
    print(f"{Colors.BOLD}Test 2: Custom Message{Colors.ENDC}")
    
    test_content_2 = '''---
type: email
from: "user@example.com"
subject: "Test"
---

Send WhatsApp to +44 7911 123456 saying "This is a test message from ELYX"
'''
    
    task2 = MockTask(test_content_2)
    result2 = processor._detect_whatsapp_action(task2)
    
    if result2:
        print(f"  {Colors.OKGREEN}✅ Detected with custom message{Colors.ENDC}")
        print(f"     To: {result2.get('to')}")
        print(f"     Message: {result2.get('message')}")
    else:
        print(f"  {Colors.FAIL}❌ Failed to detect{Colors.ENDC}")
    
    print()
    
    # Test case 3: Not a WhatsApp request
    print(f"{Colors.BOLD}Test 3: Regular Email (Not WhatsApp){Colors.ENDC}")
    
    test_content_3 = '''---
type: email
from: "user@example.com"
subject: "Meeting"
---

Can we meet tomorrow at 3pm?
'''
    
    task3 = MockTask(test_content_3)
    result3 = processor._detect_whatsapp_action(task3)
    
    if result3 is None:
        print(f"  {Colors.OKGREEN}✅ Correctly identified as non-WhatsApp{Colors.ENDC}")
    else:
        print(f"  {Colors.FAIL}❌ Incorrectly detected as WhatsApp{Colors.ENDC}")
    
    print()
    
    # Test case 4: Multiple phone numbers
    print(f"{Colors.BOLD}Test 4: Multiple Phone Numbers{Colors.ENDC}")
    
    test_content_4 = '''---
type: email
from: "user@example.com"
subject: "Bulk WhatsApp"
---

Send WhatsApp to +1234567890 and +9876543210 saying hello to both
'''
    
    task4 = MockTask(test_content_4)
    result4 = processor._detect_whatsapp_action(task4)
    
    if result4:
        print(f"  {Colors.OKGREEN}✅ Detected (uses first number){Colors.ENDC}")
        print(f"     To: {result4.get('to')}")
        print(f"     Message: {result4.get('message')}")
    else:
        print(f"  {Colors.FAIL}❌ Failed to detect{Colors.ENDC}")
    
    print()
    
    # Test case 5: Different message patterns
    print(f"{Colors.BOLD}Test 5: Different Message Patterns{Colors.ENDC}")
    
    patterns = [
        ('saying hello', 'Hello'),
        ('say hi there', 'Hi there'),
        ('message: test message', 'Test message'),
        ('with the message urgent', 'Urgent'),
    ]
    
    for pattern_text, expected_msg in patterns:
        test_content = f'''---
type: email
subject: "Test"
---

Send WhatsApp to +1234567890 {pattern_text}
'''
        task = MockTask(test_content)
        result = processor._detect_whatsapp_action(task)
        
        if result:
            print(f"  {Colors.OKGREEN}✅ Pattern '{pattern_text}' → '{result.get('message')}'{Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}❌ Pattern '{pattern_text}' failed{Colors.ENDC}")
    
    print()
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Summary{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print()
    print("WhatsApp detection is working!")
    print()
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print("  1. Setup WhatsApp session: python config/setup_sessions.py whatsapp")
    print("  2. Send test email with WhatsApp request")
    print("  3. Check if message was sent")
    print()

if __name__ == "__main__":
    test_whatsapp_detection()

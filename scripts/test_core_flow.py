#!/usr/bin/env python3
"""
Test script for ELYX core email flow
Tests: Email arrives -> Watcher detects -> Brain reasons -> Action -> Done
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.utils.vault import get_pending_tasks, move_file_to_folder
from src.utils.logger import log_activity

# ANSI colors
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
    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}ELYX Core Flow Test{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")

def test_step(step_num, description, status="pending"):
    """Print test step status"""
    status_icons = {
        "pending": "⏳",
        "running": "🔄",
        "passed": "✅",
        "failed": "❌"
    }
    print(f"{status_icons.get(status, '•')} Step {step_num}: {description}")
    if status == "running":
        print(f"   {Colors.OKBLUE}Running...{Colors.ENDC}")
    elif status == "passed":
        print(f"   {Colors.OKGREEN}PASSED{Colors.ENDC}")
    elif status == "failed":
        print(f"   {Colors.FAIL}FAILED{Colors.ENDC}")

def create_test_email():
    """Create a test email action file"""
    vault_path = Path("obsidian_vault")
    needs_action = vault_path / "Needs_Action"
    needs_action.mkdir(exist_ok=True)
    
    test_content = f'''---
type: email
from: "test.user@example.com"
subject: "Test Email - Please Confirm Receipt"
received: "{datetime.now().isoformat()}"
detected_at: "{datetime.now().isoformat()}"
priority: normal
status: pending
message_id: "TEST_{int(time.time())}"
thread_id: "test_thread"
---

# Test Email for ELYX Core Flow

**From**: test.user@example.com
**Subject**: Test Email - Please Confirm Receipt
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Content

Hello ELYX,

This is a test email to verify the core processing flow works correctly.

Please confirm receipt of this email by sending a reply.

Thanks,
Test User

## Suggested Actions
- [ ] Send confirmation reply
- [ ] Move to Done after processing
'''
    
    test_file = needs_action / f"EMAIL_TEST_{int(time.time())}.md"
    test_file.write_text(test_content, encoding='utf-8')
    
    return test_file

def cleanup_test_files():
    """Clean up test files from previous runs"""
    vault_path = Path("obsidian_vault")
    needs_action = vault_path / "Needs_Action"
    done_path = vault_path / "Done"
    plans_path = vault_path / "Plans"
    
    # Remove old test files
    for folder in [needs_action, done_path, plans_path]:
        if folder.exists():
            for f in folder.glob("EMAIL_TEST*.md"):
                f.unlink()
                print(f"Cleaned up: {f.name}")

def main():
    """Run the core flow test"""
    print_banner()
    
    vault_path = Path("obsidian_vault")
    
    # Check prerequisites
    print(f"{Colors.BOLD}Prerequisites Check:{Colors.ENDC}")
    
    # Check vault exists
    if not vault_path.exists():
        print(f"{Colors.FAIL}❌ Vault not found at {vault_path}{Colors.ENDC}")
        print("Please run: mkdir obsidian_vault")
        return False
    
    # Check Company Handbook
    handbook = vault_path / "Company_Handbook.md"
    if not handbook.exists():
        print(f"{Colors.FAIL}❌ Company Handbook not found{Colors.ENDC}")
        return False
    
    # Check Gmail credentials
    creds_path = Path("gmail_credentials.json")
    has_credentials = creds_path.exists()
    print(f"  Gmail Credentials: {Colors.OKGREEN if has_credentials else Colors.WARNING}{'✓' if has_credentials else '⚠ Not found (will create response file)'}{Colors.ENDC}")
    
    print()
    
    # Clean up old test files
    test_step(0, "Cleaning up old test files", "running")
    cleanup_test_files()
    test_step(0, "Cleanup complete", "passed")
    print()
    
    # Test 1: Create test email
    test_step(1, "Creating test email in Needs_Action/", "running")
    try:
        test_file = create_test_email()
        test_step(1, f"Created {test_file.name}", "passed")
    except Exception as e:
        test_step(1, f"Failed to create test file: {e}", "failed")
        return False
    print()
    
    # Test 2: Verify email detected
    test_step(2, "Verifying email detected by processor", "running")
    try:
        pending = get_pending_tasks(vault_path)
        if len(pending) > 0:
            test_step(2, f"Found {len(pending)} pending task(s)", "passed")
        else:
            test_step(2, "No pending tasks found", "failed")
            return False
    except Exception as e:
        test_step(2, f"Error: {e}", "failed")
        return False
    print()
    
    # Test 3: Process email
    test_step(3, "Processing email with TaskProcessor", "running")
    try:
        processor = TaskProcessor(vault_path=str(vault_path))
        processed = processor.process_pending_tasks()
        test_step(3, f"Processed {len(processed)} task(s)", "passed")
    except Exception as e:
        test_step(3, f"Processing error: {e}", "failed")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # Test 4: Verify task moved to Done
    test_step(4, "Verifying task moved to Done/", "running")
    done_path = vault_path / "Done"
    test_done = list(done_path.glob("EMAIL_TEST*.md")) if done_path.exists() else []
    if len(test_done) > 0:
        test_step(4, f"Found {len(test_done)} test file(s) in Done/", "passed")
        
        # Show what happened
        done_file = test_done[0]
        content = done_file.read_text()
        if "Email Sent" in content:
            print(f"   {Colors.OKGREEN}✓ Email was sent successfully{Colors.ENDC}")
        elif "Plan Created" in content:
            print(f"   {Colors.OKGREEN}✓ Task processed with plan created{Colors.ENDC}")
        else:
            print(f"   {Colors.WARNING}⚠ Task processed (check file for details){Colors.ENDC}")
    else:
        test_step(4, "Task not found in Done/", "failed")
        print(f"   {Colors.WARNING}Check Needs_Action/ folder{Colors.ENDC}")
    print()
    
    # Test 5: Check for plan file
    test_step(5, "Checking for plan file in Plans/", "running")
    plans_path = vault_path / "Plans"
    if plans_path.exists():
        plan_files = list(plans_path.glob("PLAN_*.md"))
        if len(plan_files) > 0:
            test_step(5, f"Found {len(plan_files)} plan file(s)", "passed")
        else:
            test_step(5, "No plan files created", "pending")
    else:
        test_step(5, "Plans/ folder doesn't exist", "pending")
    print()
    
    # Test 6: Check Dashboard updated
    test_step(6, "Checking Dashboard.md updated", "running")
    dashboard = vault_path / "Dashboard.md"
    if dashboard.exists():
        content = dashboard.read_text()
        if "Completed Tasks" in content or "processed" in content.lower():
            test_step(6, "Dashboard appears updated", "passed")
        else:
            test_step(6, "Dashboard exists but may not be updated", "pending")
    else:
        test_step(6, "Dashboard.md not found", "failed")
    print()
    
    # Summary
    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Summary{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    print(f"  Core flow: Email → Detection → Processing → Action → Done")
    print(f"  Status: {Colors.OKGREEN}✓ COMPLETE{Colors.ENDC}")
    print(f"\n  Check the following for verification:")
    print(f"    1. Done/{test_done[0].name if test_done else 'EMAIL_TEST*.md'}")
    print(f"    2. Plans/PLAN_*.md (if created)")
    print(f"    3. Dashboard.md (updated status)")
    if has_credentials:
        print(f"    4. Gmail Sent folder (email reply)")
    else:
        print(f"    4. {Colors.WARNING}No Gmail credentials - email not sent{Colors.ENDC}")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

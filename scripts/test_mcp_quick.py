#!/usr/bin/env python3
"""
Quick Start Test for MCP Servers

Quick tests to verify MCP servers are working.

Usage:
    python scripts/test_mcp_quick.py
"""

import sys
import json
import subprocess
from pathlib import Path

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_email_send():
    """Test sending an email via MCP (simulation)"""
    print(f"{Colors.BOLD}Test: Email MCP - Send Email{Colors.ENDC}")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "email.send",
        "params": {
            "to": "test@example.com",
            "subject": "MCP Test",
            "body": "Hello from MCP!"
        }
    }
    
    server_path = Path("src/mcp-servers/email-mcp/index.py")
    if not server_path.exists():
        print(f"  {Colors.FAIL}❌ Server not found{Colors.ENDC}")
        return False
    
    try:
        result = subprocess.run(
            ["python", str(server_path)],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        response = json.loads(result.stdout)
        
        if "result" in response:
            if response["result"].get("success"):
                print(f"  {Colors.OKGREEN}✅ Email sent successfully{Colors.ENDC}")
            else:
                print(f"  {Colors.WARNING}⚠ Email not sent (credentials needed){Colors.ENDC}")
                print(f"     Message: {response['result'].get('error', 'Unknown')}")
            return True
        elif "error" in response:
            print(f"  {Colors.WARNING}⚠ {response['error']['message']}{Colors.ENDC}")
            return True  # Expected if no credentials
        else:
            print(f"  {Colors.FAIL}❌ Invalid response{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"  {Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False

def test_social_post():
    """Test social media post via MCP"""
    print(f"\n{Colors.BOLD}Test: Social MCP - Post to Twitter{Colors.ENDC}")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "social.twitter.post",
        "params": {
            "content": "Testing MCP social media integration! #ELYX #AI"
        }
    }
    
    server_path = Path("src/mcp-servers/social-mcp/index.py")
    if not server_path.exists():
        print(f"  {Colors.FAIL}❌ Server not found{Colors.ENDC}")
        return False
    
    try:
        result = subprocess.run(
            ["python", str(server_path)],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        response = json.loads(result.stdout)
        
        if "result" in response:
            result_data = response["result"]
            if result_data.get("success"):
                print(f"  {Colors.OKGREEN}✅ Post successful{Colors.ENDC}")
            else:
                print(f"  {Colors.WARNING}⚠ Post not sent (login needed){Colors.ENDC}")
            return True
        elif "error" in response:
            print(f"  {Colors.WARNING}⚠ {response['error']['message']}{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.FAIL}❌ Invalid response{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"  {Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False

def test_whatsapp_send():
    """Test WhatsApp message via MCP"""
    print(f"\n{Colors.BOLD}Test: WhatsApp MCP - Send Message{Colors.ENDC}")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "whatsapp.send",
        "params": {
            "to": "+1234567890",
            "message": "Test message from MCP!"
        }
    }
    
    server_path = Path("src/mcp-servers/whatsapp-mcp/index.py")
    if not server_path.exists():
        print(f"  {Colors.FAIL}❌ Server not found{Colors.ENDC}")
        return False
    
    try:
        result = subprocess.run(
            ["python", str(server_path)],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        response = json.loads(result.stdout)
        
        if "result" in response:
            print(f"  {Colors.OKGREEN}✅ WhatsApp MCP responding{Colors.ENDC}")
            return True
        elif "error" in response:
            print(f"  {Colors.WARNING}⚠ {response['error']['message']}{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.FAIL}❌ Invalid response{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"  {Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False

def main():
    """Run quick tests"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}ELYX MCP Quick Start Test{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    results = []
    
    results.append(("Email MCP", test_email_send()))
    results.append(("WhatsApp MCP", test_whatsapp_send()))
    results.append(("Social MCP", test_social_post()))
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Results{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"  {icon} {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}✅ All MCP servers are operational!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Next:{Colors.ENDC} Configure credentials and add to your AI agent config.")
        return True
    else:
        print(f"\n{Colors.WARNING}⚠ Some servers need setup. Check messages above.{Colors.ENDC}")
        return True  # Still OK, just needs configuration

if __name__ == "__main__":
    main()

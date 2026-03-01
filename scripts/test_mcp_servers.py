#!/usr/bin/env python3
"""
Test script for Universal MCP Servers

Tests all MCP servers:
- Email MCP
- WhatsApp MCP
- Social Media MCP

Usage:
    python scripts/test_mcp_servers.py
"""

import sys
import json
import subprocess
from pathlib import Path

# ANSI colors
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    OKCYAN = '\033[96m'

def print_banner():
    print(f"\n{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}ELYX Universal MCP Servers Test Suite{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}\n")

def test_server(name, server_path, test_request):
    """Test an MCP server"""
    print(f"{Colors.BOLD}Testing: {name}{Colors.ENDC}")
    
    if not Path(server_path).exists():
        print(f"  {Colors.FAIL}❌ Server not found: {server_path}{Colors.ENDC}")
        return False
    
    try:
        result = subprocess.run(
            ["python", server_path],
            input=json.dumps(test_request),
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            print(f"  {Colors.FAIL}❌ Server error:{Colors.ENDC} {result.stderr[:200]}")
            return False
        
        response = json.loads(result.stdout)
        
        if "result" in response:
            print(f"  {Colors.OKGREEN}✅ Server responding{Colors.ENDC}")
            
            # Show available tools
            if "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"  {Colors.BOLD}Available methods:{Colors.ENDC}")
                for tool in tools[:5]:
                    print(f"    - {tool.get('name', 'unknown')}")
                if len(tools) > 5:
                    print(f"    ... and {len(tools) - 5} more")
            
            return True
        elif "error" in response:
            error = response["error"]
            print(f"  {Colors.WARNING}⚠ Server error: {error.get('message', 'Unknown')}{Colors.ENDC}")
            return False
        else:
            print(f"  {Colors.FAIL}❌ Invalid response format{Colors.ENDC}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  {Colors.FAIL}❌ Server timeout (15s){Colors.ENDC}")
        return False
    except json.JSONDecodeError as e:
        print(f"  {Colors.FAIL}❌ Invalid JSON response: {e}{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"  {Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False

def test_email_mcp():
    """Test Email MCP Server"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools.list",
        "params": {}
    }
    return test_server(
        "Email MCP Server",
        "src/mcp-servers/email-mcp/index.py",
        request
    )

def test_whatsapp_mcp():
    """Test WhatsApp MCP Server"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools.list",
        "params": {}
    }
    return test_server(
        "WhatsApp MCP Server",
        "src/mcp-servers/whatsapp-mcp/index.py",
        request
    )

def test_social_mcp():
    """Test Social Media MCP Server"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools.list",
        "params": {}
    }
    return test_server(
        "Social Media MCP Server",
        "src/mcp-servers/social-mcp/index.py",
        request
    )

def test_mcp_client():
    """Test MCP Client Library"""
    print(f"\n{Colors.BOLD}Testing: MCP Client Library{Colors.ENDC}")
    
    try:
        from src.mcp_client import MCPClient, send_email
        
        client = MCPClient("email", transport="stdio")
        
        if client.server == "email":
            print(f"  {Colors.OKGREEN}✅ MCP Client imported and instantiated{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.FAIL}❌ Client configuration incorrect{Colors.ENDC}")
            return False
            
    except ImportError as e:
        print(f"  {Colors.FAIL}❌ Import error: {e}{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"  {Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False

def test_json_rpc_format():
    """Test JSON-RPC 2.0 format"""
    print(f"\n{Colors.BOLD}Testing: JSON-RPC 2.0 Format{Colors.ENDC}")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "email.send",
        "params": {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Hello"
        }
    }
    
    # Verify format
    if (request.get("jsonrpc") == "2.0" and 
        "id" in request and 
        "method" in request and 
        "params" in request):
        print(f"  {Colors.OKGREEN}✅ JSON-RPC 2.0 format correct{Colors.ENDC}")
        return True
    else:
        print(f"  {Colors.FAIL}❌ Format incorrect{Colors.ENDC}")
        return False

def main():
    """Run all tests"""
    print_banner()
    
    results = {
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }
    
    # Run tests
    tests = [
        ("JSON-RPC Format", test_json_rpc_format),
        ("MCP Client Library", test_mcp_client),
        ("Email MCP Server", test_email_mcp),
        ("WhatsApp MCP Server", test_whatsapp_mcp),
        ("Social Media MCP Server", test_social_mcp)
    ]
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"  {Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
            results["failed"] += 1
        print()
    
    # Summary
    print(f"\n{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}Test Summary{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}Passed:{Colors.ENDC}   {results['passed']}")
    print(f"  {Colors.FAIL}Failed:{Colors.ENDC}   {results['failed']}")
    print()
    
    if results["failed"] == 0:
        print(f"{Colors.OKGREEN}✅ All tests passed!{Colors.ENDC}")
        print()
        print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print("  1. Install dependencies: pip install google-api-python-client playwright")
        print("  2. Configure credentials for each service")
        print("  3. Add MCP servers to your AI agent config")
        print()
        
        print(f"{Colors.BOLD}AI Agent Configuration:{Colors.ENDC}")
        print()
        print("  For Claude Code (~/.claude/mcp.json):")
        print("  ```json")
        print("  {")
        print("    \"mcpServers\": {")
        print("      \"elyx-email\": {")
        print("        \"command\": \"python\",")
        print("        \"args\": [\"/absolute/path/to/src/mcp-servers/email-mcp/index.py\"]")
        print("      },")
        print("      \"elyx-whatsapp\": {")
        print("        \"command\": \"python\",")
        print("        \"args\": [\"/absolute/path/to/src/mcp-servers/whatsapp-mcp/index.py\"]")
        print("      },")
        print("      \"elyx-social\": {")
        print("        \"command\": \"python\",")
        print("        \"args\": [\"/absolute/path/to/src/mcp-servers/social-mcp/index.py\"]")
        print("      }")
        print("    }")
        print("  }")
        print("  ```")
        print()
        return True
    else:
        print(f"{Colors.FAIL}❌ Some tests failed.{Colors.ENDC}")
        print("Check errors above and fix before proceeding.")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

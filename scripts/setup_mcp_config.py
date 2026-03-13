#!/usr/bin/env python3
"""
MCP Server Setup Script

Configures MCP servers for different AI agents:
- Claude Code
- Qwen Coder
- Gemini CLI
- Codex

Usage:
    python scripts/setup_mcp_config.py --agent claude
    python scripts/setup_mcp_config.py --agent all
"""

import sys
import json
import os
from pathlib import Path
import argparse

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    OKCYAN = '\033[96m'

def get_project_root():
    """Get absolute path to project root"""
    return Path(__file__).parent.parent.resolve()

def get_mcp_server_config(server_name):
    """Get MCP server configuration"""
    project_root = get_project_root()
    
    configs = {
        "email": {
            "command": "python",
            "args": [str(project_root / "src" / "mcp-servers" / "email-mcp" / "index.py")],
            "env": {
                "GMAIL_CREDENTIALS_PATH": str(project_root / "gmail_credentials.json")
            }
        },
        "whatsapp": {
            "command": "python",
            "args": [str(project_root / "src" / "mcp-servers" / "whatsapp-mcp" / "index.py")],
            "env": {}
        },
        "social": {
            "command": "python",
            "args": [str(project_root / "src" / "mcp-servers" / "social-mcp" / "index.py")],
            "env": {}
        },
        "fs": {
            "command": "python",
            "args": [str(project_root / "src" / "mcp-servers" / "fs-mcp" / "index.py")],
            "env": {}
        }
    }
    
    return configs.get(server_name, {})

def setup_claude_config():
    """Setup Claude Code MCP configuration"""
    print(f"\n{Colors.BOLD}Setting up Claude Code MCP Configuration{Colors.ENDC}")
    
    # Determine config path
    if os.name == 'nt':  # Windows
        config_dir = Path.home() / ".claude"
    else:  # Linux/Mac
        config_dir = Path.home() / ".claude"
    
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "mcp.json"
    
    # Load existing config or create new
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except Exception:
            config = {"mcpServers": {}}
    else:
        config = {"mcpServers": {}}
    
    # Add ELYX MCP servers
    config["mcpServers"]["elyx-email"] = get_mcp_server_config("email")
    config["mcpServers"]["elyx-whatsapp"] = get_mcp_server_config("whatsapp")
    config["mcpServers"]["elyx-social"] = get_mcp_server_config("social")
    
    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"  {Colors.OKGREEN}✅ Claude MCP config saved to: {config_file}{Colors.ENDC}")
    print(f"\n  {Colors.BOLD}Config file:{Colors.ENDC} {config_file}")
    print(f"  {Colors.BOLD}Restart Claude Code for changes to take effect.{Colors.ENDC}")
    
    return True

def setup_gemini_config():
    """Setup Gemini CLI MCP configuration"""
    print(f"\n{Colors.BOLD}Setting up Gemini CLI MCP Configuration{Colors.ENDC}")
    
    project_root = get_project_root()
    config_file = project_root / "gemini-mcp-config.json"
    
    config = {
        "mcpServers": [
            {
                "name": "elyx-email",
                "type": "stdio",
                "command": "python",
                "args": [str(project_root / "src" / "mcp-servers" / "email-mcp" / "index.py")],
                "env": {
                    "GMAIL_CREDENTIALS_PATH": str(project_root / "gmail_credentials.json")
                }
            },
            {
                "name": "elyx-whatsapp",
                "type": "stdio",
                "command": "python",
                "args": [str(project_root / "src" / "mcp-servers" / "whatsapp-mcp" / "index.py")]
            },
            {
                "name": "elyx-social",
                "type": "stdio",
                "command": "python",
                "args": [str(project_root / "src" / "mcp-servers" / "social-mcp" / "index.py")]
            }
        ]
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"  {Colors.OKGREEN}✅ Gemini MCP config saved to: {config_file}{Colors.ENDC}")
    print(f"\n  {Colors.BOLD}Usage:{Colors.ENDC}")
    print(f"    gemini -p \"Send email...\" --mcp-config {config_file}")
    
    return True

def setup_qwen_config():
    """Setup Qwen Coder MCP configuration"""
    print(f"\n{Colors.BOLD}Setting up Qwen Coder MCP Configuration{Colors.ENDC}")
    
    project_root = get_project_root()
    
    # Create example Python script
    example_file = project_root / "qwen_mcp_example.py"
    
    example_code = f'''#!/usr/bin/env python3
"""
Qwen Coder + MCP Integration Example
"""

from src.mcp_client import MCPClient, send_email, send_whatsapp, post_to_social

# Example 1: Send email
def send_email_example():
    client = MCPClient("email", transport="stdio")
    
    result = client.call("email.send", {{
        "to": "user@example.com",
        "subject": "Hello from Qwen",
        "body": "This email was sent via Universal MCP protocol!"
    }})
    
    print(f"Email sent: {{result}}")

# Example 2: Send WhatsApp
def send_whatsapp_example():
    client = MCPClient("whatsapp", transport="stdio")
    
    result = client.call("whatsapp.send", {{
        "to": "+1234567890",
        "message": "Hello from Qwen!"
    }})
    
    print(f"WhatsApp: {{result}}")

# Example 3: Post to social media
def post_social_example():
    client = MCPClient("social", transport="stdio")
    
    result = client.call("social.twitter.post", {{
        "content": "Posted via MCP! #ELYX #AI"
    }})
    
    print(f"Twitter: {{result}}")

if __name__ == "__main__":
    # Run examples
    send_email_example()
    send_whatsapp_example()
    post_social_example()
'''
    
    with open(example_file, 'w') as f:
        f.write(example_code)
    
    print(f"  {Colors.OKGREEN}✅ Qwen MCP example created: {example_file}{Colors.ENDC}")
    print(f"\n  {Colors.BOLD}Usage:{Colors.ENDC}")
    print(f"    qwen --yolo -p \"Run the MCP example\"")
    print(f"    python {example_file}")
    
    return True

def setup_codex_config():
    """Setup Codex MCP configuration"""
    print(f"\n{Colors.BOLD}Setting up Codex MCP Configuration{Colors.ENDC}")
    
    project_root = get_project_root()
    
    # Create example Python script
    example_file = project_root / "codex_mcp_example.py"
    
    example_code = f'''#!/usr/bin/env python3
"""
Codex + MCP Integration Example
"""

import subprocess
import json

def call_mcp(method, params):
    """Call MCP server via JSON-RPC"""
    request = {{
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }}
    
    result = subprocess.run(
        ["python", "src/mcp-servers/email-mcp/index.py"],
        input=json.dumps(request),
        capture_output=True,
        text=True
    )
    
    response = json.loads(result.stdout)
    
    if "error" in response:
        raise Exception(response["error"]["message"])
    
    return response["result"]

# Example: Send email
result = call_mcp("email.send", {{
    "to": "dev@example.com",
    "subject": "Code Complete",
    "body": "The feature has been implemented."
}})

print(f"Email sent: {{result}}")
'''
    
    with open(example_file, 'w') as f:
        f.write(example_code)
    
    print(f"  {Colors.OKGREEN}✅ Codex MCP example created: {example_file}{Colors.ENDC}")
    print(f"\n  {Colors.BOLD}Usage:{Colors.ENDC}")
    print(f"    codex exec -p \"Run the MCP example\"")
    print(f"    python {example_file}")
    
    return True

def setup_all():
    """Setup all AI agent configurations"""
    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Setting Up All MCP Configurations{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    
    results = []
    
    results.append(("Claude Code", setup_claude_config()))
    results.append(("Gemini CLI", setup_gemini_config()))
    results.append(("Qwen Coder", setup_qwen_config()))
    results.append(("Codex", setup_codex_config()))
    
    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Setup Summary{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"  {icon} {name}")
    
    print(f"\n{Colors.BOLD}All configurations complete!{Colors.ENDC}")
    print(f"\n{Colors.OKGREEN}MCP Servers Available:{Colors.ENDC}")
    print(f"  - Email (Gmail)")
    print(f"  - WhatsApp")
    print(f"  - Social Media (LinkedIn, Twitter, Facebook, Instagram)")
    print(f"\n{Colors.BOLD}Test with:{Colors.ENDC}")
    print(f"  python scripts/test_mcp_quick.py")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Setup MCP server configurations for AI agents"
    )
    parser.add_argument(
        "--agent",
        choices=["claude", "gemini", "qwen", "codex", "all"],
        default="all",
        help="AI agent to configure (default: all)"
    )
    
    args = parser.parse_args()
    
    if args.agent == "all":
        setup_all()
    elif args.agent == "claude":
        setup_claude_config()
    elif args.agent == "gemini":
        setup_gemini_config()
    elif args.agent == "qwen":
        setup_qwen_config()
    elif args.agent == "codex":
        setup_codex_config()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Universal WhatsApp MCP Server
Provides WhatsApp messaging capabilities via JSON-RPC 2.0 protocol

Works with any AI agent: Claude, Qwen, Gemini, Codex

Usage:
    # Via stdio (for AI agents)
    python src/mcp-servers/whatsapp-mcp/index.py
    
    # Direct test
    echo '{"jsonrpc":"2.0","id":1,"method":"whatsapp.send","params":{"to":"+1234567890","message":"Hello"}}' | \
    python src/mcp-servers/whatsapp-mcp/index.py
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Playwright imports for WhatsApp Web automation
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Install with: pip install playwright", file=sys.stderr)


class WhatsAppMCPServer:
    """WhatsApp MCP Server implementation"""
    
    def __init__(self, session_path: str = None, headless: bool = True):
        """
        Initialize WhatsApp MCP Server
        
        Args:
            session_path: Path to store browser session
            headless: Run browser in headless mode
        """
        self.session_path = session_path or os.getenv('WHATSAPP_SESSION_PATH') or 'whatsapp_session'
        self.headless = headless
        self.browser = None
        self.page = None
        self._playwright = None
        
        if not PLAYWRIGHT_AVAILABLE:
            print("Warning: Playwright not available. WhatsApp functions will not work.", file=sys.stderr)
    
    def _ensure_browser(self):
        """Ensure browser is open and WhatsApp Web is loaded"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        if self.browser is None:
            self._playwright = sync_playwright().start()
            self.browser = self._playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox'
                ]
            )
            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        
        return True
    
    def send_message(self, to: str, message: str, is_group: bool = False) -> Dict[str, Any]:
        """Send WhatsApp message"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        try:
            self._ensure_browser()
            
            # Navigate to WhatsApp Web
            self.page.goto('https://web.whatsapp.com', timeout=60000)
            
            # Wait for chat list to load
            try:
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
            except PlaywrightTimeout:
                # Show QR code - user needs to scan
                return {
                    "success": False,
                    "error": "QR_CODE_REQUIRED",
                    "message": "Please scan QR code in WhatsApp Web to authenticate"
                }
            
            # Search for contact
            search_box = self.page.locator('div[contenteditable="true"][data-tab="3"]')
            if search_box:
                search_box.fill(to)
                self.page.keyboard.press('Enter')
            
            # Type and send message
            input_box = self.page.locator('div[contenteditable="true"][data-tab="10"]')
            if input_box:
                input_box.fill(message)
                self.page.keyboard.press('Enter')
                
                return {
                    "success": True,
                    "to": to,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "status": "sent"
                }
            else:
                return {
                    "success": False,
                    "error": "INPUT_NOT_FOUND",
                    "message": "Could not find message input box"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": "SEND_FAILED",
                "message": str(e)
            }
    
    def search_messages(self, query: str, contact: str = None) -> Dict[str, Any]:
        """Search WhatsApp messages"""
        # Simplified implementation - in production would search actual messages
        return {
            "success": True,
            "query": query,
            "contact": contact,
            "results": [],
            "message": "Search not implemented in current version"
        }
    
    def mark_as_read(self, chat_ids: List[str]) -> Dict[str, Any]:
        """Mark chats as read"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        try:
            self._ensure_browser()
            
            marked_count = 0
            for chat_id in chat_ids:
                # Click on chat to mark as read (simplified)
                chat_element = self.page.locator(f'[data-testid="{chat_id}"]')
                if chat_element:
                    chat_element.click()
                    marked_count += 1
            
            return {
                "success": True,
                "marked_count": marked_count,
                "message": f"Marked {marked_count} chat(s) as read"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "MARK_READ_FAILED",
                "message": str(e)
            }
    
    def get_tools(self) -> Dict[str, Any]:
        """Get available tools"""
        return {
            "tools": [
                {
                    "name": "whatsapp.send",
                    "description": "Send WhatsApp message",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Phone number or contact name"},
                            "message": {"type": "string", "description": "Message to send"},
                            "isGroup": {"type": "boolean", "description": "Whether sending to a group"}
                        },
                        "required": ["to", "message"]
                    }
                },
                {
                    "name": "whatsapp.search",
                    "description": "Search WhatsApp messages",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "contact": {"type": "string", "description": "Contact to search in"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "whatsapp.mark_read",
                    "description": "Mark chats as read",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "chat_ids": {"type": "array", "items": {"type": "string"}, "description": "Chat IDs to mark as read"}
                        },
                        "required": ["chat_ids"]
                    }
                }
            ]
        }
    
    def close(self):
        """Close browser connection"""
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()


# JSON-RPC Server Handler

def handle_request(server: WhatsAppMCPServer, request: Dict) -> Dict:
    """Handle JSON-RPC request"""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    try:
        if method == 'tools.list':
            result = server.get_tools()
        elif method == 'whatsapp.send':
            result = server.send_message(
                to=params.get('to'),
                message=params.get('message'),
                is_group=params.get('isGroup', False)
            )
        elif method == 'whatsapp.search':
            result = server.search_messages(
                query=params.get('query', ''),
                contact=params.get('contact')
            )
        elif method == 'whatsapp.mark_read':
            result = server.mark_as_read(
                chat_ids=params.get('chat_ids', [])
            )
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }


def main():
    """Main entry point"""
    print("Starting WhatsApp MCP Server (Python)...", file=sys.stderr)
    
    # Initialize server
    server = WhatsAppMCPServer()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("Warning: Playwright not available. Install with: pip install playwright", file=sys.stderr)
    else:
        print("WhatsApp MCP Server ready", file=sys.stderr)
    
    # Process stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(server, request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {e}"
                }
            }
            print(json.dumps(error_response), flush=True)
    
    # Cleanup
    server.close()


if __name__ == "__main__":
    main()

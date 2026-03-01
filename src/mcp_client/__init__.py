"""
Universal MCP Client for ELYX
Works with any AI agent: Claude, Qwen, Gemini, Codex

Provides JSON-RPC 2.0 communication with MCP servers via stdio or HTTP.
"""

import json
import subprocess
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers"""
    
    def __init__(self, server: str, transport: str = "stdio", 
                 server_path: str = None, http_url: str = None,
                 env: Optional[Dict] = None):
        """
        Initialize MCP client
        
        Args:
            server: Server name (email, whatsapp, social, odoo, fs)
            transport: Transport type (stdio or http)
            server_path: Path to server script (for stdio)
            http_url: HTTP endpoint (for http transport)
            env: Environment variables for server process
        """
        self.server = server
        self.transport = transport
        self.server_path = server_path
        self.http_url = http_url or "http://localhost:8080/rpc"
        self.env = env or {}
        
        # Auto-detect server path if not provided
        if not server_path and transport == "stdio":
            project_root = Path(__file__).parent.parent.parent
            self.server_path = str(project_root / "src" / "mcp-servers" / f"{server}-mcp" / "index.py")
            
            # Fallback to Node.js version if Python not found
            if not Path(self.server_path).exists():
                self.server_path = str(project_root / "src" / "mcp-servers" / f"{server}-mcp" / "index.js")
        
        logger.info(f"MCP Client initialized: {server} via {transport}")
    
    def call(self, method: str, params: Optional[Dict[str, Any]] = None, 
             timeout: int = 30) -> Dict[str, Any]:
        """
        Call MCP server method
        
        Args:
            method: Method name (e.g., "email.send")
            params: Method parameters
            timeout: Request timeout in seconds
            
        Returns:
            Server response result
        """
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        if self.transport == "stdio":
            return self._call_stdio(request, timeout)
        elif self.transport == "http":
            return self._call_http(request, timeout)
        else:
            raise ValueError(f"Unknown transport: {self.transport}")
    
    def _call_stdio(self, request: Dict, timeout: int) -> Dict:
        """Call via stdio"""
        try:
            # Determine if Python or Node.js server
            server_path = Path(self.server_path)
            
            if server_path.suffix == ".py":
                cmd = ["python", str(server_path)]
            else:
                cmd = ["node", str(server_path)]
            
            logger.debug(f"Calling MCP server: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                input=json.dumps(request),
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**self.env}
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or f"Server returned code {result.returncode}"
                logger.error(f"MCP server error: {error_msg}")
                raise RuntimeError(f"MCP server error: {error_msg}")
            
            # Parse response
            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {result.stdout[:200]}")
                raise RuntimeError(f"Invalid JSON response from server: {e}")
            
            if "error" in response:
                error = response["error"]
                error_msg = error.get("message", "Unknown error")
                logger.error(f"MCP error: {error_msg}")
                raise RuntimeError(f"MCP error: {error_msg}")
            
            result_data = response.get("result", {})
            logger.debug(f"MCP call successful: {method}")
            return result_data
            
        except subprocess.TimeoutExpired:
            logger.error(f"MCP call timed out after {timeout}s")
            raise RuntimeError(f"MCP call timed out after {timeout}s")
        except FileNotFoundError as e:
            logger.error(f"Server not found: {self.server_path}")
            raise RuntimeError(f"MCP server not found at {self.server_path}: {e}")
        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            raise
    
    def _call_http(self, request: Dict, timeout: int) -> Dict:
        """Call via HTTP"""
        try:
            response = requests.post(
                self.http_url,
                json=request,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                error = result["error"]
                error_msg = error.get("message", "Unknown error")
                logger.error(f"MCP error: {error_msg}")
                raise RuntimeError(f"MCP error: {error_msg}")
            
            return result.get("result", {})
            
        except requests.exceptions.Timeout:
            logger.error(f"MCP HTTP call timed out after {timeout}s")
            raise RuntimeError(f"HTTP call timed out")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to MCP gateway at {self.http_url}")
            raise RuntimeError(f"Cannot connect to MCP gateway")
        except Exception as e:
            logger.error(f"MCP HTTP call failed: {e}")
            raise
    
    def batch_call(self, calls: List[tuple], timeout: int = 60) -> List[Dict]:
        """
        Make multiple calls in batch
        
        Args:
            calls: List of (method, params) tuples
            timeout: Total timeout for all calls
            
        Returns:
            List of results
        """
        if self.transport == "http":
            # Batch in single HTTP request
            requests_data = [
                {"jsonrpc": "2.0", "id": i, "method": method, "params": params or {}}
                for i, (method, params) in enumerate(calls)
            ]
            
            try:
                response = requests.post(
                    self.http_url,
                    json=requests_data,
                    timeout=timeout,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                results = response.json()
                return [r.get("result") for r in results]
                
            except Exception as e:
                logger.error(f"Batch HTTP call failed: {e}")
                raise
        else:
            # Sequential for stdio
            results = []
            for method, params in calls:
                try:
                    result = self.call(method, params, timeout=timeout // len(calls))
                    results.append(result)
                except Exception as e:
                    logger.error(f"Batch call failed for {method}: {e}")
                    results.append({"error": str(e)})
            return results
    
    def list_tools(self) -> Dict[str, Any]:
        """
        List available tools/methods from server
        
        Returns:
            Dictionary of available methods and their schemas
        """
        try:
            return self.call("tools.list", {})
        except Exception:
            # Fallback: return known methods based on server type
            return self._get_known_tools()
    
    def _get_known_tools(self) -> Dict[str, Any]:
        """Get known tool definitions for each server type"""
        tools = {
            "email": {
                "email.send": {
                    "description": "Send email",
                    "params": ["to", "subject", "body", "isHtml", "cc", "bcc", "attachments"]
                },
                "email.draft": {
                    "description": "Create draft email",
                    "params": ["to", "subject", "body", "isHtml"]
                },
                "email.search": {
                    "description": "Search emails",
                    "params": ["query", "maxResults"]
                }
            },
            "whatsapp": {
                "whatsapp.send": {
                    "description": "Send WhatsApp message",
                    "params": ["to", "message", "isGroup"]
                }
            },
            "social": {
                "social.linkedin.post": {"description": "Post to LinkedIn"},
                "social.twitter.post": {"description": "Post to Twitter"},
                "social.facebook.post": {"description": "Post to Facebook"},
                "social.instagram.post": {"description": "Post to Instagram"}
            },
            "odoo": {
                "odoo.invoice.create": {"description": "Create invoice"},
                "odoo.payment.record": {"description": "Record payment"}
            },
            "fs": {
                "fs.read": {"description": "Read file"},
                "fs.write": {"description": "Write file"},
                "fs.move": {"description": "Move file"}
            }
        }
        
        return tools.get(self.server, {})


# Convenience functions for common operations

def send_email(to: str, subject: str, body: str, **kwargs) -> Dict:
    """Send email via MCP"""
    client = MCPClient("email")
    return client.call("email.send", {
        "to": to,
        "subject": subject,
        "body": body,
        **kwargs
    })


def send_whatsapp(to: str, message: str, **kwargs) -> Dict:
    """Send WhatsApp message via MCP"""
    client = MCPClient("whatsapp")
    return client.call("whatsapp.send", {
        "to": to,
        "message": message,
        **kwargs
    })


def post_to_social(platform: str, content: str, **kwargs) -> Dict:
    """Post to social media via MCP"""
    client = MCPClient("social")
    method = f"social.{platform}.post"
    return client.call(method, {
        "content": content,
        **kwargs
    })


def read_file(path: str) -> str:
    """Read file via MCP"""
    client = MCPClient("fs")
    result = client.call("fs.read", {"path": path})
    return result.get("content", "")


def write_file(path: str, content: str) -> Dict:
    """Write file via MCP"""
    client = MCPClient("fs")
    return client.call("fs.write", {
        "path": path,
        "content": content
    })


__all__ = [
    "MCPClient",
    "send_email",
    "send_whatsapp",
    "post_to_social",
    "read_file",
    "write_file"
]

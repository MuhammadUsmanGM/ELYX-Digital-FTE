#!/usr/bin/env python3
"""
Universal Email MCP Server
Provides Gmail capabilities via JSON-RPC 2.0 protocol

Works with any AI agent: Claude, Qwen, Gemini, Codex

Usage:
    # Via stdio (for AI agents)
    python src/mcp-servers/email-mcp/index.py
    
    # Direct test
    echo '{"jsonrpc":"2.0","id":1,"method":"email.send","params":{"to":"test@example.com","subject":"Test","body":"Hello"}}' | \
    python src/mcp-servers/email-mcp/index.py
"""

import sys
import json
import base64
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from datetime import datetime

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Warning: Google API libraries not installed. Install with: pip install google-api-python-client google-auth-oauthlib", file=sys.stderr)


class EmailMCPServer:
    """Email MCP Server implementation"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize Email MCP Server
        
        Args:
            credentials_path: Path to Gmail OAuth credentials
            token_path: Path to store/load token
        """
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH') or 'gmail_credentials.json'
        self.token_path = token_path or os.getenv('GMAIL_TOKEN_PATH') or 'gmail_token.json'
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Gmail API service"""
        if not GOOGLE_AVAILABLE:
            return
        
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_path):
                try:
                    creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
                except Exception as e:
                    print(f"Warning: Could not load token: {e}", file=sys.stderr)
            
            # Refresh or authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"Warning: Token refresh failed: {e}", file=sys.stderr)
                        creds = None
                
                if not creds and os.path.exists(self.credentials_path):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        print(f"Warning: Authentication failed: {e}", file=sys.stderr)
                elif not os.path.exists(self.credentials_path):
                    print(f"Warning: Gmail credentials not found at {self.credentials_path}", file=sys.stderr)
            
            if creds and creds.valid:
                self.service = build('gmail', 'v1', credentials=creds)
                
                # Save token for next time
                try:
                    with open(self.token_path, 'w') as f:
                        f.write(creds.to_json())
                except Exception as e:
                    print(f"Warning: Could not save token: {e}", file=sys.stderr)
                    
        except Exception as e:
            print(f"Warning: Gmail initialization error: {e}", file=sys.stderr)
    
    def send_email(self, to: str, subject: str, body: str, 
                   is_html: bool = False, cc: List[str] = None, 
                   bcc: List[str] = None, attachments: List[str] = None) -> Dict[str, Any]:
        """Send email via Gmail"""
        if not self.service:
            raise RuntimeError("Gmail service not initialized. Check credentials.")
        
        try:
            # Create message
            message = self._create_message(
                sender="me",
                to=to,
                subject=subject,
                message_text=body,
                message_type="html" if is_html else "plain",
                cc=cc,
                bcc=bcc,
                attachments=attachments
            )
            
            # Send
            sent_message = self.service.users().messages().send(
                userId="me",
                body=message
            ).execute()
            
            return {
                "success": True,
                "message_id": sent_message['id'],
                "thread_id": sent_message['threadId'],
                "status": "sent"
            }
            
        except HttpError as error:
            raise RuntimeError(f"Gmail API error: {error}")
    
    def draft_email(self, to: str, subject: str, body: str,
                    is_html: bool = False) -> Dict[str, Any]:
        """Create draft email"""
        if not self.service:
            raise RuntimeError("Gmail service not initialized")
        
        try:
            message = self._create_message(
                sender="me",
                to=to,
                subject=subject,
                message_text=body,
                message_type="html" if is_html else "plain"
            )
            
            draft = self.service.users().drafts().create(
                userId="me",
                body={'message': message}
            ).execute()
            
            return {
                "success": True,
                "draft_id": draft['id'],
                "message": "Draft created successfully"
            }
            
        except HttpError as error:
            raise RuntimeError(f"Gmail API error: {error}")
    
    def search_emails(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search Gmail"""
        if not self.service:
            raise RuntimeError("Gmail service not initialized")
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get metadata for each message
            emails = []
            for msg in messages:
                try:
                    full = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'To', 'Subject', 'Date']
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in full['payload']['headers']}
                    emails.append({
                        "id": msg['id'],
                        "threadId": msg['threadId'],
                        "from": headers.get('From', ''),
                        "to": headers.get('To', ''),
                        "subject": headers.get('Subject', ''),
                        "date": headers.get('Date', ''),
                        "snippet": full.get('snippet', '')
                    })
                except Exception:
                    continue
            
            return {
                "success": True,
                "count": len(emails),
                "emails": emails
            }
            
        except HttpError as error:
            raise RuntimeError(f"Gmail API error: {error}")
    
    def read_email(self, email_id: str) -> Dict[str, Any]:
        """Read email by ID"""
        if not self.service:
            raise RuntimeError("Gmail service not initialized")
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            payload = message['payload']
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            
            # Get body
            body = ''
            if payload.get('body', {}).get('data'):
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            elif payload.get('parts'):
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and part.get('body', {}).get('data'):
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            
            return {
                "success": True,
                "id": message['id'],
                "threadId": message['threadId'],
                "from": headers.get('From', ''),
                "to": headers.get('To', ''),
                "subject": headers.get('Subject', ''),
                "date": headers.get('Date', ''),
                "body": body,
                "snippet": message.get('snippet', '')
            }
            
        except HttpError as error:
            raise RuntimeError(f"Gmail API error: {error}")
    
    def mark_as_read(self, email_ids: List[str]) -> Dict[str, Any]:
        """Mark emails as read"""
        if not self.service:
            raise RuntimeError("Gmail service not initialized")
        
        try:
            for email_id in email_ids:
                self.service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    requestBody={'removeLabelIds': ['UNREAD']}
                ).execute()
            
            return {
                "success": True,
                "marked_count": len(email_ids),
                "message": f"Marked {len(email_ids)} email(s) as read"
            }
            
        except HttpError as error:
            raise RuntimeError(f"Gmail API error: {error}")
    
    def archive_emails(self, email_ids: List[str]) -> Dict[str, Any]:
        """Archive emails"""
        if not self.service:
            raise RuntimeError("Gmail service not initialized")
        
        try:
            for email_id in email_ids:
                self.service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    requestBody={'removeLabelIds': ['INBOX']}
                ).execute()
            
            return {
                "success": True,
                "archived_count": len(email_ids),
                "message": f"Archived {len(email_ids)} email(s)"
            }
            
        except HttpError as error:
            raise RuntimeError(f"Gmail API error: {error}")
    
    def _create_message(self, sender: str, to: str, subject: str, 
                        message_text: str, message_type: str = "plain",
                        cc: List[str] = None, bcc: List[str] = None,
                        attachments: List[str] = None) -> dict:
        """Create MIME message for Gmail API"""
        if message_type == "html":
            message = MIMEMultipart()
            message.attach(MIMEText(message_text, 'html'))
        else:
            message = MIMEText(message_text)
        
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        # Add CC/BCC
        if cc:
            message['cc'] = ', '.join(cc) if isinstance(cc, list) else cc
        if bcc:
            message['bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc
        
        # Add attachments (with path sandboxing)
        if attachments:
            # Only allow attachments from the project directory or vault
            allowed_roots = [
                Path.cwd().resolve(),
                Path(os.getenv('OBSIDIAN_VAULT_PATH', 'obsidian_vault')).resolve(),
            ]
            for file_path in attachments:
                try:
                    resolved = Path(file_path).resolve()
                    # Verify the file is within an allowed directory
                    if not any(str(resolved).startswith(str(root)) for root in allowed_roots):
                        print(f"Warning: Attachment path outside allowed directories, skipping: {file_path}", file=sys.stderr)
                        continue
                    with open(resolved, "rb") as f:
                        part = MIMEBase('application', "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f"attachment; filename={resolved.name}"
                        )
                        message.attach(part)
                except Exception as e:
                    print(f"Warning: Could not attach {file_path}: {e}", file=sys.stderr)
        
        # Encode
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {'raw': raw_message}
    
    def get_tools(self) -> Dict[str, Any]:
        """Get available tools"""
        return {
            "tools": [
                {
                    "name": "email.send",
                    "description": "Send an email via Gmail",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Recipient email"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"},
                            "isHtml": {"type": "boolean", "description": "Whether body is HTML"},
                            "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"},
                            "bcc": {"type": "array", "items": {"type": "string"}, "description": "BCC recipients"},
                            "attachments": {"type": "array", "items": {"type": "string"}, "description": "Attachment paths"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                },
                {
                    "name": "email.draft",
                    "description": "Create a draft email",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Recipient email"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"},
                            "isHtml": {"type": "boolean", "description": "Whether body is HTML"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                },
                {
                    "name": "email.search",
                    "description": "Search Gmail for emails",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Gmail search query"},
                            "maxResults": {"type": "integer", "description": "Maximum results", "default": 10}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "email.read",
                    "description": "Read email by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "email_id": {"type": "string", "description": "Gmail message ID"}
                        },
                        "required": ["email_id"]
                    }
                },
                {
                    "name": "email.mark_read",
                    "description": "Mark emails as read",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "email_ids": {"type": "array", "items": {"type": "string"}, "description": "Email IDs to mark as read"}
                        },
                        "required": ["email_ids"]
                    }
                },
                {
                    "name": "email.archive",
                    "description": "Archive emails",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "email_ids": {"type": "array", "items": {"type": "string"}, "description": "Email IDs to archive"}
                        },
                        "required": ["email_ids"]
                    }
                }
            ]
        }


# JSON-RPC Server Handler

def handle_request(server: EmailMCPServer, request: Dict) -> Dict:
    """Handle JSON-RPC request"""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    try:
        if method == 'tools.list':
            result = server.get_tools()
        elif method == 'email.send':
            result = server.send_email(
                to=params.get('to'),
                subject=params.get('subject'),
                body=params.get('body'),
                is_html=params.get('isHtml', False),
                cc=params.get('cc'),
                bcc=params.get('bcc'),
                attachments=params.get('attachments')
            )
        elif method == 'email.draft':
            result = server.draft_email(
                to=params.get('to'),
                subject=params.get('subject'),
                body=params.get('body'),
                is_html=params.get('isHtml', False)
            )
        elif method == 'email.search':
            result = server.search_emails(
                query=params.get('query', ''),
                max_results=params.get('maxResults', 10)
            )
        elif method == 'email.read':
            result = server.read_email(
                email_id=params.get('email_id')
            )
        elif method == 'email.mark_read':
            result = server.mark_as_read(
                email_ids=params.get('email_ids', [])
            )
        elif method == 'email.archive':
            result = server.archive_emails(
                email_ids=params.get('email_ids', [])
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
    print("Starting Email MCP Server (Python)...", file=sys.stderr)
    
    # Initialize server
    server = EmailMCPServer()
    
    if not server.service:
        print("Warning: Gmail service not available. Check credentials.", file=sys.stderr)
    else:
        print("Email MCP Server ready", file=sys.stderr)
    
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


if __name__ == "__main__":
    main()

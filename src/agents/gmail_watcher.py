from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from ..base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os
import sys

# Add project root to path for local imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str = None):
        import os
        from src.config.manager import get_config
        
        # Use config for check interval, default to 120s
        check_interval = get_config('check_interval.gmail', 120)
        super().__init__(vault_path, check_interval=check_interval)
        
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH') or get_config('gmail.credentials_path')
        self.creds = None
        self.service = None
        
        if self.credentials_path and os.path.exists(self.credentials_path):
            try:
                self.creds = Credentials.from_authorized_user_file(self.credentials_path)
                self.service = build('gmail', 'v1', credentials=self.creds)
            except Exception as e:
                self.logger.error(f"Failed to initialize Gmail service: {e}")
        else:
            self.logger.warning(f"Gmail credentials not found at {self.credentials_path}")
            
        self.processed_ids = set()

    def check_for_updates(self) -> list:
        if not self.service:
            return []

        try:
            # Check for unread and important messages
            results = self.service.users().messages().list(
                userId='me', q='is:unread is:important'
            ).execute()
            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
        except Exception as e:
            self.logger.error(f"Error checking for Gmail updates: {e}")
            return []

    def create_action_file(self, message) -> Path:
        if not self.service:
            raise Exception("Gmail service not initialized")

        try:
            msg = self.service.users().messages().get(
                userId='me', id=message['id']
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
            sender = headers.get('From', 'Unknown Sender')
            subject = headers.get('Subject', 'No Subject')
            date_sent = headers.get('Date', datetime.now().isoformat())
            snippet = msg.get('snippet', '')
            thread_id = msg.get('threadId', 'unknown')

            content = f'''---
type: email
from: "{sender}"
subject: "{subject}"
received: "{date_sent}"
detected_at: "{datetime.now().isoformat()}"
priority: high
status: pending
message_id: "{message['id']}"
thread_id: "{thread_id}"
---

# New Email from {sender}

**Subject**: {subject}
**Date**: {date_sent}

## Content Snippet
{snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] View full thread {thread_id}
- [ ] Archive after processing
'''
            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
            filepath.write_text(content, encoding='utf-8')
            self.processed_ids.add(message['id'])
            return filepath
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise
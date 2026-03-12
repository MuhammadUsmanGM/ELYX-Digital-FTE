from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest
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
                self._refresh_credentials_if_needed()
                self.service = build('gmail', 'v1', credentials=self.creds)
            except Exception as e:
                self.logger.error(f"Failed to initialize Gmail service: {e}")
        else:
            self.logger.warning(f"Gmail credentials not found at {self.credentials_path}")
            
        self.processed_ids = self._load_processed_ids("gmail")

    def _refresh_credentials_if_needed(self):
        """Refresh OAuth token if expired or about to expire."""
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(GoogleAuthRequest())
                # Persist refreshed token back to disk
                if self.credentials_path:
                    with open(self.credentials_path, 'w') as f:
                        f.write(self.creds.to_json())
                self.logger.info("Gmail OAuth token refreshed successfully")
            except Exception as e:
                self.logger.error(f"Failed to refresh Gmail OAuth token: {e}")

    def check_for_updates(self) -> list:
        if not self.service:
            return []

        try:
            # Refresh token before each check cycle
            self._refresh_credentials_if_needed()

            # Paginate through all unread important messages
            all_messages = []
            page_token = None
            while True:
                kwargs = {'userId': 'me', 'q': 'is:unread is:important', 'maxResults': 100}
                if page_token:
                    kwargs['pageToken'] = page_token
                results = self.service.users().messages().list(**kwargs).execute()
                all_messages.extend(results.get('messages', []))
                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            return [m for m in all_messages if m['id'] not in self.processed_ids]
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
            self._save_processed_ids("gmail", self.processed_ids)
            return filepath
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise
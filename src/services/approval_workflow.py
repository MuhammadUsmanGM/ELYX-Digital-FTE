import os
import uuid
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

class ApprovalStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class MessageType(Enum):
    EMAIL = "EMAIL"
    MESSAGE = "MESSAGE"
    POST = "POST"

class ApprovalWorkflow:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"
        self.rejected_dir = self.vault_path / "Rejected"

        # Create directories if they don't exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)
        self.rejected_dir.mkdir(exist_ok=True)

    @staticmethod
    def _parse_expiration(content: str) -> Optional[datetime]:
        """Parse the 'expires' field from YAML frontmatter. Returns None if missing/malformed."""
        lines = content.split('\n')
        if len(lines) < 3 or lines[0].strip() != '---':
            return None
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                try:
                    fm = yaml.safe_load('\n'.join(lines[1:i])) or {}
                    expires = fm.get('expires')
                    if expires is None:
                        return None
                    if isinstance(expires, datetime):
                        return expires
                    return datetime.fromisoformat(str(expires))
                except (yaml.YAMLError, ValueError, TypeError):
                    return None
        return None

    @staticmethod
    def _sanitize_id(approval_id: str) -> str:
        """Sanitize approval_id to prevent path traversal (#55)."""
        import re
        # Only allow UUID-like characters (alphanumeric and hyphens)
        sanitized = re.sub(r'[^a-zA-Z0-9\-]', '', approval_id)
        if not sanitized or sanitized != approval_id:
            raise ValueError(f"Invalid approval ID: contains disallowed characters")
        return sanitized

    def create_approval_request(
        self,
        message_type: MessageType,
        action: str,
        recipient: str,
        reason: str,
        amount: Optional[float] = None,
        expiration_hours: int = 24
    ) -> str:
        """
        Create an approval request file in the Pending_Approval folder

        Args:
            message_type: Type of message requiring approval
            action: Description of the action requiring approval
            recipient: Target recipient of the action
            reason: Justification for the action
            amount: Amount involved (for financial actions)
            expiration_hours: Hours until approval request expires

        Returns:
            ID of the created approval request
        """
        approval_id = str(uuid.uuid4())  # always safe, but sanitize on read paths
        expiration_time = datetime.now() + timedelta(hours=expiration_hours)

        content = f"""---
type: approval_request
message_type: {message_type.value}
action: {action}
recipient: {recipient}
reason: {reason}
created: {datetime.now().isoformat()}
expires: {expiration_time.isoformat()}
status: pending
"""

        if amount is not None:
            content += f"amount: {amount}\n"

        content += f"""---

## Action Details
- **Action**: {action}
- **Recipient**: {recipient}
- **Reason**: {reason}
"""

        if amount is not None:
            content += f"- **Amount**: ${amount:.2f}\n"

        content += """
## To Approve
Move this file to the /Approved/ folder.

## To Reject
Move this file to the /Rejected/ folder.
"""

        filepath = self.pending_approval_dir / f"APPROVAL_{approval_id}.md"
        filepath.write_text(content)

        return approval_id

    def check_approval_status(self, approval_id: str) -> ApprovalStatus:
        """
        Check the status of an approval request by looking for the file
        in the appropriate folder

        Args:
            approval_id: ID of the approval request to check

        Returns:
            Current status of the approval request
        """
        approval_id = self._sanitize_id(approval_id)
        # Check each folder for the approval file
        pending_file = self.pending_approval_dir / f"APPROVAL_{approval_id}.md"
        approved_file = self.approved_dir / f"APPROVAL_{approval_id}.md"
        rejected_file = self.rejected_dir / f"APPROVAL_{approval_id}.md"

        if approved_file.exists():
            return ApprovalStatus.APPROVED
        elif rejected_file.exists():
            return ApprovalStatus.REJECTED
        elif pending_file.exists():
            # Check if expired
            content = pending_file.read_text()
            expiration = self._parse_expiration(content)
            if expiration is not None and expiration < datetime.now():
                return ApprovalStatus.EXPIRED
            return ApprovalStatus.PENDING
        else:
            # File doesn't exist anywhere, possibly processed
            return ApprovalStatus.EXPIRED

    def move_approval_to_approved(self, approval_id: str) -> bool:
        """
        Move an approval request from pending to approved folder

        Args:
            approval_id: ID of the approval request to approve

        Returns:
            True if successful, False otherwise
        """
        approval_id = self._sanitize_id(approval_id)
        pending_file = self.pending_approval_dir / f"APPROVAL_{approval_id}.md"
        approved_file = self.approved_dir / f"APPROVAL_{approval_id}.md"

        if pending_file.exists():
            pending_file.rename(approved_file)
            return True
        return False

    def move_approval_to_rejected(self, approval_id: str) -> bool:
        """
        Move an approval request from pending to rejected folder

        Args:
            approval_id: ID of the approval request to reject

        Returns:
            True if successful, False otherwise
        """
        approval_id = self._sanitize_id(approval_id)
        pending_file = self.pending_approval_dir / f"APPROVAL_{approval_id}.md"
        rejected_file = self.rejected_dir / f"APPROVAL_{approval_id}.md"

        if pending_file.exists():
            pending_file.rename(rejected_file)
            return True
        return False

    def execute_approved_action(self, approval_id: str) -> bool:
        """
        Execute the action for an approved request

        Args:
            approval_id: ID of the approved action to execute

        Returns:
            True if successful, False otherwise
        """
        approval_id = self._sanitize_id(approval_id)
        approved_file = self.approved_dir / f"APPROVAL_{approval_id}.md"

        if not approved_file.exists():
            return False

        # Read the approval details
        content = approved_file.read_text()

        # Check expiration before executing
        expiration_time = self._parse_expiration(content)
        if expiration_time is not None and expiration_time < datetime.now():
            # Expired — move to rejected folder and refuse execution
            expired_content = content.replace("status: pending", "status: expired")
            rejected_file = self.rejected_dir / f"EXPIRED_APPROVAL_{approval_id}.md"
            rejected_file.write_text(expired_content)
            approved_file.unlink()
            return False

        # Extract action details from YAML frontmatter
        lines = content.split('\n')
        yaml_start = -1
        yaml_end = -1

        for i, line in enumerate(lines):
            if line.strip() == "---":
                if yaml_start == -1:
                    yaml_start = i
                else:
                    yaml_end = i
                    break

        if yaml_start != -1 and yaml_end != -1:
            yaml_block = lines[yaml_start + 1:yaml_end]
            details = {}

            for line in yaml_block:
                if ':' in line:
                    key, value = line.split(':', 1)
                    details[key.strip()] = value.strip()

            # Mark the approval as executed by moving it to Done folder
            done_dir = self.vault_path / "Done"
            done_dir.mkdir(exist_ok=True)
            done_file = done_dir / f"EXECUTED_APPROVAL_{approval_id}.md"

            # Update the status in the content
            executed_content = content.replace("status: pending", "status: executed")
            executed_content = executed_content.replace(
                f"## To Approve\nMove this file to the /Approved/ folder.",
                f"## Status\nThis action has been executed."
            )

            done_file.write_text(executed_content)

            # Remove the approved file
            approved_file.unlink()

            return True

        return False

    def get_pending_approvals(self) -> list:
        """
        Get list of all pending approval requests

        Returns:
            List of approval IDs that are pending
        """
        pending_files = list(self.pending_approval_dir.glob("APPROVAL_*.md"))
        approval_ids = []

        for file in pending_files:
            # Extract approval ID from filename
            approval_id = file.stem.replace("APPROVAL_", "")

            # Check if expired
            content = file.read_text()
            expiration_time = self._parse_expiration(content)
            if expiration_time is not None and expiration_time < datetime.now():
                # Move expired approval to rejected folder
                self.move_approval_to_expired(approval_id)
            else:
                approval_ids.append(approval_id)

        return approval_ids

    def move_approval_to_expired(self, approval_id: str) -> bool:
        """
        Move an expired approval request to the rejected folder

        Args:
            approval_id: ID of the approval request to expire

        Returns:
            True if successful, False otherwise
        """
        approval_id = self._sanitize_id(approval_id)
        pending_file = self.pending_approval_dir / f"APPROVAL_{approval_id}.md"
        rejected_file = self.rejected_dir / f"EXPIRED_APPROVAL_{approval_id}.md"

        if pending_file.exists():
            # Update content to indicate expiration
            content = pending_file.read_text()
            expired_content = content.replace("status: pending", "status: expired")
            rejected_file.write_text(expired_content)
            pending_file.unlink()
            return True
        return False
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

from src.services.communication_channel import ChannelType as CommunicationChannel


class ResponseType(Enum):
    INFORMATIONAL = "INFORMATIONAL"
    ACTION_REQUEST = "ACTION_REQUEST"
    STATUS_UPDATE = "STATUS_UPDATE"
    CONFIRMATION = "CONFIRMATION"
    FEED_POST = "FEED_POST"


class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConversationTracker:
    """
    Service to track conversation context across communication channels
    """
    def __init__(self, vault_path: str = "./obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.conversations_dir = self.vault_path / "Conversations"
        self.conversations_dir.mkdir(exist_ok=True)

    def create_conversation_context(self, original_message_id: str, channel: CommunicationChannel,
                                   original_sender: str, conversation_thread_id: Optional[str] = None,
                                   context_summary: str = "") -> Dict[str, Any]:
        """
        Create a new conversation context record

        Args:
            original_message_id: ID of the original message that started the conversation
            channel: Communication channel of the original message
            original_sender: Identifier of the original sender
            conversation_thread_id: Platform-specific thread identifier
            context_summary: Brief summary of the conversation context

        Returns:
            Dictionary representing the conversation context
        """
        conversation_id = f"conv_{int(time.time())}_{original_message_id[:8]}"

        conversation_context = {
            "id": conversation_id,
            "original_channel": channel.value,
            "original_sender": original_sender,
            "original_message_id": original_message_id,
            "conversation_thread_id": conversation_thread_id or conversation_id,
            "context_summary": context_summary,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "participants": [original_sender],
            "message_count": 1
        }

        # Save to file
        self._save_conversation_context(conversation_id, conversation_context)

        return conversation_context

    def get_conversation_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation context by ID

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Conversation context dictionary or None if not found
        """
        file_path = self.conversations_dir / f"{conversation_id}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading conversation context {conversation_id}: {e}")
            return None

    def update_conversation_context(self, conversation_id: str, **updates) -> bool:
        """
        Update conversation context with new information

        Args:
            conversation_id: ID of the conversation to update
            **updates: Fields to update in the conversation context

        Returns:
            True if update was successful, False otherwise
        """
        context = self.get_conversation_context(conversation_id)
        if not context:
            return False

        # Update with provided fields
        for key, value in updates.items():
            context[key] = value

        # Update last activity
        context["last_activity"] = datetime.now().isoformat()

        # Increment message count if this is a new message
        if "is_new_message" in updates and updates["is_new_message"]:
            context["message_count"] = context.get("message_count", 1) + 1

        # Save updated context
        self._save_conversation_context(conversation_id, context)

        return True

    def _save_conversation_context(self, conversation_id: str, context: Dict[str, Any]):
        """
        Save conversation context to file

        Args:
            conversation_id: ID of the conversation
            context: Conversation context dictionary to save
        """
        file_path = self.conversations_dir / f"{conversation_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)

    def link_response_to_conversation(self, conversation_id: str, response_message_id: str,
                                     response_content: str, sender: str) -> bool:
        """
        Link a response message to a conversation context

        Args:
            conversation_id: ID of the conversation
            response_message_id: ID of the response message
            response_content: Content of the response
            sender: Who sent the response

        Returns:
            True if linking was successful, False otherwise
        """
        context = self.get_conversation_context(conversation_id)
        if not context:
            return False

        # Add response to conversation history
        responses = context.get("responses", [])
        responses.append({
            "id": response_message_id,
            "content": response_content,
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        })
        context["responses"] = responses

        # Update participants if needed
        participants = set(context.get("participants", []))
        participants.add(sender)
        context["participants"] = list(participants)

        # Save updated context
        self._save_conversation_context(conversation_id, context)

        return True

    def find_conversation_by_original_sender(self, original_sender: str, channel: CommunicationChannel) -> Optional[Dict[str, Any]]:
        """
        Find an active conversation by the original sender and channel

        Args:
            original_sender: Identifier of the original sender
            channel: Communication channel

        Returns:
            Conversation context dictionary or None if not found
        """
        # Look through all conversation files
        for file_path in self.conversations_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    context = json.load(f)

                # Check if this is the right conversation
                if (context.get("original_sender") == original_sender and
                    context.get("original_channel") == channel.value and
                    context.get("active", False)):

                    # Check if conversation is still active (not too old)
                    last_activity = datetime.fromisoformat(context["last_activity"])
                    if datetime.now() - last_activity < timedelta(days=30):  # Active within 30 days
                        return context
            except Exception as e:
                print(f"Error reading conversation file {file_path}: {e}")
                continue

        return None

    def deactivate_conversation(self, conversation_id: str) -> bool:
        """
        Mark a conversation as inactive

        Args:
            conversation_id: ID of the conversation to deactivate

        Returns:
            True if deactivation was successful, False otherwise
        """
        return self.update_conversation_context(conversation_id, active=False)

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently active conversations

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversation context dictionaries
        """
        conversations = []

        for file_path in self.conversations_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    context = json.load(f)

                conversations.append(context)
            except Exception as e:
                print(f"Error reading conversation file {file_path}: {e}")
                continue

        # Sort by last activity (most recent first) and return limited results
        conversations.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        return conversations[:limit]

    def cleanup_inactive_conversations(self, days_old: int = 30) -> int:
        """
        Remove conversation contexts that have been inactive for specified days

        Args:
            days_old: Number of days after which to clean up inactive conversations

        Returns:
            Number of conversations cleaned up
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_up = 0

        for file_path in self.conversations_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    context = json.load(f)

                # Check if conversation is inactive and old
                if not context.get("active", True):
                    last_activity = datetime.fromisoformat(context["last_activity"])
                    if last_activity < cutoff_date:
                        file_path.unlink()  # Delete the file
                        cleaned_up += 1
            except Exception as e:
                print(f"Error processing conversation file {file_path}: {e}")
                continue

        return cleaned_up
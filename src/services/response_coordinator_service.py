"""
Response Coordinator Service - Orchestrates response sending across all channels
"""
import asyncio
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from src.services.response_coordinator import ResponseCoordinator
from src.response_handlers.base_handler import CommunicationChannel, ResponseStatus
from src.services.conversation_tracker import ConversationTracker, ResponseType, Priority
from src.services.approval_workflow import ApprovalWorkflow, MessageType


class ResponseCoordinatorService:
    """
    Service layer that coordinates the response coordinator with the orchestrator
    """
    def __init__(self, vault_path: str = "./obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.response_coordinator = ResponseCoordinator(vault_path=vault_path)
        self.conversation_tracker = ConversationTracker(vault_path)
        self.approval_workflow = ApprovalWorkflow(vault_path)

        # Response queue for async processing
        self.response_queue = asyncio.Queue()

        # Set up logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Rate limiting tracking
        self.rate_limits = {
            CommunicationChannel.EMAIL: {"requests": [], "limit": 250, "window": 86400},  # 250/day for Gmail
            CommunicationChannel.LINKEDIN: {"requests": [], "limit": 100, "window": 3600},  # 100/hour estimate
            CommunicationChannel.WHATSAPP: {"requests": [], "limit": 50, "window": 3600},  # 50/hour estimate
            CommunicationChannel.FACEBOOK: {"requests": [], "limit": 50, "window": 3600},  # 50/hour
            CommunicationChannel.TWITTER: {"requests": [], "limit": 2400, "window": 86400},  # 2400/day
            CommunicationChannel.INSTAGRAM: {"requests": [], "limit": 25, "window": 3600},  # 25/hour
        }

    async def queue_response(
        self,
        original_message_id: str,
        channel: CommunicationChannel,
        recipient_identifier: str,
        content: str,
        response_type: ResponseType = ResponseType.INFORMATIONAL,
        priority: Priority = Priority.MEDIUM,
        requires_approval: bool = False,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Queue a response to be sent to the specified recipient

        Args:
            original_message_id: ID of the original message that triggered this response
            channel: Communication channel to send the response through
            recipient_identifier: Platform-specific identifier for the recipient
            content: Content of the response message
            response_type: Type of response
            priority: Priority level of the response
            requires_approval: Whether this response requires approval before sending
            subject: Subject for email responses (optional)

        Returns:
            Dictionary with response details and status
        """
        response_id = f"resp_{int(time.time())}_{original_message_id[:8]}"

        # Check if approval is required based on content or configuration
        if requires_approval or self._requires_approval(content, response_type):
            # Create approval request
            approval_id = self.approval_workflow.create_approval_request(
                message_type=MessageType.MESSAGE,
                action=f"Send {response_type.value} response via {channel.value}",
                recipient=recipient_identifier,
                reason=f"Response to message {original_message_id}: {content[:100]}...",
                amount=None
            )

            return {
                "id": response_id,
                "status": ResponseStatus.APPROVAL_REQUIRED.value,
                "approval_id": approval_id,
                "queued_at": time.time(),
                "channel": channel.value,
                "recipient": recipient_identifier
            }

        # Check rate limits before queuing
        if not self._check_rate_limit(channel):
            return {
                "id": response_id,
                "status": ResponseStatus.FAILED.value,
                "error": "Rate limit exceeded",
                "queued_at": time.time()
            }

        # Create response message object
        response_message = {
            "id": response_id,
            "original_message_id": original_message_id,
            "channel": channel,
            "recipient_identifier": recipient_identifier,
            "content": content,
            "response_type": response_type,
            "priority": priority,
            "status": ResponseStatus.QUEUED.value,
            "subject": subject,
            "queued_at": time.time()
        }

        # Add to queue
        await self.response_queue.put(response_message)

        # Track in conversation context
        conversation = self.conversation_tracker.find_conversation_by_original_sender(
            recipient_identifier, channel
        )

        if conversation:
            self.conversation_tracker.link_response_to_conversation(
                conversation["id"],
                response_id,
                content,
                "AI_Employee"
            )
        else:
            # Create new conversation context if none exists
            self.conversation_tracker.create_conversation_context(
                original_message_id,
                channel,
                recipient_identifier,
                context_summary=f"Response to: {content[:100]}..."
            )

        return {
            "id": response_id,
            "status": ResponseStatus.QUEUED.value,
            "queued_at": time.time(),
            "channel": channel.value,
            "recipient": recipient_identifier
        }

    def get_response_status(self, response_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific response

        Args:
            response_id: ID of the response to check

        Returns:
            Dictionary with response status or None if not found
        """
        # This would interface with a database or file system to track response statuses
        # For now, we'll return a placeholder
        return self.response_coordinator.get_response_status(response_id)

    async def process_response_queue(self):
        """
        Process responses in the queue asynchronously
        """
        while True:
            try:
                # Get next response from queue
                response_message = await self.response_queue.get()

                # Send the response
                result = await self._send_response_now(response_message)

                # Update response status
                response_message["status"] = result.get("status", ResponseStatus.FAILED.value)
                response_message["sent_at"] = time.time()

                # Add to rate limit tracking
                self._record_rate_limit_call(response_message["channel"])

                # Mark task as done
                self.response_queue.task_done()

            except Exception as e:
                print(f"Error processing response queue: {e}")
                await asyncio.sleep(1)  # Brief pause before continuing

    async def _send_response_now(self, response_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a response immediately using the appropriate handler

        Args:
            response_message: Response message object to send

        Returns:
            Dictionary with send result
        """
        channel = response_message["channel"]
        recipient = response_message["recipient_identifier"]
        content = response_message["content"]
        subject = response_message.get("subject")

        try:
            response_type = response_message.get("response_type")
            if channel == CommunicationChannel.EMAIL:
                result = await self.response_coordinator.email_handler.send_response(
                    recipient, content, subject=subject or "Response from AI Employee"
                )
            elif channel == CommunicationChannel.LINKEDIN:
                if response_type == ResponseType.FEED_POST:
                    result = await self.response_coordinator.linkedin_handler.post_to_feed(content)
                else:
                    result = await self.response_coordinator.linkedin_handler.send_response(recipient, content)
            elif channel == CommunicationChannel.WHATSAPP:
                result = await self.response_coordinator.whatsapp_handler.send_response(recipient, content)
            elif channel == CommunicationChannel.FACEBOOK:
                if response_type == ResponseType.FEED_POST:
                    result = await self.response_coordinator.facebook_handler.post_to_feed(content)
                else:
                    result = await self.response_coordinator.facebook_handler.send_response(recipient, content)
            elif channel == CommunicationChannel.TWITTER:
                if response_type == ResponseType.FEED_POST:
                    result = await self.response_coordinator.twitter_handler.post_tweet(content)
                else:
                    result = await self.response_coordinator.twitter_handler.send_response(recipient, content)
            elif channel == CommunicationChannel.INSTAGRAM:
                if response_type == ResponseType.FEED_POST:
                    result = await self.response_coordinator.instagram_handler.post_to_feed(
                        content, response_message.get("image_path")
                    )
                else:
                    result = await self.response_coordinator.instagram_handler.send_response(recipient, content)
            else:
                raise ValueError(f"Unsupported communication channel: {channel}")

            return result

        except Exception as e:
            return await self._handle_send_error(response_message, e)

    def _requires_approval(self, content: str, response_type: ResponseType) -> bool:
        """
        Determine if a response requires approval based on content or type

        Args:
            content: Content of the response
            response_type: Type of response

        Returns:
            True if approval is required, False otherwise
        """
        # Check for sensitive keywords
        sensitive_keywords = [
            'payment', 'money', 'financial', 'contract', 'agreement', 'legal',
            'confidential', 'secret', 'private', 'salary', 'compensation'
        ]

        content_lower = content.lower()
        has_sensitive_words = any(word in content_lower for word in sensitive_keywords)

        # Certain response types always require approval
        approval_required_types = [
            ResponseType.ACTION_REQUEST
        ]

        return has_sensitive_words or response_type in approval_required_types

    def _check_rate_limit(self, channel: CommunicationChannel) -> bool:
        """
        Check if we're within rate limits for the specified channel

        Args:
            channel: Communication channel to check

        Returns:
            True if within limits, False if exceeded
        """
        limit_info = self.rate_limits[channel]
        current_time = time.time()

        # Remove old requests outside the time window
        limit_info["requests"] = [
            req_time for req_time in limit_info["requests"]
            if current_time - req_time < limit_info["window"]
        ]

        # Check if we're under the limit
        return len(limit_info["requests"]) < limit_info["limit"]

    def _record_rate_limit_call(self, channel: CommunicationChannel):
        """
        Record a call for rate limiting purposes

        Args:
            channel: Communication channel of the call
        """
        limit_info = self.rate_limits[channel]
        limit_info["requests"].append(time.time())

    async def _handle_send_error(self, response_message: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Handle errors during response sending

        Args:
            response_message: The response message that failed
            error: The error that occurred

        Returns:
            Dictionary with error details
        """
        print(f"Error sending response: {error}")
        return {
            "status": ResponseStatus.FAILED.value,
            "error": str(error),
            "timestamp": time.time(),
            "recipient": response_message.get("recipient_identifier", "unknown")
        }
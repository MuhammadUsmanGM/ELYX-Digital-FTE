import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class CommunicationChannel(Enum):
    EMAIL = "EMAIL"
    LINKEDIN = "LINKEDIN"
    WHATSAPP = "WHATSAPP"
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"
    INSTAGRAM = "INSTAGRAM"


class ResponseStatus(Enum):
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class BaseResponseHandler(ABC):
    """
    Abstract base class for response handlers across different communication channels
    """
    def __init__(self, channel: CommunicationChannel):
        self.channel = channel
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def send_response(self, recipient_identifier: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Send a response to the specified recipient

        Args:
            recipient_identifier: Platform-specific identifier for the recipient
            content: Content of the response message
            **kwargs: Additional platform-specific parameters

        Returns:
            Dictionary containing response details and status
        """
        pass

    @abstractmethod
    def validate_recipient(self, recipient_identifier: str) -> bool:
        """
        Validate that the recipient identifier is valid for this channel

        Args:
            recipient_identifier: Platform-specific identifier for the recipient

        Returns:
            True if valid, False otherwise
        """
        pass

    def format_response(self, content: str, response_format: Optional[str] = None) -> str:
        """
        Format the response content appropriately for the channel

        Args:
            content: Raw content to format
            response_format: Specific format to apply (optional)

        Returns:
            Formatted content string
        """
        # Default formatting - can be overridden by subclasses
        return content.strip()

    async def handle_error(self, error: Exception, recipient_identifier: str, content: str) -> Dict[str, Any]:
        """
        Handle errors during response sending

        Args:
            error: The exception that occurred
            recipient_identifier: Recipient identifier
            content: Content that was being sent

        Returns:
            Dictionary with error details and status
        """
        self.logger.error(f"Error sending {self.channel.value} response to {recipient_identifier}: {str(error)}")
        return {
            "status": ResponseStatus.FAILED.value,
            "error": str(error),
            "timestamp": time.time(),
            "recipient": recipient_identifier
        }

    def log_response_attempt(self, recipient_identifier: str, content: str, status: ResponseStatus):
        """
        Log the response attempt for audit purposes

        Args:
            recipient_identifier: Recipient identifier
            content: Content that was sent
            status: Status of the response attempt
        """
        self.logger.info(f"Response attempt to {recipient_identifier} via {self.channel.value}: {status.value}")
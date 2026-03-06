import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class ChannelType(Enum):
    EMAIL = "EMAIL"
    LINKEDIN = "LINKEDIN"
    WHATSAPP = "WHATSAPP"
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"
    INSTAGRAM = "INSTAGRAM"

# Alias — drop-in replacement for src.response_handlers.base_handler.CommunicationChannel
CommunicationChannelEnum = ChannelType

class ResponseStatus(Enum):
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"

class CommunicationChannel(ABC):
    def __init__(self, name: str, channel_type: ChannelType, status: str = "ACTIVE"):
        self.id = f"{name}_{int(time.time())}"
        self.name = name
        self.type = channel_type
        self.status = status
        self.created_at = time.time()
        self.updated_at = time.time()
        self.rate_limits = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the communication platform"""
        pass

    @abstractmethod
    def send_message(self, recipient: str, content: str, subject: Optional[str] = None) -> Dict[str, Any]:
        """Send a message through this channel"""
        pass

    @abstractmethod
    def receive_messages(self) -> list:
        """Receive messages from this channel"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to the communication platform"""
        pass

    def update_status(self, new_status: str):
        """Update the status of the communication channel"""
        self.status = new_status
        self.updated_at = time.time()

    def check_rate_limit(self) -> bool:
        """Check if rate limits are exceeded"""
        # Implement rate limiting logic
        return True  # Placeholder - implement actual rate limiting

    def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log communication activity for auditing"""
        log_entry = {
            "timestamp": time.time(),
            "channel_id": self.id,
            "activity_type": activity_type,
            "details": details
        }
        self.logger.info(f"Activity log: {log_entry}")
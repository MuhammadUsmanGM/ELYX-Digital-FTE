"""
Response models for communication API
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class CommunicationChannel(str, Enum):
    """
    Communication channels supported by the AI employee
    """
    EMAIL = "EMAIL"
    LINKEDIN = "LINKEDIN"
    WHATSAPP = "WHATSAPP"
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"
    INSTAGRAM = "INSTAGRAM"


class ResponseType(str, Enum):
    """
    Types of responses that can be sent
    """
    INFORMATIONAL = "INFORMATIONAL"
    ACTION_REQUEST = "ACTION_REQUEST"
    CONFIRMATION = "CONFIRMATION"
    STATUS_UPDATE = "STATUS_UPDATE"
    FEED_POST = "FEED_POST"


class Priority(str, Enum):
    """
    Priority levels for responses
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ResponseStatus(str, Enum):
    """
    Status of a response
    """
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class SendResponseRequest(BaseModel):
    """
    Request model for sending a response
    """
    original_message_id: str = Field(..., description="ID of the original message that triggered this response")
    channel: CommunicationChannel = Field(..., description="Channel to send the response through")
    recipient_identifier: str = Field(..., description="Platform-specific identifier for the recipient")
    content: str = Field(..., description="Content of the response message")
    response_type: ResponseType = Field(ResponseType.INFORMATIONAL, description="Type of response")
    priority: Priority = Field(Priority.MEDIUM, description="Priority level of the response")
    requires_approval: bool = Field(False, description="Whether this response requires approval before sending")
    subject: Optional[str] = Field(None, description="Subject for email responses")


class SendResponseResponse(BaseModel):
    """
    Response model for send response operation
    """
    id: str = Field(..., description="Unique ID of the response")
    status: ResponseStatus = Field(..., description="Current status of the response")
    queued_at: str = Field(..., description="Timestamp when response was queued")
    channel: CommunicationChannel = Field(..., description="Channel the response was sent through")
    recipient: str = Field(..., description="Recipient identifier")


class ResponseStatusResponse(BaseModel):
    """
    Response model for getting response status
    """
    id: str = Field(..., description="ID of the response")
    status: ResponseStatus = Field(..., description="Current status of the response")
    timestamp: str = Field(..., description="Timestamp of the status")


class ConversationContextResponse(BaseModel):
    """
    Response model for conversation context
    """
    id: str = Field(..., description="Unique ID of the conversation")
    original_channel: CommunicationChannel = Field(..., description="Original channel of the conversation")
    original_sender: str = Field(..., description="Original sender identifier")
    context_summary: str = Field(..., description="Summary of the conversation context")
    created_at: str = Field(..., description="When the conversation was started")
    last_activity: str = Field(..., description="When the last activity occurred")
    participants: List[str] = Field(..., description="List of participants in the conversation")
    message_count: int = Field(..., description="Total number of messages in the conversation")
    active: bool = Field(..., description="Whether the conversation is still active")


class ConversationSummary(BaseModel):
    """
    Summary of a conversation for listing purposes
    """
    id: str = Field(..., description="Unique ID of the conversation")
    original_channel: CommunicationChannel = Field(..., description="Original channel of the conversation")
    original_sender: str = Field(..., description="Original sender identifier")
    last_message: str = Field(..., description="Preview of the last message")
    last_timestamp: str = Field(..., description="When the last message was received")
    unread_count: int = Field(..., description="Number of unread messages")
    active: bool = Field(..., description="Whether the conversation is still active")
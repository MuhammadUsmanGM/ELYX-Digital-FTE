"""
Communication API routes for AI Employee response system.
Uses the unified sender (direct_social_sender) for all platforms.
"""
import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Dict, Any
from datetime import datetime

from src.services.communication_channel import ChannelType, ResponseStatus
from src.services.conversation_tracker import ConversationTracker, ResponseType, Priority
from src.api.models.response_models import (
    SendResponseRequest,
    SendResponseResponse,
    ResponseStatusResponse,
    ConversationContextResponse,
    CommunicationChannel,
    ResponseType,
    Priority,
    ResponseStatus,
)

communication_router = APIRouter(prefix="/communication", tags=["communication"])


async def _verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Verify API key for communication endpoints that send messages."""
    expected_key = os.getenv("ELYX_API_KEY", "")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key not configured on server (set ELYX_API_KEY env var)",
        )
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


def _get_vault_path() -> str:
    from src.config.manager import get_config
    config = get_config()
    return config.get("vault_path", "./obsidian_vault")


@communication_router.post("/send-response", response_model=SendResponseResponse)
async def send_response(request: SendResponseRequest, _key=Depends(_verify_api_key)):
    """Send a response through the unified sender."""
    try:
        from src.services.direct_social_sender import send_message

        channel = request.channel.value if hasattr(request.channel, 'value') else str(request.channel)
        result = send_message(
            platform=channel.lower(),
            recipient=request.recipient_identifier,
            content=request.content,
            subject=request.subject,
        )

        resp_status = "SENT" if result.get("success") else "FAILED"
        return SendResponseResponse(
            id=f"msg_{int(datetime.now().timestamp())}",
            status=ResponseStatus[resp_status],
            queued_at=datetime.now().isoformat(),
            channel=request.channel,
            recipient=request.recipient_identifier,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error sending response: {e}")


@communication_router.post("/send-direct", response_model=SendResponseResponse)
async def send_direct_response(request: SendResponseRequest, _key=Depends(_verify_api_key)):
    """Send a response directly (same as send-response — unified sender is always direct)."""
    return await send_response(request)


@communication_router.get("/conversation/{conversation_id}", response_model=ConversationContextResponse)
async def get_conversation_context(conversation_id: str):
    """Get context for a conversation."""
    try:
        tracker = ConversationTracker(_get_vault_path())
        context = tracker.get_conversation_context(conversation_id)
        if not context:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Conversation {conversation_id} not found")
        return ConversationContextResponse(
            id=context.get("id"),
            original_channel=context.get("original_channel"),
            original_sender=context.get("original_sender"),
            context_summary=context.get("context_summary"),
            created_at=context.get("created_at"),
            last_activity=context.get("last_activity"),
            participants=context.get("participants", []),
            message_count=context.get("message_count", 0),
            active=context.get("active", True),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error getting conversation context: {e}")


@communication_router.get("/conversations", response_model=Dict[str, Any])
async def get_active_conversations():
    """Get list of active conversations."""
    try:
        tracker = ConversationTracker(_get_vault_path())
        conversations = tracker.get_recent_conversations(limit=50)
        return {
            "conversations": conversations,
            "total_count": len(conversations),
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error getting conversations: {e}")

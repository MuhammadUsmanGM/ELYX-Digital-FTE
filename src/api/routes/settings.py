from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...services.database import get_db, UserPreference
from ...services.preference_service import UserPreferenceService

router = APIRouter(prefix="/settings", tags=["settings"])

class OnboardingRequest(BaseModel):
    user_id: str = "default_user"
    anthropic_key: Optional[str] = None
    selected_channels: List[str] = []
    timezone: Optional[str] = "UTC"

class SettingsResponse(BaseModel):
    success: bool
    onboarded: bool
    updated_at: datetime

@router.post("/onboard", response_model=SettingsResponse)
async def complete_onboarding(request: OnboardingRequest, db: Session = Depends(get_db)):
    """
    Complete the onboarding process for a user
    """
    try:
        pref_service = UserPreferenceService(db)
        
        # Save Anthropic Key if provided (in a real app, this should be encrypted)
        if request.anthropic_key:
            pref_service.set_preference(
                request.user_id, 
                "anthropic_api_key", 
                request.anthropic_key,
                category="api_keys"
            )
        
        # Save Selected Channels
        pref_service.set_preference(
            request.user_id,
            "active_channels",
            request.selected_channels,
            category="integrations"
        )
        
        # Set onboarded flag
        pref_service.set_preference(
            request.user_id,
            "onboarding_complete",
            True,
            category="system"
        )
        
        return SettingsResponse(
            success=True,
            onboarded=True,
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save onboarding data"
        )

@router.get("/status/{user_id}", response_model=Dict[str, Any])
async def get_onboarding_status(user_id: str, db: Session = Depends(get_db)):
    """
    Check if a user has completed onboarding
    """
    pref_service = UserPreferenceService(db)
    onboarded = pref_service.get_preference(user_id, "onboarding_complete", category="system")
    
    return {
        "user_id": user_id,
        "onboarded": onboarded if onboarded is not None else False
    }

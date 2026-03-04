"""
User and Team Management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ...services.database import get_db_session, TeamMember
from ..api_models import TeamMemberResponse, TeamMemberCreateRequest

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[TeamMemberResponse])
async def get_team_members(db: Session = Depends(get_db_session)):
    """
    Get all team members
    """
    members = db.query(TeamMember).all()
    if not members:
        # Seed some data if empty for the hackathon showcase
        seed_members = [
            TeamMember(
                name="Usman Mustafa",
                email="usman@elyx.ai",
                role="Neural Architect",
                status="active",
                permissions=["admin", "neural_core_access", "reality_manipulation"],
                avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Usman"
            ),
            TeamMember(
                name="Sarah Chen",
                email="sarah@elyx.ai",
                role="Logic Operator",
                status="active",
                permissions=["task_management", "temporal_audit"],
                avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"
            ),
            TeamMember(
                name="Marcus Vane",
                email="marcus@elyx.ai",
                role="Strategic Analyst",
                status="active",
                permissions=["analytics_view", "business_logic"],
                avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=Marcus"
            )
        ]
        for m in seed_members:
            db.add(m)
        db.commit()
        members = db.query(TeamMember).all()
        
    return members

@router.post("/", response_model=TeamMemberResponse)
async def add_team_member(request: TeamMemberCreateRequest, db: Session = Depends(get_db_session)):
    """
    Add a new team member
    """
    new_member = TeamMember(
        name=request.name,
        email=request.email,
        role=request.role,
        status=request.status,
        permissions=request.permissions,
        avatar=request.avatar or f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.name}"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(user_id: str, db: Session = Depends(get_db_session)):
    """
    Remove a team member
    """
    member = db.query(TeamMember).filter(TeamMember.id == user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
    return None

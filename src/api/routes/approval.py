"""
Approval Workflow API routes for Silver Tier Personal AI Employee System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...services.database import get_db_session, Task, ApprovalRequest
from ...services.task_service import TaskService
from ..api_models import TaskResponse

# Create router for approval endpoints
approval_router = APIRouter(prefix="/approvals", tags=["approvals"])

@approval_router.get("/pending", response_model=List[TaskResponse])
async def get_pending_approvals(
    db: Session = Depends(get_db_session)
):
    """
    Get all pending approval requests
    """
    # Initialize service
    task_service = TaskService(db)

    # Get tasks that are awaiting approval
    pending_tasks = task_service.get_tasks_by_status("awaiting_approval")

    # Convert to response format
    return [TaskResponse.from_orm(task) for task in pending_tasks]


@approval_router.post("/{approval_id}/approve", response_model=TaskResponse)
async def approve_request(
    approval_id: str,
    db: Session = Depends(get_db_session),
    x_user: Optional[str] = Header(None, alias="X-User")
):
    """
    Approve a specific approval request
    """
    actor = x_user or "api_user"

    # Find the approval request in the database
    approval_request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id
    ).first()

    if not approval_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request with ID {approval_id} not found"
        )

    # Update the approval request status
    approval_request.status = "approved"
    approval_request.approved_by = actor
    approval_request.approved_at = datetime.utcnow()

    # Update the associated task status to processing
    task = db.query(Task).filter(
        Task.id == approval_request.task_id
    ).first()

    if task:
        task.status = "processing"
        task.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(approval_request)

        # Return the updated task
        if task:
            return TaskResponse.from_orm(task)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task associated with approval {approval_id} not found"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error approving request"
        )


@approval_router.post("/{approval_id}/reject", response_model=TaskResponse)
async def reject_request(
    approval_id: str,
    db: Session = Depends(get_db_session),
    x_user: Optional[str] = Header(None, alias="X-User")
):
    """
    Reject a specific approval request
    """
    actor = x_user or "api_user"

    # Find the approval request in the database
    approval_request = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id
    ).first()

    if not approval_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request with ID {approval_id} not found"
        )

    # Update the approval request status
    approval_request.status = "rejected"
    approval_request.rejected_by = actor
    approval_request.rejected_at = datetime.utcnow()

    # Update the associated task status to failed
    task = db.query(Task).filter(
        Task.id == approval_request.task_id
    ).first()

    if task:
        task.status = "failed"
        task.last_error = "Approval rejected"
        task.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(approval_request)

        # Return the updated task
        if task:
            return TaskResponse.from_orm(task)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task associated with approval {approval_id} not found"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error rejecting request"
        )


# Additional approval endpoints can be added here
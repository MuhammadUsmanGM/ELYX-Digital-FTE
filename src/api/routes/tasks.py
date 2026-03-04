"""
Task Management API routes for Silver Tier Personal AI Employee System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...services.database import get_db_session
from ...services.task_service import TaskService
from ...services.preference_service import UserPreferenceService
from ...services.interaction_service import InteractionService
from ..api_models import (
    TaskResponse,
    TaskCreateRequest,
    TaskUpdateRequest,
    BulkUpdateRequest,
    BulkUpdateResponse,
    TaskStatus,
    TaskPriority,
    TaskCategory,
    TaskSource
)

# Create router for task endpoints
task_router = APIRouter(prefix="/tasks", tags=["tasks"])

@task_router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter tasks by status"),
    category: Optional[TaskCategory] = Query(None, description="Filter tasks by category"),
    source: Optional[TaskSource] = Query(None, description="Filter tasks by source"),
    priority: Optional[TaskPriority] = Query(None, description="Filter tasks by priority"),
    assigned_to: Optional[str] = Query(None, description="Filter tasks by assignee"),
    limit: int = Query(20, ge=1, le=100, description="Limit number of results returned"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db_session)
):
    """
    List all tasks with filtering and pagination options
    """
    # Initialize service
    task_service = TaskService(db)

    # Build filters
    filters = {}
    if status:
        filters["status"] = status.value
    if category:
        filters["category"] = category.value
    if source:
        filters["source"] = source.value
    if priority:
        filters["priority"] = priority.value
    if assigned_to:
        filters["assigned_to"] = assigned_to

    # Get tasks with filters
    all_tasks = task_service.get_by_filter(**filters)

    # Apply pagination
    paginated_tasks = all_tasks[offset:offset+limit]

    # Convert to response format
    return [TaskResponse.from_orm(task) for task in paginated_tasks]


@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreateRequest,
    db: Session = Depends(get_db_session)
):
    """
    Create a new task in the system
    """
    # Initialize service
    task_service = TaskService(db)

    try:
        # Create task using service
        created_task = task_service.create_task(
            title=task_create.title,
            description=task_create.description,
            status=task_create.status.value if task_create.status else "pending",
            priority=task_create.priority.value if task_create.priority else "medium",
            category=task_create.category.value,
            source=task_create.source.value if task_create.source else "api",
            assigned_to=task_create.assigned_to,
            due_date=task_create.due_date,
            task_metadata=task_create.task_metadata,
            parent_task_id=task_create.parent_task_id,
            estimated_duration=task_create.estimated_duration
        )

        return TaskResponse.from_orm(created_task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get a specific task by its ID
    """
    # Initialize service
    task_service = TaskService(db)

    task = task_service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return TaskResponse.from_orm(task)


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """
    Update an existing task
    """
    # Initialize service
    task_service = TaskService(db)

    # Prepare update data from the request
    update_data = {}
    for field, value in task_update.dict(exclude_unset=True).items():
        if value is not None:
            if isinstance(value, (TaskStatus, TaskPriority)):
                update_data[field] = value.value
            else:
                update_data[field] = value

    updated_task = task_service.update(task_id, update_data)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return TaskResponse.from_orm(updated_task)


@task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Delete a task from the system
    """
    # Initialize service
    task_service = TaskService(db)

    success = task_service.delete(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return


@task_router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_failed_task(
    task_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Attempt to retry a failed task
    """
    # Initialize service
    task_service = TaskService(db)

    try:
        task = task_service.retry_failed_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task with ID {task_id} cannot be retried (may not be in failed status)"
            )

        return TaskResponse.from_orm(task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@task_router.post("/bulk-update", response_model=BulkUpdateResponse)
async def bulk_update_tasks(
    bulk_request: BulkUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """
    Update multiple tasks at once
    """
    # Initialize service
    task_service = TaskService(db)

    # Prepare update data
    update_data = {}
    for field, value in bulk_request.updates.dict(exclude_unset=True).items():
        if value is not None:
            if isinstance(value, (TaskStatus, TaskPriority)):
                update_data[field] = value.value
            else:
                update_data[field] = value

    result = task_service.bulk_update_tasks(bulk_request.task_ids, update_data)

    # Convert errors to the expected format
    errors = []
    for error in result.get('errors', []):
        errors.append({
            "task_id": error.get('task_id', ''),
            "error": error.get('error', '')
        })

    return BulkUpdateResponse(
        updated_count=result['updated_count'],
        failed_count=result['failed_count'],
        errors=errors
    )


# Additional task endpoints can be added here
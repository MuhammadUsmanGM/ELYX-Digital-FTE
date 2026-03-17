"""
Dashboard API routes for Silver Tier Personal AI Employee System
"""
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from ...services.database import get_db_session
from ...services.task_service import TaskService
from ...services.preference_service import UserPreferenceService
from ...services.interaction_service import InteractionService
from ..api_models import (
    DashboardStatusResponse,
    AnalyticsRequest,
    AnalyticsResponse,
    TaskOverviewResponse,
    TaskResponse,
    UserPreferenceResponse,
    UserPreferenceCreateRequest
)
from ...config.manager import ConfigManager

# Create router for dashboard endpoints
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@dashboard_router.get("/status", response_model=DashboardStatusResponse)
async def get_system_status(db: Session = Depends(get_db_session)):
    """
    Get current system status
    """
    # Initialize services
    task_service = TaskService(db)

    # Get basic stats
    total_tasks = task_service.count()
    pending_approvals = task_service.count(status="awaiting_approval")

    # Calculate tasks processed today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    completed_today = db.query(TaskService.entity_class).filter(
        TaskService.entity_class.status == "completed",
        TaskService.entity_class.completed_at >= today_start,
        TaskService.entity_class.completed_at < today_end
    ).count()

    # Mock active agents count (would come from actual monitoring)
    active_agents = 5

    # Calculate mock uptime (assuming system started 1 hour ago)
    uptime = "1 hour, 23 minutes"

    return DashboardStatusResponse(
        status="active",
        active_agents=active_agents,
        tasks_processed_today=completed_today,
        pending_approvals=pending_approvals,
        system_uptime=uptime,
        last_update=datetime.utcnow()
    )


@dashboard_router.get("/analytics", response_model=AnalyticsResponse)
async def get_system_analytics(
    request: AnalyticsRequest = Depends(),
    db: Session = Depends(get_db_session)
):
    """
    Get system analytics with specified timeframe and granularity
    """
    # Initialize services
    task_service = TaskService(db)
    interaction_service = InteractionService(db)

    # Get time filters based on timeframe
    now = datetime.utcnow()
    if request.timeframe == "today":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif request.timeframe == "week":
        start_time = now - timedelta(days=7)
    elif request.timeframe == "month":
        start_time = now - timedelta(days=30)
    elif request.timeframe == "quarter":
        start_time = now - timedelta(days=90)
    elif request.timeframe == "year":
        start_time = now - timedelta(days=365)
    else:
        start_time = now - timedelta(days=7)  # Default to week

    # Calculate metrics
    total_tasks = task_service.count()

    # Get tasks by status
    tasks_by_status = {}
    for status_val in ["pending", "processing", "completed", "failed", "awaiting_approval"]:
        count = task_service.count(status=status_val)
        tasks_by_status[status_val] = count

    # Get tasks by category
    tasks_by_category = {}
    for category in ["email", "file", "calendar", "crm", "custom"]:
        count = task_service.count(category=category)
        tasks_by_category[category] = count

    # Calculate approval metrics
    approvals_granted = task_service.db.query(task_service.entity_class).filter(
        task_service.entity_class.status == "completed",
        task_service.entity_class.id.like("%")  # This would link to approval requests in a real implementation
    ).count()

    # Calculate average response time (mock data)
    average_response_time = 12.5  # in seconds

    # Calculate success rate (mock calculation)
    completed_count = tasks_by_status.get("completed", 0)
    total_processed = completed_count + tasks_by_status.get("failed", 0)
    success_rate = (completed_count / total_processed * 100) if total_processed > 0 else 100.0

    # Calculate user satisfaction (mock based on positive interactions)
    positive_interactions = interaction_service.db.query(InteractionService.entity_class).filter(
        InteractionService.entity_class.outcome == "positive"
    ).count()
    total_interactions = interaction_service.db.query(InteractionService.entity_class).count()
    user_satisfaction = (positive_interactions / total_interactions * 100) if total_interactions > 0 else 85.0

    # Calculate trends
    improving = True  # Mock trend
    percentage_change = 12.5  # Mock percentage change

    # Engagement by hour (temporal density)
    engagement_by_hour = []
    for hour in range(24):
        # Mock calculation based on simulated activity patterns
        engagement = 20 + (80 * (1 - abs(hour - 14) / 12) * (0.8 + 0.2 * (datetime.utcnow().microsecond % 100) / 100))
        engagement_by_hour.append({
            "hour": hour,
            "engagement": min(100.0, max(0.0, engagement))
        })

    # Communication stats breakdown
    communication_stats = {
        "email": tasks_by_category.get("email", 0) * 2.5,  # scaling for effect
        "whatsapp": tasks_by_category.get("custom", 0) * 1.8,
        "linkedin": tasks_by_category.get("crm", 0) * 1.2,
        "internal": total_tasks * 0.4
    }

    return AnalyticsResponse(
        timeframe=request.timeframe,
        metrics={
            "tasks_processed": total_tasks,
            "approvals_granted": approvals_granted,
            "average_response_time": average_response_time,
            "success_rate": success_rate,
            "user_satisfaction": user_satisfaction,
            "task_completion_by_category": tasks_by_category,
            "communication_stats": communication_stats,
            "engagement_by_hour": engagement_by_hour
        },
        trends={
            "improving": improving,
            "percentage_change": percentage_change
        }
    )


@dashboard_router.get("/tasks", response_model=TaskOverviewResponse)
async def get_task_overview(
    status: Optional[str] = Query(None, description="Filter tasks by status"),
    category: Optional[str] = Query(None, description="Filter tasks by category"),
    limit: int = Query(20, ge=1, le=100, description="Limit number of results returned"),
    db: Session = Depends(get_db_session)
):
    """
    Get an overview of tasks in the system
    """
    # Initialize service
    task_service = TaskService(db)

    # Build filters
    filters = {}
    if status:
        if status not in ["pending", "processing", "completed", "failed", "awaiting_approval"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
        filters["status"] = status

    if category:
        if category not in ["email", "file", "calendar", "crm", "custom"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )
        filters["category"] = category

    # Get all tasks with filters
    all_tasks = task_service.get_by_filter(**filters)
    total_tasks = len(all_tasks)

    # Get tasks by status
    tasks_by_status = {}
    for status_val in ["pending", "processing", "completed", "failed", "awaiting_approval"]:
        count = task_service.count(status=status_val)
        tasks_by_status[status_val] = count

    # Get tasks by category
    tasks_by_category = {}
    for category_val in ["email", "file", "calendar", "crm", "custom"]:
        count = task_service.count(category=category_val)
        tasks_by_category[category_val] = count

    # Get recent tasks (limit to specified number)
    recent_tasks = all_tasks[:limit]
    recent_tasks_response = [TaskResponse.from_orm(task) for task in recent_tasks]

    # Get next scheduled tasks (tasks with due dates in the future)
    future_tasks = db.query(task_service.entity_class).filter(
        task_service.entity_class.due_date > datetime.utcnow(),
        task_service.entity_class.status != "completed"
    ).order_by(task_service.entity_class.due_date).limit(5).all()

    next_scheduled_response = [TaskResponse.from_orm(task) for task in future_tasks]

    return TaskOverviewResponse(
        total_tasks=total_tasks,
        tasks_by_status=tasks_by_status,
        tasks_by_category=tasks_by_category,
        recent_tasks=recent_tasks_response,
        next_scheduled=next_scheduled_response
    )


@dashboard_router.get("/preferences", response_model=dict)
async def get_user_preferences(db: Session = Depends(get_db_session)):
    """
    Get learned user preferences and settings
    """
    # Initialize service
    preference_service = UserPreferenceService(db)

    # Get all preferences (using a mock user ID for demo purposes)
    # In a real implementation, this would come from authentication
    user_id = "demo_user@example.com"
    preferences = preference_service.get_preferences_by_user(user_id)

    # Convert to response format
    preferences_response = [UserPreferenceResponse.from_orm(pref) for pref in preferences]

    # Calculate learning confidence (average of all preference confidences)
    if preferences:
        avg_confidence = sum(p.confidence_level for p in preferences if p.confidence_level is not None) / len(preferences)
    else:
        avg_confidence = 0.0

    return {
        "preferences": preferences_response,
        "learning_confidence": avg_confidence,
        "last_updated": datetime.utcnow().isoformat()
    }


@dashboard_router.post("/preferences", response_model=dict)
async def update_user_preference(
    request: UserPreferenceCreateRequest,
    db: Session = Depends(get_db_session)
):
    """
    Update or create a user preference
    """
    # Initialize service
    preference_service = UserPreferenceService(db)

    # Check if preference exists
    existing = preference_service.get_preference(request.user_id, request.preference_key)
    
    if existing:
        # Update existing
        updated = preference_service.update_preference_value(
            request.user_id, 
            request.preference_key, 
            request.preference_value
        )
        return {
            "status": "updated",
            "preference": UserPreferenceResponse.from_orm(updated)
        }
    else:
        # Create new
        new_pref = preference_service.create_preference(
            request.user_id,
            request.preference_key,
            request.preference_value,
            request.preference_type or "operational"
        )
        return {
            "status": "created",
            "preference": UserPreferenceResponse.from_orm(new_pref)
        }


# Additional dashboard endpoints can be added here


@dashboard_router.get("/activity", response_model=dict)
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=200, description="Max number of activities"),
):
    """
    Return recent activity events from the vault audit trail.

    The audit trail is newline-delimited JSON at `<vault_path>/Logs/audit_trail.json`.
    """
    cfg = ConfigManager().config
    vault_path = cfg.get("vault_path", "obsidian_vault")
    audit_file = Path(vault_path) / "Logs" / "audit_trail.json"

    if not audit_file.exists():
        return {"source": "none", "activities": []}

    activities: List[dict] = []
    try:
        lines = audit_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            activities.append(
                {
                    "timestamp": entry.get("timestamp"),
                    "action_type": entry.get("action_type"),
                    "message": entry.get("message"),
                    "actor": entry.get("actor"),
                }
            )
            if len(activities) >= limit:
                break
    except Exception:
        return {"source": "error", "activities": []}

    return {"source": "audit_trail", "activities": activities}

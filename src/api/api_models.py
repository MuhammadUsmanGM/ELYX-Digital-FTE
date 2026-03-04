"""
Pydantic models for Silver Tier Personal AI Employee System API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCategory(str, Enum):
    EMAIL = "email"
    FILE = "file"
    CALENDAR = "calendar"
    CRM = "crm"
    CUSTOM = "custom"


class TaskSource(str, Enum):
    GMAIL = "gmail"
    WHATSAPP = "whatsapp"
    FILESYSTEM = "filesystem"
    CALENDAR = "calendar"
    API = "api"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalLevel(str, Enum):
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class TaskResponse(BaseModel):
    """Response model for Task entity"""
    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    category: TaskCategory
    source: TaskSource
    created_at: datetime
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    completed_at: Optional[datetime] = None
    task_metadata: Optional[Dict[str, Any]] = None
    parent_task_id: Optional[str] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    confidence_score: Optional[float] = None
    retry_count: Optional[int] = 0
    last_error: Optional[str] = None

    class Config:
        from_attributes = True


class TaskCreateRequest(BaseModel):
    """Request model for creating a new Task"""
    title: str = Field(..., max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[TaskStatus] = Field(TaskStatus.PENDING, description="Task status")
    priority: Optional[TaskPriority] = Field(TaskPriority.MEDIUM, description="Task priority")
    category: TaskCategory = Field(..., description="Task category")
    source: Optional[TaskSource] = Field(TaskSource.API, description="Task source")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    assigned_to: Optional[str] = Field(None, description="Who the task is assigned to")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional task metadata")
    parent_task_id: Optional[str] = Field(None, description="Parent task ID if this is a sub-task")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")

    class Config:
        use_enum_values = True


class TaskUpdateRequest(BaseModel):
    """Request model for updating a Task"""
    title: Optional[str] = Field(None, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    assigned_to: Optional[str] = Field(None, description="Who the task is assigned to")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional task metadata")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")

    class Config:
        use_enum_values = True


class ApprovalRequestResponse(BaseModel):
    """Response model for ApprovalRequest entity"""
    id: str
    task_id: str
    requester: Optional[str] = None
    approver: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    status: ApprovalStatus
    approval_level: Optional[ApprovalLevel] = None
    business_impact: Optional[str] = None
    financial_impact_amount: Optional[float] = None
    financial_impact_currency: Optional[str] = None
    escalation_required: Optional[bool] = False
    escalation_reason: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserPreferenceResponse(BaseModel):
    """Response model for UserPreference entity"""
    id: str
    user_id: str
    preference_key: str
    preference_value: Optional[str] = None
    preference_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    confidence_level: Optional[float] = None
    usage_count: Optional[int] = 0
    effectiveness_score: Optional[float] = None

    class Config:
        from_attributes = True


class UserPreferenceCreateRequest(BaseModel):
    """Request model for creating a UserPreference"""
    user_id: str = Field(..., description="User identifier")
    preference_key: str = Field(..., description="Preference key")
    preference_value: Any = Field(..., description="Preference value (will be serialized)")
    preference_type: Optional[str] = Field("operational", description="Type of preference")


class InteractionLogResponse(BaseModel):
    """Response model for InteractionLog entity"""
    id: str
    user_id: str
    interaction_type: Optional[str] = None
    task_id: Optional[str] = None
    action_taken: Optional[str] = None
    system_response: Optional[str] = None
    timestamp: datetime
    context_snapshot: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = None
    feedback_text: Optional[str] = None
    learning_applied: Optional[bool] = False

    class Config:
        from_attributes = True


class InteractionLogCreateRequest(BaseModel):
    """Request model for creating an InteractionLog"""
    user_id: str = Field(..., description="User identifier")
    interaction_type: str = Field(..., description="Type of interaction")
    action_taken: str = Field(..., description="Description of user action")
    system_response: str = Field(..., description="Description of system behavior")
    task_id: Optional[str] = Field(None, description="Associated task ID")
    context_snapshot: Optional[Dict[str, Any]] = Field(None, description="System state at time of interaction")
    outcome: Optional[str] = Field("neutral", description="Outcome of interaction")
    feedback_text: Optional[str] = Field(None, description="User feedback text")


class AnalyticsSnapshotResponse(BaseModel):
    """Response model for AnalyticsSnapshot entity"""
    id: str
    snapshot_time: datetime
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    dimension_labels: Optional[Dict[str, Any]] = None
    calculated_from: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStatusResponse(BaseModel):
    """Response model for dashboard status endpoint"""
    status: str
    active_agents: int
    tasks_processed_today: int
    pending_approvals: int
    system_uptime: str
    last_update: datetime


class AnalyticsRequest(BaseModel):
    """Request model for analytics endpoint"""
    timeframe: str = Field("week", description="Timeframe for analytics")
    granularity: str = Field("daily", description="Granularity of the analytics")


class AnalyticsResponse(BaseModel):
    """Response model for analytics endpoint"""
    timeframe: str
    metrics: Dict[str, Any]
    trends: Dict[str, Any]


class TaskOverviewResponse(BaseModel):
    """Response model for task overview endpoint"""
    total_tasks: int
    tasks_by_status: Dict[str, int]
    tasks_by_category: Dict[str, int]
    recent_tasks: List[TaskResponse]
    next_scheduled: List[TaskResponse]


class BulkUpdateRequest(BaseModel):
    """Request model for bulk update endpoint"""
    task_ids: List[str]
    updates: TaskUpdateRequest


class BulkUpdateResponse(BaseModel):
    """Response model for bulk update endpoint"""
    updated_count: int
    failed_count: int
    errors: List[Dict[str, str]]


class TeamMemberResponse(BaseModel):
    """Response model for TeamMember entity"""
    id: str
    name: str
    email: str
    role: Optional[str] = None
    status: str
    last_active: datetime
    avatar: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class TeamMemberCreateRequest(BaseModel):
    """Request model for creating a TeamMember"""
    name: str
    email: str
    role: Optional[str] = "Operator"
    status: Optional[str] = "active"
    avatar: Optional[str] = None
    permissions: Optional[List[str]] = []



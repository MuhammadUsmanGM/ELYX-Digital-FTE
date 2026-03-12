"""
Task Service for Silver Tier Personal AI Employee System
Handles enhanced task management with analytics and learning capabilities
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from datetime import datetime, timedelta
import uuid

from .base_service import BaseService, ValidationError, NotFoundError
from .database import Task, ApprovalRequest
from ..utils.logger import log_activity


class TaskService(BaseService[Task]):
    """
    Enhanced Task Service for Silver Tier with advanced features
    """

    def __init__(self, db_session: Session):
        super().__init__(db_session, Task)

    def create_task(self,
                   title: str,
                   description: str = "",
                   status: str = "pending",
                   priority: str = "medium",
                   category: str = "custom",
                   source: str = "api",
                   assigned_to: str = "ai",
                   due_date: Optional[datetime] = None,
                   task_metadata: Optional[Dict] = None,
                   parent_task_id: Optional[str] = None,
                   estimated_duration: Optional[int] = None) -> Task:
        """
        Create a new enhanced task

        Args:
            title: Task title
            description: Task description
            status: Task status (pending, processing, completed, failed, awaiting_approval)
            priority: Task priority (low, medium, high, critical)
            category: Task category (email, file, calendar, crm, custom)
            source: Task source (gmail, whatsapp, filesystem, calendar, api)
            assigned_to: Who the task is assigned to
            due_date: Task due date
            metadata: Additional metadata for the task
            parent_task_id: ID of parent task if this is a sub-task
            estimated_duration: Estimated time to complete in minutes

        Returns:
            The created Task object
        """
        # Validate inputs
        if not title or len(title.strip()) == 0:
            raise ValidationError("Task title is required")

        if priority not in ["low", "medium", "high", "critical"]:
            raise ValidationError(f"Invalid priority: {priority}")

        if status not in ["pending", "processing", "completed", "failed", "awaiting_approval"]:
            raise ValidationError(f"Invalid status: {status}")

        if category not in ["email", "file", "calendar", "crm", "custom"]:
            raise ValidationError(f"Invalid category: {category}")

        if source not in ["gmail", "whatsapp", "filesystem", "calendar", "api"]:
            raise ValidationError(f"Invalid source: {source}")

        # Create task object
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            status=status,
            priority=priority,
            category=category,
            source=source,
            assigned_to=assigned_to,
            due_date=due_date,
            task_metadata=task_metadata or {},
            parent_task_id=parent_task_id,
            estimated_duration=estimated_duration,
            created_at=datetime.utcnow()
        )

        # Log the creation
        log_activity("TASK_CREATED", f"Task '{title}' created with ID {task.id}", "obsidian_vault")

        return self.create(task)

    def get_task_with_relationships(self, task_id: str) -> Optional[Task]:
        """
        Get a task with its relationships (parent, children, approval request)

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object with relationships loaded, or None if not found
        """
        try:
            task = self.db.query(Task).filter(Task.id == task_id).first()
            if task:
                # Explicitly load relationships if needed
                if task.parent_task_id:
                    parent = self.db.query(Task).filter(Task.id == task.parent_task_id).first()
                    task.parent = parent
            return task
        except Exception as e:
            self.logger.error(f"Error getting task with relationships: {str(e)}")
            raise

    def update_task_status(self, task_id: str, new_status: str) -> Optional[Task]:
        """
        Update the status of a task

        Args:
            task_id: ID of the task to update
            new_status: New status for the task

        Returns:
            Updated Task object, or None if task not found
        """
        if new_status not in ["pending", "processing", "completed", "failed", "awaiting_approval"]:
            raise ValidationError(f"Invalid status: {new_status}")

        task = self.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task", task_id)

        old_status = task.status
        task.status = new_status
        task.updated_at = datetime.utcnow()

        # If changing to completed, set completion time
        if new_status == "completed" and old_status != "completed":
            task.completed_at = datetime.utcnow()
            task.actual_duration = int((task.completed_at - task.created_at).total_seconds()) // 60  # in minutes

        # If changing from completed, clear completion time
        if old_status == "completed" and new_status != "completed":
            task.completed_at = None
            task.actual_duration = None

        try:
            self.db.commit()
            self.db.refresh(task)

            log_activity("TASK_STATUS_UPDATE",
                       f"Task '{task.title}' status changed from '{old_status}' to '{new_status}'",
                       "obsidian_vault")

            return task
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating task status: {str(e)}")
            raise

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """
        Get all tasks with a specific status

        Args:
            status: Status to filter by

        Returns:
            List of tasks with the specified status
        """
        if status not in ["pending", "processing", "completed", "failed", "awaiting_approval"]:
            raise ValidationError(f"Invalid status: {status}")

        return self.get_by_filter(status=status)

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """
        Get all tasks with a specific category

        Args:
            category: Category to filter by

        Returns:
            List of tasks with the specified category
        """
        if category not in ["email", "file", "calendar", "crm", "custom"]:
            raise ValidationError(f"Invalid category: {category}")

        return self.get_by_filter(category=category)

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """
        Get all tasks with a specific priority

        Args:
            priority: Priority to filter by

        Returns:
            List of tasks with the specified priority
        """
        if priority not in ["low", "medium", "high", "critical"]:
            raise ValidationError(f"Invalid priority: {priority}")

        return self.get_by_filter(priority=priority)

    def get_overdue_tasks(self) -> List[Task]:
        """
        Get all tasks that are overdue

        Returns:
            List of overdue tasks
        """
        now = datetime.utcnow()
        overdue_tasks = self.db.query(Task).filter(
            Task.due_date < now,
            Task.status != "completed",
            Task.status != "failed"
        ).all()
        return overdue_tasks

    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """
        Get all tasks created within a date range

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of tasks created within the date range
        """
        tasks = self.db.query(Task).filter(
            Task.created_at >= start_date,
            Task.created_at <= end_date
        ).all()
        return tasks

    def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about tasks

        Returns:
            Dictionary with task statistics
        """
        stats = {}

        # Count by status
        stats['by_status'] = {}
        for status in ["pending", "processing", "completed", "failed", "awaiting_approval"]:
            stats['by_status'][status] = self.count(status=status)

        # Count by category
        stats['by_category'] = {}
        for category in ["email", "file", "calendar", "crm", "custom"]:
            stats['by_category'][category] = self.count(category=category)

        # Count by priority
        stats['by_priority'] = {}
        for priority in ["low", "medium", "high", "critical"]:
            stats['by_priority'][priority] = self.count(priority=priority)

        # Count total tasks
        stats['total'] = self.count()

        # Count completed tasks today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        stats['completed_today'] = self.db.query(Task).filter(
            Task.status == "completed",
            Task.completed_at >= today_start,
            Task.completed_at < today_end
        ).count()

        # Average estimated vs actual duration
        completed_tasks = self.db.query(Task).filter(
            Task.status == "completed",
            Task.estimated_duration.isnot(None),
            Task.actual_duration.isnot(None)
        ).all()

        if completed_tasks:
            avg_estimated = sum(t.estimated_duration for t in completed_tasks) / len(completed_tasks)
            avg_actual = sum(t.actual_duration for t in completed_tasks) / len(completed_tasks)
            stats['avg_estimated_duration'] = avg_estimated
            stats['avg_actual_duration'] = avg_actual
        else:
            stats['avg_estimated_duration'] = 0
            stats['avg_actual_duration'] = 0

        return stats

    def retry_failed_task(self, task_id: str) -> Optional[Task]:
        """
        Retry a failed task by resetting its status and incrementing retry count

        Args:
            task_id: ID of the failed task to retry

        Returns:
            Updated Task object, or None if task not found
        """
        task = self.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task", task_id)

        if task.status != "failed":
            raise ValidationError(f"Task with ID {task_id} is not in failed status")

        # Reset status and increment retry count
        task.status = "pending"
        task.retry_count = task.retry_count + 1
        task.last_error = None  # Clear the last error
        task.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(task)

            log_activity("TASK_RETRY",
                       f"Task '{task.title}' retry #{task.retry_count} initiated",
                       "obsidian_vault")

            return task
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error retrying task: {str(e)}")
            raise

    def get_hierarchical_tasks(self, root_task_id: str) -> List[Task]:
        """
        Get a task and all its child tasks recursively

        Args:
            root_task_id: ID of the root task

        Returns:
            List of tasks in hierarchical order
        """
        def get_children(task_id: str) -> List[Task]:
            children = self.get_by_filter(parent_task_id=task_id)
            all_tasks = children[:]
            for child in children:
                all_tasks.extend(get_children(child.id))
            return all_tasks

        root_task = self.get_by_id(root_task_id)
        if not root_task:
            raise NotFoundError("Task", root_task_id)

        hierarchical_tasks = [root_task]
        hierarchical_tasks.extend(get_children(root_task_id))
        return hierarchical_tasks

    # Fields that are safe to update via bulk operations
    BULK_UPDATABLE_FIELDS = {
        'title', 'description', 'status', 'priority', 'category',
        'assigned_to', 'due_date', 'estimated_duration', 'task_metadata',
    }

    def bulk_update_tasks(self, task_ids: List[str], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update multiple tasks at once

        Args:
            task_ids: List of task IDs to update
            updates: Dictionary of fields to update (only allowlisted fields accepted)

        Returns:
            Dictionary with results of the bulk update
        """
        results = {
            'updated_count': 0,
            'failed_count': 0,
            'errors': []
        }

        for task_id in task_ids:
            try:
                task = self.get_by_id(task_id)
                if task:
                    # Update only allowlisted fields
                    for key, value in updates.items():
                        if key in self.BULK_UPDATABLE_FIELDS and hasattr(task, key):
                            setattr(task, key, value)

                    task.updated_at = datetime.utcnow()
                    self.db.commit()
                    self.db.refresh(task)
                    results['updated_count'] += 1

                    log_activity("TASK_BULK_UPDATE",
                               f"Task '{task.title}' updated in bulk operation",
                               "obsidian_vault")
                else:
                    results['failed_count'] += 1
                    results['errors'].append({
                        'task_id': task_id,
                        'error': f'Task not found'
                    })
            except Exception as e:
                results['failed_count'] += 1
                results['errors'].append({
                    'task_id': task_id,
                    'error': str(e)
                })

        return results
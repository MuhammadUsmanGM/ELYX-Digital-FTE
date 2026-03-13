"""
Database Initialization Script for Silver Tier Personal AI Employee System
Initializes the database with all required tables and sample data
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base, Task, UserPreference, InteractionLog, ApprovalRequest, AnalyticsSnapshot
from datetime import datetime, timedelta
import uuid


def init_database(database_url: str = None):
    """
    Initialize the database with all required tables

    Args:
        database_url: Database connection URL (defaults to environment variable or sqlite)
    """
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///elyx.db")

    print(f"Initializing database with URL: {database_url}")

    # Create engine and tables
    engine = create_engine(database_url)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully")

    # Create a session to add sample data if needed
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if database is empty by checking if tasks table has any records
        task_count = session.query(Task).count()

        if task_count == 0:
            print("Adding sample data to database...")
            add_sample_data(session)
        else:
            print(f"Database already initialized with {task_count} tasks")

        session.commit()
        print("Database initialization completed successfully")

    except Exception as e:
        session.rollback()
        print(f"Error during database initialization: {str(e)}")
        raise
    finally:
        session.close()


def add_sample_data(session):
    """
    Add sample data to the database for initial setup
    """
    print("Adding sample tasks...")

    # Sample tasks
    sample_tasks = [
        Task(
            id=str(uuid.uuid4()),
            title="Process weekly expense reports",
            description="Review and approve weekly expense reports from team members",
            status="pending",
            priority="high",
            category="custom",
            source="gmail",
            assigned_to="ai",
            created_at=datetime.utcnow() - timedelta(hours=1),
            due_date=datetime.utcnow() + timedelta(days=2),
            estimated_duration=45,
            confidence_score=0.85
        ),
        Task(
            id=str(uuid.uuid4()),
            title="Schedule quarterly review meeting",
            description="Coordinate with stakeholders to schedule the quarterly review meeting",
            status="processing",
            priority="medium",
            category="calendar",
            source="calendar",
            assigned_to="ai",
            created_at=datetime.utcnow() - timedelta(minutes=30),
            due_date=datetime.utcnow() + timedelta(days=1),
            estimated_duration=30,
            confidence_score=0.72
        ),
        Task(
            id=str(uuid.uuid4()),
            title="Update client contact information",
            description="Update contact information for enterprise clients in CRM",
            status="awaiting_approval",
            priority="medium",
            category="crm",
            source="api",
            assigned_to="human",
            created_at=datetime.utcnow() - timedelta(hours=3),
            due_date=datetime.utcnow() + timedelta(days=3),
            estimated_duration=20,
            confidence_score=0.90
        )
    ]

    for task in sample_tasks:
        session.add(task)

    print("Adding sample user preferences...")

    # Sample user preferences
    sample_preferences = [
        UserPreference(
            id=str(uuid.uuid4()),
            user_id="user@example.com",
            preference_key="email_response_style",
            preference_value='{"style": "professional", "tone": "friendly_but_formal", "length": "concise"}',
            preference_type="communication",
            confidence_level=0.8,
            usage_count=25,
            effectiveness_score=0.75,
            created_at=datetime.utcnow() - timedelta(days=7),
            updated_at=datetime.utcnow()
        ),
        UserPreference(
            id=str(uuid.uuid4()),
            user_id="user@example.com",
            preference_key="approval_threshold",
            preference_value='{"amount": 500, "currency": "USD", "requires_approval": true}',
            preference_type="security",
            confidence_level=0.9,
            usage_count=15,
            effectiveness_score=0.88,
            created_at=datetime.utcnow() - timedelta(days=10),
            updated_at=datetime.utcnow()
        ),
        UserPreference(
            id=str(uuid.uuid4()),
            user_id="user@example.com",
            preference_key="default_task_priority",
            preference_value='{"value": "medium"}',
            preference_type="operational",
            confidence_level=0.6,
            usage_count=50,
            effectiveness_score=0.82,
            created_at=datetime.utcnow() - timedelta(days=15),
            updated_at=datetime.utcnow()
        )
    ]

    for pref in sample_preferences:
        session.add(pref)

    print("Adding sample interactions...")

    # Sample interaction logs
    sample_interactions = [
        InteractionLog(
            id=str(uuid.uuid4()),
            user_id="user@example.com",
            interaction_type="approval",
            task_id=sample_tasks[2].id,
            action_taken="Approved client contact update",
            system_response="Requested approval for updating client contact information",
            context_snapshot='{"task_details": {"title": "Update client contact information", "category": "crm"}}',
            outcome="positive",
            feedback_text="Good job identifying the need for approval",
            learning_applied=True,
            timestamp=datetime.utcnow() - timedelta(hours=2)
        ),
        InteractionLog(
            id=str(uuid.uuid4()),
            user_id="user@example.com",
            interaction_type="correction",
            task_id=sample_tasks[0].id,
            action_taken="Corrected expense category",
            system_response="Categorized as travel expenses",
            context_snapshot='{"task_details": {"title": "Process weekly expense reports", "category": "finance"}}',
            outcome="positive",
            feedback_text="Corrected category from office supplies to travel",
            learning_applied=True,
            timestamp=datetime.utcnow() - timedelta(hours=4)
        )
    ]

    for interaction in sample_interactions:
        session.add(interaction)

    print("Adding sample approval requests...")

    # Sample approval request linked to the task awaiting approval
    sample_approval = ApprovalRequest(
        id=str(uuid.uuid4()),
        task_id=sample_tasks[2].id,  # Link to the task awaiting approval
        requester="system",
        approver="user@example.com",
        reason="Updating client contact information requires approval",
        created_at=datetime.utcnow() - timedelta(hours=3),
        expires_at=datetime.utcnow() + timedelta(days=7),
        status="pending",
        approval_level="manager",
        business_impact="medium",
        financial_impact_amount=0,
        financial_impact_currency="USD",
        escalation_required=False,
        escalation_reason=None,
        approved_by=None,
        approved_at=None,
        rejected_by=None,
        rejected_at=None
    )

    session.add(sample_approval)

    print("Adding sample analytics snapshots...")

    # Sample analytics snapshots
    sample_analytics = [
        AnalyticsSnapshot(
            id=str(uuid.uuid4()),
            snapshot_time=datetime.utcnow() - timedelta(hours=1),
            metric_name="tasks_processed",
            metric_value=42,
            metric_unit="count",
            dimension_labels={"category": "email", "priority": "high"},
            calculated_from="task_processing_logs"
        ),
        AnalyticsSnapshot(
            id=str(uuid.uuid4()),
            snapshot_time=datetime.utcnow() - timedelta(hours=1),
            metric_name="approval_rate",
            metric_value=0.85,
            metric_unit="percentage",
            dimension_labels={"category": "finance", "priority": "high"},
            calculated_from="approval_workflow_logs"
        ),
        AnalyticsSnapshot(
            id=str(uuid.uuid4()),
            snapshot_time=datetime.utcnow() - timedelta(hours=1),
            metric_name="average_response_time",
            metric_value=12.5,
            metric_unit="seconds",
            dimension_labels={"category": "email"},
            calculated_from="task_processing_times"
        )
    ]

    for analytic in sample_analytics:
        session.add(analytic)

    print("Sample data added successfully")


def main():
    """
    Main function to run the database initialization
    """
    print("Starting Silver Tier database initialization...")

    # Use DATABASE_URL from environment or default to SQLite
    database_url = os.getenv("DATABASE_URL", "sqlite:///elyx.db")

    try:
        init_database(database_url)
        print(f"Database initialized successfully at: {database_url}")
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
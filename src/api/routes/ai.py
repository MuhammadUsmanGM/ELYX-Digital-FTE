"""
AI Capabilities API Routes for Gold Tier Personal AI Employee System
Provides endpoints for advanced AI features, strategic planning, risk assessment, and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...services.database import get_db_session
from ...services.ai_service_minimal import AIService
from ...api.api_models import (
    TaskResponse,
    TaskCreateRequest,
    TaskUpdateRequest,
    AnalyticsResponse,
    UserPreferenceResponse
)

# Create router for AI endpoints
ai_router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize AI service
ai_service = AIService()


@ai_router.post("/tasks/enhanced", response_model=TaskResponse)
async def process_enhanced_task(
    task_create: TaskCreateRequest,
    user_id: str = Query("default_user", description="User ID for personalization"),
    db: Session = Depends(get_db_session)
):
    """
    Process a task with full AI capabilities including NLP analysis, predictions, and recommendations
    """
    try:
        # Prepare task data for AI processing
        task_data = {
            'id': getattr(task_create, 'id', None),
            'title': task_create.title,
            'description': task_create.description or '',
            'category': task_create.category.value,
            'source': task_create.source.value if task_create.source else 'api',
            'created_at': datetime.utcnow().isoformat()
        }

        # Process task with AI service
        enhanced_task = ai_service.process_task_request(task_data, user_id)

        # Convert to response format
        # Note: This is a simplified conversion - in a real implementation,
        # you'd need to properly map the enhanced task to the TaskResponse format
        task_response = TaskResponse(
            id=enhanced_task.get('id', 'temp_id'),
            title=enhanced_task['title'],
            description=enhanced_task.get('description', ''),
            status=enhanced_task.get('status', 'pending'),
            priority=enhanced_task.get('priority', 'medium'),
            category=enhanced_task['category'],
            source=enhanced_task['source'],
            created_at=datetime.fromisoformat(enhanced_task['created_at']) if isinstance(enhanced_task['created_at'], str) else enhanced_task['created_at'],
            updated_at=enhanced_task.get('updated_at'),
            due_date=enhanced_task.get('due_date'),
            assigned_to=enhanced_task.get('assigned_to'),
            completed_at=enhanced_task.get('completed_at'),
            task_metadata=enhanced_task.get('enriched_metadata', {}),
            parent_task_id=enhanced_task.get('parent_task_id'),
            estimated_duration=enhanced_task.get('estimated_duration'),
            actual_duration=enhanced_task.get('actual_duration'),
            confidence_score=enhanced_task.get('ai_analysis', {}).get('predictions', {}).get('confidence_score')
        )

        return task_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing enhanced task: {str(e)}"
        )


@ai_router.get("/insights/strategic", response_model=Dict[str, Any])
async def get_strategic_insights(
    user_id: str = Query("default_user", description="User ID for personalization"),
    time_window_days: int = Query(30, description="Time window in days for analysis"),
    db: Session = Depends(get_db_session)
):
    """
    Generate strategic insights based on historical data and patterns
    """
    try:
        time_window = timedelta(days=time_window_days)
        insights = ai_service.generate_strategic_insights(user_id, time_window)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating strategic insights: {str(e)}"
        )


@ai_router.post("/decisions/assist", response_model=Dict[str, Any])
async def assist_with_decision(
    decision_data: Dict[str, Any],
    user_id: str = Query("default_user", description="User ID for personalization"),
    db: Session = Depends(get_db_session)
):
    """
    Assist with decision making using AI capabilities
    """
    try:
        decision_support = ai_service.assist_with_decision_making(decision_data, user_id)
        return decision_support
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error providing decision assistance: {str(e)}"
        )


@ai_router.post("/collaboration/start", response_model=Dict[str, Any])
async def start_collaboration(
    collaboration_data: Dict[str, Any],
    user_id: str = Query("default_user", description="User ID for personalization"),
    db: Session = Depends(get_db_session)
):
    """
    Start a human-AI collaboration session
    """
    try:
        task_description = collaboration_data.get('task_description', '')
        if not task_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task description is required for collaboration"
            )

        collaboration = ai_service.engage_in_collaboration(task_description, user_id)
        return collaboration
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error starting collaboration: {str(e)}"
        )


@ai_router.get("/dashboard/personalized", response_model=Dict[str, Any])
async def get_personalized_dashboard(
    user_id: str = Query("default_user", description="User ID for personalization"),
    db: Session = Depends(get_db_session)
):
    """
    Generate a personalized dashboard based on user profile and preferences
    """
    try:
        dashboard = ai_service.generate_personalized_dashboard(user_id)
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating personalized dashboard: {str(e)}"
        )


@ai_router.post("/learn/from-interaction", response_model=Dict[str, Any])
async def learn_from_interaction(
    interaction_data: Dict[str, Any],
    user_id: str = Query("default_user", description="User ID for personalization"),
    db: Session = Depends(get_db_session)
):
    """
    Learn from an interaction and update AI models
    """
    try:
        user_input = interaction_data.get('user_input', '')
        system_response = interaction_data.get('system_response', '')
        positive_feedback = interaction_data.get('positive_feedback', True)

        if not user_input or not system_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both user_input and system_response are required"
            )

        learning_results = ai_service.learn_from_interaction(
            user_input, system_response, user_id, positive_feedback
        )
        return learning_results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error learning from interaction: {str(e)}"
        )


@ai_router.get("/analytics/system", response_model=Dict[str, Any])
async def get_system_analytics(
    db: Session = Depends(get_db_session)
):
    """
    Get comprehensive system analytics and performance metrics
    """
    try:
        analytics = ai_service.get_system_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting system analytics: {str(e)}"
        )


@ai_router.post("/reports/business-intelligence", response_model=Dict[str, Any])
async def generate_bi_report(
    report_params: Dict[str, Any],
    user_id: str = Query("default_user", description="User ID for personalization"),
    db: Session = Depends(get_db_session)
):
    """
    Generate a business intelligence report
    """
    try:
        report_type = report_params.get('report_type', 'performance')
        time_period = report_params.get('time_period', 'last_month')

        report = ai_service.generate_business_intelligence_report(
            user_id=user_id,
            report_type=report_type,
            time_period=time_period
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating BI report: {str(e)}"
        )


@ai_router.get("/capabilities/available", response_model=Dict[str, Any])
async def get_available_ai_capabilities(
    db: Session = Depends(get_db_session)
):
    """
    Get list of available AI capabilities
    """
    capabilities = {
        "nlp_processing": {
            "description": "Advanced NLP with entity recognition, sentiment analysis, and intent classification",
            "features": ["entity_extraction", "sentiment_analysis", "intent_classification", "keyword_extraction", "text_summarization"]
        },
        "prediction": {
            "description": "Task completion, duration, and resource prediction models",
            "features": ["completion_probability", "duration_prediction", "priority_prediction", "resource_prediction", "forecasting"]
        },
        "recommendation": {
            "description": "Personalized recommendations using content and collaborative filtering",
            "features": ["task_recommendations", "strategic_objectives", "resource_matching", "risk_mitigation"]
        },
        "reasoning": {
            "description": "Logical reasoning, constraint solving, and decision support",
            "features": ["logical_evaluation", "constraint_satisfaction", "mathematical_solving", "decision_support"]
        },
        "memory": {
            "description": "Persistent memory and learning system",
            "features": ["episodic_memory", "semantic_memory", "procedural_memory", "learning_from_interaction", "pattern_identification"]
        },
        "collaboration": {
            "description": "Human-AI collaboration and communication",
            "features": ["emotion_detection", "adaptive_communication", "collaborative_tasking", "feedback_integration"]
        }
    }

    return capabilities


# Additional AI endpoints can be added here
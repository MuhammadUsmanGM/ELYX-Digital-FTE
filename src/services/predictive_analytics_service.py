"""
Predictive Analytics Service for Silver Tier Personal AI Employee System
Provides predictive analytics and task prediction capabilities
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from dataclasses import dataclass
from enum import Enum

from .database import Task, UserPreference, InteractionLog
from .task_service import TaskService
from .preference_service import UserPreferenceService
from .interaction_service import InteractionService
from ..utils.logger import log_activity


@dataclass
class PredictionResult:
    """Data class for prediction results"""
    predicted_task: str
    confidence: float  # 0-1
    estimated_time: int  # in minutes
    category: str
    priority: str
    recommended_action: str
    explanation: str


class TrendDirection(Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    PEAKING = "peaking"


class PredictiveAnalyticsService:
    """
    Service for predictive analytics and task prediction in Silver Tier
    """

    def __init__(self, db_session):
        self.db = db_session
        self.task_service = TaskService(db_session)
        self.preference_service = UserPreferenceService(db_session)
        self.interaction_service = InteractionService(db_session)

    def predict_upcoming_tasks(self, user_id: str, days_ahead: int = 7) -> List[PredictionResult]:
        """
        Predict upcoming tasks based on historical patterns and user preferences

        Args:
            user_id: User identifier
            days_ahead: Number of days to predict ahead

        Returns:
            List of predicted tasks with confidence scores
        """
        predictions = []

        # Get user's historical tasks
        historical_tasks = self.db.query(Task).filter(
            Task.assigned_to == user_id
        ).all()

        if not historical_tasks:
            # No historical data, return empty predictions
            return predictions

        # Analyze patterns in historical tasks
        task_patterns = self._analyze_task_patterns(historical_tasks)

        # Get user preferences to refine predictions
        user_preferences = self.preference_service.get_preferences_by_user(user_id)

        # Generate predictions based on patterns and preferences
        for pattern in task_patterns:
            if pattern['frequency'] > 0.1:  # Only predict frequent tasks
                prediction = self._generate_prediction_from_pattern(
                    pattern, user_preferences, days_ahead
                )
                if prediction:
                    predictions.append(prediction)

        # Sort by confidence score
        predictions.sort(key=lambda x: x.confidence, reverse=True)

        log_activity("TASK_PREDICTION",
                   f"Generated {len(predictions)} task predictions for user {user_id}",
                   "obsidian_vault")

        return predictions

    def _analyze_task_patterns(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Analyze patterns in historical tasks

        Args:
            tasks: List of historical tasks

        Returns:
            List of task patterns with frequency and characteristics
        """
        patterns = []

        # Group tasks by title similarity (for recurring tasks)
        title_groups = defaultdict(list)
        for task in tasks:
            # Normalize title for grouping
            normalized_title = task.title.lower().strip()
            title_groups[normalized_title].append(task)

        # Analyze each group
        for title, task_group in title_groups.items():
            if len(task_group) < 2:  # Need at least 2 occurrences to establish a pattern
                continue

            # Calculate recurrence pattern
            timestamps = [t.created_at for t in task_group]
            timestamps.sort()

            # Calculate intervals between occurrences
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).days
                intervals.append(interval)

            # Calculate average interval and frequency
            avg_interval = statistics.mean(intervals) if intervals else 0
            frequency = len(task_group) / len(tasks)  # Relative frequency

            # Determine category and priority patterns
            categories = [t.category for t in task_group]
            priorities = [t.priority for t in task_group]

            category_mode = Counter(categories).most_common(1)[0][0] if categories else "custom"
            priority_mode = Counter(priorities).most_common(1)[0][0] if priorities else "medium"

            # Estimate typical duration
            durations = [t.estimated_duration for t in task_group if t.estimated_duration]
            typical_duration = statistics.mean(durations) if durations else 30

            pattern = {
                'title': title,
                'frequency': frequency,
                'avg_interval_days': avg_interval,
                'category': category_mode,
                'priority': priority_mode,
                'typical_duration': typical_duration,
                'occurrence_count': len(task_group),
                'recent_occurrences': task_group[-3:]  # Last 3 occurrences
            }

            patterns.append(pattern)

        return patterns

    def _generate_prediction_from_pattern(
        self,
        pattern: Dict[str, Any],
        user_preferences: List[UserPreference],
        days_ahead: int
    ) -> Optional[PredictionResult]:
        """
        Generate a prediction from a task pattern

        Args:
            pattern: Task pattern to generate prediction from
            user_preferences: User preferences to refine prediction
            days_ahead: Number of days to predict ahead

        Returns:
            PredictionResult or None if prediction is not reliable
        """
        # Calculate confidence based on pattern strength
        confidence = min(1.0, pattern['frequency'] * 2)  # Boost frequency for confidence

        # Adjust confidence based on regularity
        if pattern['avg_interval_days'] > 0:
            # More regular patterns get higher confidence
            regularity_factor = 1.0 / (1.0 + pattern['avg_interval_days'] / 30)  # Normalize to 30 days
            confidence *= (0.7 + 0.3 * regularity_factor)

        # Apply user preferences to refine prediction
        refined_category = self._apply_category_preference(
            pattern['category'], user_preferences
        )
        refined_priority = self._apply_priority_preference(
            pattern['priority'], user_preferences
        )

        # Determine if task is likely to occur in the next days_ahead
        recent_tasks = pattern['recent_occurrences']
        if recent_tasks:
            last_occurrence = max(t.created_at for t in recent_tasks)
            days_since_last = (datetime.utcnow() - last_occurrence).days

            # If we're approaching the average interval, increase likelihood
            if days_since_last >= pattern['avg_interval_days'] * 0.8:
                confidence *= 1.5  # Increase confidence if due

        # Cap confidence at 0.95 for safety
        confidence = min(0.95, confidence)

        # Only return prediction if confidence is reasonable
        if confidence < 0.3:
            return None

        # Determine recommended action based on category
        if refined_category == "email":
            recommended_action = "monitor_inbox_and_respond"
        elif refined_category == "calendar":
            recommended_action = "schedule_and_prepare"
        elif refined_category == "finance":
            recommended_action = "review_and_approve_if_within_threshold"
        else:
            recommended_action = "process_according_to_preferences"

        return PredictionResult(
            predicted_task=pattern['title'],
            confidence=confidence,
            estimated_time=int(pattern['typical_duration']),
            category=refined_category,
            priority=refined_priority,
            recommended_action=recommended_action,
            explanation=f"Based on pattern occurring {pattern['occurrence_count']} times with avg interval of {pattern['avg_interval_days']:.1f} days"
        )

    def _apply_category_preference(self, category: str, user_preferences: List[UserPreference]) -> str:
        """
        Apply user preferences to refine category prediction

        Args:
            category: Original category
            user_preferences: User preferences

        Returns:
            Refined category
        """
        for pref in user_preferences:
            if pref.preference_key == "default_task_category" and pref.confidence_level > 0.6:
                try:
                    pref_value = self.preference_service.deserialize_preference_value(pref)
                    if isinstance(pref_value, dict) and "value" in pref_value:
                        return pref_value["value"]
                    elif isinstance(pref_value, str):
                        return pref_value
                except Exception:
                    continue

        return category

    def _apply_priority_preference(self, priority: str, user_preferences: List[UserPreference]) -> str:
        """
        Apply user preferences to refine priority prediction

        Args:
            priority: Original priority
            user_preferences: User preferences

        Returns:
            Refined priority
        """
        for pref in user_preferences:
            if pref.preference_key == "default_task_priority" and pref.confidence_level > 0.6:
                try:
                    pref_value = self.preference_service.deserialize_preference_value(pref)
                    if isinstance(pref_value, dict) and "value" in pref_value:
                        return pref_value["value"]
                    elif isinstance(pref_value, str):
                        return pref_value
                except Exception:
                    continue

        return priority

    def get_behavioral_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get behavioral insights based on user interactions and task patterns

        Args:
            user_id: User identifier

        Returns:
            Dictionary with behavioral insights
        """
        insights = {
            'productivity_patterns': {},
            'communication_style': {},
            'decision_making': {},
            'task_handling': {},
            'trends': {}
        }

        # Get user's tasks and interactions
        tasks = self.db.query(Task).filter(Task.assigned_to == user_id).all()
        interactions = self.interaction_service.get_interactions_by_user(user_id)

        # Analyze productivity patterns
        if tasks:
            insights['productivity_patterns'] = self._analyze_productivity_patterns(tasks)

        # Analyze communication style from preferences and interactions
        user_preferences = self.preference_service.get_preferences_by_user(user_id)
        insights['communication_style'] = self._analyze_communication_style(
            user_preferences, interactions
        )

        # Analyze decision making from approval interactions
        insights['decision_making'] = self._analyze_decision_making(interactions)

        # Analyze task handling patterns
        insights['task_handling'] = self._analyze_task_handling(tasks)

        # Analyze trends over time
        insights['trends'] = self._analyze_trends(tasks, interactions)

        return insights

    def _analyze_productivity_patterns(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Analyze productivity patterns from tasks
        """
        patterns = {
            'peak_performance_hours': [],
            'task_completion_rate': 0.0,
            'average_completion_time': 0,
            'preferred_categories': [],
            'efficiency_score': 0.0
        }

        if not tasks:
            return patterns

        # Calculate completion rate
        completed_tasks = [t for t in tasks if t.status == 'completed']
        patterns['task_completion_rate'] = len(completed_tasks) / len(tasks)

        # Calculate average completion time
        completion_times = []
        for task in completed_tasks:
            if task.created_at and task.completed_at:
                completion_time = (task.completed_at - task.created_at).total_seconds() / 60  # in minutes
                completion_times.append(completion_time)

        if completion_times:
            patterns['average_completion_time'] = statistics.mean(completion_times)

        # Find peak performance hours (based on completion times)
        hour_counts = defaultdict(int)
        for task in completed_tasks:
            if task.completed_at:
                hour = task.completed_at.hour
                hour_counts[hour] += 1

        if hour_counts:
            peak_hour = max(hour_counts, key=hour_counts.get)
            patterns['peak_performance_hours'] = [peak_hour]

        # Determine preferred categories
        categories = [t.category for t in tasks]
        category_counts = Counter(categories)
        patterns['preferred_categories'] = [cat for cat, _ in category_counts.most_common(3)]

        # Calculate efficiency score (completion rate * inverse of avg completion time)
        if patterns['average_completion_time'] > 0:
            patterns['efficiency_score'] = patterns['task_completion_rate'] * (
                60 / patterns['average_completion_time']  # Normalize to per-hour basis
            )
        else:
            patterns['efficiency_score'] = patterns['task_completion_rate']

        return patterns

    def _analyze_communication_style(self, user_preferences: List[UserPreference], interactions: List[InteractionLog]) -> Dict[str, Any]:
        """
        Analyze communication style from preferences and interactions
        """
        style = {
            'tone': 'professional',
            'response_length': 'medium',
            'formality_level': 'medium',
            'preferred_channels': [],
            'feedback_style': 'constructive'
        }

        # Get communication preferences
        for pref in user_preferences:
            if pref.preference_key.startswith('email_') or pref.preference_key.startswith('communication_'):
                try:
                    pref_value = self.preference_service.deserialize_preference_value(pref)
                    if isinstance(pref_value, dict):
                        for key, value in pref_value.items():
                            if key in style:
                                style[key] = value
                    elif isinstance(pref_value, str):
                        if 'communication' in pref.preference_key:
                            style['tone'] = pref_value
                except Exception:
                    continue

        # Analyze from interactions
        feedback_texts = [i.feedback_text for i in interactions if i.feedback_text]
        if feedback_texts:
            # Simple analysis of feedback style
            positive_indicators = ['good', 'well', 'excellent', 'great', 'perfect']
            negative_indicators = ['bad', 'poor', 'terrible', 'wrong', 'incorrect']

            positive_count = sum(1 for text in feedback_texts if any(indicator in text.lower() for indicator in positive_indicators))
            negative_count = sum(1 for text in feedback_texts if any(indicator in text.lower() for indicator in negative_indicators))

            if positive_count > negative_count:
                style['feedback_style'] = 'positive'
            elif negative_count > positive_count:
                style['feedback_style'] = 'critical'

        return style

    def _analyze_decision_making(self, interactions: List[InteractionLog]) -> Dict[str, Any]:
        """
        Analyze decision making patterns from approval interactions
        """
        decision_patterns = {
            'approval_rate': 0.0,
            'average_decision_time': 0,
            'risk_tolerance': 'medium',
            'decision_consistency': 0.0
        }

        if not interactions:
            return decision_patterns

        # Find approval interactions
        approval_interactions = [i for i in interactions if i.interaction_type == 'approval']

        if approval_interactions:
            approved_count = sum(1 for i in approval_interactions if i.outcome == 'positive')
            decision_patterns['approval_rate'] = approved_count / len(approval_interactions) if approval_interactions else 0

            # Calculate average decision time
            decision_times = []
            for interaction in approval_interactions:
                if interaction.timestamp:
                    # This would require knowing when the request was made
                    # For now, we'll use a placeholder
                    decision_times.append(10)  # Placeholder: 10 minutes average

            if decision_times:
                decision_patterns['average_decision_time'] = statistics.mean(decision_times)

            # Determine risk tolerance based on approval rate
            if decision_patterns['approval_rate'] > 0.8:
                decision_patterns['risk_tolerance'] = 'high'
            elif decision_patterns['approval_rate'] < 0.5:
                decision_patterns['risk_tolerance'] = 'low'
            else:
                decision_patterns['risk_tolerance'] = 'medium'

        return decision_patterns

    def _analyze_task_handling(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Analyze task handling patterns
        """
        handling_patterns = {
            'delegation_frequency': 0.0,
            'escalation_tendency': 'low',
            'task_batching_preference': 'medium',
            'quality_score': 0.0,
            'speed_vs_accuracy': 'balanced'
        }

        if not tasks:
            return handling_patterns

        # Calculate delegation frequency (tasks assigned to others vs self)
        self_assigned = sum(1 for t in tasks if t.assigned_to and 'user' in t.assigned_to.lower())
        handling_patterns['delegation_frequency'] = (len(tasks) - self_assigned) / len(tasks) if tasks else 0

        # Calculate quality score based on retries and failures
        failed_tasks = [t for t in tasks if t.status == 'failed']
        retry_tasks = [t for t in tasks if t.retry_count and t.retry_count > 0]

        # Quality is inversely related to failure and retry rates
        failure_rate = len(failed_tasks) / len(tasks)
        retry_rate = len(retry_tasks) / len(tasks)
        handling_patterns['quality_score'] = 1.0 - (failure_rate * 0.6 + retry_rate * 0.4)

        # Determine speed vs accuracy preference based on task duration and outcomes
        if handling_patterns['quality_score'] > 0.8:
            handling_patterns['speed_vs_accuracy'] = 'accuracy_focused'
        elif handling_patterns['quality_score'] < 0.5:
            handling_patterns['speed_vs_accuracy'] = 'speed_focused'
        else:
            handling_patterns['speed_vs_accuracy'] = 'balanced'

        return handling_patterns

    def _analyze_trends(self, tasks: List[Task], interactions: List[InteractionLog]) -> Dict[str, Any]:
        """
        Analyze trends in task and interaction patterns
        """
        trends = {
            'task_volume_trend': TrendDirection.STABLE,
            'productivity_trend': TrendDirection.STABLE,
            'engagement_trend': TrendDirection.STABLE,
            'learning_progress': TrendDirection.INCREASING
        }

        if not tasks:
            return trends

        # Analyze task volume trend over the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_tasks = [t for t in tasks if t.created_at and t.created_at > thirty_days_ago]

        if len(recent_tasks) >= 2:
            # Compare first half vs second half of the period
            mid_point = len(recent_tasks) // 2
            first_half = recent_tasks[:mid_point]
            second_half = recent_tasks[mid_point:]

            if len(second_half) > len(first_half) * 1.2:
                trends['task_volume_trend'] = TrendDirection.INCREASING
            elif len(second_half) < len(first_half) * 0.8:
                trends['task_volume_trend'] = TrendDirection.DECREASING

        # Analyze productivity trend based on completion rates
        if tasks:
            # Calculate completion rates for different periods
            completed_recent = len([t for t in recent_tasks if t.status == 'completed'])
            recent_rate = completed_recent / len(recent_tasks) if recent_tasks else 0

            older_tasks = [t for t in tasks if t.created_at and t.created_at <= thirty_days_ago]
            completed_older = len([t for t in older_tasks if t.status == 'completed'])
            older_rate = completed_older / len(older_tasks) if older_tasks else 0

            if recent_rate > older_rate * 1.1:
                trends['productivity_trend'] = TrendDirection.INCREASING
            elif recent_rate < older_rate * 0.9:
                trends['productivity_trend'] = TrendDirection.DECREASING

        # Engagement trend based on interaction frequency
        if interactions:
            recent_interactions = [i for i in interactions if i.timestamp and i.timestamp > thirty_days_ago]
            if len(recent_interactions) > len(interactions) * 0.6:  # More than 60% in last 30 days
                trends['engagement_trend'] = TrendDirection.INCREASING

        return trends

    def generate_personalized_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on analytics

        Args:
            user_id: User identifier

        Returns:
            List of personalized recommendations
        """
        recommendations = []

        # Get behavioral insights
        insights = self.get_behavioral_insights(user_id)

        # Generate recommendations based on insights
        if insights['productivity_patterns']['peak_performance_hours']:
            peak_hour = insights['productivity_patterns']['peak_performance_hours'][0]
            recommendations.append({
                'type': 'scheduling',
                'title': 'Optimal Scheduling Recommendation',
                'description': f'Schedule important tasks around {peak_hour}:00 when you are most productive',
                'priority': 'high'
            })

        if insights['decision_making']['risk_tolerance'] == 'low':
            recommendations.append({
                'type': 'workflow',
                'title': 'Conservative Decision Workflow',
                'description': 'Consider setting up additional approval steps for important decisions to match your cautious approach',
                'priority': 'medium'
            })

        if insights['task_handling']['delegation_frequency'] < 0.3:
            recommendations.append({
                'type': 'efficiency',
                'title': 'Delegation Opportunity',
                'description': 'Consider delegating more routine tasks to improve efficiency',
                'priority': 'medium'
            })

        if insights['productivity_patterns']['efficiency_score'] < 0.5:
            recommendations.append({
                'type': 'improvement',
                'title': 'Productivity Enhancement',
                'description': 'Focus on improving task completion efficiency through better time management',
                'priority': 'high'
            })

        # Get upcoming task predictions
        predicted_tasks = self.predict_upcoming_tasks(user_id, days_ahead=7)
        if predicted_tasks:
            top_predictions = predicted_tasks[:3]  # Top 3 predictions
            recommendations.append({
                'type': 'prediction',
                'title': 'Upcoming Task Predictions',
                'description': f'Based on patterns, you may have {len(top_predictions)} tasks coming up soon',
                'details': [pred.predicted_task for pred in top_predictions],
                'priority': 'medium'
            })

        log_activity("PERSONALIZED_RECOMMENDATIONS",
                   f"Generated {len(recommendations)} recommendations for user {user_id}",
                   "obsidian_vault")

        return recommendations
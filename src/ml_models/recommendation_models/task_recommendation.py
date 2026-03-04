"""
Task Recommendation Engine for ELYX AI Service.
Provides content-based, collaborative, and hybrid task recommendations.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskRecommendationEngine:
    """Generates task recommendations using heuristic scoring (no heavy ML deps)."""

    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._models_loaded: Dict[str, bool] = {}

    def load_model(self, model_name: str) -> bool:
        """Load a recommendation model (no-op for heuristic engine)."""
        self._models_loaded[model_name] = True
        self.logger.debug(f"Recommendation model '{model_name}' ready (heuristic mode)")
        return True

    def recommend_tasks_hybrid(self, user_id: str, user_profile: Dict[str, Any],
                                tasks_df=None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Generate hybrid recommendations combining content and collaborative signals.

        Args:
            user_id: User identifier
            user_profile: User profile with preferences
            tasks_df: DataFrame or list of task dicts
            top_k: Number of recommendations to return

        Returns:
            List of recommendation dicts with task_id, score, reason
        """
        tasks = self._df_to_list(tasks_df)
        if not tasks:
            return []

        scored = []
        preferred_categories = user_profile.get('preferred_categories', [])

        for task in tasks[:top_k]:
            score = 0.5
            reasons = []

            title = str(task.get('title', '')).lower()
            category = str(task.get('category', '')).lower()
            priority = str(task.get('priority', 'medium')).lower()

            # Boost matching categories
            if category in preferred_categories:
                score += 0.2
                reasons.append(f"Matches preferred category: {category}")

            # Boost high priority
            if priority in ('critical', 'high'):
                score += 0.15
                reasons.append(f"High priority task")

            # Boost tasks with deadlines
            if task.get('due_date'):
                score += 0.1
                reasons.append("Has a deadline")

            if not reasons:
                reasons.append("General recommendation based on workload")

            scored.append({
                'task_id': task.get('id', 'unknown'),
                'title': task.get('title', ''),
                'score': round(min(score, 1.0), 3),
                'reasons': reasons,
                'method': 'hybrid',
            })

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_k]

    def recommend_tasks_content_based(self, user_profile: Dict[str, Any],
                                       tasks_df=None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Content-based recommendations using task text similarity to user preferences.

        Args:
            user_profile: User profile with preferred keywords/categories
            tasks_df: DataFrame or list of task dicts
            top_k: Number of recommendations

        Returns:
            List of recommendation dicts
        """
        tasks = self._df_to_list(tasks_df)
        if not tasks:
            return []

        preferred_kw = set(user_profile.get('preferred_keywords', []))
        scored = []

        for task in tasks:
            title_words = set(str(task.get('title', '')).lower().split())
            desc_words = set(str(task.get('description', '')).lower().split())
            all_words = title_words | desc_words

            overlap = len(all_words & preferred_kw)
            score = min(0.4 + overlap * 0.15, 1.0)

            scored.append({
                'task_id': task.get('id', 'unknown'),
                'title': task.get('title', ''),
                'score': round(score, 3),
                'reasons': [f"Content match ({overlap} keywords)"] if overlap else ["General suggestion"],
                'method': 'content_based',
            })

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_k]

    def generate_personalized_dashboard_widgets(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized dashboard widget suggestions based on user profile.

        Args:
            user_profile: User profile with preferences and usage patterns

        Returns:
            List of widget configuration dicts
        """
        widgets = [
            {
                'widget_id': 'task_overview',
                'title': 'Task Overview',
                'type': 'summary',
                'priority': 1,
                'config': {'show_completed': True, 'show_pending': True},
            },
            {
                'widget_id': 'pending_approvals',
                'title': 'Pending Approvals',
                'type': 'list',
                'priority': 2,
                'config': {'max_items': 5},
            },
            {
                'widget_id': 'recent_activity',
                'title': 'Recent Activity',
                'type': 'timeline',
                'priority': 3,
                'config': {'days': 7},
            },
        ]

        # Add role-specific widgets
        role = user_profile.get('role', 'operator')
        if role in ('ceo', 'executive', 'manager'):
            widgets.append({
                'widget_id': 'strategic_insights',
                'title': 'Strategic Insights',
                'type': 'chart',
                'priority': 1,
                'config': {'metrics': ['productivity', 'completion_rate', 'response_time']},
            })
            widgets.append({
                'widget_id': 'financial_summary',
                'title': 'Financial Summary',
                'type': 'kpi',
                'priority': 2,
                'config': {'show_revenue': True, 'show_expenses': True},
            })

        # Add communication widgets if user uses messaging
        preferred = user_profile.get('preferred_channels', [])
        if any(ch in preferred for ch in ['whatsapp', 'email', 'linkedin']):
            widgets.append({
                'widget_id': 'communication_hub',
                'title': 'Communication Hub',
                'type': 'feed',
                'priority': 2,
                'config': {'channels': preferred},
            })

        widgets.sort(key=lambda w: w['priority'])
        return widgets

    @staticmethod
    def _df_to_list(tasks_df) -> List[Dict[str, Any]]:
        """Convert a pandas DataFrame or list to list of dicts."""
        if tasks_df is None:
            return []
        try:
            # If it's a pandas DataFrame
            if hasattr(tasks_df, 'to_dict'):
                return tasks_df.to_dict('records')
        except Exception:
            pass
        # Already a list
        if isinstance(tasks_df, list):
            return tasks_df
        return []

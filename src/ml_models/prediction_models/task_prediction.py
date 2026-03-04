"""
Task Prediction Engine for ELYX AI Service.
Predicts task completion probability, duration, priority, and resource needs.
"""
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskPredictionEngine:
    """Predicts task metrics using heuristic rules (no heavy ML deps required)."""

    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._models_loaded: Dict[str, bool] = {}

        # Priority keywords
        self._priority_keywords = {
            'critical': {'urgent', 'critical', 'emergency', 'asap', 'blocker', 'down'},
            'high': {'important', 'payment', 'invoice', 'deadline', 'overdue', 'client'},
            'medium': {'review', 'update', 'check', 'follow', 'schedule', 'report'},
            'low': {'fyi', 'optional', 'minor', 'someday', 'idea', 'nice'},
        }

        # Duration heuristics (minutes)
        self._duration_hints = {
            'email': 10, 'message': 5, 'whatsapp': 5, 'report': 60, 'meeting': 45,
            'invoice': 30, 'plan': 90, 'review': 30, 'analysis': 120, 'presentation': 180,
        }

    def load_model(self, model_name: str) -> bool:
        """Load a prediction model (no-op for heuristic engine, kept for interface compat)."""
        self._models_loaded[model_name] = True
        self.logger.debug(f"Model '{model_name}' ready (heuristic mode)")
        return True

    def predict_comprehensive_task_metrics(self, task_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict comprehensive metrics for a task.

        Args:
            task_features: Dict with title, description, category, source, created_at

        Returns:
            Dict with completion_probability, estimated_duration, priority, resource_needs, confidence_score
        """
        title = str(task_features.get('title', '')).lower()
        desc = str(task_features.get('description', '')).lower()
        category = str(task_features.get('category', 'custom')).lower()
        source = str(task_features.get('source', 'api')).lower()
        combined = f"{title} {desc}"

        priority = self._predict_priority(combined)
        duration = self._predict_duration(combined, category)
        completion = self._predict_completion_probability(combined, priority)

        return {
            'completion_probability': completion,
            'estimated_duration_minutes': duration,
            'predicted_priority': priority,
            'resource_needs': self._predict_resources(combined, category),
            'confidence_score': round(0.5 + random.uniform(0, 0.3), 3),
            'predictions': {
                'will_require_approval': any(w in combined for w in ['payment', 'contract', 'financial', 'salary']),
                'is_time_sensitive': any(w in combined for w in ['urgent', 'asap', 'deadline', 'overdue']),
                'complexity': 'high' if duration > 60 else ('medium' if duration > 20 else 'low'),
            },
            'predicted_at': datetime.now().isoformat(),
        }

    def _predict_priority(self, text: str) -> str:
        for priority, keywords in self._priority_keywords.items():
            if any(kw in text for kw in keywords):
                return priority
        return 'medium'

    def _predict_duration(self, text: str, category: str) -> int:
        # Check category first
        if category in self._duration_hints:
            return self._duration_hints[category]
        # Check text for duration hints
        for hint, minutes in self._duration_hints.items():
            if hint in text:
                return minutes
        return 30  # Default 30 minutes

    def _predict_completion_probability(self, text: str, priority: str) -> float:
        base = {'critical': 0.85, 'high': 0.75, 'medium': 0.65, 'low': 0.55}.get(priority, 0.6)
        # Slightly adjust based on text length (longer = more complex = slightly lower)
        if len(text) > 500:
            base -= 0.05
        return round(min(base + random.uniform(-0.05, 0.1), 0.99), 3)

    def _predict_resources(self, text: str, category: str) -> Dict[str, Any]:
        resources = {'human_hours': 0.5, 'automation_possible': True, 'external_deps': []}
        if any(w in text for w in ['meeting', 'call', 'discussion']):
            resources['human_hours'] = 1.0
            resources['automation_possible'] = False
        if any(w in text for w in ['api', 'integration', 'external']):
            resources['external_deps'].append('third_party_service')
        if any(w in text for w in ['email', 'gmail']):
            resources['external_deps'].append('email_service')
        return resources

    def generate_forecast(self, time_horizon_days: int = 14) -> Dict[str, Any]:
        """
        Generate a forecast for task metrics over the given horizon.

        Returns:
            Dict with daily predictions and trend info
        """
        today = datetime.now()
        daily = []
        for i in range(time_horizon_days):
            day = today + timedelta(days=i)
            daily.append({
                'date': day.strftime('%Y-%m-%d'),
                'predicted_tasks': max(1, int(5 + random.gauss(0, 2))),
                'predicted_completion_rate': round(0.7 + random.uniform(-0.1, 0.15), 3),
                'predicted_workload': round(3 + random.uniform(-1, 2), 1),
            })

        return {
            'horizon_days': time_horizon_days,
            'daily_forecast': daily,
            'trend': 'stable',
            'confidence': round(0.6 + random.uniform(0, 0.2), 3),
            'generated_at': datetime.now().isoformat(),
        }

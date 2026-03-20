"""
Interaction Log Service for Silver Tier Personal AI Employee System
Handles tracking of all interactions for learning and adaptation
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from enum import Enum

from .base_service import BaseService, ValidationError, NotFoundError
from .database import InteractionLog
from ..utils.logger import log_activity


class InteractionType(Enum):
    APPROVAL = "approval"
    CORRECTION = "correction"
    FEEDBACK = "feedback"
    OVERRIDE = "override"
    QUERY = "query"


class InteractionService(BaseService[InteractionLog]):
    """
    Interaction Service for Silver Tier with learning capabilities
    """

    def __init__(self, db_session: Session):
        super().__init__(db_session, InteractionLog)

    def create_interaction(self,
                          user_id: str,
                          interaction_type: str,
                          action_taken: str,
                          system_response: str,
                          task_id: Optional[str] = None,
                          context_snapshot: Optional[Dict] = None,
                          outcome: str = "neutral",
                          feedback_text: Optional[str] = None) -> InteractionLog:
        """
        Create a new interaction log entry

        Args:
            user_id: User identifier
            interaction_type: Type of interaction (approval, correction, feedback, override, query)
            action_taken: Description of user action
            system_response: Description of system behavior
            task_id: Associated task ID (optional)
            context_snapshot: System state at time of interaction
            outcome: Outcome of interaction (positive, negative, neutral)
            feedback_text: User feedback text (optional)

        Returns:
            The created InteractionLog object
        """
        # Validate inputs
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        if interaction_type not in [it.value for it in InteractionType]:
            raise ValidationError(f"Invalid interaction type: {interaction_type}")

        if outcome not in ["positive", "negative", "neutral"]:
            raise ValidationError(f"Invalid outcome: {outcome}")

        # Validate context snapshot is JSON-compatible (column is JSON type,
        # so SQLAlchemy handles serialization — don't double-encode with json.dumps)
        serialized_context = None
        if context_snapshot:
            try:
                json.dumps(context_snapshot)  # validate only
                serialized_context = context_snapshot
            except TypeError as e:
                raise ValidationError(f"Context snapshot is not JSON serializable: {str(e)}")

        # Create interaction log object
        interaction = InteractionLog(
            user_id=user_id,
            interaction_type=interaction_type,
            task_id=task_id,
            action_taken=action_taken,
            system_response=system_response,
            context_snapshot=serialized_context,
            outcome=outcome,
            feedback_text=feedback_text,
            learning_applied=False,  # Initially not applied to learning
            timestamp=datetime.utcnow()
        )

        # Log the creation
        log_activity("INTERACTION_LOGGED",
                   f"Interaction of type '{interaction_type}' logged for user '{user_id}'",
                   "obsidian_vault")

        return self.create(interaction)

    def get_interactions_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[InteractionLog]:
        """
        Get all interactions for a specific user

        Args:
            user_id: User identifier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of InteractionLog objects for the user
        """
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id
        ).offset(skip).limit(limit).all()

        return interactions

    def get_interactions_by_type(self, user_id: str, interaction_type: str,
                                skip: int = 0, limit: int = 100) -> List[InteractionLog]:
        """
        Get all interactions of a specific type for a user

        Args:
            user_id: User identifier
            interaction_type: Type of interactions to get
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of InteractionLog objects
        """
        if interaction_type not in [it.value for it in InteractionType]:
            raise ValidationError(f"Invalid interaction type: {interaction_type}")

        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id,
            InteractionLog.interaction_type == interaction_type
        ).offset(skip).limit(limit).all()

        return interactions

    def get_interactions_by_outcome(self, user_id: str, outcome: str,
                                   skip: int = 0, limit: int = 100) -> List[InteractionLog]:
        """
        Get all interactions with a specific outcome for a user

        Args:
            user_id: User identifier
            outcome: Outcome to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of InteractionLog objects
        """
        if outcome not in ["positive", "negative", "neutral"]:
            raise ValidationError(f"Invalid outcome: {outcome}")

        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id,
            InteractionLog.outcome == outcome
        ).offset(skip).limit(limit).all()

        return interactions

    def get_interactions_by_date_range(self, user_id: str, start_date: datetime,
                                      end_date: datetime) -> List[InteractionLog]:
        """
        Get all interactions within a date range for a user

        Args:
            user_id: User identifier
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of InteractionLog objects
        """
        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id,
            InteractionLog.timestamp >= start_date,
            InteractionLog.timestamp <= end_date
        ).all()

        return interactions

    def get_interactions_by_task(self, task_id: str) -> List[InteractionLog]:
        """
        Get all interactions associated with a specific task

        Args:
            task_id: Task identifier

        Returns:
            List of InteractionLog objects
        """
        if not task_id or len(task_id.strip()) == 0:
            raise ValidationError("Task ID is required")

        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.task_id == task_id
        ).all()

        return interactions

    def mark_learning_applied(self, interaction_id: str) -> Optional[InteractionLog]:
        """
        Mark that learning has been applied from a specific interaction

        Args:
            interaction_id: ID of the interaction

        Returns:
            Updated InteractionLog object, or None if not found
        """
        interaction = self.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundError("InteractionLog", interaction_id)

        interaction.learning_applied = True

        try:
            self.db.commit()
            self.db.refresh(interaction)

            log_activity("INTERACTION_LEARNING_APPLIED",
                       f"Learning applied from interaction {interaction_id}",
                       "obsidian_vault")

            return interaction
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error marking learning applied: {str(e)}")
            raise

    def get_unapplied_learning_interactions(self, user_id: str) -> List[InteractionLog]:
        """
        Get all interactions for a user that haven't had learning applied

        Args:
            user_id: User identifier

        Returns:
            List of InteractionLog objects with learning not applied
        """
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id,
            InteractionLog.learning_applied == False
        ).all()

        return interactions

    def get_interaction_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics about interactions for a user

        Args:
            user_id: User identifier

        Returns:
            Dictionary with interaction statistics
        """
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        stats = {}

        # Count by interaction type
        stats['by_type'] = {}
        for itype in [it.value for it in InteractionType]:
            stats['by_type'][itype] = self.db.query(InteractionLog).filter(
                InteractionLog.user_id == user_id,
                InteractionLog.interaction_type == itype
            ).count()

        # Count by outcome
        stats['by_outcome'] = {}
        for outcome in ["positive", "negative", "neutral"]:
            stats['by_outcome'][outcome] = self.db.query(InteractionLog).filter(
                InteractionLog.user_id == user_id,
                InteractionLog.outcome == outcome
            ).count()

        # Count total interactions
        stats['total'] = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id
        ).count()

        # Count applied vs unapplied learning
        stats['learning_applied'] = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id,
            InteractionLog.learning_applied == True
        ).count()

        stats['learning_not_applied'] = stats['total'] - stats['learning_applied']

        # Calculate positive/negative ratio
        pos_count = stats['by_outcome']['positive']
        neg_count = stats['by_outcome']['negative']
        if pos_count + neg_count > 0:
            stats['positive_negative_ratio'] = pos_count / (pos_count + neg_count)
        else:
            stats['positive_negative_ratio'] = 0.5  # Neutral if no positive/negative interactions

        # Get recent interactions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stats['recent_interactions'] = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id,
            InteractionLog.timestamp >= thirty_days_ago
        ).count()

        return stats

    def get_feedback_interactions(self, user_id: str) -> List[InteractionLog]:
        """
        Get all feedback interactions for a user

        Args:
            user_id: User identifier

        Returns:
            List of InteractionLog objects with feedback
        """
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.user_id == user_id,
            InteractionLog.interaction_type == "feedback",
            InteractionLog.feedback_text.isnot(None),
            InteractionLog.feedback_text != ""
        ).all()

        return interactions

    def get_pattern_from_interactions(self, user_id: str, interaction_type: str) -> Dict[str, Any]:
        """
        Analyze patterns from interactions of a specific type for a user

        Args:
            user_id: User identifier
            interaction_type: Type of interaction to analyze

        Returns:
            Dictionary with pattern analysis
        """
        if interaction_type not in [it.value for it in InteractionType]:
            raise ValidationError(f"Invalid interaction type: {interaction_type}")

        interactions = self.get_interactions_by_type(user_id, interaction_type)

        if not interactions:
            return {
                'count': 0,
                'most_common_outcome': None,
                'average_context_complexity': 0,
                'trends': []
            }

        # Analyze patterns
        outcome_counts = {}
        context_sizes = []

        for interaction in interactions:
            outcome = interaction.outcome
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

            # Estimate context complexity by the size of the context snapshot
            if interaction.context_snapshot:
                try:
                    context_dict = json.loads(interaction.context_snapshot)
                    context_sizes.append(len(json.dumps(context_dict)))
                except json.JSONDecodeError:
                    context_sizes.append(0)

        most_common_outcome = max(outcome_counts, key=outcome_counts.get) if outcome_counts else None

        avg_context_size = sum(context_sizes) / len(context_sizes) if context_sizes else 0

        # Look for temporal trends (simple analysis)
        interactions.sort(key=lambda x: x.timestamp)
        recent_outcomes = [i.outcome for i in interactions[-5:]]  # Last 5 interactions
        older_outcomes = [i.outcome for i in interactions[:5]]   # First 5 interactions

        trend = "stable"
        if recent_outcomes and older_outcomes:
            recent_positive = recent_outcomes.count("positive")
            older_positive = older_outcomes.count("positive")

            if recent_positive > older_positive:
                trend = "improving"
            elif recent_positive < older_positive:
                trend = "declining"

        return {
            'count': len(interactions),
            'most_common_outcome': most_common_outcome,
            'average_context_complexity': avg_context_size,
            'trends': [trend],
            'outcome_distribution': outcome_counts
        }

    def deserialize_context_snapshot(self, interaction: InteractionLog) -> Optional[Dict]:
        """
        Helper method to deserialize the context snapshot

        Args:
            interaction: InteractionLog object

        Returns:
            Deserialized context snapshot or None
        """
        if not interaction.context_snapshot:
            return None

        try:
            return json.loads(interaction.context_snapshot)
        except json.JSONDecodeError:
            self.logger.error(f"Error deserializing context snapshot: {interaction.context_snapshot}")
            return None

    def aggregate_interactions_for_model_training(self, user_id: str) -> Dict[str, Any]:
        """
        Prepare interaction data for model training

        Args:
            user_id: User identifier

        Returns:
            Dictionary with aggregated interaction data for training
        """
        all_interactions = self.get_interactions_by_user(user_id)

        # Group interactions by type and outcome
        training_data = {
            'user_id': user_id,
            'interaction_types': {},
            'outcomes_by_type': {},
            'common_patterns': {},
            'feedback_analysis': {
                'positive_feedback': [],
                'negative_feedback': [],
                'neutral_feedback': []
            }
        }

        for interaction in all_interactions:
            # Group by type
            itype = interaction.interaction_type
            if itype not in training_data['interaction_types']:
                training_data['interaction_types'][itype] = 0
            training_data['interaction_types'][itype] += 1

            # Group outcomes by type
            if itype not in training_data['outcomes_by_type']:
                training_data['outcomes_by_type'][itype] = {}
            outcome = interaction.outcome
            if outcome not in training_data['outcomes_by_type'][itype]:
                training_data['outcomes_by_type'][itype][outcome] = 0
            training_data['outcomes_by_type'][itype][outcome] += 1

            # Collect feedback
            if interaction.feedback_text:
                if interaction.outcome == "positive":
                    training_data['feedback_analysis']['positive_feedback'].append(interaction.feedback_text)
                elif interaction.outcome == "negative":
                    training_data['feedback_analysis']['negative_feedback'].append(interaction.feedback_text)
                else:
                    training_data['feedback_analysis']['neutral_feedback'].append(interaction.feedback_text)

        # Identify common patterns
        for itype, count in training_data['interaction_types'].items():
            if count > 1:  # Only consider types that occurred more than once
                pattern_analysis = self.get_pattern_from_interactions(user_id, itype)
                training_data['common_patterns'][itype] = pattern_analysis

        return training_data
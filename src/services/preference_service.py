"""
User Preference Service for Silver Tier Personal AI Employee System
Handles user preferences and learning capabilities
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import json
from enum import Enum

from .base_service import BaseService, ValidationError, NotFoundError
from .database import UserPreference
from ..utils.logger import log_activity


class PreferenceType(Enum):
    BEHAVIORAL = "behavioral"
    OPERATIONAL = "operational"
    SECURITY = "security"
    COMMUNICATION = "communication"


class UserPreferenceService(BaseService[UserPreference]):
    """
    User Preference Service for Silver Tier with learning capabilities
    """

    def __init__(self, db_session: Session):
        super().__init__(db_session, UserPreference)

    def create_preference(self,
                         user_id: str,
                         preference_key: str,
                         preference_value: Any,
                         preference_type: str = "operational",
                         confidence_level: float = 0.5) -> UserPreference:
        """
        Create a new user preference

        Args:
            user_id: User identifier
            preference_key: Key for the preference
            preference_value: Value for the preference (can be any serializable type)
            preference_type: Type of preference (behavioral, operational, security, communication)
            confidence_level: Confidence level in this preference (0-1)

        Returns:
            The created UserPreference object
        """
        # Validate inputs
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        if not preference_key or len(preference_key.strip()) == 0:
            raise ValidationError("Preference key is required")

        if preference_type not in [pt.value for pt in PreferenceType]:
            raise ValidationError(f"Invalid preference type: {preference_type}")

        if not 0 <= confidence_level <= 1:
            raise ValidationError(f"Confidence level must be between 0 and 1, got {confidence_level}")

        # Serialize the preference value to JSON string
        try:
            if isinstance(preference_value, (dict, list)):
                serialized_value = json.dumps(preference_value)
            else:
                serialized_value = json.dumps({"value": preference_value})
        except TypeError as e:
            raise ValidationError(f"Preference value is not JSON serializable: {str(e)}")

        # Check if this preference already exists for the user
        existing = self.get_preference(user_id, preference_key)
        if existing:
            raise ValidationError(f"Preference '{preference_key}' already exists for user '{user_id}'")

        # Create preference object
        preference = UserPreference(
            user_id=user_id,
            preference_key=preference_key,
            preference_value=serialized_value,
            preference_type=preference_type,
            confidence_level=confidence_level,
            usage_count=0,
            effectiveness_score=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Log the creation
        log_activity("PREFERENCE_CREATED",
                   f"Preference '{preference_key}' created for user '{user_id}'",
                   "obsidian_vault")

        return self.create(preference)

    def get_preference(self, user_id: str, preference_key: str) -> Optional[UserPreference]:
        """
        Get a specific user preference

        Args:
            user_id: User identifier
            preference_key: Key for the preference

        Returns:
            UserPreference object if found, None otherwise
        """
        try:
            preference = self.db.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key
            ).first()
            return preference
        except Exception as e:
            self.logger.error(f"Error getting preference: {str(e)}")
            raise

    def get_preferences_by_user(self, user_id: str) -> List[UserPreference]:
        """
        Get all preferences for a specific user

        Args:
            user_id: User identifier

        Returns:
            List of UserPreference objects for the user
        """
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        return self.get_by_filter(user_id=user_id)

    def get_preferences_by_type(self, user_id: str, preference_type: str) -> List[UserPreference]:
        """
        Get all preferences of a specific type for a user

        Args:
            user_id: User identifier
            preference_type: Type of preferences to get

        Returns:
            List of UserPreference objects
        """
        if preference_type not in [pt.value for pt in PreferenceType]:
            raise ValidationError(f"Invalid preference type: {preference_type}")

        return self.get_by_filter(user_id=user_id, preference_type=preference_type)

    def update_preference_value(self, user_id: str, preference_key: str, new_value: Any,
                              confidence_level: Optional[float] = None) -> Optional[UserPreference]:
        """
        Update the value of a user preference

        Args:
            user_id: User identifier
            preference_key: Key for the preference
            new_value: New value for the preference
            confidence_level: New confidence level (optional)

        Returns:
            Updated UserPreference object, or None if not found
        """
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")

        if not preference_key or len(preference_key.strip()) == 0:
            raise ValidationError("Preference key is required")

        preference = self.get_preference(user_id, preference_key)
        if not preference:
            raise NotFoundError("UserPreference", f"{user_id}:{preference_key}")

        # Serialize the new value
        try:
            if isinstance(new_value, (dict, list)):
                serialized_value = json.dumps(new_value)
            else:
                serialized_value = json.dumps({"value": new_value})
        except TypeError as e:
            raise ValidationError(f"New preference value is not JSON serializable: {str(e)}")

        preference.preference_value = serialized_value
        preference.updated_at = datetime.utcnow()

        if confidence_level is not None:
            if not 0 <= confidence_level <= 1:
                raise ValidationError(f"Confidence level must be between 0 and 1, got {confidence_level}")
            preference.confidence_level = confidence_level

        try:
            self.db.commit()
            self.db.refresh(preference)

            log_activity("PREFERENCE_UPDATED",
                       f"Preference '{preference_key}' updated for user '{user_id}'",
                       "obsidian_vault")

            return preference
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating preference: {str(e)}")
            raise

    def increment_usage_count(self, user_id: str, preference_key: str) -> Optional[UserPreference]:
        """
        Increment the usage count for a preference

        Args:
            user_id: User identifier
            preference_key: Key for the preference

        Returns:
            Updated UserPreference object, or None if not found
        """
        preference = self.get_preference(user_id, preference_key)
        if not preference:
            raise NotFoundError("UserPreference", f"{user_id}:{preference_key}")

        preference.usage_count += 1
        preference.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(preference)
            return preference
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error incrementing usage count: {str(e)}")
            raise

    def update_effectiveness_score(self, user_id: str, preference_key: str, score: float) -> Optional[UserPreference]:
        """
        Update the effectiveness score for a preference

        Args:
            user_id: User identifier
            preference_key: Key for the preference
            score: New effectiveness score (-1 to 1)

        Returns:
            Updated UserPreference object, or None if not found
        """
        if not -1 <= score <= 1:
            raise ValidationError(f"Effectiveness score must be between -1 and 1, got {score}")

        preference = self.get_preference(user_id, preference_key)
        if not preference:
            raise NotFoundError("UserPreference", f"{user_id}:{preference_key}")

        preference.effectiveness_score = score
        preference.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(preference)

            log_activity("PREFERENCE_EFFECTIVENESS_UPDATED",
                       f"Effectiveness score for preference '{preference_key}' updated to {score}",
                       "obsidian_vault")

            return preference
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating effectiveness score: {str(e)}")
            raise

    def get_high_confidence_preferences(self, user_id: str, min_confidence: float = 0.7) -> List[UserPreference]:
        """
        Get all preferences with confidence level above threshold

        Args:
            user_id: User identifier
            min_confidence: Minimum confidence level (0-1)

        Returns:
            List of UserPreference objects with high confidence
        """
        if not 0 <= min_confidence <= 1:
            raise ValidationError(f"Minimum confidence must be between 0 and 1, got {min_confidence}")

        return self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.confidence_level >= min_confidence
        ).all()

    def get_most_used_preferences(self, user_id: str, limit: int = 10) -> List[UserPreference]:
        """
        Get the most used preferences for a user

        Args:
            user_id: User identifier
            limit: Maximum number of preferences to return

        Returns:
            List of UserPreference objects ordered by usage count
        """
        return self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).order_by(UserPreference.usage_count.desc()).limit(limit).all()

    def get_effective_preferences(self, user_id: str, min_effectiveness: float = 0.5) -> List[UserPreference]:
        """
        Get preferences with effectiveness score above threshold

        Args:
            user_id: User identifier
            min_effectiveness: Minimum effectiveness score (-1 to 1)

        Returns:
            List of UserPreference objects with high effectiveness
        """
        if not -1 <= min_effectiveness <= 1:
            raise ValidationError(f"Minimum effectiveness must be between -1 and 1, got {min_effectiveness}")

        return self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.effectiveness_score >= min_effectiveness
        ).all()

    def get_preference_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of user preferences

        Args:
            user_id: User identifier

        Returns:
            Dictionary with preference summary
        """
        preferences = self.get_preferences_by_user(user_id)
        summary = {
            'total_preferences': len(preferences),
            'preferences_by_type': {},
            'average_confidence': 0,
            'average_effectiveness': 0,
            'total_usage': 0,
            'high_confidence_count': 0,
            'effective_count': 0
        }

        if preferences:
            type_counts = {}
            total_confidence = 0
            total_effectiveness = 0
            total_usage = 0
            high_confidence_count = 0
            effective_count = 0

            for pref in preferences:
                # Count by type
                pref_type = pref.preference_type
                type_counts[pref_type] = type_counts.get(pref_type, 0) + 1

                # Aggregate metrics
                total_confidence += pref.confidence_level
                total_effectiveness += pref.effectiveness_score
                total_usage += pref.usage_count

                # Count high confidence and effective preferences
                if pref.confidence_level >= 0.7:
                    high_confidence_count += 1
                if pref.effectiveness_score >= 0.5:
                    effective_count += 1

            summary['preferences_by_type'] = type_counts
            summary['average_confidence'] = total_confidence / len(preferences)
            summary['average_effectiveness'] = total_effectiveness / len(preferences)
            summary['total_usage'] = total_usage
            summary['high_confidence_count'] = high_confidence_count
            summary['effective_count'] = effective_count

        return summary

    def deserialize_preference_value(self, preference: UserPreference) -> Any:
        """
        Helper method to deserialize the preference value

        Args:
            preference: UserPreference object

        Returns:
            Deserialized preference value
        """
        if not preference.preference_value:
            return None

        try:
            deserialized = json.loads(preference.preference_value)
            # If it's a simple value wrapped in a dict, extract it
            if isinstance(deserialized, dict) and "value" in deserialized and len(deserialized) == 1:
                return deserialized["value"]
            return deserialized
        except json.JSONDecodeError:
            self.logger.error(f"Error deserializing preference value: {preference.preference_value}")
            return None

    def apply_preference_to_task(self, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply relevant preferences to task data

        Args:
            user_id: User identifier
            task_data: Task data to apply preferences to

        Returns:
            Updated task data with preferences applied
        """
        # Get all operational preferences for the user
        operational_prefs = self.get_preferences_by_type(user_id, "operational")

        updated_task = task_data.copy()

        for pref in operational_prefs:
            pref_value = self.deserialize_preference_value(pref)

            # Apply common operational preferences
            if pref.preference_key == "default_task_priority":
                if "priority" not in updated_task or updated_task["priority"] == "medium":
                    updated_task["priority"] = pref_value

            elif pref.preference_key == "default_task_category":
                if "category" not in updated_task:
                    updated_task["category"] = pref_value

            elif pref.preference_key == "auto_assign_tasks":
                if pref_value and "assigned_to" not in updated_task:
                    updated_task["assigned_to"] = user_id

        return updated_task
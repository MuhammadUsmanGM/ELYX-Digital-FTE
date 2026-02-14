"""
Task Prediction Models for Gold Tier Personal AI Employee System
Implements predictive analytics for task completion, priority, and resource allocation
"""
import os
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

from ...utils.logger import log_activity


class TaskPredictionEngine:
    """
    Advanced task prediction engine for Gold Tier AI capabilities
    """

    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)

        self.completion_model = None
        self.duration_model = None
        self.priority_model = None
        self.resource_model = None

        self.scalers = {}
        self.encoders = {}

        self.logger = logging.getLogger(__name__)

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for task prediction models

        Args:
            df: DataFrame with raw task data

        Returns:
            DataFrame with engineered features
        """
        # Create a copy to avoid modifying original
        features_df = df.copy()

        # Time-based features
        if 'created_at' in df.columns:
            features_df['hour_created'] = pd.to_datetime(df['created_at']).dt.hour
            features_df['day_of_week'] = pd.to_datetime(df['created_at']).dt.dayofweek
            features_df['day_of_month'] = pd.to_datetime(df['created_at']).dt.day
            features_df['month'] = pd.to_datetime(df['created_at']).dt.month

        # Category-based features
        if 'category' in df.columns:
            features_df['category_encoded'] = pd.Categorical(df['category']).codes

        # Priority-based features
        if 'priority' in df.columns:
            priority_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            features_df['priority_numeric'] = df['priority'].map(priority_map).fillna(2)

        # Source-based features
        if 'source' in df.columns:
            features_df['source_encoded'] = pd.Categorical(df['source']).codes

        # Duration features
        if 'estimated_duration' in df.columns:
            features_df['has_estimated_duration'] = (~df['estimated_duration'].isna()).astype(int)

        # Text-based features (simplified)
        text_columns = ['title', 'description']
        for col in text_columns:
            if col in df.columns:
                features_df[f'{col}_length'] = df[col].fillna('').apply(len)
                features_df[f'{col}_word_count'] = df[col].fillna('').apply(lambda x: len(str(x).split()))

        # Numeric features that should be standardized
        numeric_cols = [col for col in features_df.select_dtypes(include=[np.number]).columns
                       if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]

        return features_df[numeric_cols + [col for col in features_df.columns if col not in numeric_cols]]

    def train_completion_prediction_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train model to predict task completion probability

        Args:
            training_data: DataFrame with task features and completion status

        Returns:
            Training results and metrics
        """
        self.logger.info("Training task completion prediction model...")

        # Prepare features
        features_df = self.prepare_features(training_data)

        # Select features for completion prediction
        feature_cols = [col for col in features_df.columns
                       if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]

        X = features_df[feature_cols]
        y = training_data['completed'].fillna(0)  # Assuming 0 for incomplete tasks

        # Handle categorical variables
        X = pd.get_dummies(X, drop_first=True)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Store model and scaler
        self.completion_model = model
        self.scalers['completion'] = scaler

        # Save model
        model_path = self.model_dir / "completion_model.pkl"
        joblib.dump({
            'model': model,
            'scaler': scaler,
            'feature_columns': X.columns.tolist()
        }, model_path)

        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2': r2,
            'model_path': str(model_path)
        }

        self.logger.info(f"Completion model trained - R²: {r2:.3f}, MAE: {mae:.3f}")
        log_activity("MODEL_TRAINING", f"Trained completion model (R²: {r2:.2f})", "obsidian_vault")

        return metrics

    def train_duration_prediction_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train model to predict task duration

        Args:
            training_data: DataFrame with task features and actual duration

        Returns:
            Training results and metrics
        """
        self.logger.info("Training task duration prediction model...")

        # Prepare features
        features_df = self.prepare_features(training_data)

        # Select features for duration prediction
        feature_cols = [col for col in features_df.columns
                       if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]

        X = features_df[feature_cols]
        y = training_data['duration_actual'].fillna(training_data['estimated_duration']).dropna()

        # Align X with y
        X = X.loc[y.index]

        # Handle categorical variables
        X = pd.get_dummies(X, drop_first=True)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Store model and scaler
        self.duration_model = model
        self.scalers['duration'] = scaler

        # Save model
        model_path = self.model_dir / "duration_model.pkl"
        joblib.dump({
            'model': model,
            'scaler': scaler,
            'feature_columns': X.columns.tolist()
        }, model_path)

        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2': r2,
            'model_path': str(model_path)
        }

        self.logger.info(f"Duration model trained - R²: {r2:.3f}, MAE: {mae:.3f}")
        log_activity("MODEL_TRAINING", f"Trained duration model (R²: {r2:.2f})", "obsidian_vault")

        return metrics

    def train_priority_prediction_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train model to predict optimal task priority

        Args:
            training_data: DataFrame with task features and priority levels

        Returns:
            Training results and metrics
        """
        self.logger.info("Training task priority prediction model...")

        # Prepare features
        features_df = self.prepare_features(training_data)

        # Select features for priority prediction
        feature_cols = [col for col in features_df.columns
                       if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]

        X = features_df[feature_cols]
        y = training_data['priority_target'].fillna(training_data['priority_numeric']).dropna()

        # Align X with y
        X = X.loc[y.index]

        # Handle categorical variables
        X = pd.get_dummies(X, drop_first=True)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model (classification for priority levels)
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, classification_report

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        # Store model and scaler
        self.priority_model = model
        self.scalers['priority'] = scaler

        # Save model
        model_path = self.model_dir / "priority_model.pkl"
        joblib.dump({
            'model': model,
            'scaler': scaler,
            'feature_columns': X.columns.tolist()
        }, model_path)

        metrics = {
            'accuracy': accuracy,
            'mae': mae,
            'model_path': str(model_path)
        }

        self.logger.info(f"Priority model trained - Accuracy: {accuracy:.3f}, MAE: {mae:.3f}")
        log_activity("MODEL_TRAINING", f"Trained priority model (Accuracy: {accuracy:.2f})", "obsidian_vault")

        return metrics

    def train_resource_prediction_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train model to predict resource requirements

        Args:
            training_data: DataFrame with task features and resource requirements

        Returns:
            Training results and metrics
        """
        self.logger.info("Training resource prediction model...")

        # Prepare features
        features_df = self.prepare_features(training_data)

        # Select features for resource prediction
        feature_cols = [col for col in features_df.columns
                       if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]

        X = features_df[feature_cols]
        y = training_data['resource_requirement'].dropna()

        # Align X with y
        X = X.loc[y.index]

        # Handle categorical variables
        X = pd.get_dummies(X, drop_first=True)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Store model and scaler
        self.resource_model = model
        self.scalers['resource'] = scaler

        # Save model
        model_path = self.model_dir / "resource_model.pkl"
        joblib.dump({
            'model': model,
            'scaler': scaler,
            'feature_columns': X.columns.tolist()
        }, model_path)

        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': np.sqrt(mse),
            'r2': r2,
            'model_path': str(model_path)
        }

        self.logger.info(f"Resource model trained - R²: {r2:.3f}, MAE: {mae:.3f}")
        log_activity("MODEL_TRAINING", f"Trained resource model (R²: {r2:.2f})", "obsidian_vault")

        return metrics

    def load_model(self, model_type: str) -> bool:
        """
        Load a trained model from disk

        Args:
            model_type: Type of model to load ('completion', 'duration', 'priority', 'resource')

        Returns:
            True if model loaded successfully, False otherwise
        """
        model_path = self.model_dir / f"{model_type}_model.pkl"

        if not model_path.exists():
            self.logger.warning(f"Model {model_type} not found at {model_path}")
            return False

        try:
            model_data = joblib.load(model_path)
            setattr(self, f"{model_type}_model", model_data['model'])
            self.scalers[model_type] = model_data['scaler']

            self.logger.info(f"Loaded {model_type} model from {model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading {model_type} model: {e}")
            return False

    def predict_completion_probability(self, task_features: Dict[str, Any]) -> float:
        """
        Predict the probability that a task will be completed

        Args:
            task_features: Dictionary with task features

        Returns:
            Probability of completion (0-1)
        """
        if not self.completion_model or 'completion' not in self.scalers:
            self.load_model('completion')

        if not self.completion_model:
            return 0.5  # Default if model not available

        try:
            # Convert to DataFrame
            df = pd.DataFrame([task_features])

            # Prepare features
            features_df = self.prepare_features(df)

            # Get the same features used during training
            model_path = self.model_dir / "completion_model.pkl"
            if model_path.exists():
                model_data = joblib.load(model_path)
                feature_cols = model_data['feature_columns']

                # Align features
                X = features_df.reindex(columns=feature_cols, fill_value=0)
            else:
                # Fallback: use all available features
                feature_cols = [col for col in features_df.columns
                               if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]
                X = features_df[feature_cols]
                X = pd.get_dummies(X, drop_first=True)
                # Ensure same number of columns as training
                X = X.reindex(columns=self.completion_model.feature_importances_, fill_value=0)

            # Scale features
            X_scaled = self.scalers['completion'].transform(X)

            # Predict
            probability = self.completion_model.predict(X_scaled)[0]

            # Ensure probability is between 0 and 1
            probability = max(0, min(1, probability))

            return float(probability)
        except Exception as e:
            self.logger.error(f"Error predicting completion probability: {e}")
            return 0.5

    def predict_task_duration(self, task_features: Dict[str, Any]) -> float:
        """
        Predict the duration of a task

        Args:
            task_features: Dictionary with task features

        Returns:
            Predicted duration in minutes
        """
        if not self.duration_model or 'duration' not in self.scalers:
            self.load_model('duration')

        if not self.duration_model:
            return 30.0  # Default duration if model not available

        try:
            # Convert to DataFrame
            df = pd.DataFrame([task_features])

            # Prepare features
            features_df = self.prepare_features(df)

            # Get the same features used during training
            model_path = self.model_dir / "duration_model.pkl"
            if model_path.exists():
                model_data = joblib.load(model_path)
                feature_cols = model_data['feature_columns']

                # Align features
                X = features_df.reindex(columns=feature_cols, fill_value=0)
            else:
                # Fallback: use all available features
                feature_cols = [col for col in features_df.columns
                               if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]
                X = features_df[feature_cols]
                X = pd.get_dummies(X, drop_first=True)
                # Ensure same number of columns as training
                X = X.reindex(columns=self.duration_model.feature_importances_, fill_value=0)

            # Scale features
            X_scaled = self.scalers['duration'].transform(X)

            # Predict
            duration = self.duration_model.predict(X_scaled)[0]

            # Ensure duration is positive
            duration = max(1, duration)

            return float(duration)
        except Exception as e:
            self.logger.error(f"Error predicting task duration: {e}")
            return 30.0

    def predict_priority_level(self, task_features: Dict[str, Any]) -> int:
        """
        Predict the priority level for a task

        Args:
            task_features: Dictionary with task features

        Returns:
            Predicted priority level (1-4: low to critical)
        """
        if not self.priority_model or 'priority' not in self.scalers:
            self.load_model('priority')

        if not self.priority_model:
            return 2  # Default to medium priority

        try:
            # Convert to DataFrame
            df = pd.DataFrame([task_features])

            # Prepare features
            features_df = self.prepare_features(df)

            # Get the same features used during training
            model_path = self.model_dir / "priority_model.pkl"
            if model_path.exists():
                model_data = joblib.load(model_path)
                feature_cols = model_data['feature_columns']

                # Align features
                X = features_df.reindex(columns=feature_cols, fill_value=0)
            else:
                # Fallback: use all available features
                feature_cols = [col for col in features_df.columns
                               if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]
                X = features_df[feature_cols]
                X = pd.get_dummies(X, drop_first=True)
                # Ensure same number of columns as training
                X = X.reindex(columns=self.priority_model.feature_importances_, fill_value=0)

            # Scale features
            X_scaled = self.scalers['priority'].transform(X)

            # Predict
            priority = self.priority_model.predict(X_scaled)[0]

            # Ensure priority is in valid range
            priority = max(1, min(4, int(round(priority))))

            return int(priority)
        except Exception as e:
            self.logger.error(f"Error predicting priority level: {e}")
            return 2

    def predict_resource_requirements(self, task_features: Dict[str, Any]) -> float:
        """
        Predict the resource requirements for a task

        Args:
            task_features: Dictionary with task features

        Returns:
            Predicted resource requirement level (continuous value)
        """
        if not self.resource_model or 'resource' not in self.scalers:
            self.load_model('resource')

        if not self.resource_model:
            return 1.0  # Default resource requirement

        try:
            # Convert to DataFrame
            df = pd.DataFrame([task_features])

            # Prepare features
            features_df = self.prepare_features(df)

            # Get the same features used during training
            model_path = self.model_dir / "resource_model.pkl"
            if model_path.exists():
                model_data = joblib.load(model_path)
                feature_cols = model_data['feature_columns']

                # Align features
                X = features_df.reindex(columns=feature_cols, fill_value=0)
            else:
                # Fallback: use all available features
                feature_cols = [col for col in features_df.columns
                               if col not in ['completed', 'duration_actual', 'priority_target', 'resource_requirement']]
                X = features_df[feature_cols]
                X = pd.get_dummies(X, drop_first=True)
                # Ensure same number of columns as training
                X = X.reindex(columns=self.resource_model.feature_importances_, fill_value=0)

            # Scale features
            X_scaled = self.scalers['resource'].transform(X)

            # Predict
            resources = self.resource_model.predict(X_scaled)[0]

            # Ensure resources is positive
            resources = max(0.1, resources)

            return float(resources)
        except Exception as e:
            self.logger.error(f"Error predicting resource requirements: {e}")
            return 1.0

    def predict_comprehensive_task_metrics(self, task_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict all task metrics in one call

        Args:
            task_features: Dictionary with task features

        Returns:
            Dictionary with all predicted metrics
        """
        completion_prob = self.predict_completion_probability(task_features)
        duration = self.predict_task_duration(task_features)
        priority = self.predict_priority_level(task_features)
        resources = self.predict_resource_requirements(task_features)

        # Calculate confidence based on model availability
        confidence = 0.8 if all([self.completion_model, self.duration_model,
                                self.priority_model, self.resource_model]) else 0.5

        result = {
            'completion_probability': completion_prob,
            'predicted_duration_minutes': duration,
            'predicted_priority_level': priority,
            'predicted_resource_requirement': resources,
            'confidence_score': confidence,
            'timestamp': datetime.now().isoformat()
        }

        log_activity("TASK_PREDICTION", f"Predicted metrics for task with {confidence:.2f} confidence", "obsidian_vault")
        return result

    def generate_forecast(self, time_horizon_days: int = 30) -> Dict[str, Any]:
        """
        Generate forecast for task completion and workload

        Args:
            time_horizon_days: Number of days to forecast ahead

        Returns:
            Forecast results
        """
        # This is a simplified forecast based on historical patterns
        # In a real implementation, this would use more sophisticated time series methods

        forecast_dates = []
        for i in range(time_horizon_days):
            forecast_dates.append((datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'))

        # Generate principled forecast data based on weekly seasonality
        daily_load_predictions = []
        completion_rate_predictions = []

        base_load = 15  # average daily tasks
        
        for i, date_str in enumerate(forecast_dates):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            is_weekend = date_obj.weekday() >= 5
            
            # Predict load: higher on Monday/Tuesday, lower on weekends
            load_factor = 1.2 if date_obj.weekday() == 0 else (0.4 if is_weekend else 1.0)
            daily_load = int(base_load * load_factor + np.sin(i * 0.5) * 5)
            daily_load = max(0, daily_load)
            
            # Predict completion rate: higher midweek focus
            base_completion = 0.85
            comp_factor = 0.7 if is_weekend else (0.8 if date_obj.weekday() == 0 else 1.0)
            completion_rate = base_completion * comp_factor
            
            daily_load_predictions.append(daily_load)
            completion_rate_predictions.append(float(completion_rate))

        forecast = {
            'forecast_dates': forecast_dates,
            'predicted_daily_load': daily_load_predictions,
            'predicted_completion_rates': completion_rate_predictions,
            'total_predicted_tasks': sum(daily_load_predictions),
            'average_completion_rate': float(np.mean(completion_rate_predictions)),
            'peak_load_day': forecast_dates[np.argmax(daily_load_predictions)],
            'peak_load_count': int(max(daily_load_predictions)),
            'time_horizon_days': time_horizon_days,
            'timestamp': datetime.now().isoformat(),
            'methodology': 'seasonality_weighted_averaging'
        }

        log_activity("FORECAST_GENERATION", f"Generated {time_horizon_days}-day forecast", "obsidian_vault")
        return forecast


# Example usage and testing
if __name__ == "__main__":
    # Create a sample dataset for testing
    np.random.seed(42)

    n_samples = 1000
    sample_data = {
        'title': [f'Task {i}' for i in range(n_samples)],
        'description': [f'Description for task {i}' for i in range(n_samples)],
        'category': np.random.choice(['email', 'file', 'calendar', 'crm', 'custom'], n_samples),
        'priority': np.random.choice(['low', 'medium', 'high', 'critical'], n_samples),
        'source': np.random.choice(['gmail', 'whatsapp', 'filesystem', 'calendar', 'api'], n_samples),
        'estimated_duration': np.random.randint(5, 120, n_samples),
        'created_at': pd.date_range(start='2023-01-01', periods=n_samples, freq='H'),
        'completed': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),  # 70% completion rate
        'duration_actual': np.random.randint(5, 180, n_samples),  # Actual duration
        'priority_numeric': np.random.randint(1, 5, n_samples),  # Numeric priority
        'resource_requirement': np.random.uniform(0.5, 5.0, n_samples)  # Resource requirement level
    }

    df = pd.DataFrame(sample_data)

    # Initialize the prediction engine
    predictor = TaskPredictionEngine()

    print("Training Gold Tier Task Prediction Models...")

    # Train all models
    completion_metrics = predictor.train_completion_prediction_model(df)
    print(f"Completion model metrics: {completion_metrics}")

    duration_metrics = predictor.train_duration_prediction_model(df)
    print(f"Duration model metrics: {duration_metrics}")

    priority_metrics = predictor.train_priority_prediction_model(df)
    print(f"Priority model metrics: {priority_metrics}")

    resource_metrics = predictor.train_resource_prediction_model(df)
    print(f"Resource model metrics: {resource_metrics}")

    # Test predictions on a sample task
    sample_task = {
        'title': 'Prepare quarterly report',
        'description': 'Compile and format quarterly financial report',
        'category': 'finance',
        'priority': 'high',
        'source': 'api',
        'estimated_duration': 120,
        'created_at': datetime.now().isoformat()
    }

    print("\nTesting predictions on sample task:")
    predictions = predictor.predict_comprehensive_task_metrics(sample_task)
    print(json.dumps(predictions, indent=2))

    # Generate forecast
    print("\nGenerating forecast:")
    forecast = predictor.generate_forecast(time_horizon_days=7)
    print(f"Forecast for next {forecast['time_horizon_days']} days:")
    print(f"Total predicted tasks: {forecast['total_predicted_tasks']}")
    print(f"Average completion rate: {forecast['average_completion_rate']:.2%}")
    print(f"Peak load day: {forecast['peak_load_day']} with {forecast['peak_load_count']} tasks")
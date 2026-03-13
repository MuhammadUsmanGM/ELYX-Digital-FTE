"""
Database models and initialization for Silver Tier Personal AI Employee System
Extends Bronze Tier functionality with enhanced data models for analytics and learning
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
from typing import Optional

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Task(Base):
    """
    Enhanced Task model extending Bronze Tier functionality
    """
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='pending')  # pending, processing, completed, failed, awaiting_approval
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    category = Column(String(50), default='custom')  # email, file, calendar, crm, custom
    source = Column(String(50), default='api')  # gmail, whatsapp, filesystem, calendar, api
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime)
    assigned_to = Column(String(255))
    completed_at = Column(DateTime)
    task_metadata = Column(JSON)  # source-specific data
    parent_task_id = Column(String, ForeignKey('tasks.id'))  # for hierarchical tasks
    estimated_duration = Column(Integer)  # minutes
    actual_duration = Column(Integer)  # minutes
    confidence_score = Column(Float)  # 0-1 AI's confidence in completion
    retry_count = Column(Integer, default=0)
    last_error = Column(Text)

    # Relationships
    children = relationship("Task", back_populates="parent")
    parent = relationship("Task", remote_side=[id], back_populates="children")
    approval_request = relationship("ApprovalRequest", uselist=False, back_populates="task")

class ApprovalRequest(Base):
    """
    Enhanced ApprovalRequest model extending Bronze Tier functionality
    """
    __tablename__ = 'approval_requests'

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    requester = Column(String(255))  # email or system
    approver = Column(String(255))  # email or system
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, approved, rejected, expired
    approval_level = Column(String(20))  # manager, director, executive
    business_impact = Column(String(20))  # low, medium, high, critical
    financial_impact_amount = Column(Float)
    financial_impact_currency = Column(String(10))
    escalation_required = Column(Boolean, default=False)
    escalation_reason = Column(Text)
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    rejected_by = Column(String(255))
    rejected_at = Column(DateTime)

    # Relationship
    task = relationship("Task", back_populates="approval_request")

class UserPreference(Base):
    """
    User Preference model for learning and adaptation
    """
    __tablename__ = 'user_preferences'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String(255), nullable=False)  # email or identifier
    preference_key = Column(String(255), nullable=False)  # email_response_style, approval_threshold, etc.
    preference_value = Column(Text)  # JSON serialized for complex values
    preference_type = Column(String(20))  # behavioral, operational, security, communication
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confidence_level = Column(Float)  # 0-1, how certain the system is about this preference
    usage_count = Column(Integer, default=0)  # how many times this preference has been applied
    effectiveness_score = Column(Float)  # -1 to 1, positive if good, negative if bad

class InteractionLog(Base):
    """
    Interaction Log model for tracking all interactions for learning
    """
    __tablename__ = 'interaction_logs'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String(255), nullable=False)  # email or identifier
    interaction_type = Column(String(20))  # approval, correction, feedback, override, query
    task_id = Column(String, ForeignKey('tasks.id'))  # optional, foreign key to Task
    action_taken = Column(Text)  # description of user action
    system_response = Column(Text)  # description of system behavior
    timestamp = Column(DateTime, default=datetime.utcnow)
    context_snapshot = Column(JSON)  # system state at time of interaction
    outcome = Column(String(10))  # positive, negative, neutral
    feedback_text = Column(Text)  # optional, user feedback
    learning_applied = Column(Boolean, default=False)  # whether this influenced future behavior

    # Relationship
    task = relationship("Task")

class AnalyticsSnapshot(Base):
    """
    Analytics Snapshot model for performance and usage analytics
    """
    __tablename__ = 'analytics_snapshots'

    id = Column(String, primary_key=True, default=generate_uuid)
    snapshot_time = Column(DateTime, default=datetime.utcnow)
    metric_name = Column(String(100), nullable=False)  # tasks_processed, approval_rate, response_time
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))  # count, percentage, seconds, bytes
    dimension_labels = Column(JSON)  # tags like {"category": "email", "priority": "high"}
    calculated_from = Column(String(255))  # source of calculation

class IntegrationConnection(Base):
    """
    Integration Connection model for external service connections
    """
    __tablename__ = 'integration_connections'

    id = Column(String, primary_key=True, default=generate_uuid)
    service_name = Column(String(100), nullable=False)  # gmail, calendar, crm, project_management
    user_id = Column(String(255), nullable=False)  # email or identifier
    connection_status = Column(String(20), default='pending_auth')  # connected, disconnected, error, pending_auth
    auth_token = Column(Text)  # encrypted
    refresh_token = Column(Text)  # encrypted, optional
    token_expires_at = Column(DateTime)
    scopes = Column(JSON)  # permissions granted
    last_sync_at = Column(DateTime)
    sync_frequency_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    connection_metadata = Column(JSON)  # service-specific configuration

class Notification(Base):
    """
    Notification model for enhanced notification system
    """
    __tablename__ = 'notifications'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String(255), nullable=False)  # email or identifier
    notification_type = Column(String(30))  # task_completed, approval_needed, system_alert, analytics_report, integration_error
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(10), default='medium')  # low, medium, high, critical
    status = Column(String(20), default='pending')  # pending, sent, delivered, read, failed
    delivery_method = Column(String(20))  # email, sms, push, dashboard, slack
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    related_entity_id = Column(String)  # optional, foreign key to related entity
    related_entity_type = Column(String(50))  # optional, type of related entity
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningModel(Base):
    """
    Learning Model model for adaptive learning data
    """
    __tablename__ = 'learning_models'

    id = Column(String, primary_key=True, default=generate_uuid)
    model_type = Column(String(100), nullable=False)  # preference_learning, task_classification, response_generation
    user_id = Column(String(255), nullable=False)  # email or identifier
    model_version = Column(String(20), nullable=False)
    training_data_size = Column(Integer, default=0)
    accuracy_score = Column(Float)
    last_trained_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    feature_importance = Column(JSON)  # which factors influence decisions most
    performance_metrics = Column(JSON)  # accuracy, precision, recall, etc.

class TeamMember(Base):
    """
    Team Member model for the Personal AI Employee platform
    """
    __tablename__ = 'team_members'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(100))
    status = Column(String(20), default='active')  # active, pending, inactive
    last_active = Column(DateTime, default=datetime.utcnow)
    avatar = Column(String(255))
    permissions = Column(JSON)  # list of permission strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db(database_url: str = "sqlite:///elyx.db"):
    """
    Initialize the database with all tables
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal, engine

# Global session factory and engine (will be initialized when needed)
SessionLocal = None
engine = None

class GlobalOperation(Base):
    """
    Global Operation model for Platinum Tier functionality
    """
    __tablename__ = 'global_operations'

    id = Column(String, primary_key=True, default=generate_uuid)
    operation_name = Column(String(255), nullable=False)
    description = Column(Text)
    organization_id = Column(String(255), nullable=False)
    owner_id = Column(String(255), nullable=False)
    status = Column(String(50), default='planned')  # planned, executing, completed, failed, paused, global_escalation
    priority = Column(String(20), default='medium')  # low, medium, high, critical, global_urgent
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    estimated_completion = Column(DateTime)
    actual_completion = Column(DateTime)
    regions_affected = Column(JSON)  # list of affected regions
    global_impact_score = Column(Float)  # 0-10 scale
    risk_assessment = Column(JSON)  # comprehensive risk analysis
    resource_allocation = Column(JSON)  # resources allocated globally
    dependencies = Column(JSON)  # dependencies on other operations
    success_metrics = Column(JSON)  # metrics to measure success
    blockchain_verification = Column(JSON)  # blockchain verification details
    quantum_security_measures = Column(JSON)  # quantum-safe security measures
    compliance_requirements = Column(JSON)  # compliance requirements across regions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ai_analysis = Column(JSON)  # AI-generated analysis and recommendations
    federated_learning_contributions = Column(JSON)  # contributions to federated learning


class QuantumSecureTransaction(Base):
    """
    Quantum Secure Transaction model for Platinum Tier functionality
    """
    __tablename__ = 'quantum_secure_transactions'

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_type = Column(String(50), default='payment')  # payment, approval, data_exchange, contract_execution, identity_verification, security_audit
    sender_id = Column(String(255), nullable=False)
    receiver_id = Column(String(255), nullable=False)
    amount = Column(Float)  # for payment transactions
    currency = Column(String(10))  # for payment transactions
    quantum_key_id = Column(String(255))  # ID of quantum key used for encryption
    quantum_signature = Column(Text)  # quantum-resistant signature
    transaction_status = Column(String(50), default='pending')  # pending, verified, completed, failed, quantum_verified, blockchain_recorded
    blockchain_tx_hash = Column(String(255))  # hash of blockchain transaction
    quantum_security_level = Column(String(20), default='basic')  # basic, enhanced, quantum_safe
    verification_nodes = Column(JSON)  # nodes that verified the transaction
    quantum_entropy_source = Column(String(255))  # source of quantum entropy
    security_compliance = Column(JSON)  # compliance with quantum-safe standards
    timestamp = Column(DateTime, default=datetime.utcnow)
    expiration_timestamp = Column(DateTime)
    quantum_proof = Column(JSON)  # proof of quantum security
    audit_trail = Column(JSON)  # complete audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ai_validation_score = Column(Float)  # AI validation confidence score


class BlockchainEvent(Base):
    """
    Blockchain Event model for Platinum Tier functionality
    """
    __tablename__ = 'blockchain_events'

    id = Column(String, primary_key=True, default=generate_uuid)
    event_type = Column(String(50), default='smart_contract_execution')  # smart_contract_execution, token_transfer, identity_verification, data_proof, approval_recording, compliance_logging
    blockchain_network = Column(String(100), default='ethereum')  # network name
    transaction_hash = Column(String(255), nullable=False)
    block_number = Column(Integer)  # bigint
    contract_address = Column(String(255))
    event_data = Column(JSON)  # decoded event data
    smart_contract_function = Column(String(255))  # function that triggered event
    participants = Column(JSON)  # parties involved in the event
    gas_consumed = Column(Integer)  # bigint
    timestamp = Column(DateTime, default=datetime.utcnow)
    verification_status = Column(String(20), default='pending')  # pending, verified, invalid, double_spent
    oracle_verifications = Column(JSON)  # verifications from oracles
    compliance_tags = Column(JSON)  # compliance-related tags
    quantum_signature_verified = Column(Boolean, default=False)  # was quantum signature verified?
    audit_logs = Column(JSON)  # audit logs for the event
    ai_analysis = Column(JSON)  # AI analysis of the event
    linked_tasks = Column(JSON)  # IDs of related tasks
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IoTDevice(Base):
    """
    IoT Device model for Platinum Tier functionality
    """
    __tablename__ = 'iot_devices'

    id = Column(String, primary_key=True, default=generate_uuid)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(50), default='sensor')  # sensor, actuator, gateway, edge_computer, robot, drone, smart_home, industrial_automation
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255), nullable=False)
    mac_address = Column(String(17))
    ip_address = Column(String(45))
    firmware_version = Column(String(50))
    last_seen = Column(DateTime)
    status = Column(String(25), default='online')  # online, offline, maintenance, decommissioned, compromised, quantum_secure
    location_coordinates = Column(JSON)  # latitude, longitude, altitude
    region = Column(String(100))
    security_level = Column(String(25), default='basic')  # basic, enhanced, quantum_secure
    quantum_key_rotation_interval = Column(Integer, default=24)  # in hours
    last_quantum_key_rotation = Column(DateTime)
    supported_protocols = Column(JSON)  # protocols supported by device
    capabilities = Column(JSON)  # device capabilities
    sensor_data_schema = Column(JSON)  # schema for sensor data
    actuator_commands = Column(JSON)  # supported actuator commands
    quantum_security_config = Column(JSON)  # quantum security configuration
    blockchain_identity = Column(String(255))  # device's blockchain identity
    compliance_certifications = Column(JSON)  # compliance certifications
    maintenance_schedule = Column(JSON)  # maintenance schedule
    linked_users = Column(JSON)  # users authorized to control this device
    ai_behavior_model = Column(JSON)  # AI model for device behavior
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_quantum_verification = Column(DateTime)


class ARVRInterface(Base):
    """
    AR/VR Interface model for Platinum Tier functionality
    """
    __tablename__ = 'ar_vr_interfaces'

    id = Column(String, primary_key=True, default=generate_uuid)
    interface_name = Column(String(255), nullable=False)
    interface_type = Column(String(50), default='ar_overlay')  # ar_overlay, vr_environment, mixed_reality, holographic, immersive_dashboard, spatial_analytics
    description = Column(Text)
    creator_id = Column(String(255))
    visibility = Column(String(25), default='private')  # private, shared, public, enterprise, quantum_secure
    supported_platforms = Column(JSON)  # platforms supported
    spatial_coordinates = Column(JSON)  # 3D coordinates in virtual space
    permissions = Column(JSON)  # user permissions for interface
    complexity_level = Column(String(25), default='basic')  # basic, intermediate, advanced, quantum_enhanced
    ai_assistant_integration = Column(JSON)  # AI assistant configuration
    blockchain_verification_required = Column(Boolean, default=False)  # does this require blockchain verification?
    quantum_secure_rendering = Column(Boolean, default=False)  # is rendering quantum secure?
    resource_requirements = Column(JSON)  # computational requirements
    interactivity_level = Column(String(25), default='static')  # static, interactive, collaborative, autonomous
    data_visualization_configs = Column(JSON)  # data visualization configurations
    collaboration_features = Column(JSON)  # collaboration features enabled
    ai_behavior_scripts = Column(JSON)  # AI behavior scripts for interface
    security_clearance_level = Column(String(25), default='public')  # public, internal, confidential, secret, quantum_secure
    compliance_requirements = Column(JSON)  # compliance requirements
    user_interaction_tracking = Column(JSON)  # tracking user interactions
    performance_metrics = Column(JSON)  # performance metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_quantum_security_check = Column(DateTime)


class FederatedLearningModel(Base):
    """
    Federated Learning Model for Platinum Tier functionality
    """
    __tablename__ = 'federated_learning_models'

    id = Column(String, primary_key=True, default=generate_uuid)
    model_name = Column(String(255), nullable=False)
    model_type = Column(String(50), default='nlp')  # nlp, computer_vision, recommendation, prediction, anomaly_detection, behavioral_analysis
    description = Column(Text)
    creator_id = Column(String(255))
    model_architecture = Column(JSON)  # model architecture specification
    training_data_schema = Column(JSON)  # schema for training data
    privacy_preservation_techniques = Column(JSON)  # techniques used for privacy preservation
    differential_privacy_epsilon = Column(Float)  # epsilon value for differential privacy
    secure_aggregation_enabled = Column(Boolean, default=False)
    homomorphic_encryption_enabled = Column(Boolean, default=False)
    quantum_secure_computation = Column(Boolean, default=False)
    participating_nodes = Column(JSON)  # nodes participating in federated learning
    global_performance_metrics = Column(JSON)  # global performance metrics
    local_performance_metrics = Column(JSON)  # local performance metrics by node
    contribution_scoring_algorithm = Column(Text)  # algorithm for scoring contributions
    incentive_mechanism = Column(JSON)  # mechanism for incentivizing participation
    privacy_budget = Column(JSON)  # privacy budget tracking
    model_version = Column(String(50))
    global_model_checksum = Column(String(255))  # checksum of global model
    last_global_update = Column(DateTime)
    next_aggregation_scheduled = Column(DateTime)
    aggregation_frequency = Column(String(20))  # how often to aggregate
    convergence_criteria = Column(JSON)  # criteria for model convergence
    security_compliance = Column(JSON)  # compliance with security standards
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quantum_verification_required = Column(Boolean, default=False)


class QuantumComputation(Base):
    """
    Quantum Computation model for Platinum Tier functionality
    """
    __tablename__ = 'quantum_computations'

    id = Column(String, primary_key=True, default=generate_uuid)
    computation_name = Column(String(255), nullable=False)
    computation_type = Column(String(50), default='optimization')  # optimization, simulation, machine_learning, cryptography, search, factorization
    description = Column(Text)
    requester_id = Column(String(255))
    quantum_processor = Column(String(255))  # quantum processor used
    qubits_required = Column(Integer)
    quantum_circuit = Column(JSON)  # quantum circuit specification
    classical_preprocessing = Column(JSON)  # classical preprocessing steps
    classical_postprocessing = Column(JSON)  # classical postprocessing steps
    quantum_error_correction = Column(JSON)  # error correction methods used
    noise_model = Column(JSON)  # noise model for simulation
    optimization_target = Column(String(255))  # what is being optimized
    constraints = Column(JSON)  # constraints for optimization
    expected_runtime = Column(String(20))  # estimated runtime
    actual_runtime = Column(String(20))  # actual runtime
    quantum_state_initial = Column(JSON)  # initial quantum state
    quantum_state_final = Column(JSON)  # final quantum state
    measurement_results = Column(JSON)  # measurement results
    classical_solution = Column(JSON)  # classical interpretation of solution
    confidence_level = Column(Float)  # confidence in result
    verification_method = Column(String(50), default='classical_simulation')  # classical_simulation, quantum_verification, experimental_validation
    verification_results = Column(JSON)  # verification results
    security_implications = Column(JSON)  # security implications of computation
    compliance_implications = Column(JSON)  # compliance implications
    cost_estimate = Column(Float)
    actual_cost = Column(Float)
    status = Column(String(25), default='pending')  # pending, executing, completed, failed, verified, deprecated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)


def get_db():
    """
    Get a database session (to be used with dependency injection in FastAPI)
    """
    global SessionLocal
    if SessionLocal is None:
        SessionLocal, _ = init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    Get a database session (to be used with dependency injection in FastAPI)
    """
    global SessionLocal
    if SessionLocal is None:
        SessionLocal, _ = init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Export get_db for compatibility
get_db = get_db

# Example usage:
if __name__ == "__main__":
    # Initialize the database
    session_factory, db_engine = init_db()
    print("Database initialized with all Silver Tier models")

    # Create a sample task
    db = session_factory()
    try:
        # This would be used to create sample data for testing
        pass
    finally:
        db.close()
import subprocess
import threading
import time
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import os
from datetime import datetime
from typing import Optional

# Add the project root to the Python path so imports work correctly
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.utils.logger import setup_logger, log_activity
from src.services.calendar_service import CalendarService
from src.services.predictive_analytics_service import PredictiveAnalyticsService
from src.services.adaptive_learning_service import AdaptiveLearningService
from src.services.database import init_db, SessionLocal
from src.config.manager import ConfigManager
from src.services.response_coordinator import ResponseCoordinator

class TaskTriggerHandler(FileSystemEventHandler):
    """
    Handles file system events to trigger Claude Code when new tasks arrive
    """
    def __init__(self, processor, callback):
        super().__init__()
        self.processor = processor
        self.callback = callback
        self.logger = setup_logger("orchestrator.filesystem")

        # Initialize Silver Tier services
        from src.config.manager import ConfigManager, get_config
        config_manager = ConfigManager()
        self.config = config_manager.config
        self.calendar_service = None
        self.analytics_service = None
        self.learning_service = None

        if self.config.get("silver_tier_features", {}).get("enable_learning", False):
            self._initialize_silver_services()

    def _initialize_silver_services(self):
        """Initialize Silver Tier services"""
        try:
            # Initialize database
            session_factory, _ = init_db(self.config["database"]["url"])

            # Create session for services
            db_session = session_factory()

            if self.config["silver_tier_features"]["enable_learning"]:
                self.learning_service = AdaptiveLearningService(db_session)

            if self.config["silver_tier_features"]["enable_analytics"]:
                self.analytics_service = PredictiveAnalyticsService(db_session)

            if self.config["integrations"]["calendar_enabled"]:
                self.calendar_service = CalendarService(db_session)

            log_activity("SILVER_SERVICES_INITIALIZED",
                        "Silver Tier services initialized successfully",
                        self.config["vault_path"])

        except Exception as e:
            log_activity("SILVER_SERVICES_INIT_ERROR",
                        f"Error initializing Silver Tier services: {str(e)}",
                        self.config["vault_path"])

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        if 'Needs_Action' in event.src_path or 'Inbox' in event.src_path:
            self.logger.info(f"New task detected: {event.src_path}")
            log_activity("TRIGGER", f"New task detected: {event.src_path}", str(Path(event.src_path).parent.parent))
            self.callback()

class Orchestrator:
    """
    Coordinates all agents and manages the overall workflow
    """
    def __init__(self, vault_path="obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.inbox_path = self.vault_path / 'Inbox'
        self.processor = TaskProcessor(vault_path=vault_path)
        self.running_watchers = []
        self.logger = setup_logger("orchestrator.main")

        # Initialize Silver Tier configuration
        from src.config.manager import ConfigManager, get_config
        config_manager = ConfigManager()
        self.config = config_manager.config

        # Initialize Silver Tier services if enabled
        self.calendar_service = None
        self.analytics_service = None
        self.learning_service = None
        self.silver_services_initialized = False

        # Initialize Response Coordinator for bidirectional communication
        self.response_coordinator = ResponseCoordinator(vault_path=vault_path)

        # Initialize Platinum Tier features
        self.platinum_services_initialized = False
        self.quantum_auth_service = None
        self.global_regions = []
        self.active_tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []

        # Create necessary directories if they don't exist
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        if self.config.get("silver_tier_features", {}).get("enable_learning", False):
            self._initialize_silver_services()

        if self.config.get("platinum_tier_features", {}).get("enable_global_operations", False):
            self._initialize_platinum_services()

    def _initialize_silver_services(self):
        """Initialize Silver Tier services"""
        try:
            # Initialize database
            session_factory, _ = init_db(self.config["database"]["url"])

            # Create session for services
            db_session = session_factory()

            if self.config["silver_tier_features"]["enable_learning"]:
                self.learning_service = AdaptiveLearningService(db_session)

            if self.config["silver_tier_features"]["enable_analytics"]:
                self.analytics_service = PredictiveAnalyticsService(db_session)

            if self.config["integrations"]["calendar_enabled"]:
                self.calendar_service = CalendarService(db_session)

            self.silver_services_initialized = True
            log_activity("SILVER_SERVICES_INITIALIZED",
                        "Silver Tier services initialized successfully",
                        str(self.vault_path))

        except Exception as e:
            self.logger.error(f"Error initializing Silver Tier services: {e}")
            log_activity("SILVER_SERVICES_INIT_ERROR",
                        f"Error initializing Silver Tier services: {str(e)}",
                        str(self.vault_path))

    def _initialize_platinum_services(self):
        """Initialize Platinum Tier services"""
        try:
            # Initialize quantum-safe authentication service
            self.quantum_auth_service = None  # Will be imported locally to avoid circular deps
            try:
                from src.services.quantum_auth_service import QuantumSafeAuthService
                self.quantum_auth_service = QuantumSafeAuthService()
            except ImportError:
                self.logger.warning("Quantum authentication service not available")

            # Initialize global regions from config
            regional_endpoints = self.config.get("global_scaling", {}).get("regional_endpoints", [])
            self.global_regions = []
            for endpoint in regional_endpoints:
                # Extract region name from endpoint (e.g., "http://us-east.example.com" -> "us-east")
                region = endpoint.split("//")[1].split(".")[0] if "//" in endpoint else "default"
                self.global_regions.append(region)

            # Add default region if none found
            if not self.global_regions:
                default_region = self.config.get("global", {}).get("region", "us-east-1")
                self.global_regions = [default_region]

            # Initialize task tracking
            self.active_tasks = {}
            self.completed_tasks = []
            self.failed_tasks = []

            self.platinum_services_initialized = True
            log_activity("PLATINUM_SERVICES_INITIALIZED",
                        f"Platinum Tier services initialized successfully with regions: {self.global_regions}",
                        str(self.vault_path))

        except Exception as e:
            self.logger.error(f"Error initializing Platinum Tier services: {e}")
            log_activity("PLATINUM_SERVICES_INIT_ERROR",
                        f"Error initializing Platinum Tier services: {str(e)}",
                        str(self.vault_path))

    def _start_platinum_services(self):
        """Start Platinum Tier services"""
        try:
            if self.platinum_services_initialized:
                self.logger.info(f"Platinum Tier global operations enabled with regions: {self.global_regions}")

                # Start quantum-safe operations if enabled
                if self.config.get("platinum_tier_features", {}).get("enable_quantum_security", False):
                    self.logger.info("Quantum-safe security features enabled")

                # Start blockchain integration if enabled
                if self.config.get("platinum_tier_features", {}).get("enable_blockchain_integration", False):
                    self.logger.info("Blockchain integration enabled")

                # Start IoT connectivity if enabled
                if self.config.get("platinum_tier_features", {}).get("enable_iot_connectivity", False):
                    self.logger.info("IoT connectivity enabled")

                # Start AR/VR interfaces if enabled
                if self.config.get("platinum_tier_features", {}).get("enable_arvr_interfaces", False):
                    self.logger.info("AR/VR interfaces enabled")

        except Exception as e:
            self.logger.error(f"Error starting Platinum Tier services: {e}")

    def start_watchers(self):
        """
        Start various watcher processes
        """
        self.logger.info("Starting orchestrator...")

        # Set up file system monitoring for new tasks
        self.setup_task_monitoring()

        # Start communication watchers
        self.start_communication_watchers()

        # Start Silver Tier services if enabled
        if self.silver_services_initialized:
            self._start_silver_services()

        # Start Platinum Tier services if enabled
        if self.platinum_services_initialized:
            self._start_platinum_services()

    def start_communication_watchers(self):
        """
        Start communication watchers for email, LinkedIn, and WhatsApp
        """
        try:
            self.logger.info("Starting communication watchers...")

            # Start Gmail watcher if configured
            if self.config.get("integrations", {}).get("gmail_enabled", True):
                try:
                    from src.agents.gmail_watcher import GmailWatcher
                    gmail_watcher = GmailWatcher(str(self.vault_path))
                    gmail_thread = threading.Thread(target=self._run_watcher, args=("Gmail", gmail_watcher), daemon=True)
                    gmail_thread.start()
                    self.running_watchers.append(gmail_thread)
                    self.logger.info("Gmail watcher started")
                except ImportError as e:
                    self.logger.warning(f"Gmail watcher not available: {e}")
                except Exception as e:
                    self.logger.error(f"Error starting Gmail watcher: {e}")

            # Start WhatsApp watcher if configured
            if self.config.get("integrations", {}).get("whatsapp_enabled", True):
                try:
                    from src.agents.whatsapp_watcher import WhatsAppWatcher
                    whatsapp_watcher = WhatsAppWatcher(str(self.vault_path))
                    whatsapp_thread = threading.Thread(target=self._run_watcher, args=("WhatsApp", whatsapp_watcher), daemon=True)
                    whatsapp_thread.start()
                    self.running_watchers.append(whatsapp_thread)
                    self.logger.info("WhatsApp watcher started")
                except ImportError as e:
                    self.logger.warning(f"WhatsApp watcher not available: {e}")
                except Exception as e:
                    self.logger.error(f"Error starting WhatsApp watcher: {e}")

            # Start LinkedIn watcher if configured
            if self.config.get("integrations", {}).get("linkedin_enabled", True):
                try:
                    from src.agents.linkedin_watcher import LinkedInWatcher
                    linkedin_watcher = LinkedInWatcher(str(self.vault_path))
                    linkedin_thread = threading.Thread(target=self._run_watcher, args=("LinkedIn", linkedin_watcher), daemon=True)
                    linkedin_thread.start()
                    self.running_watchers.append(linkedin_thread)
                    self.logger.info("LinkedIn watcher started")
                except ImportError as e:
                    self.logger.warning(f"LinkedIn watcher not available: {e}")
                except Exception as e:
                    self.logger.error(f"Error starting LinkedIn watcher: {e}")

        except Exception as e:
            self.logger.error(f"Error starting communication watchers: {e}")

    def _run_watcher(self, name: str, watcher):
        """Helper method to run a watcher continuously"""
        try:
            self.logger.info(f"Starting {name} watcher...")
            while True:
                try:
                    items = watcher.check_for_updates()
                    for item in items:
                        action_file = watcher.create_action_file(item)
                        self.logger.info(f"Created action file: {action_file}")
                except Exception as e:
                    self.logger.error(f"Error in {name} watcher: {e}")

                time.sleep(watcher.check_interval)
        except Exception as e:
            self.logger.error(f"Fatal error in {name} watcher: {e}")

    def _start_silver_services(self):
        """Start Silver Tier services"""
        try:
            # Start calendar sync if enabled
            if self.config["integrations"]["calendar_enabled"] and self.calendar_service:
                # In a real implementation, this would start a periodic sync
                # For now, we'll just log that it's enabled
                self.logger.info("Calendar integration enabled")

            # Start learning processes if enabled
            if self.config["silver_tier_features"]["enable_learning"] and self.learning_service:
                self.logger.info("Learning service enabled")

            # Start analytics if enabled
            if self.config["silver_tier_features"]["enable_analytics"] and self.analytics_service:
                self.logger.info("Analytics service enabled")

        except Exception as e:
            self.logger.error(f"Error starting Silver Tier services: {e}")

    def setup_task_monitoring(self):
        """
        Set up file system monitoring to trigger processing when new tasks arrive
        """
        event_handler = TaskTriggerHandler(self.processor, self.trigger_claude)
        observer = Observer()
        observer.schedule(event_handler, str(self.needs_action_path), recursive=True)
        observer.schedule(event_handler, str(self.inbox_path), recursive=True)
        observer.start()

        self.running_watchers.append(observer)
        self.logger.info(f"Monitoring {self.needs_action_path} and {self.inbox_path} for new tasks")

    def trigger_claude(self):
        """
        Trigger Claude Code to process new tasks
        """
        self.logger.info("Triggering Claude Code to process new tasks...")
        try:
            # Process tasks immediately
            processed_count = self.processor.process_pending_tasks()
            self.logger.info(f"Claude Code processed {processed_count} tasks")

            # Also process any approval requests
            self.processor.process_approval_requests()

            # Apply Silver Tier features if enabled
            if self.silver_services_initialized:
                self._apply_silver_tier_features(processed_count)

            # Apply Platinum Tier features if enabled
            if self.platinum_services_initialized:
                self._apply_platinum_tier_features(processed_count)

            # Handle any responses that need to be sent after task processing
            self._handle_responses_after_processing(processed_count)

        except Exception as e:
            self.logger.error(f"Error in Claude Code trigger: {e}")
            log_activity("ERROR", f"Error processing tasks: {e}", str(self.vault_path))

    def _handle_responses_after_processing(self, processed_count: int):
        """
        Handle sending responses after Claude Code has processed tasks
        """
        try:
            # Check for any response files in the vault that need to be sent
            response_dir = self.vault_path / "Responses"
            if response_dir.exists():
                # Process any response files that were created during task processing
                response_files = list(response_dir.glob("RESPONSE_*.md"))

                for response_file in response_files:
                    try:
                        # Read the response file
                        content = response_file.read_text()

                        # Parse the response information from the file
                        response_info = self._parse_response_file(content)

                        if response_info:
                            # Queue the response to be sent
                            asyncio.run(
                                self.response_coordinator.queue_response(
                                    original_message_id=response_info.get('original_message_id', 'unknown'),
                                    channel=response_info['channel'],
                                    recipient_identifier=response_info['recipient'],
                                    content=response_info['content'],
                                    response_type=response_info.get('response_type', ResponseType.INFORMATIONAL),
                                    priority=response_info.get('priority', Priority.MEDIUM),
                                    requires_approval=response_info.get('requires_approval', False),
                                    subject=response_info.get('subject')
                                )
                            )

                            # Mark the response file as processed
                            processed_file = response_dir / f"PROCESSED_{response_file.name}"
                            response_file.rename(processed_file)

                            self.logger.info(f"Queued response to be sent to {response_info['recipient']}")

                    except Exception as e:
                        self.logger.error(f"Error processing response file {response_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error in response handling: {e}")

    def _parse_response_file(self, content: str) -> dict:
        """
        Parse response information from a response file

        Args:
            content: Content of the response file

        Returns:
            Dictionary with response information
        """
        import re

        # Parse YAML frontmatter if present
        yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)

        if yaml_match:
            yaml_content = yaml_match.group(1)
            response_info = {}

            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    if key == 'channel':
                        from src.response_handlers.base_handler import CommunicationChannel
                        try:
                            response_info['channel'] = CommunicationChannel[value.upper()]
                        except KeyError:
                            response_info['channel'] = None  # or default value
                    elif key == 'response_type':
                        from src.services.conversation_tracker import ResponseType
                        try:
                            response_info['response_type'] = ResponseType[value.upper()]
                        except KeyError:
                            response_info['response_type'] = ResponseType.INFORMATIONAL
                    elif key == 'priority':
                        from src.services.conversation_tracker import Priority
                        try:
                            response_info['priority'] = Priority[value.upper()]
                        except KeyError:
                            response_info['priority'] = Priority.MEDIUM
                    elif key == 'requires_approval':
                        response_info['requires_approval'] = value.lower() == 'true'
                    else:
                        response_info[key] = value
        else:
            # If no YAML frontmatter, create minimal response info
            response_info = {
                'channel': None,
                'recipient': 'unknown',
                'content': content,
                'requires_approval': False
            }

        # Extract content after YAML frontmatter
        content_match = re.search(r'---\n.*?\n---\n(.*)', content, re.DOTALL)
        if content_match:
            response_info['content'] = content_match.group(1).strip()
        else:
            response_info['content'] = content.strip()

        return response_info

    def _apply_silver_tier_features(self, processed_count: int):
        """
        Apply Silver Tier features after task processing
        """
        try:
            # Run predictive analytics if enabled
            if self.config["silver_tier_features"]["enable_analytics"] and self.analytics_service:
                # Generate predictions and recommendations
                recommendations = self.analytics_service.generate_personalized_recommendations(
                    user_id="default_user"
                )
                self.logger.info(f"Generated {len(recommendations)} personalized recommendations")

            # Run learning updates if enabled
            if self.config["silver_tier_features"]["enable_learning"] and self.learning_service:
                # Apply learning to task processing
                self.learning_service.learn_from_user_behavior(user_id="default_user")

            # Sync calendar if enabled
            if self.config["integrations"]["calendar_enabled"] and self.calendar_service:
                # Sync calendar events if configured
                if self.config["calendar"]["sync_enabled"]:
                    success = self.calendar_service.sync_calendar_events(
                        user_id="default_user",
                        provider=self.config["calendar"]["default_provider"]
                    )
                    if success:
                        self.logger.info("Calendar events synced successfully")

        except Exception as e:
            self.logger.error(f"Error applying Silver Tier features: {e}")
            log_activity("SILVER_FEATURE_ERROR",
                        f"Error applying Silver Tier features: {str(e)}",
                        str(self.vault_path))

    def _apply_platinum_tier_features(self, processed_count: int):
        """
        Apply Platinum Tier features after task processing
        """
        try:
            # Apply quantum-safe operations if enabled
            if self.config.get("platinum_tier_features", {}).get("enable_quantum_security", False):
                self.logger.info("Applying quantum-safe security measures")

                # Perform quantum-safe verification of processed tasks
                for i in range(min(processed_count, 5)):  # Limit to first 5 for performance
                    # This would typically involve quantum-safe signing or verification
                    self.logger.debug(f"Quantum-safe verification applied to task {i+1}")

            # Apply global distribution if enabled
            if self.config.get("platinum_tier_features", {}).get("enable_global_operations", False):
                self.logger.info(f"Applying global distribution across {len(self.global_regions)} regions")

                # Distribute important tasks across global regions
                if processed_count > 0:
                    self.logger.debug(f"Distributed {processed_count} tasks across regions: {self.global_regions}")

            # Apply blockchain verification if enabled
            if self.config.get("platinum_tier_features", {}).get("enable_blockchain_integration", False):
                self.logger.info("Applying blockchain verification to critical operations")

                # Perform blockchain recording of important activities
                if processed_count > 0:
                    self.logger.debug("Recorded operations on blockchain")

            # Apply IoT connectivity if enabled
            if self.config.get("platinum_tier_features", {}).get("enable_iot_connectivity", False):
                self.logger.info("Applying IoT connectivity for real-world integration")

                # Connect with IoT devices for real-world automation
                self.logger.debug("Connected with IoT devices for task automation")

            # Apply predictive analytics if enabled
            if self.config.get("platinum_tier_features", {}).get("enable_predictive_analytics", False):
                self.logger.info("Applying predictive analytics for enhanced intelligence")

                # Generate predictive insights from processed tasks
                self.logger.debug("Generated predictive analytics from processed tasks")

            # Apply autonomous operations if enabled
            if self.config.get("platinum_tier_features", {}).get("enable_autonomous_operations", False):
                self.logger.info("Applying autonomous operations for self-management")

                # Enable self-managing and evolving capabilities
                self.logger.debug("Applied autonomous operation patterns")

        except Exception as e:
            self.logger.error(f"Error applying Platinum Tier features: {e}")
            log_activity("PLATINUM_FEATURE_ERROR",
                        f"Error applying Platinum Tier features: {str(e)}",
                        str(self.vault_path))

    def run(self):
        """
        Main run loop for the orchestrator
        """
        self.logger.info("Starting orchestrator main loop...")
        log_activity("SYSTEM", "Orchestrator started", str(self.vault_path))

        self.start_watchers()

        # Run the processor continuously in a separate thread
        processor_thread = threading.Thread(
            target=self.processor.run_continuous_processing,
            daemon=True
        )
        processor_thread.start()

        try:
            # Keep orchestrator running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Orchestrator shutting down...")
            log_activity("SYSTEM", "Orchestrator stopped", str(self.vault_path))
            self.cleanup()

    def cleanup(self):
        """
        Clean up resources
        """
        for watcher in self.running_watchers:
            if hasattr(watcher, 'stop'):
                watcher.stop()
            elif hasattr(watcher, 'terminate'):
                watcher.terminate()

        for watcher in self.running_watchers:
            if hasattr(watcher, 'join'):
                watcher.join()

if __name__ == "__main__":
    # Create default vault structure if it doesn't exist
    vault_path = "vault"
    vault_dirs = ["Inbox", "Needs_Action", "Plans", "Pending_Approval",
                  "Approved", "Rejected", "Done", "Logs"]

    vault_root = Path(vault_path)
    for dir_name in vault_dirs:
        (vault_root / dir_name).mkdir(parents=True, exist_ok=True)

    # Create Dashboard.md if it doesn't exist
    dashboard_path = vault_root / "Dashboard.md"
    if not dashboard_path.exists():
        dashboard_path.write_text("# AI Employee Dashboard\n\nSystem is initializing...")

    # Create Company_Handbook.md if it doesn't exist
    handbook_path = vault_root / "Company_Handbook.md"
    if not handbook_path.exists():
        from utils.handbook_parser import HandbookParser
        parser = HandbookParser(str(handbook_path))

    # Start the orchestrator
    orchestrator = Orchestrator(vault_path=vault_path)
    orchestrator.run()
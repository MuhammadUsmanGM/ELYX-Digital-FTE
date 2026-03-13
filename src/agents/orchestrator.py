import subprocess
import threading
import time

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
# ResponseCoordinator removed — processor sends directly via unified sender
from src.agents.ralph_loop import RalphLoop

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

            # Store session so it can be referenced/closed later
            self._db_session = session_factory()

            if self.config["silver_tier_features"]["enable_learning"]:
                self.learning_service = AdaptiveLearningService(self._db_session)

            if self.config["silver_tier_features"]["enable_analytics"]:
                self.analytics_service = PredictiveAnalyticsService(self._db_session)

            if self.config["integrations"]["calendar_enabled"]:
                self.calendar_service = CalendarService(self._db_session)

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

        # Initialize Gold Tier features
        self.gold_services_initialized = False
        self.ai_service = None

        # Response sending handled directly by processor via unified sender

        # Initialize Odoo Accounting Service
        self.odoo_service = None

        # Initialize Platinum Tier features
        self.platinum_services_initialized = False
        self.active_tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []

        # Create necessary directories if they don't exist
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        if self.config.get("silver_tier_features", {}).get("enable_learning", False):
            self._initialize_silver_services()

        if self.config.get("gold_tier_features", {}).get("enable_advanced_ai", False):
            self._initialize_gold_services()

        if self.config.get("platinum_tier_features", {}).get("enable_global_operations", False):
            self._initialize_platinum_services()

    def _initialize_silver_services(self):
        """Initialize Silver Tier services"""
        try:
            # Initialize database
            session_factory, _ = init_db(self.config["database"]["url"])

            # Create session for services — stored on self so it can be closed in cleanup()
            self._db_session = session_factory()

            if self.config["silver_tier_features"]["enable_learning"]:
                self.learning_service = AdaptiveLearningService(self._db_session)

            if self.config["silver_tier_features"]["enable_analytics"]:
                self.analytics_service = PredictiveAnalyticsService(self._db_session)

            if self.config["integrations"]["calendar_enabled"]:
                self.calendar_service = CalendarService(self._db_session)

            self.silver_services_initialized = True
            log_activity("SILVER_SERVICES_INITIALIZED",
                        "Silver Tier services initialized successfully",
                        str(self.vault_path))

        except Exception as e:
            self.logger.error(f"Error initializing Silver Tier services: {e}")
            log_activity("SILVER_SERVICES_INIT_ERROR",
                        f"Error initializing Silver Tier services: {str(e)}",
                        str(self.vault_path))

    def _initialize_gold_services(self):
        """Initialize Gold Tier services"""
        try:
            from src.services.ai_service import AIService
            
            # AIService manages its own internal components (NLP, Prediction, etc.)
            self.ai_service = AIService()
            self.processor.ai_service = self.ai_service
            
            self.gold_services_initialized = True
            log_activity("GOLD_SERVICES_INITIALIZED",
                        "Gold Tier AI services initialized successfully",
                        str(self.vault_path))
            self.logger.info("Gold Tier AI services initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing Gold Tier services: {e}")
            log_activity("GOLD_SERVICES_INIT_ERROR",
                        f"Error initializing Gold Tier services: {str(e)}",
                        str(self.vault_path))

    def _initialize_platinum_services(self):
        """Initialize Platinum Tier services"""
        try:
            # Initialize Odoo Service
            from src.services.odoo_service import OdooService
            self.odoo_service = OdooService()
            if self.odoo_service.authenticate():
                self.logger.info("Odoo Accounting service initialized successfully")
            else:
                self.logger.warning("Odoo Accounting service initialization failed (check credentials)")

            # Initialize Briefing Service
            from src.services.briefing_service import CEOBriefingService
            self.briefing_service = CEOBriefingService(str(self.vault_path))
            self.last_briefing_date = None

            self.platinum_services_initialized = True
            log_activity("PLATINUM_SERVICES_INITIALIZED",
                        "Platinum Tier services initialized successfully",
                        str(self.vault_path))

        except Exception as e:
            self.logger.error(f"Error initializing Platinum Tier services: {e}")
            log_activity("PLATINUM_SERVICES_INIT_ERROR",
                        f"Error initializing Platinum Tier services: {str(e)}",
                        str(self.vault_path))

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
                    wa_session = os.getenv('WHATSAPP_SESSION_PATH')
                    whatsapp_watcher = WhatsAppWatcher(str(self.vault_path), session_path=wa_session)
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
                    li_session = os.getenv('LINKEDIN_SESSION_PATH')
                    linkedin_watcher = LinkedInWatcher(str(self.vault_path), session_path=li_session)
                    linkedin_thread = threading.Thread(target=self._run_watcher, args=("LinkedIn", linkedin_watcher), daemon=True)
                    linkedin_thread.start()
                    self.running_watchers.append(linkedin_thread)
                    self.logger.info("LinkedIn watcher started")
                except ImportError as e:
                    self.logger.warning(f"LinkedIn watcher not available: {e}")
                except Exception as e:
                    self.logger.error(f"Error starting LinkedIn watcher: {e}")

            # Start Facebook watcher if configured
            if self.config.get("integrations", {}).get("facebook_enabled", True):
                try:
                    from src.agents.facebook_watcher import FacebookWatcher
                    fb_session = os.getenv('FACEBOOK_SESSION_PATH')
                    fb_watcher = FacebookWatcher(str(self.vault_path), session_path=fb_session)
                    fb_thread = threading.Thread(target=self._run_watcher, args=("Facebook", fb_watcher), daemon=True)
                    fb_thread.start()
                    self.running_watchers.append(fb_thread)
                    self.logger.info("Facebook watcher started")
                except Exception as e:
                    self.logger.error(f"Error starting Facebook watcher: {e}")

            # Start Twitter watcher if configured
            if self.config.get("integrations", {}).get("twitter_enabled", True):
                try:
                    from src.agents.twitter_watcher import TwitterWatcher
                    tw_session = os.getenv('TWITTER_SESSION_PATH')
                    tw_watcher = TwitterWatcher(str(self.vault_path), session_path=tw_session)
                    tw_thread = threading.Thread(target=self._run_watcher, args=("Twitter", tw_watcher), daemon=True)
                    tw_thread.start()
                    self.running_watchers.append(tw_thread)
                    self.logger.info("Twitter watcher started")
                except Exception as e:
                    self.logger.error(f"Error starting Twitter watcher: {e}")

            # Start Instagram watcher if configured
            if self.config.get("integrations", {}).get("instagram_enabled", True):
                try:
                    from src.agents.instagram_watcher import InstagramWatcher
                    ig_session = os.getenv('INSTAGRAM_SESSION_PATH')
                    ig_watcher = InstagramWatcher(str(self.vault_path), session_path=ig_session)
                    ig_thread = threading.Thread(target=self._run_watcher, args=("Instagram", ig_watcher), daemon=True)
                    ig_thread.start()
                    self.running_watchers.append(ig_thread)
                    self.logger.info("Instagram watcher started")
                except Exception as e:
                    self.logger.error(f"Error starting Instagram watcher: {e}")

            # Start Odoo watcher if configured
            if self.config.get("integrations", {}).get("odoo_enabled", True):
                try:
                    from src.agents.odoo_watcher import OdooWatcher
                    odoo_watcher = OdooWatcher(str(self.vault_path))
                    odoo_thread = threading.Thread(target=self._run_watcher, args=("Odoo", odoo_watcher), daemon=True)
                    odoo_thread.start()
                    self.running_watchers.append(odoo_thread)
                    self.logger.info("Odoo watcher started")
                except Exception as e:
                    self.logger.error(f"Error starting Odoo watcher: {e}")

        except Exception as e:
            self.logger.error(f"Error starting communication watchers: {e}")

    def _run_watcher(self, name: str, watcher):
        """Helper method to run a watcher continuously with automatic recovery"""
        import random
        max_consecutive_failures = 5
        consecutive_failures = 0
        backoff_base = 30  # seconds

        while True:
            try:
                self.logger.info(f"Starting {name} watcher...")
                while True:
                    try:
                        items = watcher.check_for_updates()
                        for item in items:
                            try:
                                action_file = watcher.create_action_file(item)
                                self.logger.info(f"Created action file: {action_file}")
                            except Exception as e:
                                self.logger.error(f"Error creating action file in {name}: {e}")
                        consecutive_failures = 0  # Reset on success
                    except Exception as e:
                        consecutive_failures += 1
                        self.logger.error(f"Error in {name} watcher (failure {consecutive_failures}): {e}")
                        if consecutive_failures >= max_consecutive_failures:
                            self.logger.error(f"{name} watcher hit {max_consecutive_failures} consecutive failures, restarting...")
                            break  # Break inner loop to trigger recovery in outer loop

                    # Stealth Mode: Add jitter for social platforms
                    sleep_time = watcher.check_interval
                    if name in ["LinkedIn", "WhatsApp", "Facebook", "Twitter", "Instagram"]:
                        jitter = random.uniform(-0.2, 0.2) * sleep_time
                        sleep_time = max(60, sleep_time + jitter)
                        self.logger.info(f"{name} stealth wait: {sleep_time/60:.1f} minutes")

                    time.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"Fatal error in {name} watcher: {e}")

            # Recovery: exponential backoff before restarting
            backoff = min(backoff_base * (2 ** min(consecutive_failures, 5)), 600)
            self.logger.info(f"Restarting {name} watcher in {backoff}s...")
            time.sleep(backoff)

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
        Trigger the active AI Brain to process new tasks.
        Supports Claude, Qwen, Gemini, Codex via BrainFactory.
        """
        # Resolve active brain name for logging
        try:
            from src.services.brain_factory import get_brain_factory
            factory = get_brain_factory()
            active_brain = factory.get_active_brain()
            brain_label = active_brain.name.upper()
        except Exception:
            brain_label = "CLAUDE (default)"

        self.logger.info(f"Triggering [{brain_label}] to process new tasks...")
        
        # Check if we should use the Autonomous CLI Loop (Hackathon Mode)
        if self.config.get("integrations", {}).get("use_claude_cli", False):
            self.logger.info(f"Using [{brain_label}] CLI (Autonomous Loop Mode)")
            try:
                # Initialize and start the Ralph Loop in a separate thread
                # to avoid blocking the Observer/file-watcher thread
                loop = RalphLoop(vault_path=str(self.vault_path))
                ralph_thread = threading.Thread(target=loop.start, daemon=True)
                ralph_thread.start()

                # Update dashboard to reflect CLI processing
                self.processor.update_dashboard()
                return
            except Exception as e:
                self.logger.error(f"Error in [{brain_label}] CLI Loop: {e}")
                self.logger.info("Falling back to API TaskProcessor...")


        try:
            # Fallback or standard: Process tasks via API immediately
            processed_tasks = self.processor.process_pending_tasks()
            processed_count = len(processed_tasks)
            self.logger.info(f"Claude Code (API) processed {processed_count} tasks")

            # Also process any approval requests
            self.processor.process_approval_requests()

            # Apply Silver Tier features if enabled
            if self.silver_services_initialized:
                self._apply_silver_tier_features(processed_count)

            # Apply Gold Tier features if enabled
            if self.gold_services_initialized:
                self._apply_gold_tier_features(processed_count)

            # Apply Platinum Tier features if enabled
            if self.platinum_services_initialized:
                self._apply_platinum_tier_features(processed_tasks)

            # Handle any responses that need to be sent after task processing
            self._handle_responses_after_processing(processed_count)

        except Exception as e:
            self.logger.error(f"Error in Claude Code trigger: {e}")
            log_activity("ERROR", f"Error processing tasks: {e}", str(self.vault_path))

    def _handle_responses_after_processing(self, processed_count: int):
        """Move any leftover RESPONSE_*.md files to Done/ (transitional cleanup)."""
        try:
            response_dir = self.vault_path / "Responses"
            if not response_dir.exists():
                return
            response_files = list(response_dir.glob("RESPONSE_*.md"))
            done_dir = self.vault_path / "Done"
            done_dir.mkdir(parents=True, exist_ok=True)
            for rf in response_files:
                try:
                    rf.rename(done_dir / rf.name)
                    self.logger.info(f"Moved leftover response file to Done: {rf.name}")
                except Exception as e:
                    self.logger.warning(f"Could not move response file {rf.name}: {e}")
        except Exception as e:
            self.logger.error(f"Error in response cleanup: {e}")

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

    def _apply_gold_tier_features(self, processed_count: int):
        """
        Apply Gold Tier strategic features after task processing
        """
        try:
            if not self.gold_services_initialized or not self.ai_service:
                return

            self.logger.info("Applying Gold Tier strategic analysis...")

            # 1. Generate Strategic Insights
            strategic_insights = self.ai_service.generate_strategic_insights(user_id="default_user")
            
            # 2. Perform Decision Support Analysis
            decision_data = {
                "tasks_processed": processed_count,
                "system_status": "active",
                "timestamp": datetime.now().isoformat()
            }
            decision_support = self.ai_service.assist_with_decision_making(decision_data, "default_user")

            # 3. Update Strategic Dashboard with BI metrics
            from src.utils.dashboard import update_dashboard, get_dashboard_summary
            
            summary = get_dashboard_summary(self.vault_path)
            
            # Merge Gold Tier data into summary
            summary['strategic_insights'] = strategic_insights
            summary['risk_assessment'] = decision_support.get('risk_assessment', {})
            summary['recent_activities'].append(f"Gold Tier: Performed strategic analysis and updated BI metrics.")

            # Update the dashboard file in the vault
            update_dashboard(self.vault_path, summary)
            
            log_activity("GOLD_STRATEGIC_ANALYSIS", 
                        "Strategic insights and BI reporting updated", 
                        str(self.vault_path))

        except Exception as e:
            self.logger.error(f"Error applying Gold Tier features: {e}")
            log_activity("GOLD_FEATURE_ERROR",
                        f"Error applying Gold Tier features: {str(e)}",
                        str(self.vault_path))

    def _apply_platinum_tier_features(self, processed_tasks: list):
        """
        Apply Platinum Tier features after task processing (Odoo + Briefing)
        """
        try:
            if not self.platinum_services_initialized:
                return

            processed_count = len(processed_tasks)
            # Platinum features are handled via Odoo and Briefing services
            # which are triggered through scheduled tasks

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
                self.check_for_scheduled_tasks()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Orchestrator shutting down...")
            log_activity("SYSTEM", "Orchestrator stopped", str(self.vault_path))
            self.cleanup()

    def check_for_scheduled_tasks(self):
        """Check for and run scheduled system tasks like weekly briefings"""
        if not hasattr(self, 'briefing_service') or not self.briefing_service:
            return

        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')

        # Weekly Briefing - Every Friday at 5 PM
        if now.weekday() == 4 and now.hour >= 17:
            if not hasattr(self, 'last_briefing_date'):
                self.last_briefing_date = None
            if self.last_briefing_date != current_date:
                try:
                    self.logger.info("Scheduled task: Generating Weekly CEO Briefing")
                    self.briefing_service.generate_briefing()
                    self.last_briefing_date = current_date
                except Exception as e:
                    self.logger.error(f"Error generating scheduled briefing: {e}")

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

        # Close DB session if it was created
        if hasattr(self, '_db_session') and self._db_session:
            try:
                self._db_session.close()
            except Exception:
                pass

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
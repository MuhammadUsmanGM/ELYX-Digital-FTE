import os
import sys
import threading
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.orchestrator import Orchestrator
from src.config.manager import get_config
from src.utils.logger import setup_logger

def run_silver_tier():
    """
    Launch the Silver Tier components of the AI Employee
    """
    logger = setup_logger("silver_tier_launcher")
    logger.info("Starting Silver Tier AI Employee...")
    
    vault_path = get_config("vault_path", "obsidian_vault")
    
    # Initialize Orchestrator which starts watchers and handles tasks
    orchestrator = Orchestrator(vault_path=vault_path)
    
    # Silver Tier specific configuration check
    logger.info(f"Silver Tier features enabled:")
    logger.info(f"  - Analytics: {get_config('silver_tier_features.enable_analytics', False)}")
    logger.info(f"  - Learning: {get_config('silver_tier_features.enable_learning', False)}")
    logger.info(f"  - Email Integration: {get_config('integrations.gmail_enabled', False)}")
    
    # Start Orchestrator main loop
    # orchestrator.run() starts communication watchers and task monitoring
    orchestrator.run()

if __name__ == "__main__":
    try:
        run_silver_tier()
    except KeyboardInterrupt:
        print("\nSilver Tier shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error in Silver Tier: {e}")
        sys.exit(1)

import time
import logging
import os
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60, use_chrome_profile: bool = True):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Chrome profile configuration
        self.use_chrome_profile = use_chrome_profile
        self.chrome_user_data_dir = os.getenv('CHROME_USER_DATA_DIR', '')
        self.chrome_profile_name = os.getenv('CHROME_PROFILE_NAME', 'Default')
        self.browser_headless = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
        
    def get_browser_args(self):
        """Get browser launch arguments based on configuration"""
        if self.use_chrome_profile and self.chrome_user_data_dir:
            # Use existing Chrome profile (already logged in)
            return {
                'user_data_dir': self.chrome_user_data_dir,
                'headless': self.browser_headless,
                'viewport': {'width': 1280, 'height': 800},
                'locale': 'en-US',
                'args': [
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            }
        else:
            # Fallback to session-based approach
            return {
                'headless': self.browser_headless,
                'viewport': {'width': 1280, 'height': 800}
            }

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Chrome Profile: {self.chrome_user_data_dir}')
        self.logger.info(f'Headless: {self.browser_headless}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    action_file = self.create_action_file(item)
                    self.logger.info(f'Created action file: {action_file}')
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
            time.sleep(self.check_interval)
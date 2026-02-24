import time
import logging
import os
import subprocess
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
        
        # Auto-launch Chrome if closed
        self.auto_launch_chrome = True
        self.chrome_process = None
        
    def ensure_chrome_running(self):
        """
        Ensure Chrome is running with the ELYX profile.
        If not, launch it automatically.
        """
        if not self.auto_launch_chrome or not self.chrome_user_data_dir:
            return
        
        try:
            # Check if Chrome is already running with this profile
            # We'll try to detect by checking if the profile lock file exists
            lock_file = Path(self.chrome_user_data_dir) / 'SingletonLock'
            
            if not lock_file.exists():
                # Chrome is not running with this profile - launch it
                self.logger.info("Chrome profile not detected. Launching Chrome...")
                self.launch_chrome()
            else:
                self.logger.debug("Chrome profile is already running")
                
        except Exception as e:
            self.logger.error(f"Error ensuring Chrome is running: {e}")
            # Try to launch anyway
            self.launch_chrome()
    
    def launch_chrome(self):
        """
        Launch Chrome with the ELYX profile
        """
        try:
            chrome_path = None
            
            # Find Chrome executable based on OS
            if os.name == 'nt':  # Windows
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
            
            if not chrome_path:
                self.logger.error("Chrome executable not found. Please install Google Chrome.")
                return False
            
            # Launch Chrome with the ELYX profile
            cmd = [
                chrome_path,
                f'--user-data-dir={self.chrome_user_data_dir}',
                '--no-first-run',
                '--no-default-browser-check'
            ]
            
            # Start Chrome (don't wait for it)
            self.chrome_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.logger.info(f"Chrome launched with profile: {self.chrome_user_data_dir}")
            self.logger.info("Waiting for Chrome to initialize...")
            
            # Wait for Chrome to initialize
            time.sleep(5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch Chrome: {e}")
            return False
        
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
        self.logger.info(f'Auto-launch Chrome: {self.auto_launch_chrome}')
        
        # Ensure Chrome is running before starting
        if self.use_chrome_profile:
            self.ensure_chrome_running()
        
        while True:
            try:
                # Periodically check if Chrome is still running
                if self.use_chrome_profile and int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.ensure_chrome_running()
                
                items = self.check_for_updates()
                for item in items:
                    action_file = self.create_action_file(item)
                    self.logger.info(f'Created action file: {action_file}')
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
            time.sleep(self.check_interval)
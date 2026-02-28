import time
import logging
import os
import subprocess
import random
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

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
        
        # Error recovery configuration
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
        # Telemetry & Status
        self.status_file = self.vault_path / "Logs" / f"{self.__class__.__name__}_status.json"
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.start_time = datetime.now()
        self.last_check_time = None
        self.items_processed = 0
        
    def ensure_chrome_running(self):
        """Ensure Chrome is running with the ELYX profile."""
        if not self.chrome_user_data_dir:
            return
        
        try:
            lock_file = Path(self.chrome_user_data_dir) / 'SingletonLock'
            
            if not lock_file.exists():
                self.logger.info("Chrome profile not detected. Launching Chrome...")
                self.launch_chrome()
            else:
                self.logger.debug("Chrome profile is already running")
                
        except Exception as e:
            self.logger.error(f"Error ensuring Chrome is running: {e}")
            self.launch_chrome()
    
    def launch_chrome(self):
        """Launch Chrome with the ELYX profile"""
        try:
            chrome_path = None
            
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
                self.logger.error("Chrome executable not found.")
                return False
            
            cmd = [
                chrome_path,
                f'--user-data-dir={self.chrome_user_data_dir}',
                '--no-first-run',
                '--no-default-browser-check'
            ]
            
            self.chrome_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.logger.info(f"Chrome launched with profile: {self.chrome_user_data_dir}")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch Chrome: {e}")
            return False
    
    def get_browser_args(self):
        """Get browser launch arguments"""
        if self.use_chrome_profile and self.chrome_user_data_dir:
            return {
                'user_data_dir': self.chrome_user_data_dir,
                'headless': self.browser_headless,
                'viewport': {'width': 1280, 'height': 800},
                'locale': 'en-US',
                'args': [
                    '--disable-gpu', 
                    '--no-sandbox', 
                    '--disable-dev-shm-usage', 
                    '--disable-blink-features=AutomationControlled',
                    '--excludeSwitches=enable-automation',
                    '--use-fake-ui-for-media-stream'
                ]
            }
        else:
            return {'headless': self.browser_headless, 'viewport': {'width': 1280, 'height': 800}}

    def human_delay(self, min_sec=1, max_sec=3):
        """Sleep for a random human-like duration"""
        time.sleep(random.uniform(min_sec, max_sec))

    def stealth_move_mouse(self, page):
        """Simulate random mouse movements for anti-bot detection"""
        if not page: return
        try:
            viewport = page.viewport_size
            if viewport:
                x = random.randint(0, viewport['width'])
                y = random.randint(0, viewport['height'])
                page.mouse.move(x, y, steps=random.randint(5, 15))
        except Exception:
            pass

    def report_status(self, items_found=0):
        """Report watcher status for telemetry"""
        self.last_check_time = datetime.now()
        status = {
            "watcher": self.__class__.__name__,
            "status": "online",
            "last_check": self.last_check_time.isoformat(),
            "items_processed": self.items_processed,
            "consecutive_errors": self.consecutive_errors,
            "uptime_seconds": (self.last_check_time - self.start_time).total_seconds()
        }
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write status: {e}")
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with retry logic and exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                self.consecutive_errors = 0
                return result
            except Exception as e:
                self.consecutive_errors += 1
                wait_time = self.retry_delay * (2 ** attempt)
                self.logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. Waiting {wait_time}s...")
                
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All {self.max_retries} attempts failed")
                    if self.consecutive_errors >= self.max_consecutive_errors:
                        self.logger.error("Too many consecutive errors! Triggering recovery...")
                        self.recover_from_errors()
                    return None
    
    def recover_from_errors(self):
        """Recovery procedure for when too many errors occur"""
        self.logger.info("Attempting recovery from errors...")
        self.consecutive_errors = 0
        
        if self.use_chrome_profile:
            self.logger.info("Re-initializing Chrome profile...")
            try:
                self.ensure_chrome_running()
                self.logger.info("Chrome re-initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to re-initialize Chrome: {e}")
        
        self.logger.info("Recovery attempt completed")

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
        self.logger.info(f'Error Recovery: Enabled (max retries: {self.max_retries})')
        
        if self.use_chrome_profile:
            self.ensure_chrome_running()
        
        while True:
            try:
                if self.use_chrome_profile and int(time.time()) % 300 == 0:
                    self.ensure_chrome_running()
                
                items = self.execute_with_retry(self.check_for_updates)
                
                if items:
                    for item in items:
                        action_file = self.create_action_file(item)
                        self.logger.info(f'Created action file: {action_file}')
                        self.items_processed += 1
                
                self.report_status(len(items) if items else 0)
                
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
                self.report_status()
            
            # Add random jitter to check interval
            jitter = random.uniform(0.8, 1.2)
            time.sleep(self.check_interval * jitter)

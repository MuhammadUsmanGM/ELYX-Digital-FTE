import subprocess
import sys
import time
import tempfile
import psutil
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WatchdogAgent:
    """
    Monitors system health and automatically restarts failed processes
    """
    def __init__(self, vault_path="vault"):
        self.vault_path = Path(vault_path)
        self.processes = {}
        self.pid_dir = Path(tempfile.gettempdir()) / "elyx_pids"
        self.pid_dir.mkdir(parents=True, exist_ok=True)

    # Maximum number of restarts allowed before giving up (#52)
    MAX_RESTARTS = 10

    def register_process(self, name: str, process_cmd: list, auto_restart: bool = True):
        """
        Register a process to be monitored
        """
        self.processes[name] = {
            'cmd': process_cmd,
            'auto_restart': auto_restart,
            'last_check': datetime.now(),
            'restart_count': 0
        }
        logger.info(f"Registered process: {name}")

    def is_process_running(self, pid: int) -> bool:
        """
        Check if a process with the given PID is running and is a Python process
        (guards against PID reuse by unrelated processes)
        """
        try:
            if not psutil.pid_exists(pid):
                return False
            proc = psutil.Process(pid)
            # Verify it's still a Python process (not a reused PID)
            return 'python' in proc.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def get_process_pid(self, name: str) -> int:
        """
        Get the PID of a registered process from its PID file
        """
        pid_file = self.pid_dir / f"{name}.pid"
        if not pid_file.exists():
            return None

        try:
            pid = int(pid_file.read_text().strip())
            return pid
        except (ValueError, FileNotFoundError):
            return None

    def save_process_pid(self, name: str, pid: int):
        """
        Save the PID of a process to a file
        """
        pid_file = self.pid_dir / f"{name}.pid"
        pid_file.write_text(str(pid))

    def restart_process(self, name: str):
        """
        Restart a failed process (with max-restart protection)
        """
        if name not in self.processes:
            logger.error(f"Process {name} not registered")
            return False

        process_info = self.processes[name]
        if not process_info['auto_restart']:
            logger.info(f"Auto-restart disabled for {name}")
            return False

        if process_info['restart_count'] >= self.MAX_RESTARTS:
            logger.error(
                f"Process {name} exceeded max restarts ({self.MAX_RESTARTS}). "
                f"Disabling auto-restart. Manual intervention required."
            )
            process_info['auto_restart'] = False
            return False

        try:
            logger.info(f"Restarting process: {name}")

            # Start the process
            proc = subprocess.Popen(process_info['cmd'])

            # Save the PID
            self.save_process_pid(name, proc.pid)

            # Update restart count
            process_info['restart_count'] += 1

            logger.info(f"Process {name} restarted with PID: {proc.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to restart process {name}: {e}")
            return False

    def check_processes(self):
        """
        Check the status of all registered processes
        """
        for name, info in self.processes.items():
            pid = self.get_process_pid(name)

            if pid is None:
                logger.warning(f"No PID file found for {name}, attempting restart...")
                self.restart_process(name)
            elif not self.is_process_running(pid):
                logger.warning(f"Process {name} (PID: {pid}) is not running, restarting...")
                self.restart_process(name)
            else:
                logger.debug(f"Process {name} (PID: {pid}) is running normally")

    def run(self, check_interval: int = 60):
        """
        Run the watchdog continuously
        """
        logger.info("Watchdog Agent started, monitoring processes...")

        while True:
            try:
                self.check_processes()

                # Update last check time for all processes
                for name in self.processes:
                    self.processes[name]['last_check'] = datetime.now()

                time.sleep(check_interval)
            except KeyboardInterrupt:
                logger.info("Watchdog Agent stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in watchdog loop: {e}")
                time.sleep(10)  # Wait a bit before continuing after error

    def start_system_monitoring(self):
        """
        Start monitoring the complete AI Employee system.

        NOTE (#51): The orchestrator (run_elyx.py) runs watchers as threads
        internally. This watchdog is for standalone process-based deployment
        only. Do NOT run both the orchestrator and this watchdog simultaneously
        or watchers will be double-launched.
        """
        # Register only the orchestrator — it manages watchers internally
        self.register_process(
            "orchestrator",
            [sys.executable, str(Path(__file__).parent / "orchestrator.py")]
        )


def run_watchdog(vault_path="vault"):
    """
    Convenience function to start the watchdog agent
    """
    watchdog = WatchdogAgent(vault_path)
    watchdog.start_system_monitoring()
    watchdog.run()


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

    # Start the watchdog
    run_watchdog(vault_path)
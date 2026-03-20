"""
Windows Task Scheduler Integration for ELYX AI Employee

Provides:
- Register ELYX watchers as Windows scheduled tasks
- Run tasks at startup, daily, hourly, or custom schedules
- Manage task lifecycle (enable, disable, delete)
- Monitor task execution status
- Log task execution history

Requirements:
- Windows OS (uses win32com.client)
- Administrator privileges recommended for some operations
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

# Windows-specific imports
try:
    import win32com.client
    from win32com.client import Dispatch
    import pythoncom
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    # Fallback for non-Windows systems
    pass

logger = logging.getLogger(__name__)


class WindowsTaskScheduler:
    """
    Windows Task Scheduler integration for ELYX
    """
    
    # Task names for ELYX components
    TASK_NAMES = {
        'orchestrator': 'ELYX_Orchestrator',
        'gmail_watcher': 'ELYX_Gmail_Watcher',
        'whatsapp_watcher': 'ELYX_WhatsApp_Watcher',
        'linkedin_watcher': 'ELYX_LinkedIn_Watcher',
        'facebook_watcher': 'ELYX_Facebook_Watcher',
        'twitter_watcher': 'ELYX_Twitter_Watcher',
        'instagram_watcher': 'ELYX_Instagram_Watcher',
        'odoo_watcher': 'ELYX_Odoo_Watcher',
        'filesystem_watcher': 'ELYX_FileSystem_Watcher',
        'ceo_briefing': 'ELYX_CEO_Briefing',
        'scheduled_posts': 'ELYX_Scheduled_Posts',
        'vault_backup': 'ELYX_Vault_Backup'
    }
    
    # Default schedules
    DEFAULT_SCHEDULES = {
        'orchestrator': {'trigger': 'startup', 'enabled': True},
        'gmail_watcher': {'trigger': 'logon', 'enabled': True},
        'whatsapp_watcher': {'trigger': 'logon', 'enabled': True},
        'linkedin_watcher': {'trigger': 'logon', 'enabled': False},  # Disabled by default
        'facebook_watcher': {'trigger': 'logon', 'enabled': False},
        'twitter_watcher': {'trigger': 'logon', 'enabled': False},
        'instagram_watcher': {'trigger': 'logon', 'enabled': False},
        'odoo_watcher': {'trigger': 'hourly', 'enabled': True},
        'filesystem_watcher': {'trigger': 'startup', 'enabled': True},
        'ceo_briefing': {'trigger': 'weekly', 'day': 'Monday', 'time': '08:00', 'enabled': True},
        'scheduled_posts': {'trigger': 'hourly', 'enabled': True},
        'vault_backup': {'trigger': 'daily', 'time': '02:00', 'enabled': True}
    }
    
    def __init__(self, project_root: str = None):
        """
        Initialize Windows Task Scheduler
        
        Args:
            project_root: Path to ELYX project root
        """
        if not WINDOWS_AVAILABLE:
            raise RuntimeError("Windows Task Scheduler is only available on Windows")
        
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.python_exe = sys.executable
        self.tasks_created = []
        
        # Initialize COM for Windows Task Scheduler
        pythoncom.CoInitialize()
        self.scheduler = Dispatch('Schedule.Service')
        self.scheduler.Connect()
        
        logger.info("Windows Task Scheduler initialized")
    
    def _get_task_folder(self, folder_path: str = '\\'):
        """Get task folder"""
        return self.scheduler.GetFolder(folder_path)
    
    def _create_task_definition(self, name: str, description: str, exe_path: str, 
                                 args: str = '', working_dir: str = ''):
        """
        Create a task definition
        
        Args:
            name: Task name
            description: Task description
            exe_path: Path to executable
            args: Command line arguments
            working_dir: Working directory
        """
        task_def = self.scheduler.NewTask(0)
        
        # Set registration info
        task_def.RegistrationInfo.Description = description
        task_def.RegistrationInfo.Author = "ELYX AI Employee"
        
        # Set settings
        settings = task_def.Settings
        settings.Enabled = True
        settings.StartWhenAvailable = True
        settings.AllowHardTerminate = False
        settings.ExecutionTimeLimit = "PT0S"  # No time limit
        settings.Priority = 7
        settings.MultipleInstances = 1  # Ignore new instances
        settings.DisallowStartIfOnBatteries = False
        settings.StopIfGoingOnBatteries = False
        
        # Set principal (run with highest privileges)
        principal = task_def.Principal
        principal.LogonType = 3  # S4U (no password required)
        principal.RunLevel = 0  # Least privilege
        
        # Set action
        action = task_def.Actions.Create(0)  # 0 = Execute
        action.Path = exe_path
        action.Arguments = args
        action.WorkingDirectory = working_dir or str(self.project_root)
        
        return task_def
    
    def _add_trigger(self, task_def, trigger_type: str, **kwargs):
        """
        Add trigger to task definition

        Args:
            task_def: Task definition object
            trigger_type: Type of trigger (startup, logon, daily, weekly, hourly, once)
            **kwargs: Trigger-specific parameters
        """
        trigger_types = {
            'once': 1,         # TASK_TRIGGER_TIME
            'daily': 2,        # TASK_TRIGGER_DAILY
            'weekly': 3,       # TASK_TRIGGER_WEEKLY
            'monthly': 4,      # TASK_TRIGGER_MONTHLY
            'idle': 6,         # TASK_TRIGGER_IDLE
            'startup': 8,      # TASK_TRIGGER_BOOT
            'logon': 9,        # TASK_TRIGGER_LOGON
            'event': 0         # TASK_TRIGGER_EVENT
        }

        trigger = task_def.Triggers.Create(trigger_types.get(trigger_type, 1))

        if trigger_type == 'startup':
            trigger.Enabled = kwargs.get('enabled', True)

        elif trigger_type == 'logon':
            trigger.Enabled = kwargs.get('enabled', True)
            if kwargs.get('user'):
                trigger.UserId = kwargs['user']

        elif trigger_type == 'daily':
            trigger.StartBoundary = self._get_start_boundary(kwargs.get('time', '00:00'))
            trigger.Enabled = kwargs.get('enabled', True)

        elif trigger_type == 'weekly':
            trigger.DaysOfWeek = self._get_day_of_week(kwargs.get('day', 'Monday'))
            trigger.WeeksInterval = 1
            trigger.StartBoundary = self._get_start_boundary(kwargs.get('time', '00:00'))
            trigger.Enabled = kwargs.get('enabled', True)

        elif trigger_type == 'hourly':
            # Use daily trigger with 1-hour repetition
            trigger.StartBoundary = self._get_start_boundary('00:00')
            trigger.Enabled = kwargs.get('enabled', True)

            # Set repetition
            repetition = trigger.Repetition
            repetition.Interval = "PT1H"  # 1 hour
            repetition.Duration = ""  # Indefinitely
            repetition.StopAtDurationEnd = False

        elif trigger_type == 'once':
            trigger.StartBoundary = kwargs.get('start_time', datetime.now().isoformat())
            trigger.Enabled = True

        return trigger
    
    def _get_start_boundary(self, time_str: str) -> str:
        """Get start boundary in Windows Task Scheduler format"""
        # Format: YYYY-MM-DDTHH:MM:SS
        now = datetime.now()
        try:
            hour, minute = time_str.split(':')
            start = now.replace(hour=int(hour), minute=int(minute), second=0)
            if start < now:
                start += timedelta(days=1)
            return start.strftime('%Y-%m-%dT%H:%M:%S')
        except Exception:
            return now.strftime('%Y-%m-%dT%H:%M:%S')
    
    def _get_day_of_week(self, day_name: str) -> int:
        """Convert day name to day of week number"""
        days = {
            'sunday': 1,
            'monday': 2,
            'tuesday': 4,
            'wednesday': 8,
            'thursday': 16,
            'friday': 32,
            'saturday': 64
        }
        return days.get(day_name.lower(), 1)
    
    def register_task(self, task_name: str, exe_path: str = None, args: str = '',
                      trigger_type: str = 'once', working_dir: str = None,
                      description: str = '', enabled: bool = True,
                      user: str = None, password: str = None,
                      **trigger_kwargs) -> bool:
        """
        Register a task with Windows Task Scheduler

        Args:
            task_name: Name of the task
            exe_path: Path to executable (default: Python)
            args: Command line arguments
            trigger_type: Type of trigger
            working_dir: Working directory
            description: Task description
            enabled: Whether task is enabled
            user: User account to run as
            password: User password (if required)
            **trigger_kwargs: Extra keyword args forwarded to _add_trigger
                              (e.g. day, time for weekly/daily triggers)

        Returns:
            True if successful
        """
        try:
            exe_path = exe_path or self.python_exe
            working_dir = working_dir or str(self.project_root)

            # Create task definition
            task_def = self._create_task_definition(
                name=task_name,
                description=description or f"ELYX {task_name}",
                exe_path=exe_path,
                args=args,
                working_dir=working_dir
            )

            # Add trigger — forward all kwargs so day/time reach _add_trigger
            self._add_trigger(
                task_def,
                trigger_type,
                enabled=enabled,
                user=user,
                **trigger_kwargs
            )
            
            # Register task
            root_folder = self._get_task_folder('\\')
            
            if user and password:
                root_folder.RegisterTaskDefinition(
                    task_name,
                    task_def,
                    6,  # TASK_CREATE_OR_UPDATE
                    user,
                    password,
                    1   # TASK_LOGON_PASSWORD
                )
            else:
                root_folder.RegisterTaskDefinition(
                    task_name,
                    task_def,
                    6,  # TASK_CREATE_OR_UPDATE
                    '',
                    '',
                    3   # TASK_LOGON_S4U
                )
            
            self.tasks_created.append(task_name)
            logger.info(f"Task '{task_name}' registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register task '{task_name}': {e}")
            return False
    
    def unregister_task(self, task_name: str) -> bool:
        """
        Unregister (delete) a task
        
        Args:
            task_name: Name of the task
            
        Returns:
            True if successful
        """
        try:
            root_folder = self._get_task_folder('\\')
            root_folder.DeleteTask(task_name, 0)
            
            if task_name in self.tasks_created:
                self.tasks_created.remove(task_name)
            
            logger.info(f"Task '{task_name}' unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister task '{task_name}': {e}")
            return False
    
    def enable_task(self, task_name: str, enabled: bool = True) -> bool:
        """
        Enable or disable a task
        
        Args:
            task_name: Name of the task
            enabled: True to enable, False to disable
            
        Returns:
            True if successful
        """
        try:
            root_folder = self._get_task_folder('\\')
            task = root_folder.GetTask(task_name)
            task.Enabled = enabled
            
            logger.info(f"Task '{task_name}' {'enabled' if enabled else 'disabled'}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable/disable task '{task_name}': {e}")
            return False
    
    def run_task(self, task_name: str) -> bool:
        """
        Run a task immediately
        
        Args:
            task_name: Name of the task
            
        Returns:
            True if successful
        """
        try:
            root_folder = self._get_task_folder('\\')
            task = root_folder.GetTask(task_name)
            task.Run('')
            
            logger.info(f"Task '{task_name}' started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run task '{task_name}': {e}")
            return False
    
    def get_task_info(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a task
        
        Args:
            task_name: Name of the task
            
        Returns:
            Dictionary with task info or None if not found
        """
        try:
            root_folder = self._get_task_folder('\\')
            task = root_folder.GetTask(task_name)
            
            return {
                'name': task.Name,
                'enabled': task.Enabled,
                'last_run': task.LastRunTime,
                'last_result': task.LastTaskResult,
                'next_run': task.NextRunTime,
                'state': task.State,
                'number_of_missed_runs': task.NumberOfMissedRuns,
                'run_count': task.RunCount
            }
            
        except Exception as e:
            logger.error(f"Failed to get task info for '{task_name}': {e}")
            return None
    
    def list_tasks(self) -> List[str]:
        """
        List all ELYX tasks
        
        Returns:
            List of task names
        """
        elyx_tasks = []
        try:
            root_folder = self._get_task_folder('\\')
            tasks = root_folder.GetTasks(0)
            
            for task in tasks:
                if task.Name.startswith('ELYX_'):
                    elyx_tasks.append(task.Name)
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
        
        return elyx_tasks
    
    def register_elyx_tasks(self, schedules: Dict[str, Dict] = None) -> Dict[str, bool]:
        """
        Register all ELYX tasks with default or custom schedules
        
        Args:
            schedules: Custom schedules (optional)
            
        Returns:
            Dictionary of task_name -> success status
        """
        schedules = schedules or self.DEFAULT_SCHEDULES
        results = {}
        
        # Build task configurations
        task_configs = {
            'orchestrator': {
                'exe': self.python_exe,
                'args': str(self.project_root / 'run_elyx.py'),
                'description': 'ELYX Main Orchestrator - Coordinates all watchers and AI processing'
            },
            'gmail_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.gmail_watcher "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX Gmail Watcher - Monitors Gmail for important messages'
            },
            'whatsapp_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.whatsapp_watcher "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX WhatsApp Watcher - Monitors WhatsApp for urgent messages'
            },
            'linkedin_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.linkedin_watcher "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX LinkedIn Watcher - Monitors LinkedIn messages'
            },
            'facebook_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.facebook_watcher "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX Facebook Watcher - Monitors Facebook Messenger'
            },
            'twitter_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.twitter_watcher "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX Twitter Watcher - Monitors Twitter/X notifications and DMs'
            },
            'instagram_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.instagram_watcher "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX Instagram Watcher - Monitors Instagram DMs'
            },
            'odoo_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.odoo_watcher "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX Odoo Watcher - Monitors Odoo accounting for invoices and payments'
            },
            'filesystem_watcher': {
                'exe': self.python_exe,
                'args': f'-m src.agents.filesystem_watcher "{self.project_root / "watch"}" "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX File System Watcher - Monitors file drops for processing'
            },
            'ceo_briefing': {
                'exe': self.python_exe,
                'args': f'-m src.services.briefing_service "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX CEO Briefing - Generates weekly business reports every Monday at 8 AM'
            },
            'scheduled_posts': {
                'exe': self.python_exe,
                'args': f'-m src.services.social_posting_service --process-scheduled "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX Scheduled Posts - Publishes scheduled social media posts'
            },
            'vault_backup': {
                'exe': self.python_exe,
                'args': f'-m src.services.sync_vault --backup "{self.project_root / "obsidian_vault"}"',
                'description': 'ELYX Vault Backup - Backs up Obsidian vault daily at 2 AM'
            }
        }
        
        # Register each task
        for task_key, config in task_configs.items():
            schedule = schedules.get(task_key, self.DEFAULT_SCHEDULES.get(task_key, {}))
            
            if not schedule.get('enabled', True):
                results[task_key] = 'skipped'
                continue
            
            task_name = self.TASK_NAMES.get(task_key, f'ELYX_{task_key.title()}')
            
            # Determine trigger type
            trigger = schedule.get('trigger', 'once')
            trigger_kwargs = {'enabled': True}
            
            if trigger == 'weekly':
                trigger_kwargs['day'] = schedule.get('day', 'Monday')
                trigger_kwargs['time'] = schedule.get('time', '08:00')
            elif trigger == 'daily':
                trigger_kwargs['time'] = schedule.get('time', '00:00')
            
            success = self.register_task(
                task_name=task_name,
                exe_path=config['exe'],
                args=config['args'],
                trigger_type=trigger,
                description=config['description'],
                enabled=True,
                **trigger_kwargs
            )
            
            results[task_key] = 'registered' if success else 'failed'
        
        return results
    
    def unregister_all_elyx_tasks(self) -> Dict[str, bool]:
        """
        Unregister all ELYX tasks
        
        Returns:
            Dictionary of task_name -> success status
        """
        results = {}
        
        for task_name in self.TASK_NAMES.values():
            success = self.unregister_task(task_name)
            results[task_name] = 'unregistered' if success else 'failed'
        
        return results
    
    def get_all_elyx_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all ELYX tasks
        
        Returns:
            Dictionary of task_name -> status info
        """
        status = {}
        
        for task_name in self.TASK_NAMES.values():
            info = self.get_task_info(task_name)
            if info:
                status[task_name] = info
            else:
                status[task_name] = {'status': 'not_found'}
        
        return status
    
    def __del__(self):
        """Cleanup COM"""
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def main():
    """Command-line interface for Windows Task Scheduler management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ELYX Windows Task Scheduler Manager')
    parser.add_argument('action', choices=['register', 'unregister', 'status', 'list', 'run', 'enable', 'disable'],
                       help='Action to perform')
    parser.add_argument('--task', '-t', help='Specific task name (optional)')
    parser.add_argument('--project-root', '-p', help='Project root directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    if not WINDOWS_AVAILABLE:
        print("ERROR: Windows Task Scheduler is only available on Windows")
        sys.exit(1)
    
    try:
        scheduler = WindowsTaskScheduler(project_root=args.project_root)
        
        if args.action == 'register':
            if args.task:
                success = scheduler.register_task(args.task)
                print(f"Task '{args.task}': {'SUCCESS' if success else 'FAILED'}")
            else:
                results = scheduler.register_elyx_tasks()
                print("\nELYX Task Registration Results:")
                print("-" * 50)
                for task, status in results.items():
                    icon = "✓" if status == 'registered' else "○" if status == 'skipped' else "✗"
                    print(f"  {icon} {task}: {status}")
        
        elif args.action == 'unregister':
            if args.task:
                success = scheduler.unregister_task(args.task)
                print(f"Task '{args.task}': {'SUCCESS' if success else 'FAILED'}")
            else:
                results = scheduler.unregister_all_elyx_tasks()
                print("\nELYX Task Unregistration Results:")
                print("-" * 50)
                for task, status in results.items():
                    icon = "✓" if status == 'unregistered' else "✗"
                    print(f"  {icon} {task}: {status}")
        
        elif args.action == 'status':
            if args.task:
                info = scheduler.get_task_info(args.task)
                if info:
                    print(f"\nTask: {args.task}")
                    print("-" * 50)
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"Task '{args.task}' not found")
            else:
                status = scheduler.get_all_elyx_tasks_status()
                print("\nELYX Tasks Status:")
                print("-" * 50)
                for task, info in status.items():
                    if info.get('status') == 'not_found':
                        print(f"  ○ {task}: Not registered")
                    else:
                        enabled = "✓" if info.get('enabled') else "✗"
                        last_run = info.get('last_run', 'Never')
                        print(f"  {enabled} {task}: Last run: {last_run}")
        
        elif args.action == 'list':
            tasks = scheduler.list_tasks()
            print("\nRegistered ELYX Tasks:")
            print("-" * 50)
            for task in tasks:
                print(f"  - {task}")
            if not tasks:
                print("  No ELYX tasks found")
        
        elif args.action == 'run':
            if args.task:
                success = scheduler.run_task(args.task)
                print(f"Task '{args.task}': {'STARTED' if success else 'FAILED'}")
            else:
                print("ERROR: --task is required for 'run' action")
                sys.exit(1)
        
        elif args.action == 'enable':
            if args.task:
                success = scheduler.enable_task(args.task, enabled=True)
                print(f"Task '{args.task}': {'ENABLED' if success else 'FAILED'}")
            else:
                print("ERROR: --task is required for 'enable' action")
                sys.exit(1)
        
        elif args.action == 'disable':
            if args.task:
                success = scheduler.enable_task(args.task, enabled=False)
                print(f"Task '{args.task}': {'DISABLED' if success else 'FAILED'}")
            else:
                print("ERROR: --task is required for 'disable' action")
                sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

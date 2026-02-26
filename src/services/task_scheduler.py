"""
Windows Task Scheduler Integration for ELYX
Creates scheduled tasks for:
- CEO Briefing (every Monday 8 AM)
- System health check (every hour)
- Watcher restart (daily at 3 AM)
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def create_scheduled_task(task_name, action, start_time, frequency):
    """
    Create a Windows scheduled task
    
    Args:
        task_name: Name of the task
        action: Command to execute
        start_time: Start time (HH:MM format)
        frequency: ONEVENT, DAILY, WEEKLY, etc.
    """
    python_exe = sys.executable
    project_root = Path(__file__).parent.parent
    
    cmd = [
        'schtasks', '/Create',
        '/TN', f'ELYX_{task_name}',
        '/TR', f'"{python_exe}" "{action}"',
        '/SC', frequency,
        '/ST', start_time,
        '/RL', 'HIGHEST',
        '/F'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[OK] Created scheduled task: ELYX_{task_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to create task: {e}")
        return False

def setup_all_scheduled_tasks():
    """Setup all ELYX scheduled tasks"""
    project_root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("ELYX - Windows Task Scheduler Setup")
    print("=" * 70)
    print()
    
    tasks = [
        {
            'name': 'CEO_Briefing',
            'action': str(project_root / 'src' / 'services' / 'briefing_service.py'),
            'time': '08:00',
            'frequency': 'WEEKLY',
            'description': 'Generate weekly CEO briefing every Monday at 8 AM'
        },
        {
            'name': 'Health_Check',
            'action': str(project_root / 'run_elyx_status.py'),
            'time': '00:00',
            'frequency': 'HOURLY',
            'description': 'System health check every hour'
        },
        {
            'name': 'Watcher_Restart',
            'action': str(project_root / 'run_elyx.py'),
            'time': '03:00',
            'frequency': 'DAILY',
            'description': 'Restart watchers daily at 3 AM'
        }
    ]
    
    created = 0
    failed = 0
    
    for task in tasks:
        print(f"Creating task: {task['name']}")
        print(f"  Description: {task['description']}")
        print(f"  Schedule: {task['frequency']} at {task['time']}")
        
        if create_scheduled_task(task['name'], task['action'], task['time'], task['frequency']):
            created += 1
        else:
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"Setup Complete: {created} created, {failed} failed")
    print("=" * 70)
    print()
    print("To view scheduled tasks:")
    print("  Open Task Scheduler (taskschd.msc)")
    print("  Look for tasks starting with 'ELYX_'")
    print()
    print("To remove all ELYX tasks:")
    print("  python remove_scheduled_tasks.py")

if __name__ == "__main__":
    setup_all_scheduled_tasks()

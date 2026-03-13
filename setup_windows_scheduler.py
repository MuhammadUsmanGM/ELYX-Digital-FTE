#!/usr/bin/env python3
"""
ELYX Windows Task Scheduler Setup Script

Usage:
    python setup_windows_scheduler.py register    - Register all ELYX tasks
    python setup_windows_scheduler.py unregister  - Unregister all ELYX tasks
    python setup_windows_scheduler.py status      - Show status of all tasks
    python setup_windows_scheduler.py list        - List all ELYX tasks
    python setup_windows_scheduler.py run --task <name>  - Run a specific task
    python setup_windows_scheduler.py enable --task <name>  - Enable a task
    python setup_windows_scheduler.py disable --task <name> - Disable a task

Requirements:
    - Windows OS
    - Python 3.10+
    - pywin32 package (pip install pywin32)
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    print(f"\n{Colors.OKCYAN}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  ELYX Windows Task Scheduler Setup{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 70}{Colors.ENDC}\n")


def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}  {title}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'=' * 70}{Colors.ENDC}")


def check_prerequisites():
    """Check if prerequisites are met"""
    print_section("Checking Prerequisites")
    
    # Check Windows OS
    if os.name != 'nt':
        print(f"  {Colors.FAIL}X{Colors.ENDC} Windows OS required (detected: {os.name})")
        return False
    print(f"  {Colors.OKGREEN}[OK]{Colors.ENDC} Windows OS detected")
    
    # Check pywin32
    try:
        import win32com.client
        print(f"  {Colors.OKGREEN}[OK]{Colors.ENDC} pywin32 installed")
    except ImportError:
        print(f"  {Colors.FAIL}[ERR]{Colors.ENDC} pywin32 not installed")
        print(f"\n  {Colors.WARNING}Install with: pip install pywin32{Colors.ENDC}\n")
        return False
    
    # Check admin privileges (recommended but not required)
    import ctypes
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print(f"  {Colors.OKGREEN}[OK]{Colors.ENDC} Running as Administrator")
        else:
            print(f"  {Colors.WARNING}[!]{Colors.ENDC} Not running as Administrator (some features may be limited)")
    except Exception:
        print(f"  {Colors.WARNING}[!]{Colors.ENDC} Could not determine admin status")
    
    return True


def register_tasks():
    """Register all ELYX tasks"""
    from src.services.windows_task_scheduler import WindowsTaskScheduler
    
    print_section("Registering ELYX Tasks")
    
    try:
        scheduler = WindowsTaskScheduler(str(project_root))
        results = scheduler.register_elyx_tasks()
        
        print("\nRegistration Results:")
        print("-" * 70)
        
        registered = 0
        failed = 0
        skipped = 0
        
        for task, status in results.items():
            if status == 'registered':
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {task}: Registered")
                registered += 1
            elif status == 'skipped':
                print(f"  {Colors.WARNING}○{Colors.ENDC} {task}: Skipped (disabled in config)")
                skipped += 1
            else:
                print(f"  {Colors.FAIL}✗{Colors.ENDC} {task}: Failed")
                failed += 1
        
        print("\n" + "-" * 70)
        print(f"  {Colors.BOLD}Summary: {registered} registered, {skipped} skipped, {failed} failed{Colors.ENDC}")
        
        if failed == 0:
            print(f"\n  {Colors.OKGREEN}✓ All tasks registered successfully!{Colors.ENDC}")
            print(f"\n  {Colors.WARNING}Note: Tasks will run according to their schedules.{Colors.ENDC}")
            print(f"  {Colors.WARNING}      Some tasks run at startup/logon, others run hourly/daily/weekly.{Colors.ENDC}")
        else:
            print(f"\n  {Colors.FAIL}✗ Some tasks failed to register.{Colors.ENDC}")
            print(f"  {Colors.WARNING}      Run as Administrator for best results.{Colors.ENDC}")
        
        return failed == 0
        
    except Exception as e:
        print(f"\n  {Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False


def unregister_tasks():
    """Unregister all ELYX tasks"""
    from src.services.windows_task_scheduler import WindowsTaskScheduler
    
    print_section("Unregistering ELYX Tasks")
    
    try:
        scheduler = WindowsTaskScheduler(str(project_root))
        results = scheduler.unregister_all_elyx_tasks()
        
        print("\nUnregistration Results:")
        print("-" * 70)
        
        unregistered = 0
        failed = 0
        
        for task, status in results.items():
            if status == 'unregistered':
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {task}: Unregistered")
                unregistered += 1
            else:
                print(f"  {Colors.FAIL}✗{Colors.ENDC} {task}: Failed")
                failed += 1
        
        print("\n" + "-" * 70)
        print(f"  {Colors.BOLD}Summary: {unregistered} unregistered, {failed} failed{Colors.ENDC}")
        
        if failed == 0:
            print(f"\n  {Colors.OKGREEN}✓ All tasks unregistered successfully!{Colors.ENDC}")
        else:
            print(f"\n  {Colors.FAIL}✗ Some tasks failed to unregister.{Colors.ENDC}")
        
        return failed == 0
        
    except Exception as e:
        print(f"\n  {Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False


def show_status():
    """Show status of all ELYX tasks"""
    from src.services.windows_task_scheduler import WindowsTaskScheduler
    
    print_section("ELYX Tasks Status")
    
    try:
        scheduler = WindowsTaskScheduler(str(project_root))
        status = scheduler.get_all_elyx_tasks_status()
        
        print()
        
        active = 0
        inactive = 0
        not_found = 0
        
        for task, info in status.items():
            if info.get('status') == 'not_found':
                print(f"  {Colors.WARNING}○{Colors.ENDC} {task}")
                print(f"      Status: Not registered")
                not_found += 1
            else:
                enabled = info.get('enabled', False)
                last_run = info.get('last_run', 'Never')
                next_run = info.get('next_run', 'N/A')
                state = info.get('state', 'Unknown')
                
                if enabled:
                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {task}")
                    active += 1
                else:
                    print(f"  {Colors.FAIL}✗{Colors.ENDC} {task}")
                    inactive += 1
                
                print(f"      Enabled: {enabled}")
                print(f"      Last Run: {last_run}")
                print(f"      Next Run: {next_run}")
                print(f"      State: {state}")
                print()
        
        print("-" * 70)
        print(f"  {Colors.BOLD}Summary: {active} active, {inactive} inactive, {not_found} not found{Colors.ENDC}")
        
    except Exception as e:
        print(f"\n  {Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


def list_tasks():
    """List all registered ELYX tasks"""
    from src.services.windows_task_scheduler import WindowsTaskScheduler
    
    print_section("Registered ELYX Tasks")
    
    try:
        scheduler = WindowsTaskScheduler(str(project_root))
        tasks = scheduler.list_tasks()
        
        if tasks:
            print()
            for task in sorted(tasks):
                print(f"  • {task}")
            print(f"\n  {Colors.BOLD}Total: {len(tasks)} tasks{Colors.ENDC}")
        else:
            print(f"\n  {Colors.WARNING}No ELYX tasks found.{Colors.ENDC}")
            print(f"  Run 'python setup_windows_scheduler.py register' to register tasks.")
        
    except Exception as e:
        print(f"\n  {Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


def run_task(task_name: str):
    """Run a specific task immediately"""
    from src.services.windows_task_scheduler import WindowsTaskScheduler
    
    print_section(f"Running Task: {task_name}")
    
    try:
        scheduler = WindowsTaskScheduler(str(project_root))
        success = scheduler.run_task(task_name)
        
        if success:
            print(f"\n  {Colors.OKGREEN}✓ Task '{task_name}' started successfully.{Colors.ENDC}")
            print(f"  Check Task Scheduler for execution results.")
        else:
            print(f"\n  {Colors.FAIL}✗ Failed to start task '{task_name}'.{Colors.ENDC}")
        
    except Exception as e:
        print(f"\n  {Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


def enable_task(task_name: str, enable: bool):
    """Enable or disable a specific task"""
    from src.services.windows_task_scheduler import WindowsTaskScheduler
    
    action = "Enabling" if enable else "Disabling"
    print_section(f"{action} Task: {task_name}")
    
    try:
        scheduler = WindowsTaskScheduler(str(project_root))
        success = scheduler.enable_task(task_name, enabled=enable)
        
        if success:
            status = "enabled" if enable else "disabled"
            print(f"\n  {Colors.OKGREEN}✓ Task '{task_name}' {status}.{Colors.ENDC}")
        else:
            print(f"\n  {Colors.FAIL}✗ Failed to {action.lower()} task '{task_name}'.{Colors.ENDC}")
        
    except Exception as e:
        print(f"\n  {Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


def show_help():
    """Show help message"""
    print(f"""
{Colors.BOLD}ELYX Windows Task Scheduler Setup{Colors.ENDC}

{Colors.OKCYAN}Usage:{Colors.ENDC}
    python setup_windows_scheduler.py <action> [options]

{Colors.OKCYAN}Actions:{Colors.ENDC}
    register      Register all ELYX tasks with Windows Task Scheduler
    unregister    Unregister all ELYX tasks
    status        Show status of all ELYX tasks
    list          List all registered ELYX tasks
    run           Run a specific task immediately (requires --task)
    enable        Enable a specific task (requires --task)
    disable       Disable a specific task (requires --task)
    help          Show this help message

{Colors.OKCYAN}Options:{Colors.ENDC}
    --task <name>  Specify task name (required for run/enable/disable)
    --verbose      Show verbose output

{Colors.OKCYAN}Examples:{Colors.ENDC}
    python setup_windows_scheduler.py register
    python setup_windows_scheduler.py unregister
    python setup_windows_scheduler.py status
    python setup_windows_scheduler.py run --task ELYX_CEO_Briefing
    python setup_windows_scheduler.py enable --task ELYX_Gmail_Watcher
    python setup_windows_scheduler.py disable --task ELYX_Facebook_Watcher

{Colors.OKCYAN}Registered Tasks:{Colors.ENDC}
    ELYX_Orchestrator        - Main orchestrator (runs at startup)
    ELYX_Gmail_Watcher       - Gmail monitoring (runs at logon)
    ELYX_WhatsApp_Watcher    - WhatsApp monitoring (runs at logon)
    ELYX_LinkedIn_Watcher    - LinkedIn monitoring (runs at logon)
    ELYX_Facebook_Watcher    - Facebook monitoring (runs at logon)
    ELYX_Twitter_Watcher     - Twitter monitoring (runs at logon)
    ELYX_Instagram_Watcher   - Instagram monitoring (runs at logon)
    ELYX_Odoo_Watcher        - Odoo accounting (runs hourly)
    ELYX_FileSystem_Watcher  - File system monitoring (runs at startup)
    ELYX_CEO_Briefing        - Weekly CEO report (Mondays 8 AM)
    ELYX_Scheduled_Posts     - Social media posting (runs hourly)
    ELYX_Vault_Backup        - Vault backup (runs daily at 2 AM)

{Colors.OKCYAN}Requirements:{Colors.ENDC}
    - Windows OS
    - Python 3.10+
    - pywin32 package (pip install pywin32)
    - Administrator privileges (recommended)
""")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ELYX Windows Task Scheduler Setup',
        add_help=False
    )
    parser.add_argument('action', nargs='?', default='help',
                       choices=['register', 'unregister', 'status', 'list', 'run', 'enable', 'disable', 'help'])
    parser.add_argument('--task', '-t', help='Task name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--help', '-h', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    if args.help or args.action == 'help':
        show_help()
        return
    
    print_banner()
    
    # Check prerequisites for actions that need them
    if args.action in ['register', 'unregister', 'status', 'list', 'run', 'enable', 'disable']:
        if not check_prerequisites():
            print(f"\n{Colors.FAIL}Prerequisites not met. Please install required packages.{Colors.ENDC}")
            sys.exit(1)
    
    # Execute action
    if args.action == 'register':
        success = register_tasks()
    elif args.action == 'unregister':
        success = unregister_tasks()
    elif args.action == 'status':
        show_status()
        success = True
    elif args.action == 'list':
        list_tasks()
        success = True
    elif args.action == 'run':
        if not args.task:
            print(f"\n{Colors.FAIL}Error: --task is required for 'run' action{Colors.ENDC}")
            sys.exit(1)
        run_task(args.task)
        success = True
    elif args.action == 'enable':
        if not args.task:
            print(f"\n{Colors.FAIL}Error: --task is required for 'enable' action{Colors.ENDC}")
            sys.exit(1)
        enable_task(args.task, True)
        success = True
    elif args.action == 'disable':
        if not args.task:
            print(f"\n{Colors.FAIL}Error: --task is required for 'disable' action{Colors.ENDC}")
            sys.exit(1)
        enable_task(args.task, False)
        success = True
    else:
        show_help()
        success = True
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

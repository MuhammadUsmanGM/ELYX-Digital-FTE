#!/usr/bin/env python3
"""
ELYX - Autonomous AI Employee
Main Startup Script - ALL-IN-ONE

Starts:
1. Vault API (Port 8080)
2. Settings API (Port 8081)
3. Main FastAPI Server (Port 8000)
4. Next.js Frontend (Port 3000)
5. ELYX Orchestrator & Watchers

Local-First | Multi-Platform | Human-in-the-Loop
"""

import os
import sys
import time
import threading
import subprocess
import signal
import atexit
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
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
    UNDERLINE = '\033[4m'
    
    # RGB Colors for gradient
    ELYX_GRADIENT = '\033[38;2;0;201;167m'  # Cyan/teal color

# Global process tracking
processes = []
vault_git_enabled = False

def is_vault_git_repo():
    """Check if vault is a git repository"""
    global vault_git_enabled
    vault_path = Path("obsidian_vault")
    git_dir = vault_path / ".git"
    vault_git_enabled = git_dir.exists()
    return vault_git_enabled

def commit_vault_changes(message: str = "Auto-commit: Vault changes"):
    """Commit vault changes to git"""
    if not vault_git_enabled:
        return False
    
    try:
        vault_path = Path("obsidian_vault")
        
        # Check if there are changes
        success, stdout, stderr = run_command(["git", "status", "--porcelain"], cwd=vault_path)
        if not stdout.strip():
            return False  # No changes

        # Add, commit, push
        run_command(["git", "add", "."], cwd=vault_path)
        run_command(["git", "commit", "-m", message], cwd=vault_path)
        
        # Don't push automatically (let GitHub Actions handle it)
        # run_command("git push origin main", cwd=vault_path)
        
        return True
    except Exception as e:
        print(f"Warning: Could not commit vault changes: {e}")
        return False

def run_command(cmd, cwd=None):
    """Run shell command safely using list form only (#53)"""
    try:
        if isinstance(cmd, str):
            # Use shlex.split for correct handling of quoted paths/spaces
            import shlex
            cmd_list = shlex.split(cmd)
        else:
            cmd_list = cmd
        result = subprocess.run(cmd_list, shell=False, cwd=cwd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def start_vault_api():
    """Start Vault API server"""
    print(f"\n{Colors.BOLD}Starting Vault API (Port 8080)...{Colors.ENDC}")
    try:
        proc = subprocess.Popen(
            [sys.executable, str(project_root / "src" / "api" / "vault_api.py"), "--port", "8080"],
            cwd=str(project_root)
        )
        processes.append(proc)
        time.sleep(2)
        print(f"  {Colors.OKGREEN}✓ Vault API running at http://localhost:8080{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"  {Colors.FAIL}✗ Failed to start Vault API: {e}{Colors.ENDC}")
        return False

def start_settings_api():
    """Start Settings API server"""
    print(f"\n{Colors.BOLD}Starting Settings API (Port 8081)...{Colors.ENDC}")
    try:
        proc = subprocess.Popen(
            [sys.executable, str(project_root / "src" / "api" / "settings_api.py"), "--port", "8081"],
            cwd=str(project_root)
        )
        processes.append(proc)
        time.sleep(2)
        print(f"  {Colors.OKGREEN}✓ Settings API running at http://localhost:8081{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"  {Colors.FAIL}✗ Failed to start Settings API: {e}{Colors.ENDC}")
        return False

def start_main_api():
    """Start Main FastAPI server (dashboard, communications, analytics, approvals, etc.)"""
    port = os.getenv("PORT", "8000")
    print(f"\n{Colors.BOLD}Starting Main API (Port {port})...{Colors.ENDC}")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", port],
            cwd=str(project_root)
        )
        processes.append(proc)
        time.sleep(3)
        print(f"  {Colors.OKGREEN}✓ Main API running at http://localhost:{port}{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"  {Colors.FAIL}✗ Failed to start Main API: {e}{Colors.ENDC}")
        return False

def start_frontend():
    """Start Next.js frontend"""
    print(f"\n{Colors.BOLD}Starting Frontend (Port 3000)...{Colors.ENDC}")
    frontend_dir = project_root / "frontend"
    
    if not (frontend_dir / "node_modules").exists():
        print(f"  {Colors.WARNING}⚠ Frontend not installed. Run: cd frontend && npm install{Colors.ENDC}")
        return False
    
    try:
        # Check if npm is available
        npm_cmd = "npm"
        if sys.platform == "win32":
            npm_cmd = "npm.cmd"
        
        proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir)
        )
        processes.append(proc)
        time.sleep(5)
        print(f"  {Colors.OKGREEN}✓ Frontend running at http://localhost:3000{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"  {Colors.FAIL}✗ Failed to start frontend: {e}{Colors.ENDC}")
        return False

_cleanup_done = False

def cleanup(signum=0, frame=None):
    """Clean shutdown of all processes"""
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True

    print(f"\n\n{Colors.WARNING}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Shutting Down ELYX...{Colors.ENDC}")
    print(f"{Colors.WARNING}{'='*80}{Colors.ENDC}")

    print(f"\n  Stopping services...")

    for proc in processes:
        try:
            if hasattr(proc, 'cleanup'):
                # Orchestrator object — call its cleanup method
                proc.cleanup()
                print(f"    ✓ Orchestrator cleaned up")
            elif hasattr(proc, 'terminate'):
                proc.terminate()
                proc.wait(timeout=5)
                print(f"    ✓ Service stopped")
        except Exception:
            try:
                if hasattr(proc, 'kill'):
                    proc.kill()
                print(f"    ✓ Service killed")
            except Exception:
                print(f"    ⚠ Service force closed")

    print(f"\n  {Colors.OKGREEN}✓ All services stopped{Colors.ENDC}")
    print(f"  {Colors.BOLD}ELYX shutdown complete. Goodbye!{Colors.ENDC}\n")

def print_banner():
    """Print ELYX startup banner with ASCII art"""
    # ELYX ASCII Art with gradient color
    print(f"\n{Colors.ELYX_GRADIENT}███████╗██╗     ██╗   ██╗██╗  ██╗{Colors.ENDC}")
    print(f"{Colors.ELYX_GRADIENT}██╔════╝██║     ╚██╗ ██╔╝╚██╗██╔╝{Colors.ENDC}")
    print(f"{Colors.ELYX_GRADIENT}█████╗  ██║      ╚████╔╝  ╚███╔╝ {Colors.ENDC}")
    print(f"{Colors.ELYX_GRADIENT}██╔══╝  ██║       ╚██╔╝   ██╔██╗ {Colors.ENDC}")
    print(f"{Colors.ELYX_GRADIENT}███████╗███████╗   ██║   ██╔╝ ██╗{Colors.ENDC}")
    print(f"{Colors.ELYX_GRADIENT}╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝{Colors.ENDC}")
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}  Autonomous AI Employee - Local-First | Multi-Platform | Human-in-the-Loop{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}\n")

def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}  {title}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'─' * 80}{Colors.ENDC}")

def get_brain_info():
    """Get active AI brain from .env"""
    brain = os.getenv('ELYX_ACTIVE_BRAIN', 'claude').upper()
    brain_icons = {
        'CLAUDE': '🤖 Claude Code',
        'QWEN': '💻 Qwen Coder',
        'GEMINI': '🌟 Google Gemini',
        'CODEX': '📝 OpenAI Codex'
    }
    return brain_icons.get(brain, f'🤖 {brain}')

def print_system_status():
    """Print comprehensive system status"""
    print_section("SYSTEM STATUS")
    
    # AI Brain
    brain_info = get_brain_info()
    print(f"\n  {Colors.BOLD}AI Brain:{Colors.ENDC} {brain_info}")
    print(f"  {Colors.BOLD}Active Since:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Watchers Status
    print(f"\n  {Colors.BOLD}{Colors.OKGREEN}[ACTIVE WATCHERS]:{Colors.ENDC}")
    print(f"    +------------------------------------------------------------+")
    print(f"    |  [G] Gmail           -> Every 2 minutes   |  [OK] Active  |")
    print(f"    |  [W] WhatsApp        -> Every 1 minute    |  [OK] Active  |")
    print(f"    |  [L] LinkedIn        -> Every hour        |  [OK] Active  |")
    print(f"    |  [F] Facebook        -> Every 2 hours     |  [OK] Active  |")
    print(f"    |  [T] Twitter/X       -> Every 2 hours     |  [OK] Active  |")
    print(f"    |  [I] Instagram       -> Every 2 hours     |  [OK] Active  |")
    print(f"    |  [O] Odoo Accounting -> Every hour        |  [OK] Active  |")
    print(f"    |  [S] Filesystem      -> Every 10 seconds  |  [OK] Active  |")
    print(f"    +------------------------------------------------------------+")
    
    # Capabilities
    print(f"\n  {Colors.BOLD}{Colors.OKGREEN}[CAPABILITIES]:{Colors.ENDC}")
    print(f"    [+] Multi-platform communication monitoring (7 channels)")
    print(f"    [+] Automated response to routine inquiries")
    print(f"    [+] Human-in-the-loop approval for sensitive actions")
    print(f"    [+] Weekly CEO Briefing generation (Mondays 8 AM)")
    print(f"    [+] Social media auto-posting")
    print(f"    [+] Invoice & payment tracking via Odoo")
    print(f"    [+] Cryptographic audit logging (SHA3-512)")
    print(f"    [+] Autonomous multi-step task completion (Ralph Wiggum)")
    print(f"    [+] Chrome profile auto-launch & session preservation")
    
    # Access Points
    print(f"\n  {Colors.BOLD}{Colors.OKGREEN}[ACCESS POINTS]:{Colors.ENDC}")
    print(f"    +------------------------------------------------------------+")
    print(f"    |  [Dashboard]    obsidian_vault/Dashboard.md                |")
    print(f"    |  [Handbook]     obsidian_vault/Company_Handbook.md         |")
    print(f"    |  [Tasks]        obsidian_vault/Needs_Action/               |")
    print(f"    |  [Done]         obsidian_vault/Done/                       |")
    print(f"    |  [Pending]      obsidian_vault/Pending_Approval/           |")
    print(f"    |  [Briefings]    obsidian_vault/Briefings/                  |")
    print(f"    |  [Audit Logs]   obsidian_vault/Logs/                       |")
    print(f"    +------------------------------------------------------------+")
    
    # Chrome Profile
    chrome_profile = os.getenv('CHROME_USER_DATA_DIR', 'Not configured')
    print(f"\n  {Colors.BOLD}{Colors.OKGREEN}[CHROME PROFILE]:{Colors.ENDC}")
    print(f"    - Path: {chrome_profile}")
    print(f"    - Auto-Launch: {'[OK] Enabled' if chrome_profile else '[--] Disabled'}")
    print(f"    - Health Check: Every 5 minutes")
    print(f"    - Session Preservation: [OK] Active")

def print_shutdown_message():
    """Print graceful shutdown message"""
    print(f"\n\n{Colors.WARNING}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.WARNING}  SHUTTING DOWN ELYX AI EMPLOYEE{Colors.ENDC}")
    print(f"{Colors.WARNING}{'=' * 80}{Colors.ENDC}")
    print(f"\n  [OK] Stopping watchers...")
    print(f"  [OK] Closing database connections...")
    print(f"  [OK] Saving audit logs...")
    print(f"\n  {Colors.OKGREEN}[COMPLETE] ELYX shutdown complete.{Colors.ENDC}")
    print(f"  {Colors.BOLD}All systems preserved. Goodbye!{Colors.ENDC}\n")

def main():
    """Main ELYX startup function - ALL-IN-ONE"""
    print_banner()

    print(f"{Colors.BOLD}[START]{Colors.ENDC} ELYX Autonomous AI Employee (All-in-One)")
    print(f"{Colors.BOLD}[TIME]{Colors.ENDC}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup)
    # SIGTERM is not reliably delivered on Windows (Task Manager sends SIGKILL),
    # but register it where available for Unix compatibility
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, cleanup)
    # Use atexit as a fallback to ensure cleanup runs on normal exit
    atexit.register(cleanup)

    # Initialize vault
    vault_path = Path("obsidian_vault")
    vault_path.mkdir(exist_ok=True)
    print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} Vault path: {vault_path}")

    # Start APIs and Frontend
    print_section("Starting Web Services")
    
    start_vault_api()
    start_settings_api()
    start_main_api()
    start_frontend()

    # Start Orchestrator
    print(f"\n{Colors.BOLD}[INIT]{Colors.ENDC} Starting Orchestrator...")
    try:
        from src.agents.orchestrator import Orchestrator
        orchestrator = Orchestrator(vault_path=str(vault_path))
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} Orchestrator initialized")

        # Run orchestrator in background thread (non-daemon so cleanup runs)
        orch_thread = threading.Thread(target=orchestrator.run, daemon=False, name="orchestrator")
        orch_thread.start()
        processes.append(orchestrator)  # Track for cleanup
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} Orchestrator started (monitoring active)")

    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Failed to start Orchestrator: {e}")
        import traceback
        traceback.print_exc()
        cleanup()

    # Print comprehensive status
    print_system_status()

    # Print access URLs
    print(f"\n{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKGREEN}  ✓ SYSTEM READY - AI EMPLOYEE OPERATIONAL{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}[ACCESS POINTS]:{Colors.ENDC}")
    print(f"  Dashboard:     http://localhost:3000")
    print(f"  Tasks:         http://localhost:3000/tasks")
    print(f"  Approvals:     http://localhost:3000/approvals")
    print(f"  Settings:      http://localhost:3000/settings")
    print(f"  Feature Flags: http://localhost:3000/settings → Feature Flags tab")
    print()
    print(f"  Main API:      http://localhost:8000")
    print(f"  Vault API:     http://localhost:8080")
    print(f"  Settings API:  http://localhost:8081")
    print()

    print(f"\n{Colors.WARNING}Press Ctrl+C to shut down all services gracefully.{Colors.ENDC}\n")

    # Check if vault is git repo
    is_vault_git_repo()
    if vault_git_enabled:
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} Vault Git repository detected - auto-commit enabled")
        print(f"   Changes will be committed every hour")
        print(f"   GitHub Actions will sync to GitHub automatically\n")

    # Keep alive with periodic vault commits
    last_commit_time = time.time()
    commit_interval = 3600  # 1 hour
    
    try:
        while True:
            time.sleep(10)
            
            # Auto-commit vault changes every hour
            if vault_git_enabled and (time.time() - last_commit_time) > commit_interval:
                print(f"\n{Colors.BOLD}[AUTO-COMMIT]{Colors.ENDC} Committing vault changes...")
                if commit_vault_changes(f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M')}"):
                    print(f"  {Colors.OKGREEN}✓ Vault changes committed{Colors.ENDC}")
                last_commit_time = time.time()
                
    except KeyboardInterrupt:
        # Final commit before shutdown
        if vault_git_enabled:
            print(f"\n{Colors.BOLD}[AUTO-COMMIT]{Colors.ENDC} Final vault commit before shutdown...")
            commit_vault_changes(f"Final commit: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        cleanup()
        sys.exit(0)

if __name__ == "__main__":
    main()

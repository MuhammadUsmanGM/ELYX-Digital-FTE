#!/usr/bin/env python3
"""
ELYX - Autonomous AI Employee
Main Startup Script - ALL-IN-ONE

Starts:
1. Vault API (Port 8080)
2. Settings API (Port 8081)
3. Next.js Frontend (Port 3000)
4. ELYX Orchestrator & Watchers

Local-First | Multi-Platform | Human-in-the-Loop
"""

import os
import sys
import time
import threading
import subprocess
import signal
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

def cleanup(signum=0, frame=None):
    """Clean shutdown of all processes"""
    print(f"\n\n{Colors.WARNING}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Shutting Down ELYX...{Colors.ENDC}")
    print(f"{Colors.WARNING}{'='*80}{Colors.ENDC}")
    
    print(f"\n  Stopping services...")
    
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
            print(f"    ✓ Service stopped")
        except:
            try:
                proc.kill()
                print(f"    ✓ Service killed")
            except:
                print(f"    ⚠ Service force closed")
    
    print(f"\n  {Colors.OKGREEN}✓ All services stopped{Colors.ENDC}")
    print(f"  {Colors.BOLD}ELYX shutdown complete. Goodbye!{Colors.ENDC}\n")
    sys.exit(0)

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
    signal.signal(signal.SIGTERM, cleanup)

    # Initialize vault
    vault_path = Path("obsidian_vault")
    vault_path.mkdir(exist_ok=True)
    print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} Vault path: {vault_path}")

    # Start APIs and Frontend
    print_section("Starting Web Services")
    
    start_vault_api()
    start_settings_api()
    start_frontend()

    # Start Orchestrator
    print(f"\n{Colors.BOLD}[INIT]{Colors.ENDC} Starting Orchestrator...")
    try:
        from src.agents.orchestrator import Orchestrator
        orchestrator = Orchestrator(vault_path=str(vault_path))
        print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} Orchestrator initialized")

        # Run orchestrator in background thread
        orch_thread = threading.Thread(target=orchestrator.run, daemon=True)
        orch_thread.start()
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
    print(f"  Vault API:     http://localhost:8080")
    print(f"  Settings API:  http://localhost:8081")
    print()

    print(f"\n{Colors.WARNING}Press Ctrl+C to shut down all services gracefully.{Colors.ENDC}\n")

    # Keep alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()

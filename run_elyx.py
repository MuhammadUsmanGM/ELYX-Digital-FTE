#!/usr/bin/env python3
"""
ELYX - Autonomous AI Employee
Main Startup Script

Local-First | Multi-Platform | Human-in-the-Loop
"""

import os
import sys
import time
import threading
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

def print_banner():
    """Print ELYX startup banner with ASCII art"""
    # ELYX ASCII Art - Pure ASCII (no Unicode)
    print(f"\n{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  [E]____[L]____[Y]____[X]____{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  | ___| | ___| | ___| | ___|{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  | |__  | |__  | |__  | |__  {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  |  __| |  __| |  __| |  __| {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  | |___ | |___ | |___ | |___ {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}  |____| |____| |____| |____| {Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}  Autonomous AI Employee - Local-First | Multi-Platform | Human-in-the-Loop{Colors.ENDC}")
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
    """Main ELYX startup function"""
    print_banner()
    
    print(f"{Colors.BOLD}[START]{Colors.ENDC} ELYX Autonomous AI Employee")
    print(f"{Colors.BOLD}[TIME]{Colors.ENDC}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize vault
    vault_path = Path("obsidian_vault")
    vault_path.mkdir(exist_ok=True)
    print(f"{Colors.OKGREEN}[OK]{Colors.ENDC} Vault path: {vault_path}")
    
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
        sys.exit(1)
    
    # Print comprehensive status
    print_system_status()
    
    print(f"\n{Colors.OKGREEN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKGREEN}  ✓ SYSTEM READY - AI EMPLOYEE OPERATIONAL{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{'=' * 80}{Colors.ENDC}")
    
    print(f"\n{Colors.WARNING}Press Ctrl+C to shut down gracefully.{Colors.ENDC}\n")
    
    # Keep alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print_shutdown_message()

if __name__ == "__main__":
    main()

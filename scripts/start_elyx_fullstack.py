#!/usr/bin/env python3
"""
ELYX Full Stack Startup Script
Starts Vault API, Settings API, and provides instructions for Next.js frontend

Usage:
    python scripts/start_elyx_fullstack.py
"""

import subprocess
import sys
import time
from pathlib import Path

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    OKCYAN = '\033[96m'

def main():
    project_root = Path(__file__).parent.parent
    
    print(f"\n{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}ELYX Full Stack Startup{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}\n")
    
    # Start Vault API
    print(f"{Colors.BOLD}Starting Vault API Server (Port 8080)...{Colors.ENDC}")
    vault_api_process = subprocess.Popen(
        [sys.executable, str(project_root / "src" / "api" / "vault_api.py"), "--port", "8080"],
        cwd=str(project_root)
    )
    time.sleep(2)
    print(f"  {Colors.OKGREEN}✓ Vault API running at http://localhost:8080{Colors.ENDC}")
    
    # Start Settings API
    print(f"{Colors.BOLD}Starting Settings API Server (Port 8081)...{Colors.ENDC}")
    settings_api_process = subprocess.Popen(
        [sys.executable, str(project_root / "src" / "api" / "settings_api.py"), "--port", "8081"],
        cwd=str(project_root)
    )
    time.sleep(2)
    print(f"  {Colors.OKGREEN}✓ Settings API running at http://localhost:8081{Colors.ENDC}")
    
    # Frontend instructions
    print(f"\n{Colors.BOLD}Frontend Setup:{Colors.ENDC}")
    
    frontend_dir = project_root / "frontend"
    
    if (frontend_dir / "node_modules").exists():
        print(f"\n{Colors.BOLD}Services Running:{Colors.ENDC}")
        print(f"  1. Vault API:    {Colors.OKGREEN}http://localhost:8080{Colors.ENDC}")
        print(f"  2. Settings API: {Colors.OKGREEN}http://localhost:8081{Colors.ENDC}")
        print(f"  3. Frontend:     {Colors.WARNING}cd frontend && npm run dev{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Access URLs:{Colors.ENDC}")
        print(f"  - Dashboard:     http://localhost:3000/dashboard")
        print(f"  - Tasks:         http://localhost:3000/tasks")
        print(f"  - Approvals:     http://localhost:3000/approvals")
        print(f"  - Settings:      http://localhost:3000/settings")
        print(f"  - Feature Flags: http://localhost:3000/settings → Feature Flags tab")
        
        print(f"\n{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}API Endpoints:{Colors.ENDC}")
        print(f"  Vault API (8080):")
        print(f"    GET  /api/vault/summary")
        print(f"    GET  /api/vault/tasks")
        print(f"    GET  /api/vault/approvals")
        print(f"    POST /api/vault/approve")
        print(f"    POST /api/vault/reject")
        print()
        print(f"  Settings API (8081):")
        print(f"    GET  /api/settings/flags - Get all feature flags")
        print(f"    POST /api/settings/flags - Update feature flag")
        print(f"    GET  /api/settings/all - Get all settings")
        print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
        
    else:
        print(f"\n{Colors.FAIL}Frontend not installed!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Setup Instructions:{Colors.ENDC}")
        print(f"  cd frontend")
        print(f"  npm install")
        print(f"  npm run dev")
    
    print(f"\n{Colors.WARNING}Press Ctrl+C to stop all services{Colors.ENDC}\n")
    
    try:
        vault_api_process.wait()
        settings_api_process.wait()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Shutting down all services...{Colors.ENDC}")
        vault_api_process.terminate()
        settings_api_process.terminate()

if __name__ == "__main__":
    main()

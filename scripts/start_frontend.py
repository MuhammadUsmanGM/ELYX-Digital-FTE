#!/usr/bin/env python3
"""
ELYX Frontend Startup Script
Starts both Vault API and provides instructions for Next.js frontend

Usage:
    python scripts/start_frontend.py
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
    print(f"{Colors.BOLD}ELYX Frontend Startup{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}\n")
    
    # Start Vault API in background
    print(f"{Colors.BOLD}Starting Vault API Server...{Colors.ENDC}")
    
    vault_api_process = subprocess.Popen(
        [sys.executable, str(project_root / "src" / "api" / "vault_api.py"), "--port", "8080"],
        cwd=str(project_root)
    )
    
    # Wait for API to start
    time.sleep(2)
    print(f"  {Colors.OKGREEN}✓ Vault API running at http://localhost:8080{Colors.ENDC}")
    
    # Start Next.js frontend
    print(f"\n{Colors.BOLD}Starting Next.js Frontend...{Colors.ENDC}")
    print(f"  {Colors.WARNING}Note: Run 'npm run dev' in frontend/ directory{Colors.ENDC}")
    
    frontend_dir = project_root / "frontend"
    
    if (frontend_dir / "node_modules").exists():
        print(f"\n{Colors.BOLD}Commands:{Colors.ENDC}")
        print(f"  1. Vault API: {Colors.OKGREEN}Running on port 8080{Colors.ENDC}")
        print(f"  2. Frontend:  {Colors.WARNING}cd frontend && npm run dev{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Access:{Colors.ENDC}")
        print(f"  - Dashboard: http://localhost:3000/dashboard")
        print(f"  - Tasks:     http://localhost:3000/tasks")
        print(f"  - Approvals: http://localhost:3000/approvals")
    else:
        print(f"\n{Colors.FAIL}Frontend not installed!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Setup Instructions:{Colors.ENDC}")
        print(f"  cd frontend")
        print(f"  npm install")
        print(f"  npm run dev")
    
    print(f"\n{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}Vault API Endpoints:{Colors.ENDC}")
    print(f"  GET  http://localhost:8080/api/vault/summary")
    print(f"  GET  http://localhost:8080/api/vault/tasks")
    print(f"  GET  http://localhost:8080/api/vault/approvals")
    print(f"  GET  http://localhost:8080/api/vault/completed")
    print(f"  POST http://localhost:8080/api/vault/approve")
    print(f"  POST http://localhost:8080/api/vault/reject")
    print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
    
    print(f"\n{Colors.WARNING}Press Ctrl+C to stop Vault API{Colors.ENDC}\n")
    
    try:
        vault_api_process.wait()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Shutting down...{Colors.ENDC}")
        vault_api_process.terminate()

if __name__ == "__main__":
    main()

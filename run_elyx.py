#!/usr/bin/env python3
"""
Simplified ELYX Startup Script
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

print("=" * 80)
print("  ELYX - Autonomous AI Employee")
print("  Local-First | Multi-Platform | Human-in-the-Loop")
print("=" * 80)
print()
print(f"[START] ELYX Autonomous AI Employee")
print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Initialize vault
vault_path = Path("obsidian_vault")
vault_path.mkdir(exist_ok=True)
print(f"[OK] Vault path: {vault_path}")

# Start Orchestrator
print(f"\n[INIT] Starting Orchestrator...")
try:
    from src.agents.orchestrator import Orchestrator
    orchestrator = Orchestrator(vault_path=str(vault_path))
    print(f"[OK] Orchestrator initialized")
    
    # Run orchestrator in background thread
    orch_thread = threading.Thread(target=orchestrator.run, daemon=True)
    orch_thread.start()
    print(f"[OK] Orchestrator started (monitoring active)")
    
except Exception as e:
    print(f"[ERROR] Failed to start Orchestrator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("  [OK] SYSTEM READY - AI EMPLOYEE OPERATIONAL")
print("=" * 80)
print()
print("[MONITORING] Active Watchers:")
print("   • Gmail (every 2 minutes)")
print("   • WhatsApp (every 1 minute)")
print("   • LinkedIn (every hour)")
print("   • Facebook (every 2 hours)")
print("   • Twitter (every 2 hours)")
print("   • Instagram (every 2 hours)")
print("   • Odoo (every hour)")
print("   • Filesystem (every 10 seconds)")
print()
print("Press Ctrl+C to shut down gracefully.")
print()

# Keep alive
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("\n\n[SHUTDOWN] Shutting down ELYX...")
    print("[COMPLETE] ELYX shutdown complete.")

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.orchestrator import Orchestrator
import asyncio

async def test_platinum_run():
    vault_path = "obsidian_vault"
    
    # Initialize Orchestrator (it will load config and init services)
    print("🚀 Initializing Platinum Orchestrator...")
    orchestrator = Orchestrator(vault_path=vault_path)
    
    # Manually trigger services initialization if not already done by __init__
    if not orchestrator.platinum_services_initialized:
        print("Initializing Platinum services manually...")
        orchestrator._initialize_platinum_services()
        
    print(f"Platinum Initialized: {orchestrator.platinum_services_initialized}")
    print(f"Global Regions: {orchestrator.global_regions}")
    
    # Simulate processing a task and applying platinum features
    print("\n📦 Simulating task completion (Platinum Tier)...")
    orchestrator._apply_platinum_tier_features(processed_count=3)
    
    print("\n✅ Platinum processing complete. Check obsidian_vault/Dashboard.md for the report.")

if __name__ == "__main__":
    asyncio.run(test_platinum_run())

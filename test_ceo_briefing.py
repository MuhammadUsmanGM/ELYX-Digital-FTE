"""
Test CEO Briefing Service
Generates a sample CEO briefing to test the service
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.services.briefing_service import CEOBriefingService, run_ceo_briefing

print("=" * 70)
print("ELYX - CEO BRIEFING TEST")
print("=" * 70)
print()

vault = sys.argv[1] if len(sys.argv) > 1 else "obsidian_vault"

try:
    print(f"Generating CEO Briefing for vault: {vault}")
    print()
    
    briefing = run_ceo_briefing(vault)
    
    print()
    print("=" * 70)
    print("BRIEFING GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Briefing saved to: obsidian_vault/Briefings/")
    print()
    print("Summary:")
    print(f"  - Revenue This Week: ${briefing['revenue']['this_week']:.2f}")
    print(f"  - Tasks Completed: {len(briefing['completed_tasks'])}")
    print(f"  - Bottlenecks: {len(briefing['bottlenecks'])}")
    print(f"  - Suggestions: {len(briefing['suggestions'])}")
    print()
    print("Next Steps:")
    print("1. Check obsidian_vault/Briefings/ for the generated briefing")
    print("2. Review bottlenecks and suggestions")
    print("3. Schedule automatic generation (every Monday 8 AM)")
    
except Exception as e:
    print(f"[ERROR] {e}")
    print()
    print("Troubleshooting:")
    print("1. Ensure Odoo is configured in .env")
    print("2. Ensure obsidian_vault folder exists")
    print("3. Check that Done/ folder has some completed tasks")

print()
print("=" * 70)


import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.briefing_service import BriefingService
from src.utils.logger import setup_logger
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def test_briefing_generation():
    logger = setup_logger("test.briefing")
    logger.info("Starting manual Weekly CEO Briefing generation test...")
    
    # Ensure vault directories exist
    vault_path = Path("obsidian_vault")
    (vault_path / "Logs").mkdir(parents=True, exist_ok=True)
    (vault_path / "Done").mkdir(parents=True, exist_ok=True)
    
    # Initialize Service
    service = BriefingService(str(vault_path))
    
    try:
        # Generate the report
        report_path = service.generate_weekly_briefing()
        print(f"\n✅ SUCCESS: Weekly CEO Briefing generated at: {report_path}")
        print("\n--- Report Preview ---")
        # Use encoding='utf-8' to avoid 'charmap' errors on Windows
        print(report_path.read_text(encoding='utf-8')[:500] + "...")
        print("--- End Preview ---\n")
    except Exception as e:
        print(f"\n❌ ERROR generating briefing: {e}")

if __name__ == "__main__":
    test_briefing_generation()

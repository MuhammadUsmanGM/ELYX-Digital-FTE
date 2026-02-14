import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.services.ai_service import AIService

def test_process():
    vault_path = "obsidian_vault"
    
    print("Initializing Gold Tier AI Service...")
    ai_service = AIService()
    
    processor = TaskProcessor(vault_path=vault_path, ai_service=ai_service)
    
    print("Processing pending tasks...")
    count = processor.process_pending_tasks()
    print(f"Processed {count} tasks.")
    
    # Simulate the Orchestrator's post-processing call for BI reporting
    print("Generating Gold Tier Strategic Report...")
    # Since we don't have the full Orchestrator instance here, we simulate it
    strategic_insights = ai_service.generate_strategic_insights(user_id="default_user")
    decision_support = ai_service.assist_with_decision_making({"test": True}, "default_user")
    
    from src.utils.dashboard import update_dashboard, get_dashboard_summary
    summary = get_dashboard_summary(vault_path)
    summary['strategic_insights'] = strategic_insights
    summary['risk_assessment'] = decision_support.get('risk_assessment', {})
    
    update_dashboard(vault_path, summary)
    print("Dashboard updated with Gold Tier metrics.")

if __name__ == "__main__":
    test_process()

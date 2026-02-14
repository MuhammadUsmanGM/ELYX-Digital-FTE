import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.claude_skills.ai_employee_skills.processor import TaskProcessor

def test_process():
    vault_path = "obsidian_vault"
    processor = TaskProcessor(vault_path=vault_path)
    
    print("Processing pending tasks...")
    count = processor.process_pending_tasks()
    print(f"Processed {count} tasks.")

if __name__ == "__main__":
    test_process()

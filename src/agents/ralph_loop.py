import subprocess
import time
import os
from pathlib import Path
import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("RalphLoop")

class RalphLoop:
    """
    Implements the 'Ralph Wiggum' loop for autonomous task completion
    using the Claude Code CLI.
    """
    def __init__(self, vault_path: str, max_iterations: int = 5):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.max_iterations = max_iterations
        self.logger = setup_logger()

    def has_pending_tasks(self) -> bool:
        """Check if there are any .md files in Needs_Action"""
        if not self.needs_action_path.exists():
            return False
        return len(list(self.needs_action_path.glob("*.md"))) > 0

    def run_iteration(self):
        """Run one iteration of Claude Code to process tasks"""
        prompt = (
            "You are ELYX, an autonomous AI Employee. "
            "Please check the /Needs_Action folder in my Obsidian vault. "
            "For each task: "
            "1. Read the task file. "
            "2. Cross-reference with Company_Handbook.md for rules. "
            "3. Check Trusted_Contacts.md for whitelisting. "
            "4. Execute the task (draft email, post to LinkedIn, etc.) using available MCP tools. "
            "5. Move the task file to /Done when finished. "
            "Do not stop until you have processed all pending files in /Needs_Action."
        )

        self.logger.info("Starting Claude Code iteration...")
        
        # We use 'claude -p' for a non-interactive single-prompt execution
        # but the hackathon doc suggests an interactive loop if we have the hook.
        # Assuming we want it to be as autonomous as possible:
        try:
            # Note: -p allows passing a prompt directly to Claude Code
            process = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info("Claude Code finished iteration successfully.")
            self.logger.debug(f"Claude Output: {process.stdout}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Claude Code failed with exit code {e.returncode}")
            self.logger.error(f"Error output: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Unexpected error running Claude Code: {e}")

    def start(self):
        """Start the autonomous processing loop"""
        self.logger.info("ELYX Autonomous Loop (Ralph Wiggum) started.")
        
        iteration = 0
        while iteration < self.max_iterations:
            if not self.has_pending_tasks():
                self.logger.info("No pending tasks. Loop ending.")
                break
                
            iteration += 1
            self.logger.info(f"Iteration {iteration}/{self.max_iterations}")
            self.run_iteration()
            
            # Brief pause to let file system settle
            time.sleep(5)
            
        if iteration >= self.max_iterations:
            self.logger.warning("Reached maximum iterations. Some tasks might still be pending.")

if __name__ == "__main__":
    # Example usage
    loop = RalphLoop(vault_path="obsidian_vault")
    loop.start()

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
    Implements the 'Ralph Wiggum' loop for autonomous task completion.
    Now supports Universal Brain Selection (Claude, Qwen, Gemini, Codex).
    """
    def __init__(self, vault_path: str, max_iterations: int = 5):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.max_iterations = max_iterations
        self.logger = setup_logger()

        # Initialize the BrainFactory for dynamic brain selection
        try:
            from src.services.brain_factory import get_brain_factory
            self.brain_factory = get_brain_factory()
            self.active_brain = self.brain_factory.get_active_brain()
            self.logger.info(f"RalphLoop initialized with brain: '{self.active_brain.name}'")
        except Exception as e:
            self.logger.warning(f"BrainFactory unavailable ({e}). Falling back to 'claude'.")
            self.brain_factory = None
            self.active_brain = None

    def has_pending_tasks(self) -> bool:
        """Check if there are any .md files in Needs_Action"""
        if not self.needs_action_path.exists():
            return False
        return len(list(self.needs_action_path.glob("*.md"))) > 0

    def _build_command(self, prompt: str) -> list:
        """Build the command list using the active brain or fallback to claude."""
        if self.active_brain:
            return self.active_brain.build_command(prompt)
        else:
            # Fallback: hardcoded claude
            return ["claude", "-p", prompt]

    def run_iteration(self):
        """Run one iteration of the active AI brain to process tasks"""
        prompt = (
            "You are ELYX, an autonomous AI Employee. "
            "Please check the /Needs_Action folder in my Obsidian vault. "
            "For each task: "
            "1. Read the task file. "
            "2. Cross-reference with Company_Handbook.md for rules. "
            "3. Execute the task (draft email, post to LinkedIn, etc.) using available MCP tools. "
            "4. Move the task file to /Done when finished. "
            "Do not stop until you have processed all pending files in /Needs_Action."
        )

        brain_name = self.active_brain.name if self.active_brain else "claude (fallback)"
        self.logger.info(f"Starting iteration with brain: '{brain_name}'...")

        cmd = self._build_command(prompt)

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"Brain '{brain_name}' finished iteration successfully.")
            self.logger.debug(f"Output: {process.stdout}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Brain '{brain_name}' failed with exit code {e.returncode}")
            self.logger.error(f"Error output: {e.stderr}")
        except FileNotFoundError:
            self.logger.error(f"Command for brain '{brain_name}' not found. Is it installed?")
        except Exception as e:
            self.logger.error(f"Unexpected error running brain '{brain_name}': {e}")

    def switch_brain(self, brain_name: str) -> bool:
        """Switch the active brain at runtime."""
        if self.brain_factory:
            success = self.brain_factory.set_active_brain(brain_name)
            if success:
                self.active_brain = self.brain_factory.get_active_brain()
                self.logger.info(f"RalphLoop brain switched to: '{brain_name}'")
            return success
        else:
            self.logger.error("BrainFactory not available. Cannot switch brain.")
            return False

    def start(self):
        """Start the autonomous processing loop"""
        brain_name = self.active_brain.name if self.active_brain else "claude"
        self.logger.info(f"ELYX Autonomous Loop (Ralph Wiggum) started with brain: '{brain_name}'.")

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

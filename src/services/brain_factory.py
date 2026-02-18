"""
Universal Brain Factory
Allows ELYX to dynamically select between different AI coding agents
(Claude Code, Qwen, Gemini CLI, Codex) for task processing.
"""

import json
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class BrainAdapter:
    """
    Represents a single AI brain (coding agent) that can process prompts.
    """
    def __init__(self, name: str, command: str, args: List[str], description: str = ""):
        self.name = name
        self.command = command
        self.args = args
        self.description = description
        self.logger = logging.getLogger(f"Brain.{name}")

    def build_command(self, prompt: str) -> List[str]:
        """Build the full subprocess command list for this brain."""
        cmd = [self.command] + self.args + [prompt]
        return cmd

    def process(self, prompt: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute the brain with the given prompt and return the result.
        """
        cmd = self.build_command(prompt)
        self.logger.info(f"[{self.name}] Executing: {' '.join(cmd[:3])}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "brain": self.name,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            self.logger.error(f"[{self.name}] Timed out after {timeout}s")
            return {
                "brain": self.name,
                "success": False,
                "stdout": "",
                "stderr": f"Timeout after {timeout}s",
                "returncode": -1
            }
        except FileNotFoundError:
            self.logger.error(f"[{self.name}] Command '{self.command}' not found. Is it installed?")
            return {
                "brain": self.name,
                "success": False,
                "stdout": "",
                "stderr": f"Command '{self.command}' not found",
                "returncode": -2
            }
        except Exception as e:
            self.logger.error(f"[{self.name}] Unexpected error: {e}")
            return {
                "brain": self.name,
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -3
            }

    def __repr__(self):
        return f"BrainAdapter(name='{self.name}', command='{self.command}')"


class BrainFactory:
    """
    Factory that manages and provides AI brain adapters based on configuration.
    Reads from config.json and .env to determine the active brain.
    """
    # Default brain definitions (used if config.json doesn't have them)
    DEFAULT_BRAINS = {
        "claude": {
            "command": "claude",
            "args": ["-p"],
            "description": "Anthropic Claude Code - Strategic reasoning and execution"
        },
        "qwen": {
            "command": "qwen",
            "args": ["-p"],
            "description": "Alibaba Qwen Coder - Fast local coding tasks"
        },
        "gemini": {
            "command": "gemini",
            "args": ["-p"],
            "description": "Google Gemini CLI - High-volume triage and analysis"
        },
        "codex": {
            "command": "codex",
            "args": ["-p"],
            "description": "OpenAI Codex CLI - Code generation and refactoring"
        }
    }

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.brains: Dict[str, BrainAdapter] = {}
        self.active_brain_name: str = "claude"  # Default
        self._load_configuration()

    def _load_configuration(self):
        """Load brain definitions and active selection from config and env."""
        brain_config = self.DEFAULT_BRAINS.copy()

        # 1. Try to load from config.json
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
                
                brain_section = full_config.get("brain_selection", {})
                if brain_section.get("brains"):
                    brain_config.update(brain_section["brains"])
                
                if brain_section.get("active_brain"):
                    self.active_brain_name = brain_section["active_brain"]
            except Exception as e:
                logger.warning(f"Could not load brain config from {self.config_path}: {e}")

        # 2. Environment variable overrides config.json
        env_brain = os.getenv("ELYX_ACTIVE_BRAIN")
        if env_brain:
            self.active_brain_name = env_brain.lower().strip()

        # 3. Register all brain adapters
        for name, definition in brain_config.items():
            self.brains[name] = BrainAdapter(
                name=name,
                command=definition.get("command", name),
                args=definition.get("args", ["-p"]),
                description=definition.get("description", "")
            )

        logger.info(f"BrainFactory initialized. Active brain: '{self.active_brain_name}'. "
                     f"Available: {list(self.brains.keys())}")

    def get_active_brain(self) -> BrainAdapter:
        """Return the currently active brain adapter."""
        if self.active_brain_name not in self.brains:
            logger.warning(f"Active brain '{self.active_brain_name}' not found. Falling back to 'claude'.")
            self.active_brain_name = "claude"
        return self.brains[self.active_brain_name]

    def get_brain(self, name: str) -> Optional[BrainAdapter]:
        """Get a specific brain adapter by name."""
        return self.brains.get(name)

    def set_active_brain(self, name: str) -> bool:
        """Switch the active brain at runtime."""
        if name in self.brains:
            self.active_brain_name = name
            logger.info(f"Active brain switched to: '{name}'")
            return True
        else:
            logger.error(f"Cannot switch to unknown brain: '{name}'. Available: {list(self.brains.keys())}")
            return False

    def list_brains(self) -> Dict[str, str]:
        """List all available brains and their descriptions."""
        return {name: adapter.description for name, adapter in self.brains.items()}

    def register_brain(self, name: str, command: str, args: List[str], description: str = ""):
        """Register a new brain adapter dynamically."""
        self.brains[name] = BrainAdapter(name=name, command=command, args=args, description=description)
        logger.info(f"Registered new brain: '{name}' -> '{command}'")


# --- Singleton Instance ---
_brain_factory: Optional[BrainFactory] = None

def get_brain_factory(config_path: str = "config.json") -> BrainFactory:
    """Get or create the global BrainFactory singleton."""
    global _brain_factory
    if _brain_factory is None:
        _brain_factory = BrainFactory(config_path)
    return _brain_factory

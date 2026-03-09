#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook for Claude Code

This script is invoked by Claude Code's Stop hook. It checks whether there
are still unprocessed tasks in the Needs_Action folder. If tasks remain,
it exits with code 1 (blocking Claude from stopping) and prints a message
that gets fed back into Claude's prompt. If no tasks remain, it exits with
code 0 (allowing Claude to stop).

Usage in .claude/settings.local.json:
  "hooks": {
    "Stop": [{
      "command": "python scripts/ralph_stop_hook.py",
      "timeout": 10000
    }]
  }
"""

import sys
from pathlib import Path

VAULT_PATH = Path(__file__).parent.parent / "obsidian_vault"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
MAX_ITERATIONS_FILE = VAULT_PATH / "Logs" / ".ralph_iteration_count"


def get_iteration_count() -> int:
    """Track how many times the stop hook has been invoked."""
    try:
        if MAX_ITERATIONS_FILE.exists():
            return int(MAX_ITERATIONS_FILE.read_text().strip())
    except Exception:
        pass
    return 0


def increment_iteration():
    MAX_ITERATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    count = get_iteration_count() + 1
    MAX_ITERATIONS_FILE.write_text(str(count))
    return count


def reset_iteration():
    if MAX_ITERATIONS_FILE.exists():
        MAX_ITERATIONS_FILE.write_text("0")


def get_pending_tasks() -> list:
    """Return list of .md files in Needs_Action."""
    if not NEEDS_ACTION.exists():
        return []
    return [f.name for f in NEEDS_ACTION.glob("*.md")]


def main():
    max_iterations = 10
    pending = get_pending_tasks()
    iteration = increment_iteration()

    if not pending:
        # No tasks left — allow exit
        reset_iteration()
        print("TASK_COMPLETE: All tasks in Needs_Action have been processed.")
        sys.exit(0)

    if iteration >= max_iterations:
        # Safety valve — allow exit after max iterations
        reset_iteration()
        print(f"WARNING: Reached max iterations ({max_iterations}). "
              f"Remaining tasks: {', '.join(pending[:5])}")
        sys.exit(0)

    # Tasks still pending — block exit and re-inject prompt
    print(f"RALPH_WIGGUM: {len(pending)} tasks still pending in Needs_Action/ "
          f"(iteration {iteration}/{max_iterations}). "
          f"Continue processing: {', '.join(pending[:5])}")
    sys.exit(1)


if __name__ == "__main__":
    main()

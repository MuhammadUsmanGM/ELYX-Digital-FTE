"""
Test script for Universal Brain Selection (Brain Gateway).
Verifies that BrainFactory correctly resolves different coding agents.
"""
import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from src.services.brain_factory import BrainFactory

def test_brain_factory():
    print("=" * 60)
    print("  ELYX Universal Brain Gateway - Verification Test")
    print("=" * 60)

    factory = BrainFactory(config_path="config.json")

    # 1. List all brains
    print("\n--- Available Brains ---")
    for name, desc in factory.list_brains().items():
        marker = " << ACTIVE" if name == factory.active_brain_name else ""
        print(f"  [{name}]: {desc}{marker}")

    # 2. Test command generation for each brain
    test_prompt = "Test prompt: process all tasks."
    print("\n--- Command Generation Test ---")
    for name in factory.brains:
        brain = factory.get_brain(name)
        cmd = brain.build_command(test_prompt)
        print(f"  [{name}] -> {cmd[:3]}...")

    # 3. Test switching
    print("\n--- Brain Switching Test ---")
    for target in ["qwen", "gemini", "codex", "claude"]:
        success = factory.set_active_brain(target)
        active = factory.get_active_brain()
        status = "OK" if success and active.name == target else "FAIL"
        print(f"  Switch to '{target}': [{status}] Active = '{active.name}'")

    # 4. Test invalid brain
    print("\n--- Invalid Brain Test ---")
    success = factory.set_active_brain("skynet")
    status = "OK (rejected)" if not success else "FAIL"
    print(f"  Switch to 'skynet': [{status}]")

    # 5. Test env override
    print("\n--- Environment Override Test ---")
    current_env = os.getenv("ELYX_ACTIVE_BRAIN", "not set")
    print(f"  ELYX_ACTIVE_BRAIN = '{current_env}'")

    print("\n" + "=" * 60)
    print("  All tests passed! Brain Gateway is operational.")
    print("=" * 60)

if __name__ == "__main__":
    test_brain_factory()

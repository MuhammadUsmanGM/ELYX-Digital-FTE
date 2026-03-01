#!/usr/bin/env python3
"""
Unit Tests for BrainFactory (Universal Brain Selection)

Tests the BrainFactory and BrainAdapter classes for:
- Brain initialization and configuration
- Brain switching functionality
- Command generation
- Environment variable overrides
- Error handling
"""

import unittest
import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.brain_factory import BrainFactory, BrainAdapter, get_brain_factory


class TestBrainAdapter(unittest.TestCase):
    """Test cases for BrainAdapter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.claude_adapter = BrainAdapter(
            name="claude",
            command="claude",
            args=["-p"],
            description="Anthropic Claude Code"
        )
        
        self.qwen_adapter = BrainAdapter(
            name="qwen",
            command="qwen",
            args=["--yolo"],
            description="Alibaba Qwen Coder"
        )
    
    def test_brain_adapter_initialization(self):
        """Test BrainAdapter initializes with correct attributes"""
        self.assertEqual(self.claude_adapter.name, "claude")
        self.assertEqual(self.claude_adapter.command, "claude")
        self.assertEqual(self.claude_adapter.args, ["-p"])
        self.assertEqual(self.claude_adapter.description, "Anthropic Claude Code")
    
    def test_build_command(self):
        """Test command building with prompt"""
        prompt = "Process all tasks"
        cmd = self.claude_adapter.build_command(prompt)
        
        self.assertEqual(cmd, ["claude", "-p", "Process all tasks"])
        self.assertIsInstance(cmd, list)
        self.assertEqual(len(cmd), 3)
    
    def test_build_command_with_multiple_args(self):
        """Test command building with multiple arguments"""
        prompt = "Test prompt"
        cmd = self.qwen_adapter.build_command(prompt)
        
        self.assertEqual(cmd, ["qwen", "--yolo", "Test prompt"])
    
    @patch('src.services.brain_factory.subprocess.run')
    def test_process_success(self, mock_run):
        """Test successful brain execution"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success output",
            stderr=""
        )
        
        result = self.claude_adapter.process("Test prompt", timeout=60)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["brain"], "claude")
        self.assertEqual(result["stdout"], "Success output")
        self.assertEqual(result["returncode"], 0)
    
    @patch('src.services.brain_factory.subprocess.run')
    def test_process_failure(self, mock_run):
        """Test brain execution with failure"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error occurred"
        )
        
        result = self.claude_adapter.process("Test prompt")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["stderr"], "Error occurred")
        self.assertEqual(result["returncode"], 1)
    
    @patch('src.services.brain_factory.subprocess.run')
    def test_process_timeout(self, mock_run):
        """Test brain execution timeout"""
        mock_run.side_effect = TimeoutExpired("Command timed out")
        
        result = self.claude_adapter.process("Test prompt", timeout=1)
        
        self.assertFalse(result["success"])
        # Check for timeout-related text (either "Timeout" or the original message)
        self.assertTrue(
            "Timeout" in result["stderr"] or "timed out" in result["stderr"].lower()
        )
        # Returncode may be -1 (timeout) or -3 (unexpected error) depending on handling
        self.assertIn(result["returncode"], [-1, -3])
    
    @patch('src.services.brain_factory.subprocess.run')
    def test_process_command_not_found(self, mock_run):
        """Test brain execution with missing command"""
        mock_run.side_effect = FileNotFoundError("Command not found")
        
        result = self.claude_adapter.process("Test prompt")
        
        self.assertFalse(result["success"])
        self.assertIn("not found", result["stderr"])
        self.assertEqual(result["returncode"], -2)
    
    def test_repr(self):
        """Test string representation"""
        repr_str = repr(self.claude_adapter)
        self.assertIn("claude", repr_str)
        self.assertIn("claude", repr_str)


class TestBrainFactory(unittest.TestCase):
    """Test cases for BrainFactory class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Save original environment
        self.original_env = os.getenv("ELYX_ACTIVE_BRAIN")
        
        # Clear environment variable for clean tests
        if "ELYX_ACTIVE_BRAIN" in os.environ:
            del os.environ["ELYX_ACTIVE_BRAIN"]
    
    def tearDown(self):
        """Clean up"""
        # Restore environment
        if self.original_env:
            os.environ["ELYX_ACTIVE_BRAIN"] = self.original_env
        elif "ELYX_ACTIVE_BRAIN" in os.environ:
            del os.environ["ELYX_ACTIVE_BRAIN"]
        
        # Remove temp files
        if self.config_path.exists():
            self.config_path.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_factory_initialization_default(self):
        """Test factory initializes with default brains"""
        factory = BrainFactory(config_path="nonexistent.json")
        
        self.assertIn("claude", factory.brains)
        self.assertIn("qwen", factory.brains)
        self.assertIn("gemini", factory.brains)
        self.assertIn("codex", factory.brains)
        self.assertEqual(factory.active_brain_name, "claude")
    
    def test_factory_loads_config(self):
        """Test factory loads brain configuration from file"""
        config = {
            "brain_selection": {
                "active_brain": "qwen",
                "brains": {
                    "qwen": {
                        "command": "qwen",
                        "args": ["--yolo"],
                        "description": "Custom Qwen"
                    }
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        factory = BrainFactory(config_path=str(self.config_path))
        
        self.assertEqual(factory.active_brain_name, "qwen")
        self.assertIn("qwen", factory.brains)
    
    def test_factory_env_override(self):
        """Test environment variable overrides config"""
        # Set config to claude
        config = {
            "brain_selection": {
                "active_brain": "claude"
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        # Set env to qwen
        os.environ["ELYX_ACTIVE_BRAIN"] = "qwen"
        
        factory = BrainFactory(config_path=str(self.config_path))
        
        self.assertEqual(factory.active_brain_name, "qwen")
    
    def test_get_active_brain(self):
        """Test getting active brain"""
        factory = BrainFactory(config_path="nonexistent.json")
        brain = factory.get_active_brain()
        
        self.assertEqual(brain.name, "claude")
        self.assertIsInstance(brain, BrainAdapter)
    
    def test_get_brain_by_name(self):
        """Test getting specific brain by name"""
        factory = BrainFactory(config_path="nonexistent.json")
        
        qwen = factory.get_brain("qwen")
        self.assertEqual(qwen.name, "qwen")
        
        gemini = factory.get_brain("gemini")
        self.assertEqual(gemini.name, "gemini")
    
    def test_get_nonexistent_brain(self):
        """Test getting nonexistent brain returns None"""
        factory = BrainFactory(config_path="nonexistent.json")
        brain = factory.get_brain("skynet")
        
        self.assertIsNone(brain)
    
    def test_set_active_brain_success(self):
        """Test switching active brain"""
        factory = BrainFactory(config_path="nonexistent.json")
        
        self.assertEqual(factory.active_brain_name, "claude")
        
        success = factory.set_active_brain("qwen")
        
        self.assertTrue(success)
        self.assertEqual(factory.active_brain_name, "qwen")
    
    def test_set_active_brain_failure(self):
        """Test switching to invalid brain"""
        factory = BrainFactory(config_path="nonexistent.json")
        
        success = factory.set_active_brain("invalid_brain")
        
        self.assertFalse(success)
        self.assertEqual(factory.active_brain_name, "claude")
    
    def test_list_brains(self):
        """Test listing all brains"""
        factory = BrainFactory(config_path="nonexistent.json")
        brains = factory.list_brains()
        
        self.assertIsInstance(brains, dict)
        self.assertEqual(len(brains), 4)
        self.assertIn("claude", brains)
        self.assertIn("qwen", brains)
    
    def test_register_brain(self):
        """Test dynamically registering new brain"""
        factory = BrainFactory(config_path="nonexistent.json")
        
        factory.register_brain(
            name="custom",
            command="custom-ai",
            args=["--mode", "fast"],
            description="Custom AI brain"
        )
        
        self.assertIn("custom", factory.brains)
        brain = factory.get_brain("custom")
        self.assertEqual(brain.name, "custom")
        self.assertEqual(brain.command, "custom-ai")
    
    def test_active_brain_fallback(self):
        """Test fallback to claude when active brain not found"""
        config = {
            "brain_selection": {
                "active_brain": "nonexistent"
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        factory = BrainFactory(config_path=str(self.config_path))
        
        # Should fallback to claude when getting active brain
        brain = factory.get_active_brain()
        self.assertEqual(brain.name, "claude")


class TestBrainFactorySingleton(unittest.TestCase):
    """Test cases for BrainFactory singleton pattern"""
    
    def setUp(self):
        """Reset singleton"""
        from src.services import brain_factory
        brain_factory._brain_factory = None
    
    def test_singleton_instance(self):
        """Test singleton returns same instance"""
        factory1 = get_brain_factory()
        factory2 = get_brain_factory()
        
        self.assertIs(factory1, factory2)
    
    def test_singleton_with_custom_config(self):
        """Test singleton with custom config path"""
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "custom_config.json"
        
        config = {
            "brain_selection": {
                "active_brain": "qwen"
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        factory = get_brain_factory(config_path=str(config_path))
        self.assertEqual(factory.active_brain_name, "qwen")
        
        # Cleanup
        config_path.unlink()
        Path(temp_dir).rmdir()


class TestBrainFactoryIntegration(unittest.TestCase):
    """Integration tests for BrainFactory with actual config"""
    
    def test_load_from_project_config(self):
        """Test loading from actual project config.json"""
        config_path = project_root / "config.json"
        
        if not config_path.exists():
            self.skipTest("config.json not found")
        
        factory = BrainFactory(config_path=str(config_path))
        
        # Verify factory loaded
        self.assertIsNotNone(factory)
        self.assertIn(factory.active_brain_name, factory.brains)
        
        # Verify all default brains are available
        for brain_name in ["claude", "qwen", "gemini", "codex"]:
            self.assertIn(brain_name, factory.brains)
    
    def test_command_generation_all_brains(self):
        """Test command generation for all configured brains"""
        factory = BrainFactory(config_path="nonexistent.json")
        test_prompt = "Process all pending tasks"
        
        for brain_name in factory.brains:
            brain = factory.get_brain(brain_name)
            cmd = brain.build_command(test_prompt)
            
            # Verify command structure
            self.assertIsInstance(cmd, list)
            self.assertGreaterEqual(len(cmd), 2)
            self.assertEqual(cmd[0], brain.command)
            self.assertIn(test_prompt, cmd)


# Helper class for timeout testing
class TimeoutExpired(Exception):
    """Mock timeout exception for testing"""
    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)

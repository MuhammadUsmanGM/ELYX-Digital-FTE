#!/usr/bin/env python3
"""
Unit Tests for RalphLoop (Autonomous Processing Loop)

Tests the RalphLoop class for:
- Loop initialization
- Task detection
- Iteration execution
- Brain switching
- Maximum iterations handling
- Empty task handling
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.agents.ralph_loop import RalphLoop


class TestRalphLoopInitialization(unittest.TestCase):
    """Test RalphLoop initialization"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization_default_params(self):
        """Test initialization with default parameters"""
        loop = RalphLoop(vault_path=str(self.vault_path))
        
        self.assertEqual(loop.vault_path, self.vault_path)
        self.assertEqual(loop.max_iterations, 5)
        self.assertIsNotNone(loop.logger)
    
    def test_initialization_custom_iterations(self):
        """Test initialization with custom max iterations"""
        loop = RalphLoop(vault_path=str(self.vault_path), max_iterations=10)
        
        self.assertEqual(loop.max_iterations, 10)
    
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_initialization_with_brain_factory(self, mock_factory):
        """Test initialization with brain factory"""
        mock_brain = MagicMock(name="claude")
        mock_factory_instance = MagicMock()
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        
        self.assertIsNotNone(loop.brain_factory)
        self.assertIsNotNone(loop.active_brain)
    
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_initialization_brain_factory_failure(self, mock_factory):
        """Test initialization when brain factory unavailable"""
        mock_factory.side_effect = ImportError("Not available")
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        
        self.assertIsNone(loop.brain_factory)
        self.assertIsNone(loop.active_brain)


class TestHasPendingTasks(unittest.TestCase):
    """Test pending task detection"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        self.loop = RalphLoop(vault_path=str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_no_pending_tasks_empty_folder(self):
        """Test no pending tasks when folder is empty"""
        has_tasks = self.loop.has_pending_tasks()
        
        self.assertFalse(has_tasks)
    
    def test_no_pending_tasks_nonexistent_folder(self):
        """Test no pending tasks when folder doesn't exist"""
        shutil.rmtree(self.vault_path / "Needs_Action")
        
        has_tasks = self.loop.has_pending_tasks()
        
        self.assertFalse(has_tasks)
    
    def test_has_pending_tasks_with_files(self):
        """Test pending tasks when files exist"""
        # Create task files
        (self.vault_path / "Needs_Action" / "TASK_001.md").write_text("Task 1")
        (self.vault_path / "Needs_Action" / "TASK_002.md").write_text("Task 2")
        
        has_tasks = self.loop.has_pending_tasks()
        
        self.assertTrue(has_tasks)
    
    def test_has_pending_tasks_only_non_md_files(self):
        """Test with non-.md files (should not count)"""
        # Create non-.md files
        (self.vault_path / "Needs_Action" / "file.txt").write_text("Not a task")
        (self.vault_path / "Needs_Action" / "data.json").write_text("{}")
        
        has_tasks = self.loop.has_pending_tasks()
        
        self.assertFalse(has_tasks)


class TestBuildCommand(unittest.TestCase):
    """Test command building for brain execution"""
    
    def setUp(self):
        """Create vault and loop"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_build_command_with_active_brain(self, mock_factory):
        """Test command building with active brain"""
        mock_brain = MagicMock()
        mock_brain.build_command.return_value = ["claude", "-p", "Test prompt"]
        mock_factory_instance = MagicMock()
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        prompt = "Test prompt"
        
        cmd = loop._build_command(prompt)
        
        self.assertEqual(cmd, ["claude", "-p", "Test prompt"])
        mock_brain.build_command.assert_called_once_with(prompt)
    
    def test_build_command_fallback(self):
        """Test command building with fallback to claude"""
        loop = RalphLoop(vault_path=str(self.vault_path))
        loop.active_brain = None  # Simulate no active brain
        
        prompt = "Process tasks"
        cmd = loop._build_command(prompt)
        
        # Should use hardcoded claude fallback
        self.assertEqual(cmd, ["claude", "-p", "Process tasks"])


class TestRunIteration(unittest.TestCase):
    """Test iteration execution"""
    
    def setUp(self):
        """Create vault with task files"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Done").mkdir(exist_ok=True)
        (self.vault_path / "Plans").mkdir(exist_ok=True)
        (self.vault_path / "Pending_Approval").mkdir(exist_ok=True)
        
        # Create sample task
        task_file = self.vault_path / "Needs_Action" / "TASK_001.md"
        task_file.write_text("""---
type: email
---

Test task
""")
        
        # Create handbook
        handbook = self.vault_path / "Company_Handbook.md"
        handbook.write_text("# Company Handbook\n\nBusiness rules here.")
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.ralph_loop.subprocess.run')
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_run_iteration_success(self, mock_factory, mock_run):
        """Test successful iteration"""
        # Setup mocks
        mock_brain = MagicMock()
        mock_brain.build_command.return_value = ["claude", "-p", "prompt"]
        mock_factory_instance = MagicMock()
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        loop.run_iteration()
        
        # Verify subprocess was called
        mock_run.assert_called_once()
    
    @patch('src.agents.ralph_loop.subprocess.run')
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_run_iteration_failure(self, mock_factory, mock_run):
        """Test iteration with subprocess failure"""
        mock_brain = MagicMock()
        mock_brain.build_command.return_value = ["claude", "-p", "prompt"]
        mock_factory_instance = MagicMock()
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        mock_run.side_effect = Exception("Subprocess failed")
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        
        # Should not raise exception
        loop.run_iteration()
    
    @patch('src.agents.ralph_loop.subprocess.run')
    def test_run_iteration_fallback_brain(self, mock_run):
        """Test iteration with fallback brain"""
        loop = RalphLoop(vault_path=str(self.vault_path))
        loop.active_brain = None
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        loop.run_iteration()
        
        # Verify called with fallback command
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], "claude")


class TestSwitchBrain(unittest.TestCase):
    """Test brain switching functionality"""
    
    def setUp(self):
        """Create vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_switch_brain_success(self, mock_factory):
        """Test successful brain switch"""
        mock_factory_instance = MagicMock()
        mock_factory_instance.set_active_brain.return_value = True
        
        new_brain = MagicMock(name="qwen")
        mock_factory_instance.get_active_brain.return_value = new_brain
        mock_factory.return_value = mock_factory_instance
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        
        success = loop.switch_brain("qwen")
        
        self.assertTrue(success)
        mock_factory_instance.set_active_brain.assert_called_once_with("qwen")
        self.assertEqual(loop.active_brain.name, "qwen")
    
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_switch_brain_failure(self, mock_factory):
        """Test brain switch failure"""
        mock_factory_instance = MagicMock()
        mock_factory_instance.set_active_brain.return_value = False
        mock_factory.return_value = mock_factory_instance
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        
        success = loop.switch_brain("invalid_brain")
        
        self.assertFalse(success)
    
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_switch_brain_no_factory(self, mock_factory):
        """Test brain switch when factory not available"""
        mock_factory.side_effect = ImportError("Not available")
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        
        success = loop.switch_brain("qwen")
        
        self.assertFalse(success)
        self.assertIsNone(loop.brain_factory)


class TestStartLoop(unittest.TestCase):
    """Test loop start functionality"""
    
    def setUp(self):
        """Create vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.ralph_loop.RalphLoop.run_iteration')
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_start_loop_no_tasks(self, mock_factory, mock_run_iteration):
        """Test loop starts with no tasks"""
        mock_factory_instance = MagicMock()
        mock_brain = MagicMock(name="claude")
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        loop.start()
        
        # run_iteration should not be called
        mock_run_iteration.assert_not_called()
    
    @patch('src.agents.ralph_loop.RalphLoop.run_iteration')
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_start_loop_with_tasks(self, mock_factory, mock_run_iteration):
        """Test loop starts with tasks"""
        # Create task files
        for i in range(3):
            task_file = self.vault_path / "Needs_Action" / f"TASK_{i:03d}.md"
            task_file.write_text(f"Task {i}")
        
        mock_factory_instance = MagicMock()
        mock_brain = MagicMock(name="claude")
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        loop = RalphLoop(vault_path=str(self.vault_path))
        loop.start()
        
        # Should run iterations (up to max_iterations or until no tasks)
        self.assertLessEqual(mock_run_iteration.call_count, 5)
        self.assertGreater(mock_run_iteration.call_count, 0)
    
    @patch('src.agents.ralph_loop.RalphLoop.run_iteration')
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_start_loop_max_iterations(self, mock_factory, mock_run_iteration):
        """Test loop respects max iterations"""
        # Create many task files
        for i in range(20):
            task_file = self.vault_path / "Needs_Action" / f"TASK_{i:03d}.md"
            task_file.write_text(f"Task {i}")
        
        mock_factory_instance = MagicMock()
        mock_brain = MagicMock(name="claude")
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        loop = RalphLoop(vault_path=str(self.vault_path), max_iterations=3)
        loop.start()
        
        # Should stop at max iterations
        self.assertEqual(mock_run_iteration.call_count, 3)


class TestRalphLoopIntegration(unittest.TestCase):
    """Integration tests for RalphLoop"""
    
    def setUp(self):
        """Create vault with realistic structure"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
        # Create full vault structure
        for folder in ["Needs_Action", "Done", "Plans", "Pending_Approval", "Logs"]:
            (self.vault_path / folder).mkdir(exist_ok=True)
        
        # Create handbook
        handbook = self.vault_path / "Company_Handbook.md"
        handbook.write_text("""# Company Handbook

## Business Rules
1. Always prioritize customer satisfaction
2. Require approval for payments over $100
3. Respond to emails within 24 hours
""")
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_loop_with_realistic_vault(self):
        """Test loop with realistic vault structure"""
        # Create sample tasks
        tasks = [
            ("TASK_001.md", "Email response needed"),
            ("TASK_002.md", "Invoice processing"),
            ("TASK_003.md", "Meeting scheduling"),
        ]
        
        for filename, content in tasks:
            task_file = self.vault_path / "Needs_Action" / filename
            task_file.write_text(f"""---
type: task
---

{content}
""")
        
        loop = RalphLoop(vault_path=str(self.vault_path), max_iterations=3)
        
        # Verify setup
        self.assertTrue(loop.has_pending_tasks())
        self.assertEqual(len(list(self.vault_path / "Needs_Action" / "*.md")), 3)
    
    @patch('src.agents.ralph_loop.subprocess.run')
    @patch('src.agents.ralph_loop.get_brain_factory')
    def test_loop_processes_all_tasks(self, mock_factory, mock_run):
        """Test loop processes all tasks"""
        # Create tasks
        for i in range(3):
            task_file = self.vault_path / "Needs_Action" / f"TASK_{i:03d}.md"
            task_file.write_text(f"Task {i}")
        
        mock_factory_instance = MagicMock()
        mock_brain = MagicMock(name="claude")
        mock_factory_instance.get_active_brain.return_value = mock_brain
        mock_factory.return_value = mock_factory_instance
        
        mock_run.return_value = MagicMock(returncode=0, stdout="Processed", stderr="")
        
        loop = RalphLoop(vault_path=str(self.vault_path), max_iterations=5)
        loop.start()
        
        # Verify iterations ran
        self.assertGreater(mock_run.call_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

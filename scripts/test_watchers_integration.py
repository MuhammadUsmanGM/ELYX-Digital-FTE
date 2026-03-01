#!/usr/bin/env python3
"""
Integration Tests for Watcher Agents

Tests for:
- Gmail Watcher integration
- WhatsApp Watcher integration
- File System Watcher integration
- Base Watcher functionality
"""

import unittest
import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.base_watcher import BaseWatcher
from src.agents.filesystem_watcher import FileSystemWatcher


class TestBaseWatcher(unittest.TestCase):
    """Test BaseWatcher abstract class"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_base_watcher_is_abstract(self):
        """Test BaseWatcher cannot be instantiated directly"""
        with self.assertRaises(TypeError):
            watcher = BaseWatcher(vault_path=str(self.vault_path))
    
    def test_concrete_implementation(self):
        """Test concrete implementation of BaseWatcher"""
        class ConcreteWatcher(BaseWatcher):
            def check_for_updates(self):
                return []
            
            def create_action_file(self, item):
                return self.needs_action / "test.md"
        
        watcher = ConcreteWatcher(vault_path=str(self.vault_path), check_interval=1)
        
        self.assertEqual(watcher.vault_path, self.vault_path)
        self.assertEqual(watcher.check_interval, 1)
        self.assertIsNotNone(watcher.logger)


class TestFileSystemWatcherIntegration(unittest.TestCase):
    """Integration tests for FileSystemWatcher"""
    
    def setUp(self):
        """Create temporary directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "vault"
        self.watch_path = Path(self.temp_dir) / "watch"
        
        # Create directories
        self.vault_path.mkdir(exist_ok=True)
        self.watch_path.mkdir(exist_ok=True)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_filesystem_watcher_initialization(self):
        """Test FileSystemWatcher initializes correctly"""
        watcher = FileSystemWatcher(
            watch_path=str(self.watch_path),
            vault_path=str(self.vault_path)
        )
        
        self.assertEqual(watcher.watch_path, str(self.watch_path))
        self.assertEqual(watcher.vault_path, str(self.vault_path))
    
    @patch('src.agents.filesystem_watcher.Observer')
    @patch('src.agents.filesystem_watcher.FileSystemEventHandler')
    def test_filesystem_watcher_start(self, mock_handler, mock_observer):
        """Test FileSystemWatcher start method"""
        mock_observer_instance = MagicMock()
        mock_observer.return_value = mock_observer_instance
        
        watcher = FileSystemWatcher(
            watch_path=str(self.watch_path),
            vault_path=str(self.vault_path)
        )
        
        watcher.start()
        
        mock_observer.assert_called_once()
        mock_observer_instance.schedule.assert_called_once()
        mock_observer_instance.start.assert_called_once()
    
    @patch('src.agents.filesystem_watcher.Observer')
    def test_filesystem_watcher_stop(self, mock_observer):
        """Test FileSystemWatcher stop method"""
        mock_observer_instance = MagicMock()
        mock_observer.return_value = mock_observer_instance
        
        watcher = FileSystemWatcher(
            watch_path=str(self.watch_path),
            vault_path=str(self.vault_path)
        )
        watcher.observer = mock_observer_instance
        
        watcher.stop()
        
        mock_observer_instance.stop.assert_called_once()


class TestGmailWatcherIntegration(unittest.TestCase):
    """Integration tests for GmailWatcher"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.gmail_watcher.build')
    @patch('src.agents.gmail_watcher.Credentials')
    def test_gmail_watcher_initialization(self, mock_creds, mock_build):
        """Test GmailWatcher initializes with credentials"""
        from src.agents.gmail_watcher import GmailWatcher
        
        mock_creds.from_authorized_user_file.return_value = MagicMock()
        mock_build.return_value = MagicMock()
        
        watcher = GmailWatcher(vault_path=str(self.vault_path))
        
        self.assertIsNotNone(watcher.service)
        self.assertEqual(watcher.check_interval, 120)  # 2 minutes default
    
    @patch('src.agents.gmail_watcher.build')
    @patch('src.agents.gmail_watcher.Credentials')
    def test_gmail_watcher_check_for_updates(self, mock_creds, mock_build):
        """Test GmailWatcher check_for_updates method"""
        from src.agents.gmail_watcher import GmailWatcher
        
        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {
            'messages': []
        }
        mock_build.return_value = mock_service
        
        watcher = GmailWatcher(vault_path=str(self.vault_path))
        updates = watcher.check_for_updates()
        
        self.assertIsInstance(updates, list)


class TestWhatsAppWatcherIntegration(unittest.TestCase):
    """Integration tests for WhatsAppWatcher"""
    
    def setUp(self):
        """Create temporary vault and session path"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "vault"
        self.session_path = Path(self.temp_dir) / "session"
        
        self.vault_path.mkdir(exist_ok=True)
        self.session_path.mkdir(exist_ok=True)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.whatsapp_watcher.sync_playwright')
    def test_whatsapp_watcher_initialization(self, mock_playwright):
        """Test WhatsAppWatcher initializes"""
        from src.agents.whatsapp_watcher import WhatsAppWatcher
        
        watcher = WhatsAppWatcher(
            vault_path=str(self.vault_path),
            session_path=str(self.session_path)
        )
        
        self.assertEqual(watcher.check_interval, 30)  # 30 seconds default
        self.assertEqual(watcher.session_path, self.session_path)
        self.assertIsInstance(watcher.keywords, list)
    
    @patch('src.agents.whatsapp_watcher.sync_playwright')
    def test_whatsapp_watcher_keywords(self, mock_playwright):
        """Test WhatsAppWatcher keyword detection"""
        from src.agents.whatsapp_watcher import WhatsAppWatcher
        
        watcher = WhatsAppWatcher(
            vault_path=str(self.vault_path),
            session_path=str(self.session_path)
        )
        
        expected_keywords = ['urgent', 'asap', 'invoice', 'payment', 'help']
        
        for keyword in expected_keywords:
            self.assertIn(keyword, watcher.keywords)


class TestWatcherFileCreation(unittest.TestCase):
    """Test watcher action file creation"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_action_file_content(self):
        """Test action file creation with proper content"""
        from src.agents.gmail_watcher import GmailWatcher
        from datetime import datetime
        
        with patch('src.agents.gmail_watcher.build'):
            with patch('src.agents.gmail_watcher.Credentials'):
                watcher = GmailWatcher(vault_path=str(self.vault_path))
                
                # Mock message data
                message = {
                    'id': 'test_msg_123',
                    'payload': {
                        'headers': [
                            {'name': 'From', 'value': 'test@example.com'},
                            {'name': 'Subject', 'value': 'Test Subject'}
                        ]
                    },
                    'snippet': 'Test email snippet'
                }
                
                action_file = watcher.create_action_file(message)
                
                # Verify file created
                self.assertTrue(action_file.exists())
                self.assertTrue(action_file.name.startswith('EMAIL_'))
                
                # Verify content
                content = action_file.read_text(encoding='utf-8')
                self.assertIn('test@example.com', content)
                self.assertIn('Test Subject', content)
                self.assertIn('type: email', content)


class TestWatcherIntegration(unittest.TestCase):
    """Integration tests for multiple watchers"""
    
    def setUp(self):
        """Create shared vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
        (self.vault_path / "Inbox").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_multiple_watchers_share_vault(self):
        """Test multiple watchers can share same vault"""
        from src.agents.gmail_watcher import GmailWatcher
        from src.agents.filesystem_watcher import FileSystemWatcher
        
        watch_path = Path(self.temp_dir) / "watch"
        watch_path.mkdir(exist_ok=True)
        
        with patch('src.agents.gmail_watcher.build'):
            with patch('src.agents.gmail_watcher.Credentials'):
                gmail_watcher = GmailWatcher(vault_path=str(self.vault_path))
                fs_watcher = FileSystemWatcher(
                    watch_path=str(watch_path),
                    vault_path=str(self.vault_path)
                )
                
                # Both should reference same vault
                self.assertEqual(
                    Path(gmail_watcher.vault_path),
                    Path(fs_watcher.vault_path)
                )
                self.assertEqual(
                    Path(gmail_watcher.vault_path),
                    self.vault_path
                )


class TestWatcherErrorHandling(unittest.TestCase):
    """Test watcher error handling"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Needs_Action").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.gmail_watcher.build')
    @patch('src.agents.gmail_watcher.Credentials')
    def test_gmail_watcher_handles_auth_error(self, mock_creds, mock_build):
        """Test GmailWatcher handles authentication errors"""
        from src.agents.gmail_watcher import GmailWatcher
        
        mock_creds.from_authorized_user_file.side_effect = FileNotFoundError()
        
        # Should handle gracefully or raise specific exception
        with self.assertRaises(FileNotFoundError):
            GmailWatcher(vault_path=str(self.vault_path))
    
    def test_filesystem_watcher_handles_missing_path(self):
        """Test FileSystemWatcher handles missing watch path"""
        from src.agents.filesystem_watcher import FileSystemWatcher
        
        nonexistent_path = "/nonexistent/path/12345"
        
        # Should handle or raise appropriate exception
        watcher = FileSystemWatcher(
            watch_path=nonexistent_path,
            vault_path=str(self.vault_path)
        )
        
        # Watcher should initialize even if path doesn't exist
        self.assertIsNotNone(watcher)


if __name__ == "__main__":
    unittest.main(verbosity=2)

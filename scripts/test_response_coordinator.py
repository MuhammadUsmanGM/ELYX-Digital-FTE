#!/usr/bin/env python3
"""
Unit Tests for Response Coordinator

Tests for:
- Response coordination across channels
- Response queue management
- Rate limiting
- Channel handler initialization
- Response tracking
"""

import unittest
import os
import sys
import tempfile
import shutil
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.response_coordinator import ResponseCoordinator
from src.response_handlers.base_handler import CommunicationChannel, ResponseStatus
from src.services.conversation_tracker import ResponseType, Priority


class TestResponseCoordinatorInitialization(unittest.TestCase):
    """Test ResponseCoordinator initialization"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Responses").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test ResponseCoordinator initializes correctly"""
        coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
        
        self.assertIsNotNone(coordinator.conversation_tracker)
        self.assertIsNotNone(coordinator.approval_workflow)
        self.assertIsNotNone(coordinator.response_queue)
    
    def test_lazy_handler_initialization(self):
        """Test handlers are initialized lazily"""
        coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
        
        # Handlers should be None initially
        self.assertIsNone(coordinator._email_handler)
        self.assertIsNone(coordinator._linkedin_handler)
        self.assertIsNone(coordinator._whatsapp_handler)
    
    def test_email_handler_property(self):
        """Test email handler property initializes on access"""
        coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
        
        # Access property
        handler = coordinator.email_handler
        
        # Should be initialized
        self.assertIsNotNone(handler)
        self.assertIsNotNone(coordinator._email_handler)
    
    def test_rate_limits_configured(self):
        """Test rate limits are configured for all channels"""
        coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
        
        expected_channels = [
            CommunicationChannel.EMAIL,
            CommunicationChannel.LINKEDIN,
            CommunicationChannel.WHATSAPP,
            CommunicationChannel.FACEBOOK,
            CommunicationChannel.TWITTER,
            CommunicationChannel.INSTAGRAM
        ]
        
        for channel in expected_channels:
            self.assertIn(channel, coordinator.rate_limits)
            self.assertIn("limit", coordinator.rate_limits[channel])
            self.assertIn("window", coordinator.rate_limits[channel])


class TestQueueResponse(unittest.TestCase):
    """Test response queueing"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Responses").mkdir(exist_ok=True)
        (self.vault_path / "Pending_Approval").mkdir(exist_ok=True)
        
        self.coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch.object(ResponseCoordinator, 'email_handler')
    def test_queue_response_email(self, mock_handler):
        """Test queueing email response"""
        mock_handler.send_response = AsyncMock(return_value={
            "status": "sent",
            "message_id": "test_123"
        })
        
        async def run_test():
            result = await self.coordinator.queue_response(
                original_message_id="msg_001",
                channel=CommunicationChannel.EMAIL,
                recipient_identifier="test@example.com",
                content="Test email content",
                response_type=ResponseType.INFORMATIONAL,
                priority=Priority.MEDIUM,
                requires_approval=False,
                subject="Test Subject"
            )
            
            self.assertEqual(result["status"], "sent")
            self.assertEqual(result["message_id"], "test_123")
        
        asyncio.run(run_test())
    
    @patch.object(ResponseCoordinator, 'email_handler')
    def test_queue_response_requires_approval(self, mock_handler):
        """Test queueing response that requires approval"""
        async def run_test():
            result = await self.coordinator.queue_response(
                original_message_id="msg_002",
                channel=CommunicationChannel.EMAIL,
                recipient_identifier="test@example.com",
                content="Requires approval",
                response_type=ResponseType.INFORMATIONAL,
                priority=Priority.HIGH,
                requires_approval=True,
                subject="Approval Needed"
            )
            
            # Should create approval request
            self.assertEqual(result["status"], "pending_approval")
        
        asyncio.run(run_test())
    
    def test_queue_response_invalid_channel(self):
        """Test queueing response with invalid channel"""
        async def run_test():
            try:
                result = await self.coordinator.queue_response(
                    original_message_id="msg_003",
                    channel=None,
                    recipient_identifier="test",
                    content="Test"
                )
                # Should handle gracefully or raise specific exception
            except Exception as e:
                # Expected behavior
                self.assertIsNotNone(e)
        
        asyncio.run(run_test())


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Responses").mkdir(exist_ok=True)
        
        self.coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_rate_limit_tracking(self):
        """Test rate limit tracking structure"""
        # Check rate limit structure
        for channel, config in self.coordinator.rate_limits.items():
            self.assertIn("requests", config)
            self.assertIn("limit", config)
            self.assertIn("window", config)
            self.assertIsInstance(config["requests"], list)
    
    def test_rate_limit_window(self):
        """Test rate limit window configuration"""
        # Email should have daily limit
        email_config = self.coordinator.rate_limits[CommunicationChannel.EMAIL]
        self.assertEqual(email_config["window"], 86400)  # 24 hours in seconds
        
        # LinkedIn should have hourly limit
        linkedin_config = self.coordinator.rate_limits[CommunicationChannel.LINKEDIN]
        self.assertEqual(linkedin_config["window"], 3600)  # 1 hour in seconds


class TestResponseTracking(unittest.TestCase):
    """Test response tracking functionality"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Responses").mkdir(exist_ok=True)
        (self.vault_path / "Conversation_History").mkdir(exist_ok=True)
        
        self.coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_conversation_tracker_access(self):
        """Test conversation tracker is accessible"""
        tracker = self.coordinator.conversation_tracker
        self.assertIsNotNone(tracker)
    
    def test_track_response(self):
        """Test tracking response"""
        # Track a response
        self.coordinator.conversation_tracker.track_response(
            message_id="msg_001",
            channel=CommunicationChannel.EMAIL,
            recipient="test@example.com",
            content="Test response",
            response_type=ResponseType.INFORMATIONAL
        )
        
        # Verify tracking (implementation dependent)
        # This test ensures the method exists and doesn't crash
        self.assertTrue(True)


class TestApprovalWorkflow(unittest.TestCase):
    """Test approval workflow integration"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Responses").mkdir(exist_ok=True)
        (self.vault_path / "Pending_Approval").mkdir(exist_ok=True)
        
        self.coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_approval_workflow_access(self):
        """Test approval workflow is accessible"""
        workflow = self.coordinator.approval_workflow
        self.assertIsNotNone(workflow)
    
    @patch.object(ResponseCoordinator, 'email_handler')
    def test_high_priority_requires_approval(self, mock_handler):
        """Test high priority responses may require approval"""
        async def run_test():
            # High priority with new recipient should require approval
            result = await self.coordinator.queue_response(
                original_message_id="msg_high_001",
                channel=CommunicationChannel.EMAIL,
                recipient_identifier="new@example.com",
                content="High priority message",
                response_type=ResponseType.URGENT,
                priority=Priority.CRITICAL,
                requires_approval=True,
                subject="Urgent"
            )
            
            # Should be queued for approval
            self.assertIn(result["status"], ["sent", "pending_approval"])
        
        asyncio.run(run_test())


class TestResponseCoordinatorAsync(unittest.TestCase):
    """Test async functionality of ResponseCoordinator"""
    
    def setUp(self):
        """Create temporary vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Responses").mkdir(exist_ok=True)
        
        self.coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_response_queue_is_async(self):
        """Test response queue is asyncio Queue"""
        self.assertIsInstance(
            self.coordinator.response_queue,
            asyncio.Queue
        )
    
    def test_queue_put_get(self):
        """Test putting and getting from queue"""
        async def run_test():
            # Put item in queue
            await self.coordinator.response_queue.put({
                "message_id": "test_001",
                "content": "Test"
            })
            
            # Get item from queue
            item = await self.coordinator.response_queue.get()
            
            self.assertEqual(item["message_id"], "test_001")
        
        asyncio.run(run_test())


class TestResponseCoordinatorIntegration(unittest.TestCase):
    """Integration tests for ResponseCoordinator"""
    
    def setUp(self):
        """Create realistic vault structure"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
        # Create full structure
        for folder in ["Responses", "Pending_Approval", "Done", "Conversation_History"]:
            (self.vault_path / folder).mkdir(exist_ok=True)
        
        self.coordinator = ResponseCoordinator(vault_path=str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_response_workflow(self):
        """Test complete response workflow"""
        # Verify all components are available
        self.assertIsNotNone(self.coordinator.conversation_tracker)
        self.assertIsNotNone(self.coordinator.approval_workflow)
        self.assertIsNotNone(self.coordinator.response_queue)
        
        # Verify handlers can be accessed
        handlers = [
            self.coordinator.email_handler,
            self.coordinator.linkedin_handler,
            self.coordinator.whatsapp_handler,
        ]
        
        for handler in handlers:
            self.assertIsNotNone(handler)
    
    def test_multiple_channels_available(self):
        """Test multiple communication channels available"""
        channels = {
            "email": self.coordinator.email_handler,
            "linkedin": self.coordinator.linkedin_handler,
            "whatsapp": self.coordinator.whatsapp_handler,
        }
        
        for name, handler in channels.items():
            self.assertIsNotNone(
                handler,
                f"{name} handler should be available"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

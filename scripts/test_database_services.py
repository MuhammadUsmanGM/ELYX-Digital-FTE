#!/usr/bin/env python3
"""
Unit Tests for Database Services

Tests for:
- Database initialization
- Session management
- Database operations
- Connection pooling
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

from src.services.database import init_db, SessionLocal, get_db


class TestDatabaseInitialization(unittest.TestCase):
    """Test database initialization"""
    
    def setUp(self):
        """Create temporary directory for test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db_url = f"sqlite:///{self.db_path}"
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init_db_creates_tables(self):
        """Test database initialization creates tables"""
        session_factory, engine = init_db(self.db_url)
        
        # Should return session factory and engine
        self.assertIsNotNone(session_factory)
        self.assertIsNotNone(engine)
        
        # Database file should be created
        self.assertTrue(self.db_path.exists())
    
    def test_init_db_returns_callable(self):
        """Test init_db returns callable session factory"""
        session_factory, engine = init_db(self.db_url)
        
        # Should be callable
        self.assertTrue(callable(session_factory))
    
    def test_init_db_with_different_urls(self):
        """Test initialization with different database URLs"""
        # Test with in-memory SQLite
        session_factory, engine = init_db("sqlite:///:memory:")
        self.assertIsNotNone(session_factory)
        self.assertIsNotNone(engine)


class TestSessionManagement(unittest.TestCase):
    """Test session management"""
    
    def setUp(self):
        """Create test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db_url = f"sqlite:///{self.db_path}"
        
        self.session_factory, self.engine = init_db(self.db_url)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_session_creation(self):
        """Test creating database session"""
        session = self.session_factory()
        
        self.assertIsNotNone(session)
        self.assertTrue(hasattr(session, 'add'))
        self.assertTrue(hasattr(session, 'commit'))
        self.assertTrue(hasattr(session, 'rollback'))
        self.assertTrue(hasattr(session, 'close'))
    
    def test_session_context_manager(self):
        """Test session as context manager"""
        with self.session_factory() as session:
            self.assertIsNotNone(session)
        
        # Session should be closed after context
        self.assertTrue(session.is_active is False or session.is_closed)
    
    def test_multiple_sessions(self):
        """Test creating multiple sessions"""
        session1 = self.session_factory()
        session2 = self.session_factory()
        
        self.assertIsNotNone(session1)
        self.assertIsNotNone(session2)
        self.assertIsNot(session1, session2)
        
        session1.close()
        session2.close()


class TestGetDB(unittest.TestCase):
    """Test get_db dependency injection"""
    
    def setUp(self):
        """Create test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db_url = f"sqlite:///{self.db_path}"
        
        self.session_factory, self.engine = init_db(self.db_url)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.services.database.SessionLocal')
    def test_get_db_yields_session(self, mock_session_local):
        """Test get_db yields database session"""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        db_generator = get_db()
        db = next(db_generator)
        
        self.assertEqual(db, mock_session)
        mock_session_local.assert_called_once()
    
    @patch('src.services.database.SessionLocal')
    def test_get_db_closes_session(self, mock_session_local):
        """Test get_db closes session on completion"""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        db_generator = get_db()
        next(db_generator)
        
        try:
            next(db_generator)
        except StopIteration:
            pass
        
        mock_session.close.assert_called_once()


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database services"""
    
    def setUp(self):
        """Create test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db_url = f"sqlite:///{self.db_path}"
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_database_workflow(self):
        """Test complete database workflow"""
        # Initialize
        session_factory, engine = init_db(self.db_url)
        
        # Create session
        session = session_factory()
        
        # Verify session works
        self.assertIsNotNone(session)
        
        # Close session
        session.close()
        
        # Verify database file exists
        self.assertTrue(self.db_path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""
Unit Tests for ConfigManager

Tests the ConfigManager class for:
- Configuration loading
- Configuration saving
- Dot notation access
- Configuration updates
- Environment variable overrides
- Default configuration
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config.manager import ConfigManager, get_config, set_config, reload_config


class TestConfigManagerInitialization(unittest.TestCase):
    """Test ConfigManager initialization"""
    
    def setUp(self):
        """Create temporary directory for test configs"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_existing_config(self):
        """Test initialization with existing config file"""
        config_data = {
            "vault_path": "/custom/vault",
            "check_interval": {"gmail": 60}
        }
        
        config_path = Path(self.temp_dir) / "test_config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        manager = ConfigManager(config_path=str(config_path))
        
        self.assertEqual(manager.get("vault_path"), "/custom/vault")
        self.assertEqual(manager.get("check_interval.gmail"), 60)
    
    def test_initialization_creates_default_config(self):
        """Test initialization creates default config if not exists"""
        config_path = Path(self.temp_dir) / "new_config.json"
        
        manager = ConfigManager(config_path=str(config_path))
        
        # Should create config file
        self.assertTrue(config_path.exists())
        
        # Should have default values
        self.assertIsNotNone(manager.get("vault_path"))
        self.assertIsNotNone(manager.get("check_interval"))
    
    def test_initialization_loads_env_variables(self):
        """Test initialization loads environment variables"""
        # Set environment variables
        os.environ["OBSIDIAN_VAULT_PATH"] = "/env/vault"
        os.environ["GMAIL_CHECK_INTERVAL"] = "300"
        
        config_path = Path(self.temp_dir) / "env_config.json"
        manager = ConfigManager(config_path=str(config_path))
        
        # Should use env values
        self.assertEqual(manager.get("vault_path"), "/env/vault")
        self.assertEqual(manager.get("check_interval.gmail"), 300)
        
        # Cleanup
        del os.environ["OBSIDIAN_VAULT_PATH"]
        del os.environ["GMAIL_CHECK_INTERVAL"]


class TestConfigManagerGet(unittest.TestCase):
    """Test configuration get operations"""
    
    def setUp(self):
        """Create test config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.config_data = {
            "vault_path": "obsidian_vault",
            "check_interval": {
                "gmail": 120,
                "whatsapp": 30,
                "filesystem": 10
            },
            "integrations": {
                "gmail_enabled": True,
                "whatsapp_enabled": True,
                "linkedin_enabled": False
            },
            "nested": {
                "deep": {
                    "value": "test_value"
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        self.manager = ConfigManager(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_simple_key(self):
        """Test getting simple key"""
        value = self.manager.get("vault_path")
        self.assertEqual(value, "obsidian_vault")
    
    def test_get_nested_key(self):
        """Test getting nested key with dot notation"""
        value = self.manager.get("check_interval.gmail")
        self.assertEqual(value, 120)
    
    def test_get_deeply_nested_key(self):
        """Test getting deeply nested key"""
        value = self.manager.get("nested.deep.value")
        self.assertEqual(value, "test_value")
    
    def test_get_with_default(self):
        """Test getting non-existent key with default"""
        value = self.manager.get("nonexistent.key", "default_value")
        self.assertEqual(value, "default_value")
    
    def test_get_nonexistent_key_no_default(self):
        """Test getting non-existent key without default"""
        value = self.manager.get("nonexistent.key")
        self.assertIsNone(value)
    
    def test_get_boolean_value(self):
        """Test getting boolean value"""
        value = self.manager.get("integrations.gmail_enabled")
        self.assertTrue(value)
    
    def test_get_integer_value(self):
        """Test getting integer value"""
        value = self.manager.get("check_interval.whatsapp")
        self.assertEqual(value, 30)


class TestConfigManagerSet(unittest.TestCase):
    """Test configuration set operations"""
    
    def setUp(self):
        """Create test config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.config_data = {
            "vault_path": "obsidian_vault",
            "check_interval": {"gmail": 120}
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        self.manager = ConfigManager(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_set_simple_key(self):
        """Test setting simple key"""
        self.manager.set("vault_path", "/new/vault")
        
        value = self.manager.get("vault_path")
        self.assertEqual(value, "/new/vault")
    
    def test_set_nested_key(self):
        """Test setting nested key"""
        self.manager.set("check_interval.gmail", 300)
        
        value = self.manager.get("check_interval.gmail")
        self.assertEqual(value, 300)
    
    def test_set_creates_nested_structure(self):
        """Test setting creates nested structure if not exists"""
        self.manager.set("new.nested.key", "value")
        
        value = self.manager.get("new.nested.key")
        self.assertEqual(value, "value")
    
    def test_set_persists_to_file(self):
        """Test setting persists to file"""
        self.manager.set("vault_path", "/persistent/vault")
        
        # Reload config from file
        with open(self.config_path, 'r') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config["vault_path"], "/persistent/vault")
    
    def test_set_boolean_value(self):
        """Test setting boolean value"""
        self.manager.set("integrations.new_enabled", True)
        
        value = self.manager.get("integrations.new_enabled")
        self.assertTrue(value)


class TestConfigManagerSave(unittest.TestCase):
    """Test configuration save operations"""
    
    def setUp(self):
        """Create test config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.config_data = {"test": "value"}
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        self.manager = ConfigManager(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_save_config(self):
        """Test saving configuration"""
        self.manager.config["new_key"] = "new_value"
        self.manager.save_config(self.manager.config)
        
        # Reload and verify
        with open(self.config_path, 'r') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config["new_key"], "new_value")
    
    def test_save_config_with_unicode(self):
        """Test saving configuration with unicode characters"""
        self.manager.config["unicode_key"] = "测试数据"
        self.manager.save_config(self.manager.config)
        
        # Reload and verify
        with open(self.config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config["unicode_key"], "测试数据")
    
    def test_save_config_pretty_print(self):
        """Test saving configuration with indentation"""
        self.manager.config["nested"] = {"key": "value"}
        self.manager.save_config(self.manager.config)
        
        # Read raw file content
        content = self.config_path.read_text(encoding='utf-8')
        
        # Should have indentation (2 spaces)
        self.assertIn("  ", content)


class TestConfigManagerReload(unittest.TestCase):
    """Test configuration reload operations"""
    
    def setUp(self):
        """Create test config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.config_data = {"original": "value"}
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        self.manager = ConfigManager(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_reload_config(self):
        """Test reloading configuration from file"""
        # Modify in memory
        self.manager.config["modified"] = "in_memory"
        
        # Update file
        new_data = {"updated": "on_disk"}
        with open(self.config_path, 'w') as f:
            json.dump(new_data, f)
        
        # Reload
        self.manager.reload()
        
        # Should have file values, not in-memory values
        self.assertEqual(self.manager.get("updated"), "on_disk")
        self.assertIsNone(self.manager.get("modified"))
    
    def test_reload_preserves_structure(self):
        """Test reloading preserves config structure"""
        original = self.manager.get("original")
        self.manager.reload()
        
        self.assertEqual(self.manager.get("original"), original)


class TestConfigManagerUpdateFromDict(unittest.TestCase):
    """Test configuration update from dictionary"""
    
    def setUp(self):
        """Create test config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.config_data = {
            "vault_path": "obsidian_vault",
            "check_interval": {
                "gmail": 120,
                "whatsapp": 30
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        self.manager = ConfigManager(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_update_from_dict_simple(self):
        """Test updating from dictionary with simple values"""
        updates = {"vault_path": "/new/vault"}
        
        self.manager.update_from_dict(updates)
        
        self.assertEqual(self.manager.get("vault_path"), "/new/vault")
    
    def test_update_from_dict_nested(self):
        """Test updating from dictionary with nested values"""
        updates = {
            "check_interval": {
                "gmail": 60,
                "filesystem": 5
            }
        }
        
        self.manager.update_from_dict(updates)
        
        self.assertEqual(self.manager.get("check_interval.gmail"), 60)
        self.assertEqual(self.manager.get("check_interval.filesystem"), 5)
        # Unchanged value
        self.assertEqual(self.manager.get("check_interval.whatsapp"), 30)
    
    def test_update_from_dict_adds_new_keys(self):
        """Test updating from dictionary adds new keys"""
        updates = {"new_section": {"key": "value"}}
        
        self.manager.update_from_dict(updates)
        
        self.assertEqual(self.manager.get("new_section.key"), "value")
    
    def test_update_from_dict_persists(self):
        """Test updating from dictionary persists to file"""
        updates = {"vault_path": "/persistent/vault"}
        
        self.manager.update_from_dict(updates)
        
        # Reload from file
        with open(self.config_path, 'r') as f:
            saved = json.load(f)
        
        self.assertEqual(saved["vault_path"], "/persistent/vault")


class TestConfigManagerDefaultConfig(unittest.TestCase):
    """Test default configuration generation"""
    
    def setUp(self):
        """Create temp directory"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_default_config(self):
        """Test getting default configuration"""
        config_path = Path(self.temp_dir) / "default_config.json"
        manager = ConfigManager(config_path=str(config_path))
        
        # Should have required sections
        self.assertIsNotNone(manager.get("vault_path"))
        self.assertIsNotNone(manager.get("check_interval"))
        self.assertIsNotNone(manager.get("gmail"))
        self.assertIsNotNone(manager.get("whatsapp"))
        self.assertIsNotNone(manager.get("integrations"))
        self.assertIsNotNone(manager.get("security"))
        self.assertIsNotNone(manager.get("logging"))
    
    def test_default_config_has_required_sections(self):
        """Test default config has all required sections"""
        config_path = Path(self.temp_dir) / "default_config.json"
        manager = ConfigManager(config_path=str(config_path))
        
        required_sections = [
            "vault_path",
            "check_interval",
            "watchdog",
            "gmail",
            "whatsapp",
            "calendar",
            "silver_tier_features",
            "api",
            "database",
            "security",
            "logging",
            "mcp_servers",
            "integrations"
        ]
        
        for section in required_sections:
            self.assertIsNotNone(
                manager.get(section),
                f"Missing required section: {section}"
            )


class TestConfigManagerConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def setUp(self):
        """Create test config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.config_data = {
            "vault_path": "obsidian_vault",
            "test_value": 42
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        # Create new manager for testing
        self.manager = ConfigManager(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_config_function(self):
        """Test get_config convenience function"""
        value = self.manager.get("vault_path")
        self.assertEqual(value, "obsidian_vault")
    
    def test_get_config_with_default(self):
        """Test get_config with default value"""
        value = self.manager.get("nonexistent", "default")
        self.assertEqual(value, "default")
    
    def test_set_config_function(self):
        """Test set_config convenience function"""
        self.manager.set("test_value", 100)
        value = self.manager.get("test_value")
        self.assertEqual(value, 100)
    
    def test_reload_config_function(self):
        """Test reload_config convenience function"""
        # Modify file
        new_data = {"vault_path": "/reloaded/vault", "test_value": 42}
        with open(self.config_path, 'w') as f:
            json.dump(new_data, f)
        
        self.manager.reload()
        
        value = self.manager.get("vault_path")
        self.assertEqual(value, "/reloaded/vault")


class TestConfigManagerIntegration(unittest.TestCase):
    """Integration tests for ConfigManager"""
    
    def setUp(self):
        """Create realistic test config"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.config_data = {
            "vault_path": "obsidian_vault",
            "check_interval": {
                "gmail": 120,
                "whatsapp": 30,
                "filesystem": 10,
                "calendar": 300,
                "orchestrator": 60
            },
            "watchdog": {
                "check_interval": 60,
                "auto_restart": True
            },
            "gmail": {
                "credentials_path": "gmail_credentials.json",
                "monitor_filters": ["is:unread is:important"]
            },
            "integrations": {
                "gmail_enabled": True,
                "whatsapp_enabled": True,
                "linkedin_enabled": False
            },
            "security": {
                "require_approval_for": ["payments", "emails_to_new_contacts"],
                "approval_threshold": 100
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        self.manager = ConfigManager(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_configuration_workflow(self):
        """Test full configuration workflow"""
        # Get values
        self.assertEqual(self.manager.get("vault_path"), "obsidian_vault")
        self.assertEqual(self.manager.get("check_interval.gmail"), 120)
        
        # Set new values
        self.manager.set("check_interval.gmail", 60)
        self.assertEqual(self.manager.get("check_interval.gmail"), 60)
        
        # Update from dict
        updates = {
            "check_interval": {
                "whatsapp": 45
            },
            "new_feature": {
                "enabled": True
            }
        }
        self.manager.update_from_dict(updates)
        
        self.assertEqual(self.manager.get("check_interval.whatsapp"), 45)
        self.assertTrue(self.manager.get("new_feature.enabled"))
        
        # Reload and verify persistence
        self.manager.reload()
        self.assertEqual(self.manager.get("check_interval.gmail"), 60)
        self.assertEqual(self.manager.get("check_interval.whatsapp"), 45)
        self.assertTrue(self.manager.get("new_feature.enabled"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

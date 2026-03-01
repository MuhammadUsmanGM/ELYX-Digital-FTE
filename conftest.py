"""
ELYX Project-wide Pytest Configuration and Fixtures

This file provides shared fixtures and configuration for all tests.
"""

import os
import sys
import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


# ============== Session-scoped Fixtures ==============

@pytest.fixture(scope="session")
def project_root_path():
    """
    Get the project root path
    
    Returns:
        Path: Project root directory
    """
    return Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def test_output_dir():
    """
    Create a shared output directory for test artifacts
    
    Yields:
        Path: Path to test output directory
    """
    output_dir = project_root / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    yield output_dir
    
    # Cleanup after all tests
    if output_dir.exists():
        shutil.rmtree(output_dir)


# ============== Module-scoped Fixtures ==============

@pytest.fixture(scope="module")
def module_vault():
    """
    Create a temporary vault for a test module
    
    Yields:
        Path: Path to temporary vault
    """
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir)
    
    # Create standard structure
    folders = [
        "Needs_Action", "Done", "Plans", "Pending_Approval",
        "Logs", "Briefings", "Responses", "Inbox"
    ]
    
    for folder in folders:
        (vault_path / folder).mkdir(exist_ok=True)
    
    yield vault_path
    
    if Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


# ============== Function-scoped Fixtures ==============

@pytest.fixture
def temp_vault():
    """
    Create a temporary Obsidian vault structure for testing
    
    Yields:
        Path: Path to temporary vault directory
    """
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir)
    
    # Create standard vault structure
    folders = [
        "Needs_Action",
        "Done",
        "Plans",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Logs",
        "Briefings",
        "Responses",
        "Inbox",
        "Conversation_History"
    ]
    
    for folder in folders:
        (vault_path / folder).mkdir(exist_ok=True)
    
    # Create Company Handbook
    handbook = vault_path / "Company_Handbook.md"
    handbook.write_text("""# Company Handbook

## Business Rules
1. Always prioritize customer satisfaction
2. Require approval for payments over $100
3. Respond to emails within 24 hours
4. Maintain data sovereignty
""", encoding='utf-8')
    
    # Create Dashboard
    dashboard = vault_path / "Dashboard.md"
    dashboard.write_text(f"""# ELYX Dashboard

## Status: Active
## Last Updated: {datetime.now().isoformat()}
""", encoding='utf-8')
    
    yield vault_path
    
    # Cleanup
    if vault_path.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_config():
    """
    Create a temporary configuration file for testing
    
    Yields:
        tuple: (Path to config file, config data dict)
    """
    temp_dir = tempfile.mkdtemp()
    config_path = Path(temp_dir) / "test_config.json"
    
    config_data = {
        "vault_path": str(Path(temp_dir) / "vault"),
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
            "linkedin_enabled": False,
            "odoo_enabled": False
        },
        "security": {
            "require_approval_for": [
                "payments",
                "emails_to_new_contacts",
                "file_sharing"
            ],
            "approval_threshold": 100
        },
        "logging": {
            "level": "DEBUG",
            "file_logging": True
        },
        "brain_selection": {
            "active_brain": "claude",
            "brains": {
                "claude": {
                    "command": "claude",
                    "args": ["-p"],
                    "description": "Test Claude"
                }
            }
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    yield config_path, config_data
    
    # Cleanup
    if Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_env():
    """
    Mock environment variables for testing
    
    Yields:
        dict: Mock environment variables
    """
    original_env = os.environ.copy()
    
    mock_vars = {
        "OBSIDIAN_VAULT_PATH": "/tmp/test_vault",
        "GMAIL_CHECK_INTERVAL": "60",
        "WHATSAPP_CHECK_INTERVAL": "30",
        "ELYX_ACTIVE_BRAIN": "claude",
        "API_HOST": "localhost",
        "API_PORT": "8000",
        "LOG_LEVEL": "DEBUG"
    }
    
    for key, value in mock_vars.items():
        os.environ[key] = value
    
    yield mock_vars
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_email():
    """
    Sample Gmail message for testing
    
    Returns:
        dict: Sample email message data
    """
    return {
        'id': 'test_msg_123',
        'threadId': 'thread_456',
        'labelIds': ['INBOX', 'UNREAD', 'IMPORTANT'],
        'snippet': 'This is a test email snippet',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'To', 'value': 'recipient@elyx.ai'},
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2024 12:00:00 +0000'}
            ],
            'mimeType': 'text/plain',
            'body': {
                'data': 'VGVzdCBlbWFpbCBjb250ZW50'
            }
        },
        'sizeEstimate': 1234,
        'historyId': '987654',
        'internalDate': '1704110400000'
    }


@pytest.fixture
def sample_task(temp_vault):
    """
    Create a sample task file in Needs_Action folder
    
    Args:
        temp_vault: Temporary vault fixture
    
    Yields:
        Path: Path to created task file
    """
    task_file = temp_vault / "Needs_Action" / "TASK_TEST_001.md"
    task_file.write_text("""---
type: email
from: sender@example.com
subject: Test Subject
received: 2024-01-01T12:00:00
priority: high
status: pending
---

## Email Content

This is a test email for testing purposes.

## Suggested Actions

- [ ] Reply to sender
- [ ] Process request
- [ ] Archive after processing
""", encoding='utf-8')
    
    yield task_file


@pytest.fixture
def mock_brain():
    """
    Create a mock BrainAdapter for testing
    
    Returns:
        MagicMock: Mock brain adapter
    """
    mock_brain = MagicMock()
    mock_brain.name = "claude"
    mock_brain.command = "claude"
    mock_brain.args = ["-p"]
    mock_brain.description = "Mock Claude for testing"
    mock_brain.build_command.return_value = ["claude", "-p", "test prompt"]
    mock_brain.process.return_value = {
        "brain": "claude",
        "success": True,
        "stdout": "Success output",
        "stderr": "",
        "returncode": 0
    }
    
    return mock_brain


@pytest.fixture
def mock_odoo():
    """
    Create a mock OdooService for testing
    
    Returns:
        MagicMock: Mock Odoo service
    """
    mock_service = MagicMock()
    mock_service.authenticated = True
    mock_service.get_revenue_this_week.return_value = 5000.0
    mock_service.get_revenue_this_month.return_value = 20000.0
    mock_service.get_unpaid_invoices.return_value = [
        {'id': 1, 'amount_residual': 500.0, 'payment_state': 'not_paid'},
        {'id': 2, 'amount_residual': 300.0, 'payment_state': 'paid'}
    ]
    mock_service.get_overdue_invoices.return_value = [
        {'id': 3, 'amount_residual': 200.0}
    ]
    
    return mock_service


@pytest.fixture
def async_mock():
    """
    Create an async mock for testing async functions
    
    Returns:
        AsyncMock: Async mock object
    """
    return AsyncMock()


# ============== Helper Functions ==============

class TestHelpers:
    """Helper class with common test utilities"""
    
    @staticmethod
    def create_temp_file(directory: Path, filename: str, content: str) -> Path:
        """Create a temporary file with content"""
        file_path = directory / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    @staticmethod
    def parse_frontmatter(content: str) -> dict:
        """Parse YAML frontmatter from markdown content"""
        import re
        yaml_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            data = {}
            
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip().strip('"\'')
            
            return data
        
        return {}
    
    @staticmethod
    def wait_for_condition(condition, timeout=5, interval=0.1):
        """Wait for a condition to become true"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition():
                return True
            time.sleep(interval)
        
        raise TimeoutError(f"Condition not met within {timeout} seconds")


# ============== Pytest Hooks ==============

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers",
        "requires_api: marks tests that require API keys"
    )
    config.addinivalue_line(
        "markers",
        "requires_credential: marks tests that require credentials"
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to watcher tests
        if "watcher" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)
        
        # Add unit marker to unit tests
        if "unit" in item.nodeid.lower() or "test_" in item.nodeid:
            if "integration" not in item.nodeid.lower():
                item.add_marker(pytest.mark.unit)

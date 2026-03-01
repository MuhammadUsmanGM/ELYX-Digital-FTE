# ELYX Test Suite Documentation

## Overview

The ELYX test suite provides comprehensive testing coverage for the Personal AI Employee framework. It includes unit tests, integration tests, and utility fixtures.

## Test Structure

```
scripts/
├── run_all_tests.py              # Main test runner
├── test_utils.py                 # Test utilities and fixtures
├── test_brain_factory_unit.py    # BrainFactory unit tests
├── test_briefing_service.py      # BriefingService unit tests
├── test_ralph_loop.py            # RalphLoop unit tests
├── test_config_manager.py        # ConfigManager unit tests
├── test_database_services.py     # Database service tests
├── test_response_coordinator.py  # ResponseCoordinator tests
└── test_watchers_integration.py  # Watcher integration tests
```

## Running Tests

### Using the Test Runner (Recommended)

```bash
# Run all tests
python scripts/run_all_tests.py

# Run only unit tests
python scripts/run_all_tests.py --unit

# Run only integration tests
python scripts/run_all_tests.py --integration

# Run with verbose output
python scripts/run_all_tests.py --verbose

# Run specific test
python scripts/run_all_tests.py --test test_brain_factory_unit
```

### Using pytest Directly

```bash
# Run all tests
pytest

# Run specific test file
pytest scripts/test_brain_factory_unit.py

# Run specific test function
pytest scripts/test_brain_factory_unit.py::TestBrainAdapter::test_brain_adapter_initialization

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests matching pattern
pytest -k "brain"

# Run tests with marker
pytest -m unit
pytest -m integration

# Run tests in parallel
pytest -n auto
```

### Using unittest Directly

```bash
# Run specific test file
python -m unittest scripts/test_brain_factory_unit.py

# Run with verbosity
python -m unittest scripts/test_brain_factory_unit.py -v

# Run all tests in scripts directory
python -m unittest discover -s scripts -p "test_*.py"
```

## Test Categories

### Unit Tests
- **test_brain_factory_unit.py**: Tests for AI brain selection and management
- **test_briefing_service.py**: Tests for CEO briefing generation
- **test_ralph_loop.py**: Tests for autonomous processing loop
- **test_config_manager.py**: Tests for configuration management
- **test_database_services.py**: Tests for database operations

### Integration Tests
- **test_watchers_integration.py**: Tests for communication watchers
- **test_response_coordinator.py**: Tests for response coordination across channels

## Test Fixtures

### temp_vault
Creates a temporary Obsidian vault structure with all required folders:
```python
def test_with_vault(self, temp_vault):
    # temp_vault is a Path to temporary vault
    assert (temp_vault / "Needs_Action").exists()
    assert (temp_vault / "Done").exists()
```

### temp_config
Creates a temporary configuration file:
```python
def test_with_config(self, temp_config):
    config_path, config_data = temp_config
    assert config_path.exists()
    assert config_data["vault_path"] is not None
```

### mock_env_variables
Mocks environment variables for testing:
```python
def test_with_env(self, mock_env_variables):
    assert os.getenv("ELYX_ACTIVE_BRAIN") == "claude"
```

### sample_email_message
Provides sample Gmail message data:
```python
def test_email_processing(self, sample_email_message):
    assert sample_email_message["id"] == "test_msg_123"
```

### sample_task_file
Creates a sample task file in Needs_Action:
```python
def test_task_processing(self, sample_task_file):
    content = sample_task_file.read_text()
    assert "type: email" in content
```

## Test Markers

Use markers to categorize and filter tests:

```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.requires_api
def test_api_call():
    pass

@pytest.mark.requires_credential
def test_authenticated_operation():
    pass
```

### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Run tests requiring API (need credentials)
pytest -m requires_api
```

## Coverage Reports

### Generate HTML Coverage Report

```bash
pytest --cov=src --cov-report=html
# Open coverage_report/index.html in browser
```

### Generate XML Coverage Report

```bash
pytest --cov=src --cov-report=xml
# Generates coverage.xml for CI/CD integration
```

### View Coverage in Terminal

```bash
pytest --cov=src --cov-report=term-missing
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist
      
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml -n auto
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Writing New Tests

### Test File Template

```python
#!/usr/bin/env python3
"""
Unit Tests for [Component Name]

Tests for:
- Feature 1
- Feature 2
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.[module].[component] import [Component]


class TestComponent(unittest.TestCase):
    """Test [Component] functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_feature_one(self):
        """Test feature one"""
        self.assertTrue(True)
    
    def test_feature_two(self):
        """Test feature two"""
        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

### Using Fixtures (pytest)

```python
import pytest

def test_with_fixture(temp_vault):
    """Test using temp_vault fixture"""
    task_file = temp_vault / "Needs_Action" / "test.md"
    task_file.write_text("Test content")
    assert task_file.exists()
```

## Troubleshooting

### Import Errors

If you encounter import errors:
```bash
# Ensure you're running from project root
cd C:\Users\Usman Mustafa\OneDrive\Desktop\ELYX-Personal-AI-Employee

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%cd%  # Windows
```

### Credential Errors

For tests requiring credentials:
```bash
# Set up test credentials
cp .env.example .env
# Edit .env with test credentials

# Or skip credential-requiring tests
pytest -m "not requires_credential"
```

### Timeout Issues

For slow tests:
```bash
# Increase timeout
pytest --timeout=600

# Or skip slow tests
pytest -m "not slow"
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Fixtures**: Use fixtures for common setup
3. **Mocking**: Mock external dependencies (APIs, databases)
4. **Naming**: Use descriptive test names
5. **Assertions**: One assertion per test (ideally)
6. **Cleanup**: Always clean up resources in tearDown

## Coverage Goals

| Component | Current | Goal |
|-----------|---------|------|
| BrainFactory | 90% | 95% |
| BriefingService | 85% | 90% |
| RalphLoop | 80% | 90% |
| ConfigManager | 95% | 95% |
| ResponseCoordinator | 75% | 85% |
| Watchers | 70% | 80% |

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Maintain or improve coverage
4. Document test fixtures used
5. Add appropriate markers

## Support

For test-related issues:
- Check test documentation in this file
- Review test utility functions in `test_utils.py`
- Run tests with verbose output for debugging
- Check pytest logs for detailed error information

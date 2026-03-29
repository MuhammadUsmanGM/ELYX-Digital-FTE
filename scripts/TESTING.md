# ELYX Test Suite Documentation

## Overview

The ELYX test suite covers configuration management, end-to-end task flow, and watcher detection logic.

## Test Structure

```
scripts/
├── conftest.py                # Pytest fixtures (temp_vault, temp_config, mock_env, sample data)
├── test_config_manager.py     # ConfigManager unit tests
├── test_core_flow.py          # Integration test: email → watcher → processor → done
├── test_social_detection.py   # Social media keyword detection tests
├── test_whatsapp_detection.py # WhatsApp keyword detection tests
├── ralph_stop_hook.py         # Ralph Wiggum stop hook (not a test)
├── setup_vault_repo.py        # Vault git repo setup utility (not a test)
└── TESTING.md                 # This file
```

## Running Tests

```bash
# Run all tests
pytest scripts/

# Run specific test file
pytest scripts/test_config_manager.py

# Run specific test function
pytest scripts/test_core_flow.py::test_email_flow -v

# Run with coverage
pytest scripts/ --cov=src --cov-report=term-missing

# Skip tests needing credentials
pytest scripts/ -m "not requires_credential"
```

## Test Files

### test_config_manager.py
Unit tests for `src.config.config_manager.ConfigManager`:
- Loading/saving YAML config
- Default values and overrides
- Nested key access

### test_core_flow.py
Integration test for the full task pipeline:
- Email arrives → GmailWatcher creates action file → TaskProcessor picks it up → file moves to Done/
- Tests vault folder structure creation
- Tests action file format compliance

### test_social_detection.py
Tests keyword detection logic used by social media watchers:
- LinkedIn, Facebook, Twitter, Instagram keyword matching
- Priority classification based on content

### test_whatsapp_detection.py
Tests WhatsApp-specific keyword detection:
- Urgent keyword matching (`urgent`, `asap`, `invoice`, `payment`, `help`)
- Message ID deduplication logic

## Fixtures (conftest.py)

| Fixture | Description |
|---------|-------------|
| `temp_vault` | Temporary vault with Needs_Action/, Done/, Plans/, Pending_Approval/ |
| `temp_config` | Temporary YAML config file with test defaults |
| `mock_env_variables` | Mocks ELYX env vars (ELYX_ACTIVE_BRAIN, etc.) |
| `sample_email_message` | Sample Gmail API message dict |
| `sample_task_file` | Pre-created .md task file in Needs_Action/ |

## Troubleshooting

### Import Errors
```bash
# Run from project root
cd "C:\Users\Usman Mustafa\OneDrive\Desktop\ELYX-Personal-AI-Employee"

# Or set PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%cd%    # Windows
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
```

### Credential Errors
```bash
# Skip credential-requiring tests
pytest scripts/ -m "not requires_credential"
```

# Coding Rules for All Brains

## Language & Framework Standards
- **Python**: 3.13+, type hints required for function signatures
- **JavaScript/Node**: ES modules, v24+ LTS
- **FastAPI**: For all API endpoints
- **SQLAlchemy**: For database operations (SQLite via `silver_tier.db`)

## Code Style
- Keep functions small and focused (max ~50 lines)
- Use descriptive variable names - no single-letter variables except loop counters
- Handle errors with try/except - never let exceptions crash the system silently
- Log errors using the `logging` module, not print statements
- All file paths should use `pathlib.Path`, not string concatenation

## File Operations on the Vault
- Always use `Path.mkdir(parents=True, exist_ok=True)` before writing
- Read files with UTF-8 encoding
- Frontmatter in vault `.md` files uses YAML between `---` delimiters
- Never delete vault files - move them to `/Done/` or `/Rejected/`

## Security
- Never hardcode credentials - use environment variables or `credentials.json`
- Never log sensitive data (passwords, tokens, API keys)
- Validate all external input before processing
- Use parameterized queries for database operations

## Git
- Do not commit `.env`, `credentials.json`, `gmail_credentials.json`, or session files
- Commit messages: `type: short description` (e.g., `fix: resolve email parsing error`)

## Testing
- Test new watcher functionality against the vault before deploying
- Use try/except with fallback for all external service calls (Gmail API, Odoo, etc.)
- Graceful degradation - if a service is down, log and continue

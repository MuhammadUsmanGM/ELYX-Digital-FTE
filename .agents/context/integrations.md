# Available Integrations

## Active Integrations (config.json)

| Integration | Status | Check Interval |
|------------|--------|---------------|
| Gmail | Enabled | 120s |
| WhatsApp | Enabled | 3600s |
| LinkedIn | Disabled | 3600s |
| Facebook | Disabled | 7200s |
| Twitter | Disabled | 7200s |
| Instagram | Disabled | 7200s |
| Odoo | Enabled | 3600s |
| Filesystem | Enabled | 10s |

## Gmail Integration
- **Credentials**: `gmail_credentials.json`
- **OAuth setup**: `setup_gmail_auth.py`
- **Filter**: `is:unread is:important`
- **Watcher**: `src/agents/gmail_watcher.py`
- **MCP**: Email MCP server on port 8080

## WhatsApp Integration
- **Session**: `~/.whatsapp_session` (Playwright persistent context)
- **Keywords**: urgent, asap, invoice, payment, help, emergency, critical, important
- **Watcher**: `src/agents/whatsapp_watcher.py`

## Odoo Integration
- **Service**: `src/services/odoo_service.py`
- **Watcher**: `src/agents/odoo_watcher.py`
- **Protocol**: JSON-RPC API
- **Capabilities**: Invoice CRUD, partner management, payment tracking, account balances

## Social Media (Playwright-based)
Each platform uses a headless browser via Playwright:
- **LinkedIn**: `src/agents/linkedin_watcher.py`
- **Facebook**: `src/agents/facebook_watcher.py`
- **Instagram**: `src/agents/instagram_watcher.py`
- **Twitter**: `src/agents/twitter_watcher.py`
- **Session setup**: `setup_sessions.py`, `add_social_credentials.py`

## MCP Servers (config.json > mcp_servers)
- **Email MCP**: localhost:8080 - Send, draft, search emails
- **Browser MCP**: localhost:8081 - Web navigation, form filling

## Database
- **Engine**: SQLite
- **File**: `silver_tier.db`
- **ORM**: SQLAlchemy
- **Schema**: `src/services/database.py`

## API Server
- **Framework**: FastAPI
- **Entry**: `src/api/main.py`
- **Port**: 8000
- **Routes**: dashboard, tasks, approvals, AI, enterprise, communication

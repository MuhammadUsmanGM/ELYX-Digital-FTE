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

## MCP Servers (.claude/settings.local.json > mcpServers)
All MCP servers use stdio transport via `@modelcontextprotocol/sdk`.

| Server | Command | Tools |
|--------|---------|-------|
| `email-mcp` | `node src/mcp-servers/email-mcp/index.js` | send_email, draft_email, search_emails |
| `odoo-mcp` | `node src/mcp-servers/odoo-mcp/index.js` | create_invoice, register_payment, search_invoices, get_revenue, get_overdue_invoices |
| `social-mcp` | `node src/mcp-servers/social-mcp/index.js` | linkedin_post, facebook_post, twitter_post, instagram_post, schedule_post |
| `whatsapp-mcp` | `node src/mcp-servers/whatsapp-mcp/index.js` | send_message, send_bulk_message, get_recent_chats, mark_as_read |
| `filesystem-mcp` | `npx @anthropic/mcp-filesystem obsidian_vault` | read_file, write_file, list_directory |

Config locations:
- **Claude Code**: `.claude/settings.local.json` (primary)
- **Other brains**: `mcp.json` (root, same format)

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

# ELYX MCP Servers

Model Context Protocol (MCP) servers for ELYX AI Employee.

## Available MCP Servers

### 1. Email MCP Server
- Send emails via Gmail
- Draft emails for approval
- Read/search emails

### 2. Browser MCP Server  
- Navigate to websites
- Click buttons/links
- Fill forms
- Extract data from web pages

### 3. Odoo MCP Server
- Create invoices
- Register payments
- Search invoices
- Get accounting data

### 4. Social Media MCP Server
- Post to LinkedIn
- Post to Facebook
- Post to Twitter/X
- Post to Instagram

### 5. WhatsApp MCP Server
- Send WhatsApp messages
- Read WhatsApp conversations

---

## Setup Instructions

### Prerequisites
```bash
npm install -g @anthropic/mcp-cli
```

### Start MCP Servers

```bash
# Email MCP
node src/mcp-servers/email-mcp/index.js

# Browser MCP  
npx -y @anthropic/browser-mcp

# Odoo MCP
node src/mcp-servers/odoo-mcp/index.js

# Social MCP
node src/mcp-servers/social-mcp/index.js

# WhatsApp MCP
node src/mcp-servers/whatsapp-mcp/index.js
```

### Configure Claude Code

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "elyx-email",
      "command": "node",
      "args": ["/path/to/ELYX-Personal-AI-Employee/src/mcp-servers/email-mcp/index.js"]
    },
    {
      "name": "elyx-odoo",
      "command": "node",
      "args": ["/path/to/ELYX-Personal-AI-Employee/src/mcp-servers/odoo-mcp/index.js"]
    },
    {
      "name": "elyx-social",
      "command": "node",
      "args": ["/path/to/ELYX-Personal-AI-Employee/src/mcp-servers/social-mcp/index.js"]
    },
    {
      "name": "elyx-whatsapp",
      "command": "node",
      "args": ["/path/to/ELYX-Personal-AI-Employee/src/mcp-servers/whatsapp-mcp/index.js"]
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["-y", "@anthropic/browser-mcp"]
    }
  ]
}
```

---

## MCP Server Tools

### Email MCP Tools
- `send_email` - Send email to recipient
- `draft_email` - Create draft email for approval
- `search_emails` - Search Gmail

### Browser MCP Tools
- `browser_navigate` - Go to URL
- `browser_click` - Click element
- `browser_fill` - Fill form field
- `browser_screenshot` - Take screenshot

### Odoo MCP Tools
- `odoo_create_invoice` - Create customer invoice
- `odoo_register_payment` - Register payment
- `odoo_search_invoices` - Search invoices
- `odoo_get_revenue` - Get revenue data

### Social MCP Tools
- `linkedin_post` - Post to LinkedIn
- `facebook_post` - Post to Facebook
- `twitter_post` - Post to Twitter
- `instagram_post` - Post to Instagram

### WhatsApp MCP Tools
- `whatsapp_send_message` - Send WhatsApp message
- `whatsapp_read_messages` - Read recent messages

---

## Security Notes

- All sensitive actions require human approval
- Credentials stored in .env (never committed)
- Session cookies managed securely
- Rate limiting enabled

---

Last Updated: February 24, 2026

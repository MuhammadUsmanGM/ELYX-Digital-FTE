# ELYX - Autonomous AI Employee

**Local-First | Multi-Platform | Human-in-the-Loop**

---

## Quick Start

### 1. Setup (One-Time)

```bash
# Install dependencies
pip install -r requirements.txt

# Setup sessions (login to platforms)
python setup_sessions.py

# Setup Gmail (if needed)
python setup_gmail_auth.py

# Setup Odoo (if needed)
python setup_sessions.py odoo
```

### 2. Run ELYX

```bash
python run_elyx.py
```

---

## What It Does

ELYX monitors **7 communication channels** 24/7:
- 📧 Gmail
- 💬 WhatsApp
- 💼 LinkedIn
- 📘 Facebook
- 🐦 Twitter/X
- 📸 Instagram
- 📊 Odoo Accounting

**Automatically:**
- Reads messages and emails
- Detects urgent/important items
- Responds to routine inquiries
- Flags sensitive actions for approval
- Posts to social media (when requested)
- Tracks invoices and payments (via Odoo)
- Generates weekly CEO briefings

---

## Core Workflow

```
1. Message arrives (email, WhatsApp, social)
   ↓
2. Watcher detects and creates task
   ↓
3. AI processes according to Company Handbook
   ↓
4. If sensitive → Creates approval request
   ↓
5. You approve/reject via dashboard
   ↓
6. AI executes and logs result
   ↓
7. Task moved to Done/
```

---

## Access Points

### Dashboard (Web Interface)

```bash
# Terminal 1: Start Vault API
python scripts/start_frontend.py

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

**Access:**
- Dashboard: http://localhost:3000
- Tasks: http://localhost:3000/tasks
- Approvals: http://localhost:3000/approvals
- API Docs: http://localhost:3000/api-docs
- Help: http://localhost:3000/help

### Obsidian Vault (Local Files)

```
obsidian_vault/
├── Dashboard.md              # Current status
├── Company_Handbook.md       # AI rules & guidelines
├── Needs_Action/             # New tasks
├── Pending_Approval/         # Awaiting your approval
├── Done/                     # Completed tasks
├── Plans/                    # AI execution plans
├── Logs/                     # Audit trail
├── Invoices/                 # Odoo invoices
├── Accounting/               # Financial data
└── Briefings/                # Weekly reports
```

---

## Configuration

### Environment Variables (.env)

```env
# AI Brain (choose one)
ELYX_ACTIVE_BRAIN=claude

# Gmail
GMAIL_CREDENTIALS_PATH=gmail_credentials.json

# Odoo
ODOO_URL=https://elyx-ai.odoo.com
ODOO_DB=elyx-ai
ODOO_USERNAME=your-email@gmail.com
ODOO_PASSWORD=your-password

# Chrome Profile (for session persistence)
CHROME_USER_DATA_DIR=C:\Users\YourName\AppData\Local\Google\Chrome\User Data
```

### Config (config.json)

```json
{
  "vault_path": "obsidian_vault",
  "check_interval": {
    "gmail": 120,
    "whatsapp": 60,
    "odoo": 3600
  },
  "integrations": {
    "gmail_enabled": true,
    "odoo_enabled": true
  }
}
```

---

## Available Scripts

| Script | Purpose |
|--------|---------|
| `python run_elyx.py` | Start ELYX |
| `python setup_sessions.py` | Login to all platforms |
| `python setup_sessions.py odoo` | Setup Odoo |
| `python setup_gmail_auth.py` | Setup Gmail OAuth |
| `python scripts/start_frontend.py` | Start Vault API |
| `python scripts/test_core_flow.py` | Test email flow |
| `python scripts/test_mcp_servers.py` | Test MCP servers |

---

## MCP Servers (AI Tool Integration)

ELYX supports multiple AI agents via MCP:

| Agent | Command |
|-------|---------|
| Claude Code | `claude -p "..."` |
| Qwen Coder | `qwen --yolo -p "..."` |
| Gemini CLI | `gemini -p "..."` |
| Codex | `codex exec -p "..."` |

**Setup:**
```bash
python scripts/setup_mcp_config.py --agent all
```

---

## Testing

```bash
# Test core email flow
python scripts/test_core_flow.py

# Test MCP servers
python scripts/test_mcp_servers.py

# Test social media detection
python scripts/test_social_detection.py
```

---

## Troubleshooting

### "Gmail credentials not found"
```bash
python setup_gmail_auth.py
```

### "Odoo not configured"
```bash
python setup_sessions.py odoo
```

### "Vault API offline"
```bash
python scripts/start_frontend.py
```

### Check logs
```bash
cat obsidian_vault/Logs/audit_trail.json | tail -20
```

---

## Documentation

| File | Description |
|------|-------------|
| `README.md` | This file - quick start |
| `CORE_FLOW_FIXES.md` | Core email flow documentation |
| `MCP_INTEGRATION_GUIDE.md` | MCP server integration |
| `UNIVERSAL_MCP_COMPLETE.md` | Universal MCP documentation |
| `DASHBOARD_IMPLEMENTATION.md` | Dashboard usage guide |
| `ODOO_SETUP_GUIDE.md` | Odoo setup instructions |

---

## Status

| Component | Status |
|-----------|--------|
| Email Processing | ✅ Working |
| WhatsApp Monitoring | ✅ Working |
| Social Media Posting | ✅ Working |
| Odoo Integration | ✅ Working |
| Dashboard (Web) | ✅ Working |
| Approvals Workflow | ✅ Working |
| Weekly Briefings | ✅ Working |
| MCP Servers | ✅ Working |

---

**Built for the Personal AI Employee Hackathon 0**

Open Source - MIT License

# ELYX System Architecture

## Overview
ELYX is a multi-agent Personal AI Employee system that autonomously manages personal and business affairs. It uses a local-first architecture with Obsidian as the dashboard and multiple AI brains as reasoning engines.

## Core Components

### The Brain (AI Reasoning)
Multiple brains available via `config.json > brain_selection`:
- **Claude Code** (primary): Strategic reasoning, autonomous operation via Ralph Wiggum loop
- **Qwen Coder** (optional): Fast coding tasks
- **Gemini CLI** (optional): Alternative reasoning
- **Codex** (optional): Code generation

All brains share the same skills, rules, and context from `.agents/`.

### The Memory/GUI (Obsidian Vault)
Local markdown files at `obsidian_vault/` serve as the knowledge base and dashboard. See `vault-structure.md` for folder layout.

### The Senses (Watchers)
Python scripts in `src/agents/` that monitor external sources:
- `gmail_watcher.py` - Monitors Gmail for important/unread emails
- `whatsapp_watcher.py` - Monitors WhatsApp for urgent messages
- `linkedin_watcher.py` - Monitors LinkedIn messages and activity
- `facebook_watcher.py` - Monitors Facebook messages
- `instagram_watcher.py` - Monitors Instagram activity
- `twitter_watcher.py` - Monitors Twitter/X activity
- `odoo_watcher.py` - Monitors Odoo for new invoices/payments
- `filesystem_watcher.py` - Monitors file drops in watch folders

Watchers create `.md` action files in `obsidian_vault/Needs_Action/`.

### The Hands (MCP Servers)
Model Context Protocol servers for external actions:
- **Email MCP**: Send/draft/search emails
- **Browser MCP**: Web navigation, form filling
- **Filesystem MCP**: File read/write operations (built-in)

### The Orchestrator (`src/agents/orchestrator.py`)
Coordinates all agents:
1. Starts and manages watcher processes
2. Monitors `Needs_Action/` for new tasks
3. Triggers the brain to process tasks
4. Manages scheduling (briefings, audits)

### The Watchdog (`src/agents/watchdog.py`)
Monitors system health:
- Checks if processes are running
- Auto-restarts failed processes
- Logs system health metrics

### The Ralph Wiggum Loop (`src/agents/ralph_loop.py`)
Persistence mechanism that keeps the brain working until all tasks in `Needs_Action/` are processed. Uses a stop hook to prevent early termination.

## Data Flow
```
External Source → Watcher → Needs_Action/ → Brain → Plan/ → Execute → Done/
                                                   ↓
                                          Pending_Approval/ → Human → Approved/ → Execute → Done/
```

## Key Services
- `src/services/briefing_service.py` - CEO Briefing generation
- `src/services/odoo_service.py` - Odoo ERP integration
- `src/services/approval_workflow.py` - HITL approval system
- `src/services/response_coordinator.py` - Bidirectional communication
- `src/services/database.py` - SQLite database (elyx.db)

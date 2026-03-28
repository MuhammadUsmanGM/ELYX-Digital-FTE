<div align="center">
  <img src="frontend/public/animated.gif" alt="ELYX Logo" width="120" />
  <h1>ELYX</h1>
  <p><strong>A Local-First Autonomous AI Employee</strong></p>

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Hackathon](https://img.shields.io/badge/Built%20for-Personal%20AI%20Employee%20Hackathon%200-purple?style=for-the-badge)]()

</div>

---

## Overview

**ELYX** is an autonomous AI employee that runs locally on your machine. It monitors your email, social media, and file system — then reasons about incoming tasks, executes actions, and asks for your approval when needed.

You email it "send a WhatsApp message saying hello to +923001234567" and it does it. You get a LinkedIn DM and it drafts a response. An invoice comes in from Odoo and it flags it for review.

Everything stays on your machine. The vault is Markdown. The reasoning engine is swappable. Every action is logged.

Built for the **Personal AI Employee Hackathon 0**.

---

## How It Works

```mermaid
graph TB
    subgraph Sources["External Sources"]
        Gmail["Gmail"]
        WA["WhatsApp"]
        LI["LinkedIn"]
        FB["Facebook"]
        TW["Twitter / X"]
        IG["Instagram"]
        Odoo["Odoo ERP"]
        FS["File Drops"]
    end

    subgraph Watchers["Perception Layer — Python Watchers"]
        GW["Gmail Watcher"]
        WAW["WhatsApp Watcher"]
        LIW["LinkedIn Watcher"]
        FBW["Facebook Watcher"]
        TWW["Twitter Watcher"]
        IGW["Instagram Watcher"]
        OW["Odoo Watcher"]
        FSW["FileSystem Watcher"]
    end

    subgraph Vault["Obsidian Vault — Local Markdown"]
        NA["Needs Action"]
        HB["Company Handbook"]
        Plans["Plans"]
        PA["Pending Approval"]
        Approved["Approved"]
        Done["Done"]
        Logs["Logs"]
        Dash["Dashboard"]
    end

    subgraph Brain["Reasoning Layer"]
        Orch["Orchestrator"]
        TP["Task Processor"]
        RL["Ralph Wiggum Loop"]
        BF["BrainFactory — Claude / Gemini / Qwen / Codex"]
    end

    subgraph MCP["Action Layer — MCP Servers"]
        EM["email-mcp — send · draft · search"]
        WM["whatsapp-mcp — send · read"]
        SM["social-mcp — post · DM"]
        OM["odoo-mcp — invoice · payment"]
        FM["filesystem-mcp — read · write"]
    end

    subgraph HITL["Human-in-the-Loop"]
        Review["Review in Obsidian"]
        Approve["Move to Approved"]
        Reject["Move to Rejected"]
    end

    subgraph Actions["External Actions"]
        Send["Send Email"]
        WAMsg["Send WhatsApp"]
        Post["Social Media Post"]
        Pay["Register Payment"]
    end

    %% Source → Watcher
    Gmail --> GW
    WA --> WAW
    LI --> LIW
    FB --> FBW
    TW --> TWW
    IG --> IGW
    Odoo --> OW
    FS --> FSW

    %% Watcher → Vault
    GW --> NA
    WAW --> NA
    LIW --> NA
    FBW --> NA
    TWW --> NA
    IGW --> NA
    OW --> NA
    FSW --> NA

    %% Orchestrator reads vault
    NA --> Orch
    HB --> TP
    Orch --> TP
    Orch --> RL
    RL --> BF
    BF --> MCP

    %% TaskProcessor decisions
    TP -->|"Safe to automate"| Plans
    TP -->|"Needs approval"| PA
    Plans --> MCP
    Plans --> Done

    %% HITL flow
    PA --> Review
    Review --> Approve
    Review --> Reject
    Approve --> NA
    Reject --> Done

    %% MCP → Actions
    EM --> Send
    WM --> WAMsg
    SM --> Post
    OM --> Pay

    %% Logging
    TP --> Logs
    TP --> Dash

    %% Styling
    classDef sources      fill:#0d1f3c,stroke:#1f6feb,color:#79c0ff,stroke-width:1.5px
    classDef watchers     fill:#1c1206,stroke:#d97706,color:#fbbf24,stroke-width:1.5px
    classDef vault        fill:#0d2d1a,stroke:#238636,color:#56d364,stroke-width:1.5px
    classDef brain        fill:#1a0f3a,stroke:#6e40c9,color:#bc8cff,stroke-width:1.5px
    classDef mcp          fill:#2d1a1a,stroke:#b91c1c,color:#fca5a5,stroke-width:1.5px
    classDef hitl         fill:#1c1a12,stroke:#9e6a03,color:#e3b341,stroke-width:1.5px
    classDef actions      fill:#0a2a2a,stroke:#0e7490,color:#22d3ee,stroke-width:1.5px

    class Gmail,WA,LI,FB,TW,IG,Odoo,FS sources
    class GW,WAW,LIW,FBW,TWW,IGW,OW,FSW watchers
    class NA,HB,Plans,PA,Approved,Done,Logs,Dash vault
    class Orch,TP,RL,BF brain
    class EM,WM,SM,OM,FM mcp
    class Review,Approve,Reject hitl
    class Send,WAMsg,Post,Pay actions
```

---

## What It Can Do

**Communication**
- Monitor Gmail, WhatsApp, LinkedIn, Facebook, Twitter, Instagram
- Auto-respond to routine messages based on handbook rules
- Cross-platform dispatch: email it to send a WhatsApp, or vice versa
- Social media posting across all platforms

**Business Operations**
- Odoo accounting integration (invoices, payments, financial summaries)
- Weekly CEO briefing generation
- Task scheduling via Windows Task Scheduler

**Safety**
- Human-in-the-loop approval for sensitive actions (payments, new contacts, file sharing)
- Append-only activity logs in `/Logs/`
- All actions traceable via vault files

**Intelligence**
- Swappable AI brain (Claude, Gemini, Qwen, Codex)
- Company Handbook-driven decision making
- Predictive analytics and adaptive learning (Silver tier)

---

## Tech Stack

| Component | Technology | Role |
|:----------|:-----------|:-----|
| **Backend** | FastAPI (Python) | API server + task processing |
| **Frontend** | Next.js 16 (TypeScript) | Dashboard UI |
| **Database** | SQLite | Local persistent storage |
| **Memory** | Obsidian (Markdown vault) | Long-term memory + task files |
| **Browser Automation** | Playwright | Social media watchers + sender |
| **ERP** | Odoo Cloud (JSON-RPC) | Accounting & invoicing |
| **AI Engines** | Claude, Gemini, Qwen, Codex | Swappable reasoning cores |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- An AI provider API key (Anthropic recommended)
- Playwright browsers: `playwright install chromium`

### Quick Start

```bash
# 1. Install backend dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Configure environment
cp .env.example .env   # Edit with your API keys

# 4. Start everything
python run_elyx.py
```

The startup script launches:
- FastAPI backend (port 8000)
- Vault API (port 8080)
- Settings API (port 8081)
- Orchestrator + all enabled watchers

```bash
# 5. Start the dashboard (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` to access the dashboard.

### Platform Setup

For social media watchers, log in once via browser:

```bash
python config/setup_sessions.py whatsapp    # Scan QR code
python config/setup_sessions.py linkedin    # Log in manually
python config/setup_sessions.py twitter     # Log in manually
python config/setup_sessions.py facebook    # Log in manually
python config/setup_sessions.py instagram   # Log in manually
```

For Gmail, set up OAuth2 credentials and place them at the path specified in your `.env`.

---

## Project Structure

```
ELYX/
├── src/
│   ├── agents/              # Watchers + orchestrator + watchdog
│   │   ├── orchestrator.py  # Main coordinator
│   │   ├── gmail_watcher.py
│   │   ├── whatsapp_watcher.py
│   │   ├── linkedin_watcher.py
│   │   ├── facebook_watcher.py
│   │   ├── twitter_watcher.py
│   │   ├── instagram_watcher.py
│   │   ├── odoo_watcher.py
│   │   ├── filesystem_watcher.py
│   │   └── watchdog.py
│   ├── api/                 # FastAPI routes
│   │   ├── main.py
│   │   ├── vault_api.py
│   │   ├── settings_api.py
│   │   └── routes/
│   ├── services/            # Business logic
│   │   ├── brain_factory.py
│   │   ├── direct_social_sender.py
│   │   ├── briefing_service.py
│   │   ├── odoo_service.py
│   │   └── ...
│   ├── claude_skills/       # Task processor
│   └── config/              # ConfigManager
├── frontend/                # Next.js dashboard
├── obsidian_vault/          # Markdown vault (separate repo)
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Plans/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Done/
│   ├── Responses/
│   ├── Logs/
│   ├── Templates/
│   ├── Briefings/
│   ├── Conversations/
│   ├── Social_Posts/
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   └── Dashboard.md
├── config.json              # Runtime configuration
├── run_elyx.py              # Startup script
└── requirements.txt
```

---

## Brain Selection

Switch the reasoning engine by editing `.env`:

```env
ELYX_ACTIVE_BRAIN=claude
```

| Brain | Best For |
|:------|:---------|
| `claude` | Strategic reasoning, complex multi-step tasks |
| `qwen` | Fast local coding, lightweight operations |
| `gemini` | High-volume triage, analysis, speed |
| `codex` | Code generation and refactoring |

---

## Windows Task Scheduler

For 24/7 autonomous operation:

```bash
pip install pywin32
python config/setup_windows_scheduler.py register
python config/setup_windows_scheduler.py status
```

This registers startup tasks for the orchestrator, all watchers, scheduled briefings, and vault backups.

---

## Configuration

All runtime settings are in `config.json` and `.env`. The Settings API (port 8081) allows live toggle of features without restart.

Key toggles:
- `integrations.gmail_enabled` / `whatsapp_enabled` / `linkedin_enabled` / etc.
- `silver_tier_features.enable_analytics` / `enable_learning`
- `gold_tier_features.enable_advanced_ai`
- `integrations.use_claude_cli` (enables Ralph Loop autonomous mode)

Secrets can be injected via `CONFIG_` prefixed env vars (e.g., `CONFIG_gmail__credentials_path`) or by placing files in a `Secrets/` directory inside the vault.

---

## Security

- **Local-first**: All data stays on your machine
- **Human-in-the-loop**: Sensitive actions require approval via vault files
- **Audit logging**: Append-only activity logs with timestamps
- **Credential isolation**: Secrets in env vars or vault, never in code
- **Rate limiting**: Built-in rate limiter for social platform interactions

---

<div align="center">
  <p>Built for the Personal AI Employee Hackathon 0</p>
  <sub>Open Source - MIT License</sub>
</div>

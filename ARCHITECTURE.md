# ELYX System Architecture

## Overview

ELYX uses a modular, event-driven architecture inspired by the **Personal AI Employee Hackathon 0** blueprint. The system is designed to autonomously manage business workflows while maintaining local data sovereignty.

## Core Design Principles

1. **Local-First**: All data and credentials remain on the local machine
2. **Event-Driven**: Lightweight watchers trigger AI reasoning cycles
3. **Human-in-the-Loop**: Sensitive actions require explicit approval
4. **Cryptographic Audit**: All actions are signed and logged for traceability
5. **Modular Reasoning**: Swappable AI backends (Claude, Gemini, Qwen, Codex)

---

## System Layers

### 1. Perception Layer (Watchers)

Lightweight Python scripts that monitor external services and create structured task files.

| Watcher | Technology | Check Interval | Status |
| :--- | :--- | :--- | :--- |
| `gmail_watcher.py` | Gmail API (OAuth2) | 120s | ✅ Production |
| `whatsapp_watcher.py` | Playwright (WhatsApp Web) | 60s | ✅ Production |
| `filesystem_watcher.py` | Watchdog | 10s | ✅ Production |
| `linkedin_watcher.py` | Playwright (LinkedIn) | 3600s | 🚧 Prototype |
| `facebook_watcher.py` | Playwright (Facebook) | 7200s | 🚧 Prototype |
| `twitter_watcher.py` | Twitter API v2 | 7200s | 🚧 Prototype |
| `instagram_watcher.py` | Instagram Graph API | 7200s | 🚧 Prototype |
| `odoo_watcher.py` | Odoo JSON-RPC | 3600s | ✅ Production |

**Watcher Pattern:**

```python
# All watchers inherit from BaseWatcher
class BaseWatcher(ABC):
    def check_for_updates() -> list:
        """Return list of new items to process"""
        pass

    def create_action_file(item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def run():
        """Main loop: check → create files → sleep"""
        pass
```

**Output Format:**

When a watcher detects a new item, it creates a Markdown file in `/Needs_Action`:

```markdown
---
type: email
from: client@example.com
subject: Invoice Request
received: 2026-02-23T10:30:00Z
priority: high
status: pending
---

## Content
[Message body or extracted data]

## Suggested Actions
- [ ] Reply to sender
- [ ] Create invoice in Odoo
- [ ] Archive after processing
```

---

### 2. Reasoning Layer (Brain Core)

Executes structured decision pipelines using the selected AI model.

**Supported Brains:**

| Brain | Command | Best For |
| :--- | :--- | :--- |
| Claude | `claude -p` | Strategic reasoning, complex multi-step tasks |
| Qwen | `qwen -p` | Fast local coding, lightweight operations |
| Gemini | `gemini -p` | High-volume triage, analysis |
| Codex | `codex -p` | Code generation, refactoring |

**Brain Factory Pattern:**

```python
# src/services/brain_factory.py
class BrainFactory:
    def get_active_brain() -> AIBrain:
        """Returns configured AI brain based on .env setting"""
        pass
```

**Ralph Wiggum Loop (Persistence Pattern):**

For multi-step tasks, ELYX uses the Ralph Wiggum pattern to keep the AI working autonomously:

1. Orchestrator creates state file with prompt
2. AI works on task
3. AI tries to exit
4. Stop hook checks: Is task file in `/Done`?
5. If NO → Block exit, re-inject prompt (loop continues)
6. If YES → Allow exit (task complete)

**Reference:** [Anthropic Ralph Wiggum Plugin](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)

---

### 3. Execution Layer (Skills)

Performs deterministic actions via MCP servers and direct API calls.

**Core Skills:**

| Skill | Implementation | Status |
| :--- | :--- | :--- |
| Task Processing | `src/claude_skills/ai_employee_skills/processor.py` | ✅ Production |
| Approval Workflow | `src/services/approval_workflow.py` | ✅ Production |
| Email Sending | Email MCP Server | 🚧 Prototype |
| Browser Automation | Browser MCP (Playwright) | 🚧 Prototype |
| Odoo Integration | `src/services/odoo_service.py` | ✅ Production |
| Briefing Generation | `src/services/briefing_service.py` | ✅ Production |

**MCP Server Integration:**

```json
// ~/.config/claude-code/mcp.json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"]
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"]
    }
  ]
}
```

---

### 4. Audit Layer

Logs and cryptographically signs every strategic action for traceability.

**Components:**

| Component | File | Purpose |
| :--- | :--- | :--- |
| Action Signing | `src/utils/quantum_resistant_hash.py` | SHA3-512 hashing with salt |
| Audit Trail | `src/services/blockchain_service.py` | Append-only log with chained hashes |
| Daily Logs | `/Logs/YYYY-MM-DD_Audit.json` | Detailed execution records |

**Audit Flow:**

1. Action is executed (e.g., email sent, invoice created)
2. Action details are hashed with SHA3-512
3. Hash is recorded in `audit_trail.json` with:
   - Timestamp
   - Action type
   - Input parameters
   - Result status
4. Previous block hash is chained for integrity verification

**Example Audit Entry:**

```json
{
  "index": 42,
  "timestamp": "2026-02-23T10:30:00Z",
  "data": {
    "transaction_id": "uuid-here",
    "action_type": "email_sent",
    "details": {
      "to": "client@example.com",
      "subject": "Re: Invoice Request",
      "template_used": "invoice_response_v2"
    }
  },
  "previous_hash": "abc123...",
  "hash": "def456..."
}
```

---

## Data Flow

### Standard Task Processing

```
┌─────────────────┐
│   Watcher       │  Monitors external service (Gmail, WhatsApp, etc.)
│   (Perception)  │
└────────┬────────┘
         │
         │ 1. Detects new item
         ▼
┌─────────────────┐
│  Needs_Action/  │  Creates .md file with structured metadata
│  EMAIL_123.md   │
└────────┬────────┘
         │
         │ 2. File system event triggers
         ▼
┌─────────────────┐
│  Orchestrator   │  Detects new file via watchdog
└────────┬────────┘
         │
         │ 3. Triggers AI brain
         ▼
┌─────────────────┐
│   Brain Core    │  Reads task, checks Company_Handbook.md
│  (Claude/Qwen)  │  Creates Plan.md if multi-step
└────────┬────────┘
         │
         │ 4. Executes actions via MCP
         ▼
┌─────────────────┐
│  Action Layer   │  Sends email, updates Odoo, etc.
└────────┬────────┘
         │
         │ 5. Logs action
         ▼
┌─────────────────┐
│   Audit Log     │  SHA3-512 hash + append to chain
└────────┬────────┘
         │
         │ 6. Move to Done
         ▼
┌─────────────────┐
│     Done/       │  Task complete
└─────────────────┘
```

---

## Human-in-the-Loop Pattern

For sensitive actions, ELYX uses an approval workflow:

**Approval Flow:**

1. AI detects sensitive action (payment, new contact, file sharing)
2. Creates approval request: `/Pending_Approval/APPROVAL_[TASK_ID].md`
3. User reviews and moves file to `/Approved/` or `/Rejected/`
4. Orchestrator monitors `/Approved/` folder
5. If approved → Execute action via MCP
6. Log completion and move to `/Done/`

**Example Approval Request:**

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-02-23T10:30:00Z
expires: 2026-02-24T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A (Bank: XXXX1234)
- Reference: Invoice #1234

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

---

## Directory Structure

```
ELYX-Personal-AI-Employee/
├── src/
│   ├── agents/           # Watcher processes
│   │   ├── gmail_watcher.py
│   │   ├── whatsapp_watcher.py
│   │   ├── orchestrator.py
│   │   └── ralph_loop.py
│   ├── services/         # Business logic
│   │   ├── ai_service.py
│   │   ├── approval_workflow.py
│   │   ├── blockchain_service.py
│   │   ├── odoo_service.py
│   │   └── briefing_service.py
│   ├── utils/            # Utilities
│   │   ├── quantum_resistant_hash.py
│   │   ├── logger.py
│   │   └── handbook_parser.py
│   └── api/              # FastAPI endpoints
│       ├── main.py
│       └── routes/
├── obsidian_vault/       # Local memory & GUI
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Plans/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Done/
│   ├── Logs/
│   ├── Dashboard.md
│   └── Company_Handbook.md
├── config.json           # Configuration
├── run_complete_system.py # Main entry point
└── requirements.txt
```

---

## Security Model

### Credential Management

- All secrets stored in `.env` (never committed to Git)
- OAuth2 tokens stored locally with file permissions
- No credentials leave the local machine

### Action Verification

- Every action is hashed with SHA3-512
- Hash includes timestamp, action type, and parameters
- Chained hashing prevents tampering

### Approval Thresholds

| Action Type | Threshold | Approval Required |
| :--- | :--- | :--- |
| Email to known contact | Any | No |
| Email to new contact | Any | Yes |
| Payment | $0-$25 | No (auto) |
| Payment | $26-$100 | Manager approval |
| Payment | $101+ | Executive approval |
| File sharing | Any | Yes |
| Access changes | Any | Yes |

---

## Scaling Strategy

### Current (Single-Node)

- All processing on local machine
- Vault stored locally
- Suitable for individual users

### Planned (Multi-Node)

- Cloud VM for always-on watchers
- Local machine for approvals and sensitive actions
- Git-based vault sync between nodes

**Phase 1: Delegation via Synced Vault**

- Cloud writes to `/Needs_Action/`, `/Updates/`
- Local merges updates into `Dashboard.md`
- Claim-by-move rule prevents double-work

**Phase 2: A2A Protocol (Optional)**

- Replace some file handoffs with direct agent-to-agent messages
- Vault remains audit record

---

## Experimental Modules

The following modules are research prototypes and **not recommended for production use**:

| Module | Purpose | Status |
| :--- | :--- | :--- |
| `consciousness_emergence.py` | Self-monitoring and awareness | 🧪 Experimental |
| `reality_simulator.py` | Decision impact analysis | 🧪 Experimental |
| `existential_reasoning.py` | Purpose and meaning reasoning | 🧪 Experimental |
| `temporal_reasoner.py` | Time-based causality analysis | 🧪 Experimental |
| `bio_neural_interface.py` | Bio-signal integration (conceptual) | 🧪 Experimental |

These modules explore advanced AI concepts but lack production hardening.

---

## Performance Characteristics

| Metric | Target | Actual (Prototype) |
| :--- | :--- | :--- |
| Gmail check latency | < 2 minutes | ~120 seconds |
| WhatsApp check latency | < 1 minute | ~60 seconds |
| Task processing time | < 30 seconds | Varies by complexity |
| Audit log integrity check | < 1 second | ~200ms |
| Dashboard refresh | < 5 seconds | ~2 seconds |

---

## Known Limitations

1. **Social Media Watchers**: LinkedIn, Facebook, Twitter, Instagram watchers require manual authentication and are not production-ready
2. **Multi-Region Sync**: Requires actual cloud infrastructure (not implemented)
3. **Quantum-Resistant Crypto**: Uses SHA3-512 but not formally verified against NIST PQC standards
4. **Blockchain**: Single-node append-only log (not distributed)
5. **Consciousness Modules**: Research prototypes only

---

## References

- [Personal AI Employee Hackathon 0 Blueprint](Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Anthropic Ralph Wiggum Plugin](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)

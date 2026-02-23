# ELYX Architecture: How Claude Code Communicates Through All Channels

## 🎯 Key Insight

**Claude Code does NOT directly connect to WhatsApp, Gmail, LinkedIn, etc.**

Instead, ELYX uses a **three-layer architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│  PERCEPTION LAYER (Watchers - Python Scripts)               │
│  • Monitor external channels (Gmail, WhatsApp, LinkedIn...) │
│  • Create .md files in /Needs_Action                        │
│  • NO AI involved here - just monitoring                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ File system events
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  REASONING LAYER (Claude Code - THE BRAIN)                  │
│  • Reads .md files from /Needs_Action                       │
│  • Decides what action to take                              │
│  • Creates Plan.md for complex tasks                        │
│  • Uses Ralph Wiggum loop for persistence                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Commands via MCP
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ACTION LAYER (MCP Servers - THE HANDS)                     │
│  • Email MCP: Sends emails                                  │
│  • Browser MCP: Clicks buttons, fills forms                 │
│  • Social MCP: Posts to LinkedIn/Facebook/Twitter           │
│  • Odoo MCP: Updates invoices, payments                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📡 Step-by-Step Flow Example

### Scenario: Client sends urgent WhatsApp message

**1. Perception (WhatsApp Watcher)**
```python
# src/agents/whatsapp_watcher.py
class WhatsAppWatcher(BaseWatcher):
    def check_for_updates(self):
        # Opens WhatsApp Web via Playwright
        # Scans for unread messages with keywords
        # Returns: [{'from': 'Client A', 'text': 'URGENT: Need invoice!'}]
        
    def create_action_file(self, message):
        # Creates: /Needs_Action/WHATSAPP_12345.md
        content = """
---
type: whatsapp
from: Client A
text: URGENT: Need invoice!
received: 2026-02-23T10:30:00Z
priority: high
---
"""
        # Writes file
```

**2. Reasoning (Claude Code)**
```bash
# Orchestrator triggers Claude Code
claude -p "Check /Needs_Action folder and process new tasks"

# Claude Code reads the .md file:
# "I see an urgent WhatsApp message from Client A asking for an invoice."

# Claude Code checks Company_Handbook.md:
# "Urgent invoice requests → Create invoice in Odoo, then send to client"

# Claude Code creates Plan.md:
# /Plans/PLAN_WHATSAPP_12345.md
"""
# Plan: Process Invoice Request

- [ ] Look up Client A in Odoo
- [ ] Create invoice for agreed amount
- [ ] Send invoice via email
- [ ] Reply to WhatsApp confirming sent
- [ ] Move task to /Done
"""
```

**3. Action (MCP Servers)**
```bash
# Claude Code uses MCP servers to execute:

# 1. Odoo MCP - Create invoice
claude -p "Call Odoo MCP to create invoice for Client A"

# 2. Email MCP - Send invoice
claude -p "Call Email MCP to send invoice to client@example.com"

# 3. WhatsApp MCP (via Browser) - Send confirmation
claude -p "Call Browser MCP to send WhatsApp: 'Invoice sent!'"
```

**4. Completion**
```bash
# Claude Code moves file to /Done
# Logs action with SHA3-512 signature
# Updates Dashboard.md
```

---

## 🧠 Claude Code's Role

Claude Code is **ONLY** involved in:

1. ✅ **Reading** task files from `/Needs_Action`
2. ✅ **Deciding** what actions to take
3. ✅ **Planning** multi-step tasks (creates `Plan.md`)
4. ✅ **Orchestrating** MCP servers to execute actions
5. ✅ **Logging** completed actions

Claude Code does **NOT**:

1. ❌ Directly monitor WhatsApp/Gmail/LinkedIn (too slow, would need 24/7 API polling)
2. ❌ Directly send emails or post to social media (uses MCP servers instead)
3. ❌ Store credentials (watchers and MCP servers handle authentication)

---

## 📡 Channel Integration Details

### Gmail
| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Perception** | `gmail_watcher.py` | Gmail API (OAuth2) |
| **Reasoning** | Claude Code reads `/Needs_Action/EMAIL_*.md` | File system |
| **Action** | Email MCP Server | Gmail API |

### WhatsApp
| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Perception** | `whatsapp_watcher.py` | Playwright (WhatsApp Web) |
| **Reasoning** | Claude Code reads `/Needs_Action/WHATSAPP_*.md` | File system |
| **Action** | Browser MCP Server | Playwright (WhatsApp Web) |

### LinkedIn
| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Perception** | `linkedin_watcher.py` | Playwright (LinkedIn Web) |
| **Reasoning** | Claude Code reads `/Needs_Action/LINKEDIN_*.md` | File system |
| **Action** | Social MCP Server | Playwright (LinkedIn Web) |

### Facebook
| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Perception** | `facebook_watcher.py` | Playwright (Facebook Web) |
| **Reasoning** | Claude Code reads `/Needs_Action/FACEBOOK_*.md` | File system |
| **Action** | Social MCP Server | Playwright (Facebook Web) |

### Instagram
| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Perception** | `instagram_watcher.py` | Playwright (Instagram Web) |
| **Reasoning** | Claude Code reads `/Needs_Action/INSTAGRAM_*.md` | File system |
| **Action** | Social MCP Server | Playwright (Instagram Web) |

### Twitter/X
| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Perception** | `twitter_watcher.py` | Playwright (Twitter Web) |
| **Reasoning** | Claude Code reads `/Needs_Action/TWITTER_*.md` | File system |
| **Action** | Social MCP Server | Playwright (Twitter Web) |

### Odoo (Accounting)
| Layer | Component | Technology |
| :--- | :--- | :--- |
| **Perception** | `odoo_watcher.py` | Odoo JSON-RPC API |
| **Reasoning** | Claude Code reads `/Needs_Action/ODOO_*.md` | File system |
| **Action** | Odoo MCP Server | Odoo JSON-RPC API |

---

## 🔁 Ralph Wiggum Loop (Autonomous Operation)

The **Ralph Wiggum pattern** keeps Claude Code working autonomously:

```bash
# 1. Orchestrator creates task
echo "Process /Needs_Action files" > /tmp/current_task.txt

# 2. Claude Code works
claude -p "Process all files in /Needs_Action"

# 3. Claude tries to exit
# Ralph Wiggum hook intercepts:
if [ ! -f "/Done/TASK_COMPLETE" ]; then
    # Task not done → Re-inject prompt
    claude -p "Continue working. Task not complete yet."
fi

# 4. Loop continues until task is done
```

This solves the **"lazy agent" problem** - Claude Code keeps working until the job is done!

---

## 🛡 Human-in-the-Loop (HITL)

For sensitive actions, Claude Code **cannot act directly**:

```bash
# 1. Claude Code detects sensitive action (e.g., payment > $100)
# 2. Claude Code creates approval request:
cat > /Pending_Approval/PAYMENT_123.md << EOF
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
EOF

# 3. Human reviews and moves file to /Approved

# 4. Orchestrator detects approval
# 5. Claude Code executes payment via Odoo MCP
```

---

## 📊 Summary

| Question | Answer |
| :--- | :--- |
| **What is Claude Code's role?** | Reasoning engine - reads files, decides actions, orchestrates MCP servers |
| **Does Claude Code directly access WhatsApp/Gmail?** | NO - Watchers (Python scripts) monitor channels |
| **Does Claude Code directly send messages?** | NO - MCP servers execute actions |
| **Why this architecture?** | Separation of concerns: Watchers monitor, Claude decides, MCP acts |
| **Can I use other AIs?** | YES - Set `ELYX_ACTIVE_BRAIN=qwen` or `gemini`, but Claude Code is recommended |
| **Does Claude Code run 24/7?** | NO - Watchers run 24/7, Claude Code is triggered when tasks arrive |

---

## 🚀 Quick Test

```bash
# 1. Create a test task manually
cat > obsidian_vault/Needs_Action/TEST_001.md << EOF
---
type: test
priority: low
---

Test task: List all files in /Done folder
EOF

# 2. Trigger Claude Code
python -c "from src.services.brain_factory import get_brain_factory; brain = get_brain_factory().get_active_brain(); result = brain.process('Check /Needs_Action/TEST_001.md and complete the task'); print(result)"

# 3. Check result
cat obsidian_vault/Done/TEST_001.md  # Should show completed task
```

---

**Last Updated:** February 23, 2026  
**Reference:** [Personal AI Employee Hackathon 0](Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)

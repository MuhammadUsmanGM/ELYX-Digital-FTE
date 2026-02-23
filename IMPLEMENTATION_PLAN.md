# ELYX - Autonomous AI Employee Implementation Plan

**Based on:** Personal AI Employee Hackathon 0 Blueprint  
**Goal:** Build a fully functional autonomous AI employee with all real features working  
**Architecture:** Local-first, agent-driven, human-in-the-loop

---

## 🎯 Project Vision

Build a **single, unified autonomous AI employee** (not tiered) that proactively manages:
- **Personal Affairs:** Gmail, WhatsApp, Bank transactions
- **Business Operations:** Social media, Odoo accounting, Project tasks
- **24/7 Operation:** Always-on watchers with autonomous decision-making

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PERCEPTION LAYER                        │
│  (Watchers: Gmail, WhatsApp, LinkedIn, Facebook, Twitter)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Create .md files in /Needs_Action
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                          │
│         (Multi-Brain: Claude/Qwen/Gemini/Codex)             │
│              + Ralph Wiggum Autonomous Loop                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Execute via MCP Servers
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     ACTION LAYER                            │
│    (Email, Browser, Social Posts, Odoo Updates, Payments)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Log & Sign
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      AUDIT LAYER                            │
│        (SHA3-512 Signing + Immutable Audit Trail)           │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Feature Checklist (From Hackathon Document)

### Core Foundation (Bronze Tier - ALL REQUIRED)

- [ ] **Obsidian Vault Structure**
  - [x] `Dashboard.md` - Real-time status
  - [x] `Company_Handbook.md` - Rules of engagement
  - [ ] `Business_Goals.md` - Quarterly objectives
  - [ ] Folder structure: `/Inbox`, `/Needs_Action`, `/Plans`, `/Pending_Approval`, `/Approved`, `/Rejected`, `/Done`, `/Logs`

- [ ] **Watcher Implementation** (Python Sentinel Scripts)
  - [x] `gmail_watcher.py` - OAuth2 authenticated
  - [x] `whatsapp_watcher.py` - Playwright-based
  - [x] `filesystem_watcher.py` - Watchdog-based
  - [ ] `linkedin_watcher.py` - Playwright (needs testing)
  - [ ] `facebook_watcher.py` - Playwright (needs testing)
  - [ ] `twitter_watcher.py` - Playwright (needs testing)
  - [ ] `instagram_watcher.py` - Playwright (needs testing)

- [ ] **Claude Code Integration**
  - [x] Read from Obsidian vault
  - [x] Write to Obsidian vault
  - [ ] Ralph Wiggum loop for persistence
  - [ ] Agent Skills implementation

- [ ] **Multi-Brain Support** ✅ (Already implemented)
  - [x] Claude support
  - [x] Qwen support
  - [x] Gemini support
  - [x] Codex support
  - [x] Brain switching via `.env`

---

### Functional Assistant (Silver Tier - ALL REQUIRED)

- [ ] **Multiple Watchers Working Simultaneously**
  - [ ] Gmail + WhatsApp + at least one social platform

- [ ] **LinkedIn Automation**
  - [ ] Monitor for keyword mentions
  - [ ] Auto-post business updates to generate sales
  - [ ] Connection request handling

- [ ] **Claude Reasoning Loop**
  - [ ] Create `Plan.md` files for complex tasks
  - [ ] Multi-step task execution
  - [ ] Progress tracking

- [ ] **MCP Server Implementation**
  - [ ] Email MCP server (send/draft)
  - [ ] Browser MCP server (navigate/click)
  - [ ] Social media MCP (post updates)

- [ ] **Human-in-the-Loop (HITL)**
  - [x] Approval workflow structure
  - [ ] `/Pending_Approval` folder monitoring
  - [ ] Sensitive action detection (payments, new contacts)
  - [ ] Approval file format with clear instructions

- [ ] **Basic Scheduling**
  - [ ] Windows Task Scheduler integration OR
  - [ ] cron jobs (Mac/Linux)
  - [ ] Daily briefing at 8:00 AM

---

### Autonomous Employee (Gold Tier - ALL REQUIRED)

- [ ] **Full Cross-Domain Integration**
  - [ ] Personal (Gmail, WhatsApp) + Business (Odoo, Social) working together

- [ ] **Odoo Community Integration** ⭐ CRITICAL
  - [ ] Self-hosted local Odoo setup
  - [ ] MCP server for Odoo JSON-RPC APIs
  - [ ] Invoice monitoring
  - [ ] Payment tracking
  - [ ] Bank transaction reconciliation

- [ ] **Social Media Auto-Posting**
  - [ ] Facebook: Post messages + generate summaries
  - [ ] Instagram: Post messages + generate summaries
  - [ ] Twitter/X: Post messages + generate summaries
  - [ ] LinkedIn: Post business updates

- [ ] **Multiple MCP Servers**
  - [ ] Email MCP
  - [ ] Browser MCP
  - [ ] Odoo MCP
  - [ ] Social Media MCP

- [ ] **Weekly Business & Accounting Audit** ⭐ CRITICAL
  - [ ] CEO Briefing generation every Monday 8 AM
  - [ ] Revenue tracking from Odoo
  - [ ] Bottleneck identification
  - [ ] Proactive cost-saving suggestions

- [ ] **Error Recovery & Graceful Degradation**
  - [ ] Watcher crash recovery
  - [ ] API rate limit handling
  - [ ] Network failure retry logic

- [ ] **Comprehensive Audit Logging**
  - [x] SHA3-512 action signing
  - [x] Append-only audit trail
  - [ ] Daily logs in `/Logs/YYYY-MM-DD_Audit.json`

- [ ] **Ralph Wiggum Loop** ⭐ CRITICAL
  - [x] Stop hook implementation
  - [ ] File movement detection (`/Needs_Action` → `/Done`)
  - [ ] Autonomous multi-step task completion

- [ ] **Documentation**
  - [x] Architecture documentation (`ARCHITECTURE.md`)
  - [x] Implementation status (`IMPLEMENTATION_STATUS.md`)
  - [ ] Lessons learned document

---

### Production Deployment (Platinum Tier - OPTIONAL BUT RECOMMENDED)

- [ ] **Cloud Deployment (24/7 Operation)**
  - [ ] Oracle Cloud Free VM setup
  - [ ] Always-on watchers
  - [ ] Health monitoring
  - [ ] Auto-restart on failure

- [ ] **Work-Zone Specialization**
  - [ ] **Cloud Agent:** Email triage + draft replies + social post drafts
  - [ ] **Local Agent:** Approvals + WhatsApp + payments + final send actions

- [ ] **Vault Sync (Git-based)**
  - [ ] `/Needs_Action/<domain>/` structure
  - [ ] `/Plans/<domain>/` structure
  - [ ] `/Pending_Approval/<domain>/` structure
  - [ ] Claim-by-move rule implementation
  - [ ] Single-writer rule for `Dashboard.md`
  - [ ] Cloud → Local sync via Git

- [ ] **Security Hardening**
  - [ ] Secrets never sync (`.env` excluded)
  - [ ] WhatsApp sessions local-only
  - [ ] Banking credentials local-only

- [ ] **Odoo Cloud Deployment**
  - [ ] Deploy Odoo Community on Cloud VM
  - [ ] HTTPS setup
  - [ ] Automated backups
  - [ ] Health monitoring
  - [ ] Cloud agent draft-only accounting
  - [ ] Local approval for posting

- [ ] **Platinum Demo Gate**
  - [ ] Email arrives while Local offline
  - [ ] Cloud drafts reply + writes approval file
  - [ ] Local returns → User approves
  - [ ] Local executes send via MCP
  - [ ] Logs → Moves to `/Done`

---

## 🔧 Implementation Priority

### Phase 1: Core Foundation (Week 1-2)
1. ✅ Clean `.env` file (DONE)
2. ✅ Fix Obsidian vault structure
3. ✅ Test all existing watchers
4. ✅ Verify multi-brain switching works

### Phase 2: Silver Features (Week 3-4)
1. Implement Ralph Wiggum loop properly
2. Get LinkedIn watcher working
3. Implement MCP servers (Email + Browser)
4. Test HITL approval workflow

### Phase 3: Gold Features (Week 5-6)
1. Set up Odoo Community (local or cloud)
2. Implement Odoo integration via JSON-RPC
3. Build CEO Briefing generator
4. Get all social media auto-posting working
5. Implement error recovery

### Phase 4: Production Hardening (Week 7-8)
1. Deploy to cloud VM (Oracle/AWS)
2. Set up vault sync via Git
3. Implement work-zone specialization
4. Test Platinum demo scenario
5. Performance optimization

---

## 📁 Required File Structure

```
ELYX-Personal-AI-Employee/
├── .env                          # ✅ Cleaned up
├── config.json                   # ✅ Cleaned up
├── run_complete_system.py        # ⚠️ Needs Ralph Wiggum integration
├── run_autonomous_fte.py         # 🆕 Main entry point (create)
├── requirements.txt              # ✅ OK
├── README.md                     # ✅ Cleaned up
├── ARCHITECTURE.md               # ✅ Created
├── IMPLEMENTATION_STATUS.md      # ✅ Created
├── IMPLEMENTATION_PLAN.md        # 🆕 This file
├── obsidian_vault/
│   ├── Dashboard.md              # ✅ OK
│   ├── Company_Handbook.md       # ✅ Cleaned up
│   ├── Business_Goals.md         # 🆕 Create from template
│   ├── Inbox/                    # ✅ OK
│   ├── Needs_Action/             # ✅ OK
│   ├── Plans/                    # ✅ OK
│   ├── Pending_Approval/         # ✅ OK
│   ├── Approved/                 # ✅ OK
│   ├── Rejected/                 # ✅ OK
│   ├── Done/                     # ✅ OK
│   ├── Logs/                     # ✅ OK
│   ├── Briefings/                # 🆕 Create for CEO briefings
│   └── Accounting/               # 🆕 Create for bank transactions
├── src/
│   ├── agents/
│   │   ├── orchestrator.py       # ⚠️ Update with Ralph Wiggum
│   │   ├── ralph_loop.py         # ✅ Exists, verify working
│   │   ├── gmail_watcher.py      # ✅ Exists
│   │   ├── whatsapp_watcher.py   # ✅ Exists
│   │   ├── linkedin_watcher.py   # ⚠️ Test thoroughly
│   │   ├── facebook_watcher.py   # ⚠️ Test thoroughly
│   │   ├── twitter_watcher.py    # ⚠️ Test thoroughly
│   │   └── instagram_watcher.py  # ⚠️ Test thoroughly
│   ├── services/
│   │   ├── brain_factory.py      # ✅ Exists, verify all brains work
│   │   ├── approval_workflow.py  # ⚠️ Test end-to-end
│   │   ├── odoo_service.py       # ⚠️ Implement JSON-RPC
│   │   ├── briefing_service.py   # ⚠️ Implement CEO briefing
│   │   └── blockchain_service.py # ✅ Exists (audit logging)
│   └── mcp-servers/
│       ├── email-mcp/            # 🆕 Create
│       ├── browser-mcp/          # 🆕 Create
│       ├── odoo-mcp/             # 🆕 Create
│       └── social-mcp/           # 🆕 Create
└── frontend/
    ├── app/
    │   ├── system-monitor/       # ✅ Renamed from consciousness
    │   ├── decision-analysis/    # ✅ Renamed from reality
    │   └── scheduling/           # ✅ Renamed from temporal
    └── components/
        └── DashboardLayout.tsx   # ✅ Updated navigation
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] Each watcher can detect changes
- [ ] Each watcher creates proper `.md` files
- [ ] Brain factory switches correctly
- [ ] Ralph Wiggum loop detects completion
- [ ] Approval workflow moves files correctly

### Integration Tests
- [ ] Gmail → Orchestrator → AI Brain → Response
- [ ] WhatsApp → Orchestrator → AI Brain → Response
- [ ] Odoo sync → CEO Briefing generation
- [ ] Social media post drafting → Approval → Posting

### End-to-End Tests
- [ ] **Demo Scenario 1:** Email inquiry → AI drafts reply → User approves → AI sends
- [ ] **Demo Scenario 2:** WhatsApp urgent message → AI detects → Creates task → User approves action
- [ ] **Demo Scenario 3:** Odoo invoice received → AI logs → AI schedules payment → User approves → Payment sent
- [ ] **Demo Scenario 4:** Monday morning → AI generates CEO briefing → Shows revenue + bottlenecks

---

## 🚀 Getting Started (Quick Start)

```bash
# 1. Clone and setup
git clone <repo-url>
cd ELYX-Personal-AI-Employee

# 2. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials
# Set ELYX_ACTIVE_BRAIN=claude (or qwen/gemini/codex)

# 4. Set up Obsidian vault
# Already created in ./obsidian_vault

# 5. Run the system
python run_autonomous_fte.py

# 6. Access dashboard
cd frontend && npm run dev
# Open http://localhost:3000
```

---

## 📊 Success Metrics

| Metric | Target | Current |
| :--- | :--- | :--- |
| Watchers running simultaneously | 3+ | TBD |
| Tasks processed per day | 50+ | TBD |
| Average response time | < 30s | TBD |
| CEO Briefing accuracy | 95%+ | TBD |
| System uptime | 99%+ | TBD |
| Human approval rate | 80% auto, 20% manual | TBD |

---

## 🛠 Development Guidelines

1. **No Fictional Features:** Remove all consciousness/reality/temporal references
2. **Engineering Language:** Use professional, credible terminology
3. **Test Everything:** Every feature must have working tests
4. **Document Thoroughly:** Architecture, usage, troubleshooting
5. **Human-in-the-Loop:** Sensitive actions always require approval
6. **Local-First:** Credentials and data stay local by default
7. **Audit Everything:** All actions logged with cryptographic signatures

---

## 📞 Support & Resources

- **Hackathon Document:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Architecture:** `ARCHITECTURE.md`
- **Status:** `IMPLEMENTATION_STATUS.md`
- **Obsidian Handbook:** `obsidian_vault/Company_Handbook.md`
- **Ralph Wiggum Reference:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **MCP Documentation:** https://modelcontextprotocol.io/

---

**Last Updated:** February 23, 2026  
**Status:** Planning Phase - Ready for Implementation

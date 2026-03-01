# ELYX Vault Structure

This file documents the complete Obsidian vault structure used by ELYX.

---

## Root Level Files

| File | Purpose | Editable by AI |
|------|---------|----------------|
| `Dashboard.md` | Real-time system status | ✅ Yes (auto-update) |
| `Company_Handbook.md` | Decision rules & guidelines | ❌ No (human-maintained) |
| `Business_Goals.md` | Business objectives & targets | ❌ No (human-maintained) |

---

## Folder Structure

```
obsidian_vault/
│
├── Inbox/                          # New unprocessed items
│   └── [raw incoming files]
│
├── Needs_Action/                   # Tasks requiring processing
│   ├── EMAIL_*.md                  # Email tasks
│   ├── SOCIAL_*.md                 # Social media tasks
│   ├── FINANCE_*.md                # Financial tasks
│   ├── INVOICE_*.md                # Invoice tasks
│   ├── WHATSAPP_*.md               # WhatsApp tasks
│   └── FILE_*.md                   # File drop tasks
│
├── Plans/                          # Execution plans
│   └── PLAN_{TYPE}_{TIMESTAMP}.md
│
├── Pending_Approval/               # Awaiting human approval
│   ├── APPROVAL_*.md               # General approvals
│   ├── REVIEW_*.md                 # Review requests
│   └── SECURITY_*.md               # Security alerts
│
├── Approved/                       # Approved actions (ready to execute)
│   └── [moved from Pending_Approval]
│
├── Rejected/                       # Rejected actions
│   └── [moved from Pending_Approval]
│
├── Done/                           # Completed tasks
│   └── [all processed files]
│
├── In_Progress/                    # Currently being worked on
│   └── [claimed by active agent]
│
├── Logs/                           # System logs
│   ├── audit_trail.json            # Cryptographic audit log
│   ├── YYYY-MM-DD.log              # Daily activity logs
│   └── ERROR_*.md                  # Error reports
│
├── Briefings/                      # Generated reports
│   ├── CEO_Briefing_*.md           # Weekly CEO briefings
│   └── Financial_Report_*.md       # Financial reports
│
├── Accounting/                     # Financial data
│   ├── Current_Month.md            # Current month transactions
│   └── Reconciliation_*.md         # Reconciliation reports
│
├── Invoices/                       # Invoice records
│   ├── Outgoing/                   # Sent invoices
│   └── Incoming/                   # Received invoices
│
├── Responses/                      # Generated responses
│   ├── RESPONSE_*.md               # Draft responses
│   └── PROCESSED_*.md              # Sent responses
│
├── Social_Posts/                   # Social media content
│   ├── Drafts/                     # Draft posts
│   ├── Scheduled/                  # Scheduled posts
│   └── Published/                  # Published posts
│
├── Conversations/                  # Communication history
│   ├── Email/                      # Email threads
│   ├── WhatsApp/                   # WhatsApp conversations
│   └── Social/                     # Social media interactions
│
├── Active_Projects/                # Active project tracking
│   └── [project files]
│
├── Templates/                      # File templates
│   ├── Email_Template.md
│   ├── Approval_Template.md
│   └── Plan_Template.md
│
└── Attachments/                    # File attachments
    └── [uploaded files]
```

---

## File Format Specification

### Standard Task File

```markdown
---
type: email | social | finance | invoice | whatsapp | file_drop
from: "sender@example.com"
subject: "Email subject line"
priority: low | medium | high | critical
status: pending | processing | completed | error
created: ISO 8601 timestamp
detected_at: ISO 8601 timestamp
message_id: unique identifier
---

# Task Content

[Original content/message body]

## Suggested Actions
- [ ] Action item 1
- [ ] Action item 2

--- AI EXECUTION LOG ---
Processed by: ELYX AI Employee
Timestamp: ISO 8601 timestamp
Plan Created: [[Plans/PLAN_*.md|View Plan]]
Analysis: [AI reasoning]
Action Taken: [What was done]
Result: SUCCESS | FAILED | PENDING_APPROVAL
```

### Approval Request File

```markdown
---
type: approval_request
action: send_email | make_payment | post_social | etc.
recipient: target recipient
amount: DECIMAL (if financial)
reason: why approval is needed
created: ISO 8601 timestamp
expires: ISO 8601 timestamp
status: pending
---

## Action Details

[Description of action to be approved]

## Context

[Relevant background information]

## Risk Assessment

- Financial Impact: $X
- Reversibility: Yes/No
- Precedent: [Similar past actions]

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder.
```

### Plan File

```markdown
# Plan for Task: {TASK_FILENAME}

**Task Type**: {TYPE}
**Priority**: {PRIORITY}
**Created**: {TIMESTAMP}

## Proposed Steps

1. Step 1 description
2. Step 2 description
3. Step 3 description

## Risk Assessment

- Risk Level: LOW | MEDIUM | HIGH
- Reversibility: Yes/No
- Approval Required: Yes/No

## Execution Log

- [ ] Step 1 completed - TIMESTAMP
- [ ] Step 2 completed - TIMESTAMP
- [ ] Step 3 completed - TIMESTAMP

## Outcome

[Final result and notes]
```

---

## Folder Workflow

### Task Lifecycle

```
Inbox/
  ↓ (detected by watcher)
Needs_Action/
  ↓ (processed by AI)
  ├─→ Plans/ (plan created)
  ├─→ Pending_Approval/ (if approval needed)
  │     ↓ (human approves)
  │   Approved/
  │     ↓ (executed)
  │   Done/
  │
  └─→ Done/ (if auto-approved)
```

### Approval Workflow

```
Pending_Approval/
  ↓ (human moves to Approved/)
Approved/
  ↓ (AI executes)
Done/

OR

Pending_Approval/
  ↓ (human moves to Rejected/)
Rejected/
  ↓ (AI logs rejection)
Done/
```

---

## Naming Conventions

### Files

| Type | Pattern | Example |
|------|---------|---------|
| Email | `EMAIL_{MESSAGE_ID}.md` | `EMAIL_18a3f2b9c4d5e6f7.md` |
| Social | `SOCIAL_{PLATFORM}_{TIMESTAMP}.md` | `SOCIAL_LINKEDIN_1772347994.md` |
| Invoice | `INVOICE_{INVOICE_NUM}.md` | `INVOICE_INV-2024-001.md` |
| Finance | `FINANCE_{TYPE}_{TIMESTAMP}.md` | `FINANCE_PAYMENT_1772347994.md` |
| Plan | `PLAN_{HASH}_{TIMESTAMP}.md` | `PLAN_1f85debc_1772346794.md` |
| Approval | `APPROVAL_{ORIGINAL}_{TIMESTAMP}.md` | `APPROVAL_EMAIL_123_1772347994.md` |
| Response | `RESPONSE_{HASH}_{TIMESTAMP}.md` | `RESPONSE_74ff1e6b_1772347994.md` |

### Timestamps

All timestamps use ISO 8601 format:
- Full: `2026-03-01T12:34:56.789Z`
- Date only: `2026-03-01`

---

## Access Patterns

### Read Operations

Any AI agent can read from any folder.

### Write Operations

| Folder | Write Access |
|--------|--------------|
| Inbox/ | Watchers only |
| Needs_Action/ | Watchers, Orchestrator |
| Plans/ | AI agents |
| Pending_Approval/ | AI agents (create), Humans (move) |
| Approved/ | Humans (move), AI agents (read & execute) |
| Rejected/ | Humans (move), AI agents (read & log) |
| Done/ | AI agents (move completed) |
| Logs/ | All system components |

### Claim Mechanism

To prevent duplicate processing:

1. AI agent moves task from `Needs_Action/` to `In_Progress/{AGENT_NAME}/`
2. AI agent processes task
3. AI agent moves to `Done/` (or `Pending_Approval/`)
4. Other agents ignore files in `In_Progress/` folders

---

## Maintenance

### Daily

- Archive old logs (>30 days)
- Review stale approvals (>48h)
- Check for orphaned files in `In_Progress/`

### Weekly

- Generate CEO Briefing
- Audit financial records
- Review error logs

### Monthly

- Backup entire vault
- Review and update templates
- Archive completed projects

---

## Quick Reference

**Most Used Folders:**
- `Needs_Action/` - Check first for new tasks
- `Pending_Approval/` - Human approval queue
- `Done/` - Completed work
- `Logs/` - Audit trail

**Most Used Files:**
- `Dashboard.md` - System status
- `Company_Handbook.md` - Decision rules
- `Business_Goals.md` - Business context

---

**Version**: 2.0  
**Last Updated**: 2026-03-01

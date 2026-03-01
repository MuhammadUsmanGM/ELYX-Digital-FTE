# Obsidian Vault Structure

All vault files are at `obsidian_vault/`. This is the shared knowledge base and dashboard.

## Folder Layout

```
obsidian_vault/
├── Dashboard.md              # Main status dashboard (auto-updated)
├── Company_Handbook.md       # Decision-making rules and procedures
├── Business_Goals.md         # Revenue targets, KPIs, active projects
│
├── Needs_Action/             # Incoming tasks from watchers (brain reads from here)
│   ├── EMAIL_*.md            # Email action items
│   ├── WHATSAPP_*.md         # WhatsApp action items
│   ├── SOCIAL_*.md           # Social media action items
│   ├── FILE_*.md             # File drop action items
│   └── FINANCE_*.md          # Financial action items
│
├── Plans/                    # Execution plans created by the brain
│   └── PLAN_*.md
│
├── Pending_Approval/         # Items waiting for human approval
│   ├── REVIEW_*.md           # Review requests
│   ├── INVOICE_*.md          # Invoice approvals
│   └── POST_*.md             # Social media post approvals
│
├── Approved/                 # Human-approved items (brain executes these)
├── Rejected/                 # Human-rejected items (brain logs and closes)
├── In_Progress/              # Currently being processed (claim-by-move)
├── Done/                     # Completed tasks (archive)
│
├── Briefings/                # CEO Briefings
│   └── CEO_Briefing_*.md
│
├── Logs/                     # Audit and activity logs
│   ├── audit_trail.json      # Append-only audit log
│   └── YYYY-MM-DD_Audit.json # Daily audit logs
│
├── Inbox/                    # Raw incoming items before triage
├── Conversations/            # Conversation history/context
├── Attachments/              # File attachments
├── Templates/                # Response templates
├── Invoices/                 # Invoice records
├── Active_Projects/          # Current project tracking
└── Accounting/               # Accounting records
```

## File Frontmatter Format

All action files use YAML frontmatter:
```yaml
---
type: email|whatsapp|file_drop|finance|social
from: sender_identifier
priority: low|medium|high|critical
status: pending|in_progress|completed|rejected
created: ISO_TIMESTAMP
---
```

## Key Rules
- **Never delete files** - always move to Done/ or Rejected/
- **Claim-by-move**: First agent to move item from Needs_Action/ to In_Progress/ owns it
- **Single-writer for Dashboard.md**: Only one process updates it at a time
- **Append-only logs**: Never modify existing log entries

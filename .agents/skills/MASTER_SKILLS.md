# ELYX Master Skills Reference

This file aggregates all available skills so you can quickly determine which skill to use and how. Read this file first - only read individual SKILL.md files when you need the full detailed workflow.

---

## Skill Routing Table

Use this table to match incoming tasks to the correct skill:

| File Pattern | Task Type | Skill | Priority |
|-------------|-----------|-------|----------|
| `EMAIL_*.md` | Email triage & response | [email-processing](email-processing/SKILL.md) | By content |
| `SOCIAL_*.md` | Social media messages | [social-media-posting](social-media-posting/SKILL.md) | Medium |
| `POST_*.md` | Social media publishing | [social-media-posting](social-media-posting/SKILL.md) | Low |
| `FINANCE_*.md` | Financial operations | [odoo-accounting](odoo-accounting/SKILL.md) | High |
| `INVOICE_*.md` | Invoice management | [odoo-accounting](odoo-accounting/SKILL.md) | High |
| `WHATSAPP_*.md` | WhatsApp messages | [task-processing](task-processing/SKILL.md) | By content |
| `FILE_*.md` | File drops | [task-processing](task-processing/SKILL.md) | Low |
| `DISCREPANCY_*.md` | Financial mismatch | [odoo-accounting](odoo-accounting/SKILL.md) | Critical |
| `REVIEW_*.md` | Approval requests | [approval-workflow](approval-workflow/SKILL.md) | High |
| Any file in `/Approved/` | Execute approved action | [approval-workflow](approval-workflow/SKILL.md) | High |
| Any file in `/Rejected/` | Log rejection | [approval-workflow](approval-workflow/SKILL.md) | Low |
| Scheduled: Monday 8 AM | CEO Briefing | [ceo-briefing](ceo-briefing/SKILL.md) | Medium |
| Scheduled: Friday 5 PM | Weekly Accounting Audit | [ceo-briefing](ceo-briefing/SKILL.md) | Medium |

---

## Skill Summaries

### 1. email-processing
**When**: `EMAIL_*.md` lands in `Needs_Action/`
**What it does**:
- Classifies email: auto-respond, flag-for-review, or auto-archive
- Auto-responds to routine inquiries (project status, meeting confirmations)
- Flags financial emails (payment, invoice, transfer keywords) for approval
- Flags unknown senders with urgent requests for review
- Flags identity spoofing as Security Threat
- Moves processed items to `Done/`, logs in `Logs/`

**Approval needed**: Financial emails, unknown senders, suspicious content

### 2. social-media-posting
**When**: `SOCIAL_*.md` in `Needs_Action/` or posting is requested
**What it does**:
- Drafts platform-appropriate posts (LinkedIn, Facebook, Instagram, Twitter)
- Creates approval file in `Pending_Approval/POST_{PLATFORM}_{TIMESTAMP}.md`
- Publishes only after human moves file to `Approved/`
- Monitors social messages: replies to positive engagement, flags controversies
- Maintains consistent brand voice per platform

**Approval needed**: ALL posts require approval before publishing

### 3. task-processing
**When**: Any file in `Needs_Action/` (catch-all for tasks without a specific skill)
**What it does**:
- Scans and prioritizes tasks (Critical > High > Medium > Low)
- Creates execution plans in `Plans/PLAN_{TYPE}_{TIMESTAMP}.md`
- Routes to specific skills when task type is recognized
- Executes safe actions directly, flags sensitive actions for approval
- Moves completed tasks to `Done/`, updates `Dashboard.md`

**Approval needed**: Depends on action type (see security rules)

### 4. ceo-briefing
**When**: Monday 8 AM (weekly briefing), Friday 5 PM (accounting audit), or on request
**What it does**:
- Pulls revenue data from Odoo (invoices, payments, outstanding)
- Counts tasks completed/pending/blocked from vault folders
- Identifies bottlenecks (stale approvals >48h, failed tasks, overdue deadlines)
- Audits subscriptions per Business_Goals.md rules
- Cross-references Odoo with vault records for discrepancies
- Generates `Briefings/CEO_Briefing_{DATE}.md`

**Approval needed**: None (read-only reporting)

### 5. odoo-accounting
**When**: `FINANCE_*.md` or `INVOICE_*.md` in `Needs_Action/`, or financial data needed
**What it does**:
- Creates draft invoices in Odoo (never posts without approval)
- Tracks outstanding and overdue invoices
- Matches payments to invoices
- Detects discrepancies between ELYX records and Odoo
- Provides financial data to CEO Briefing skill

**Approval needed**: ALL invoice posting, ALL payment recording

### 6. approval-workflow
**When**: Any skill determines an action needs human approval
**What it does**:
- Creates structured approval files in `Pending_Approval/`
- Includes: action details, context, risk assessment, approve/reject instructions
- Monitors `Approved/` folder → executes the approved action
- Monitors `Rejected/` folder → logs and closes
- Flags stale requests (>48h) in Dashboard and CEO Briefing

**Approval needed**: N/A (this skill IS the approval mechanism)

---

## Decision Flowchart

```
New file in Needs_Action/
        │
        ├─ EMAIL_*     → email-processing
        ├─ SOCIAL_*    → social-media-posting
        ├─ FINANCE_*   → odoo-accounting
        ├─ INVOICE_*   → odoo-accounting
        ├─ WHATSAPP_*  → task-processing
        ├─ FILE_*      → task-processing
        └─ Other       → task-processing (catch-all)
                │
                ▼
        Is action safe?
        ├─ YES → Execute → Done/
        └─ NO  → approval-workflow → Pending_Approval/
                        │
                        ├─ Approved/ → Execute → Done/
                        └─ Rejected/ → Log → Done/
```

---

## Quick Rules (from rules/)
- **Financial**: All payments need approval. $0-25 auto-log, $26-100 manager, $101+ executive.
- **Communication**: Professional tone. AI disclosure on first contact. Never engage in arguments.
- **Security**: Never hardcode credentials. Never delete vault files. Always log actions.
- **Coding**: Python 3.13+, pathlib for paths, logging module for errors, try/except for external calls.

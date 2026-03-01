---
name: approval-workflow
description: Human-in-the-loop approval system for sensitive actions. Creates approval requests, monitors for decisions, and executes approved actions. Use whenever an action requires human authorization.
---

# Approval Workflow Skill

## Trigger
When any skill determines an action requires human approval.

## Creating an Approval Request

### 1. Generate Approval File
Create in `obsidian_vault/Pending_Approval/`:

```yaml
---
type: approval_request
action: send_email|make_payment|post_social|create_invoice|execute_action
amount: DECIMAL (if financial)
recipient: TARGET
reason: WHY_APPROVAL_NEEDED
created: ISO_TIMESTAMP
expires: EXPIRATION_TIMESTAMP
status: pending
source_file: ORIGINAL_TASK_PATH
---

## Action Details
[Clear description of what will happen if approved]

## Context
[Why this action was flagged - rule that triggered it]

## Risk Assessment
- **Risk Level**: low|medium|high|critical
- **Reversible**: yes|no

## To Approve
Move this file to /Approved/ folder.

## To Reject
Move this file to /Rejected/ folder.
```

### 2. Actions That ALWAYS Require Approval
- Payments of any amount
- Emails to new/unknown contacts
- File sharing to external parties
- Access permission changes
- Sharing confidential information
- All social media posts before publishing
- Posting invoices in Odoo
- Any action the AI is uncertain about

### 3. Monitoring for Decisions
The orchestrator periodically checks:
- `/Approved/` - for approved actions to execute
- `/Rejected/` - for rejected actions to log and close
- `/Pending_Approval/` - for stale requests (>48 hours)

### 4. Executing Approved Actions
When a file appears in `/Approved/`:
1. Read the approval file
2. Execute the approved action using the appropriate skill/MCP
3. Move the file to `/Done/`
4. Log the execution with approval reference in `/Logs/`
5. Update Dashboard.md

### 5. Handling Rejections
When a file appears in `/Rejected/`:
1. Log the rejection
2. Move to `/Done/` with status: rejected
3. If the original task needs alternative handling, create new action file

### 6. Stale Request Handling
If a request has been pending for >48 hours:
- Flag it in Dashboard.md as needing attention
- Include in next CEO Briefing as a bottleneck

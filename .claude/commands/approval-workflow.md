Human-in-the-loop approval system for sensitive actions. Creates approval requests, monitors for decisions, and executes approved actions.

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
[Why this action was flagged]

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
- All social media posts before publishing
- Posting invoices in Odoo
- Any action the AI is uncertain about

### 3. Monitoring for Decisions
Check periodically:
- `/Approved/` - for approved actions to execute
- `/Rejected/` - for rejected actions to log and close
- `/Pending_Approval/` - for stale requests (>48 hours)

### 4. Executing Approved Actions
When a file appears in `/Approved/`:
1. Read the approval file
2. Execute the approved action using the appropriate MCP server
3. Move the file to `/Done/`
4. Log the execution in `/Logs/`
5. Update Dashboard.md

### 5. Stale Request Handling
If a request has been pending for >48 hours:
- Flag it in Dashboard.md as needing attention
- Include in next CEO Briefing as a bottleneck

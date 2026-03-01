---
name: task-processing
description: Process action items from the Needs_Action folder. Read task files, create execution plans, manage task lifecycle through to completion. Core skill for the orchestration loop.
---

# Task Processing Skill

## Trigger
Files appearing in `obsidian_vault/Needs_Action/` folder.

## Workflow

### 1. Scan and Prioritize
Read all `.md` files in `Needs_Action/` and sort by priority:
1. **Critical**: System alerts, security issues
2. **High**: Urgent communications, deadlines
3. **Medium**: Routine tasks, follow-ups
4. **Low**: Administrative tasks, archiving

### 2. For Each Task

#### Step 1: Read and Understand
- Parse frontmatter (`type`, `from`, `priority`, `status`)
- Read the task content and suggested actions
- Check `obsidian_vault/Company_Handbook.md` for applicable rules

#### Step 2: Create Plan
For non-trivial tasks, create a plan file:
```
obsidian_vault/Plans/PLAN_{TASK_TYPE}_{TIMESTAMP}.md
```

Plan format:
```yaml
---
created: ISO_TIMESTAMP
status: in_progress
related_to: ORIGINAL_TASK_FILE
---

## Objective
[What needs to be done]

## Steps
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Approval Required
[Yes/No - describe what needs approval]
```

#### Step 3: Execute or Request Approval
- **Safe actions** (reading, archiving, logging): Execute directly
- **Sensitive actions** (sending emails, payments, external actions): Create approval request in `Pending_Approval/`
- **Unknown actions**: Flag for human review

#### Step 4: Complete
1. Update the plan file with completed steps
2. Move the original task from `Needs_Action/` to `Done/`
3. Log the action in `obsidian_vault/Logs/`
4. Update `Dashboard.md`

### 3. Task Types and Handlers

| Type | Handler | Approval Needed |
|------|---------|----------------|
| `email` | Email Processing Skill | If financial or unknown sender |
| `whatsapp` | Direct response or flag | If urgent from unknown |
| `file_drop` | Process file, log metadata | No |
| `social` | Social Media Posting Skill | Always for posts |
| `finance` | Odoo Accounting Skill | Always |
| `calendar` | Schedule/confirm meeting | No |

### 4. Error Handling
- If a task cannot be processed, move to `obsidian_vault/Needs_Action/` with updated status
- Log the error in `obsidian_vault/Logs/`
- If 3 consecutive failures, flag for human intervention

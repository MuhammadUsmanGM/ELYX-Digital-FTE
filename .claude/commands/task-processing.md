Process action items from the Needs_Action folder. Read task files, create execution plans, manage task lifecycle through to completion. This is the catch-all skill for tasks without a specific handler.

## Trigger
Files appearing in `obsidian_vault/Needs_Action/` folder.

## Routing Table
| File Pattern | Route To |
|-------------|----------|
| `EMAIL_*.md` | /email-processing |
| `SOCIAL_*.md` | /social-media-posting |
| `FINANCE_*.md` | /odoo-accounting |
| `INVOICE_*.md` | /odoo-accounting |
| `WHATSAPP_*.md` | Process here |
| `FILE_*.md` | Process here |
| Other | Process here |

## Workflow

### 1. Scan and Prioritize
Read all `.md` files in `Needs_Action/` and sort:
1. **Critical**: System alerts, security issues
2. **High**: Urgent communications, deadlines
3. **Medium**: Routine tasks, follow-ups
4. **Low**: Administrative tasks, archiving

### 2. For Each Task

#### Read and Understand
- Parse frontmatter (`type`, `from`, `priority`, `status`)
- Check `obsidian_vault/Company_Handbook.md` for applicable rules

#### Create Plan
For non-trivial tasks, create: `obsidian_vault/Plans/PLAN_{TYPE}_{TIMESTAMP}.md`

#### Execute or Request Approval
- **Safe actions** (reading, archiving, logging): Execute directly
- **Sensitive actions** (sending messages, payments): Create approval in `Pending_Approval/`
- **Unknown actions**: Flag for human review

#### Complete
1. Move original task from `Needs_Action/` to `Done/`
2. Log in `obsidian_vault/Logs/`
3. Update `Dashboard.md`

### 3. Error Handling
- If task cannot be processed after 3 attempts, flag for human intervention
- Log all errors in `obsidian_vault/Logs/`

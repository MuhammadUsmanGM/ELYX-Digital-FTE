Generate the Weekly CEO Briefing with revenue tracking, task summaries, bottleneck identification, and proactive suggestions.

## Trigger
- Every Monday at 8:00 AM (scheduled)
- When manually requested by user
- Friday 5 PM for weekly accounting audit

## Workflow

### 1. Gather Data

#### Revenue Data (from Odoo)
Use `mcp__odoo-mcp__get_revenue`, `mcp__odoo-mcp__get_overdue_invoices`, `mcp__odoo-mcp__search_invoices` to get:
- Total revenue this week
- Outstanding invoices
- Overdue payments
- Revenue vs target (from Business_Goals.md)

#### Task Metrics (from Vault)
Use `mcp__filesystem-mcp__list_directory` to count:
- Tasks completed this week (files in `/Done/` with this week's dates)
- Tasks pending (files in `/Needs_Action/`)
- Tasks awaiting approval (files in `/Pending_Approval/`)

#### Bottleneck Identification
- Tasks stuck in `/Pending_Approval/` for >48 hours
- Tasks that failed processing (check `/Logs/`)
- Overdue deadlines from `/Plans/`

### 2. Generate Briefing

Create file: `obsidian_vault/Briefings/CEO_Briefing_{YYYY-MM-DD}.md`

```markdown
# CEO Briefing - Week of {DATE}

## Revenue Summary
- **This Week**: ${amount}
- **MTD**: ${amount}
- **Outstanding Invoices**: {count} (${total})
- **Overdue Payments**: {count} (${total})

## Task Summary
- **Completed**: {count}
- **In Progress**: {count}
- **Pending Approval**: {count}

## Bottlenecks
{list of identified bottlenecks with recommended actions}

## Proactive Suggestions
{AI-generated suggestions based on trends and data}

## Action Items
- [ ] {prioritized action items for the CEO}
```

### 3. Notify
- Update Dashboard.md with briefing link
- Log briefing generation in `/Logs/`

### 4. Accounting Audit (Friday)
- Cross-reference Odoo records with vault records
- Flag any discrepancies as **High Priority**
- Generate audit summary in the briefing

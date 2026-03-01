---
name: ceo-briefing
description: Generate the Weekly CEO Briefing with revenue tracking, task summaries, bottleneck identification, and proactive suggestions. Use every Monday morning or when a business audit is requested.
---

# CEO Briefing Skill

## Trigger
- Every Monday at 8:00 AM (scheduled)
- When manually requested by user
- Friday 5 PM for weekly accounting audit

## Workflow

### 1. Gather Data

#### Revenue Data (from Odoo)
- Total revenue this week
- Outstanding invoices
- Overdue payments
- Revenue vs target (from Business_Goals.md)

#### Task Metrics (from Vault)
- Tasks completed this week (count files in `/Done/` with this week's dates)
- Tasks pending (count files in `/Needs_Action/`)
- Tasks awaiting approval (count files in `/Pending_Approval/`)
- Average task completion time

#### Bottleneck Identification
- Tasks stuck in `/Pending_Approval/` for >48 hours
- Tasks that failed processing (check `/Logs/`)
- Overdue deadlines from `/Plans/`

#### Subscription Audit (from Business_Goals.md rules)
- Flag subscriptions with no login in 30 days
- Flag cost increases >20%
- Flag duplicate functionality

### 2. Generate Briefing

Create file: `obsidian_vault/Briefings/CEO_Briefing_{YYYY-MM-DD}.md`

```markdown
# CEO Briefing - Week of {DATE}

## Revenue Summary
- **This Week**: ${amount}
- **MTD**: ${amount}
- **Target**: ${target} ({percentage}% achieved)
- **Outstanding Invoices**: {count} (${total})
- **Overdue Payments**: {count} (${total})

## Task Summary
- **Completed**: {count}
- **In Progress**: {count}
- **Pending Approval**: {count}
- **Failed/Blocked**: {count}

## Bottlenecks
{list of identified bottlenecks with recommended actions}

## Key Metrics
| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Client response time | X hours | <24 hours | OK/ALERT |
| Invoice payment rate | X% | >90% | OK/ALERT |
| Software costs | $X | <$500/mo | OK/ALERT |

## Proactive Suggestions
{AI-generated suggestions based on trends and data}

## Action Items
- [ ] {prioritized action items for the CEO}
```

### 3. Notify
- Update Dashboard.md with briefing link
- Log briefing generation in `/Logs/`

### 4. Accounting Audit (Friday)
When generating the Friday accounting audit:
- Cross-reference Odoo records with vault records
- Flag any discrepancies as **High Priority**
- Verify all invoices match bank statements
- Generate audit summary in the briefing

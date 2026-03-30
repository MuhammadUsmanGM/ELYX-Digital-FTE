Manage accounting operations through Odoo integration. Create invoices, track payments, monitor financial health.

## Trigger
- `FINANCE_*.md` or `INVOICE_*.md` files in `Needs_Action/`
- CEO Briefing requests financial data
- User requests financial operations

## MCP Tools Available
- `mcp__odoo-mcp__create_invoice` - Create draft invoice
- `mcp__odoo-mcp__register_payment` - Record a payment
- `mcp__odoo-mcp__search_invoices` - Search by filters (state, payment_state, partner_id)
- `mcp__odoo-mcp__get_revenue` - Revenue data by period (week/month/year)
- `mcp__odoo-mcp__get_overdue_invoices` - List overdue invoices

## Workflow

### Invoice Management
1. Read invoice request from action file
2. Create draft invoice via `mcp__odoo-mcp__create_invoice`
3. Create approval file: `Pending_Approval/INVOICE_{ID}.md`
4. **NEVER post invoices without human approval**

### Payment Tracking
1. When payment notification received
2. Match payment to invoice
3. Create verification file for human confirmation
4. Record via `mcp__odoo-mcp__register_payment` after approval

### Payment Thresholds
- $0-$25: Auto-log (still needs confirmation)
- $26-$100: Manager approval required
- $101+: Executive approval required

### Discrepancy Detection
- Compare ELYX records with Odoo data
- Any mismatch = **High Priority** alert in `Needs_Action/DISCREPANCY_{TIMESTAMP}.md`

### Safety Rules
- Can **monitor** Odoo freely
- Can **create drafts** but cannot post without approval
- **Cannot delete or modify** posted invoices
- All financial actions logged in audit trail

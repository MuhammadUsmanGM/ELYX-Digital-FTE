---
name: odoo-accounting
description: Manage accounting operations through Odoo integration. Create invoices, track payments, monitor financial health. Use when handling finance-related tasks or Odoo action files.
---

# Odoo Accounting Skill

## Trigger
- `FINANCE_*.md` or `INVOICE_*.md` files in `Needs_Action/`
- Odoo watcher detects new invoices or payments
- CEO Briefing skill requests financial data
- User requests financial operations

## Workflow

### 1. Invoice Management

#### Creating Invoices
1. Read invoice request from action file
2. Draft invoice in Odoo via MCP/JSON-RPC
3. Create approval file: `Pending_Approval/INVOICE_{ID}.md`
4. **NEVER post invoices without human approval**

#### Monitoring Invoices
- Track outstanding invoices
- Alert when invoices are overdue (>30 days)
- Generate payment reminders (draft, require approval)

### 2. Payment Tracking

#### Recording Payments
1. When payment notification received (email/bank)
2. Match payment to invoice in Odoo
3. Create verification file for human confirmation
4. **Payments must be verified against bank statements before marking as 'Paid'**

#### Payment Rules
- All payments require human approval
- $0-$25: Can be auto-logged (still needs confirmation)
- $26-$100: Manager approval required
- $101+: Executive approval required

### 3. Financial Reporting

#### Weekly Reports
Provide data to CEO Briefing skill:
- Revenue this period
- Outstanding invoices with aging
- Overdue payments
- Cash flow summary

#### Discrepancy Detection
- Compare ELYX records with Odoo data
- Any mathematical discrepancy = **High Priority Task**
- Create alert in `Needs_Action/DISCREPANCY_{TIMESTAMP}.md`

### 4. Odoo Operations via MCP

Available Odoo operations:
- `search_invoices(filters)` - Search invoices by date, status, partner
- `create_invoice(partner, lines)` - Create draft invoice
- `get_invoice(id)` - Get invoice details
- `list_partners()` - List business partners
- `get_account_balance()` - Get current account balances
- `search_payments(filters)` - Search payment records

### 5. Safety Rules
- ELYX can **monitor** Odoo freely
- ELYX can **create drafts** but cannot post without approval
- ELYX **cannot delete or modify** posted invoices
- All financial actions are logged in audit trail

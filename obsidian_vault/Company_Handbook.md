# 📘 Company Handbook

Welcome to the AI Employee's decision-making guide. This handbook defines the rules and procedures that govern how the AI Employee processes tasks and makes decisions.

## 📬 Message Priority & Response Rules (SIMPLE SYSTEM)

> [!info] Simple Priority System
>
> ELYX processes **ALL messages** from ALL channels automatically. No whitelist needed!
> Priority is determined by **content** and **context**, not a trusted contacts list.

### ✅ Auto-Respond (No approval needed)

**When to use:**
- Existing clients asking about project status
- Meeting confirmations
- Invoice requests (create draft in Odoo, flag for approval)
- General business inquiries
- Routine administrative tasks

**Claude Code Action:** Respond automatically based on Handbook guidelines

### ⚠️ Flag for Review (Approval needed)

**When to use:**
- "URGENT" requests from unknown senders
- Payment requests over $100
- First-time contacts asking for pricing/services
- Requests mentioning "confidential", "legal", "contract"
- Anything that feels suspicious or unusual

**Claude Code Action:** Create `/Pending_Approval/REVIEW_[SOURCE]_[ID].md` for human review

### 🗑️ Auto-Archive (No action needed)

**When to use:**
- Obvious spam/promotional messages
- Wrong number messages
- Bulk marketing emails
- Scam attempts

**Claude Code Action:** Archive after logging for audit trail

---

## 📨 Rules for Processing Emails

> [!tip] Email Processing
>
> - **Routine Inquiries**: Automated responses
> - **Financial Terms**: Flag emails with "payment", "invoice", "money", "transfer", "wire" for human approval
> - **Promotional**: Archive promotional emails after reading
> - **Urgent from unknown**: Flag for Manual Review (don't auto-execute)
> - **Identity Spoofing**: If an email claims to be you but comes from a different address, flag as **Security Threat**

## 💰 Rules for Financial Actions

> [!caution] Financial Guidelines
>
> - **All payments** require human approval
> - **Transactions over $100** need review
> - **Log all financial activities** for audit trail

### Approval Thresholds

- **$0-$25**: Automated processing
- **$26-$100**: Manager approval
- **$101+**: Executive approval

## 💬 Rules for Communication

> [!info] Communication Standards
>
> - **New Contacts**: Never send emails without approval
> - **Professional Tone**: Maintain professional tone in all communications
> - **AI Disclosure**: Disclose AI involvement when required

### Communication Protocols

- Use template responses when possible
- Personalize when necessary
- Follow up on outstanding requests
- Archive completed conversations

## 📋 Approval Requirements

> [!warning] Mandatory Approvals
> The following actions **always require human approval**:

- [[Payment Requests]]
- [[Emails to New Contacts]]
- [[File Sharing Requests]]
- [[Access Permission Changes]]
- [[Confidential Information Sharing]]

## 🔄 Default Actions

> [!todo] Standard Procedures
>
> - Schedule meetings when possible
> - Answer frequently asked questions
> - Process routine administrative tasks
> - Archive completed tasks

### Task Prioritization

1. **Critical**: System alerts, security issues
2. **High**: Urgent communications, deadlines
3. **Medium**: Routine tasks, follow-ups
4. **Low**: Administrative tasks, archiving

## 👔 Rules for LinkedIn & Social Media

> [!info] Social Media Protocol
>
> - **All Messages Processed**: ELYX monitors ALL messages (no whitelist needed)
> - **Unknown Connections**: Flag urgent requests from unknown contacts for Manual Review
> - **Direct Messages**: Provide general professional information. For project details, create review file.
> - **Posting**: Auto-draft posts, flag for approval before publishing

## 📱 Rules for Facebook, Instagram, and Twitter

> [!info] Social Platforms
> - **All Messages Processed**: ELYX monitors ALL activity (no whitelist)
> - **Brand Voice**: Maintain consistent, professional, helpful tone
> - **Engagement**: Prioritize replies to positive interactions
> - **Safety**: Never share private info publicly
> - **Crisis Management**: Flag controversial threads for Human Review
> - **Posting**: Draft posts, require approval before publishing

## 💰 Accounting & Odoo Protocol
> [!money] Financial Integrity
> - **Invoices**: ELYX can monitor Odoo for new invoices but **cannot delete or modify** posted invoices without manual approval.
> - **Payments**: Payments should be verified against bank statements (manual confirmation) before being marked as 'Paid' in Odoo.
> - **CEO Briefing**: Generate the Weekly Business Audit every Friday at 5 PM local time.
> - **Discrepancies**: Any mathematical discrepancy between ELYX records and Odoo must be flagged as a **High Priority Task**.

## 🔐 Audit & Accountability

### Action Logging
- **Cryptographic Signing**: Every processed task is hashed using SHA3-512 to ensure tamper detection
- **Immutable Audit Trail**: Action metadata and hashes are stored in append-only logs (`audit_trail.json`) to prevent history alteration
- **Daily Audit Logs**: Detailed execution logs stored in `/Logs/YYYY-MM-DD_Audit.json`

### Data Redundancy
- **Local Backup**: Vault data should be backed up daily to secure cloud storage
- **Git Sync**: Recommended to use Git for version control and cross-machine synchronization
- **Disaster Recovery**: Restore from `/Attachments` folder and Git history if needed

### Validation
- **Integrity Checks**: Before a task is marked 'Done', its SHA3-512 checksum is verified
- **Audit Trail**: All critical actions are logged with timestamps and action details for compliance

## 👤 Contact Management (OPTIONAL)

> [!tip] Simple Approach
>
> You DON'T need to maintain a trusted contacts list. ELYX processes ALL messages and uses Human-in-the-Loop for unknown senders.

**Optional: Keep a reference list**

If you want to maintain a reference list of important contacts, edit `Trusted_Contacts.md`. However, this is **NOT used for filtering** - it's just a reference for you.

**Primary Owner:**
- Your email and phone number (for your reference)

**Verification Rule:**
- If an unknown person claims to be a colleague, ask for their official company email to verify identity before processing urgent requests.

## 🛡️ Security Protocols

- Encrypt sensitive data
- Use secure communication channels
- Maintain audit logs
- Report security incidents

## 📈 Performance Metrics

- Response time targets
- Accuracy measurements
- Approval efficiency
- Error rates

## 🔁 Continuous Improvement

Regular reviews of:

- Decision accuracy
- Process efficiency
- User satisfaction
- System performance

---

_Last updated: `= date(now())`_
_Handbook Version: 1.0_

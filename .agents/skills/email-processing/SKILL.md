---
name: email-processing
description: Process incoming emails from Gmail watcher. Triage by priority, draft responses, flag sensitive items for approval. Use when handling EMAIL_ action files in Needs_Action folder.
---

# Email Processing Skill

## Trigger
When a file matching `EMAIL_*.md` appears in `obsidian_vault/Needs_Action/`.

## Workflow

### 1. Read and Classify
- Read the email action file frontmatter (`type`, `from`, `subject`, `priority`)
- Classify into: **auto-respond**, **flag-for-review**, or **auto-archive**

### 2. Classification Rules

**Auto-Respond (no approval needed):**
- Existing clients asking about project status
- Meeting confirmations
- Invoice requests (create draft in Odoo, flag for approval)
- General business inquiries
- Routine administrative tasks

**Flag for Review (approval needed):**
- "URGENT" from unknown senders
- Payment requests over $100
- First-time contacts asking for pricing/services
- Mentions of "confidential", "legal", "contract"
- Anything suspicious or unusual

**Auto-Archive:**
- Obvious spam/promotional messages
- Bulk marketing emails
- Scam attempts

### 3. Process Based on Classification

#### Auto-Respond
1. Draft a professional response following Company_Handbook.md tone guidelines
2. Use the Gmail MCP to send the response
3. Move the action file to `obsidian_vault/Done/`
4. Log the action in `obsidian_vault/Logs/`

#### Flag for Review
1. Create an approval file: `obsidian_vault/Pending_Approval/REVIEW_EMAIL_{ID}.md`
2. Include: original email content, suggested response, reason for flagging
3. Wait for human to move file to `/Approved/` or `/Rejected/`

#### Auto-Archive
1. Log the email metadata for audit trail
2. Move to `obsidian_vault/Done/` with status: archived

### 4. Financial Email Detection
If email contains keywords: "payment", "invoice", "money", "transfer", "wire"
- ALWAYS flag for human approval regardless of sender
- Create approval file with financial flag

### 5. Identity Verification
If an email claims to be from the owner but comes from a different address:
- Flag as **Security Threat**
- Do NOT auto-respond
- Create high-priority review file

## Output Format
After processing, update `obsidian_vault/Dashboard.md` with:
- Number of emails processed
- Actions taken (responded, flagged, archived)
- Any pending approvals

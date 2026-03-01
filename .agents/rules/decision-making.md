# Decision Making Framework

This file provides the complete decision-making framework for ELYX AI agents.

---

## The ELYX Decision Tree

```
Task Received
    ↓
┌──────────────────────────────────────────┐
│ STEP 1: Classify Task Type               │
├──────────────────────────────────────────┤
│ • EMAIL_*.md    → Email Processing       │
│ • SOCIAL_*.md   → Social Media Posting   │
│ • FINANCE_*.md  → Odoo Accounting        │
│ • INVOICE_*.md  → Odoo Accounting        │
│ • REVIEW_*.md   → Approval Workflow      │
│ • Other         → Task Processing        │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ STEP 2: Check Company Handbook           │
├──────────────────────────────────────────┤
│ Read: obsidian_vault/Company_Handbook.md │
│ • Auto-respond rules                     │
│ • Approval requirements                  │
│ • Communication guidelines               │
│ • Financial thresholds                   │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ STEP 3: Assess Risk Level                │
├──────────────────────────────────────────┤
│ LOW RISK (Execute Directly):             │
│ • Routine inquiries                      │
│ • Meeting confirmations                  │
│ • File organization                      │
│ • Status updates                         │
│                                          │
│ MEDIUM RISK (Log & Execute):             │
│ • Non-financial external comms           │
│ • Existing contact requests              │
│ • Data retrieval                         │
│                                          │
│ HIGH RISK (Require Approval):            │
│ • Financial transactions >$25            │
│ • New contact communications             │
│ • Sensitive data sharing                 │
│ • Irreversible actions                   │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ STEP 4: Execute or Flag                  │
├──────────────────────────────────────────┤
│ IF LOW/MEDIUM RISK:                      │
│ • Execute using appropriate skill        │
│ • Log in audit_trail.json                │
│ • Move to Done/                          │
│ • Update Dashboard.md                    │
│                                          │
│ IF HIGH RISK:                            │
│ • Create approval file                   │
│ • Move to Pending_Approval/              │
│ • Log approval request                   │
│ • Wait for human action                  │
└──────────────────────────────────────────┘
```

---

## Risk Assessment Matrix

### Financial Risk

| Amount | Risk Level | Action |
|--------|------------|--------|
| $0 - $25 | Low | Auto-process, log action |
| $26 - $100 | Medium | Log + notify in Dashboard |
| $101+ | High | Require human approval |
| Any (unknown sender) | High | Require human approval |

### Communication Risk

| Recipient | Content Type | Risk Level | Action |
|-----------|--------------|------------|--------|
| Existing contact | Routine | Low | Auto-respond |
| Existing contact | Sensitive | Medium | Log + consider approval |
| New contact | Any | High | Require approval |
| Unknown | Any | High | Flag for review |

### Data Access Risk

| Data Type | Risk Level | Action |
|-----------|------------|--------|
| Public info | Low | Share freely |
| Internal docs | Medium | Log access |
| Financial records | High | Require approval |
| Credentials | Critical | NEVER share |

---

## Confidence Thresholds

Before executing any action, assess your confidence:

```
Confidence > 90%  → Execute with standard logging
Confidence 70-90% → Execute with enhanced logging
Confidence 50-70% → Flag for human review
Confidence < 50%  → Do not execute, request guidance
```

### Confidence Factors

**Increase Confidence:**
- ✅ Clear instructions in Company_Handbook.md
- ✅ Similar past successful executions
- ✅ Reversible action
- ✅ Low risk impact
- ✅ Complete information available

**Decrease Confidence:**
- ❌ Ambiguous instructions
- ❌ No prior examples
- ❌ Irreversible action
- ❌ High risk impact
- ❌ Missing information

---

## Approval Decision Flowchart

```
Action Identified
    ↓
Is it financial? → YES → Require approval
    ↓ NO
Is recipient new? → YES → Require approval
    ↓ NO
Is it sensitive? → YES → Require approval
    ↓ NO
Is it reversible? → NO → Consider approval
    ↓ YES
Am I certain? → NO → Flag for review
    ↓ YES
Execute directly
```

---

## Emergency Protocols

### System Errors

If you encounter repeated errors (>3 attempts):

1. **Stop** the failing operation
2. **Log** the error in audit_trail.json
3. **Create** error report in `Logs/ERROR_{TIMESTAMP}.md`
4. **Flag** in Dashboard.md
5. **Wait** for human intervention

### Security Threats

If you detect suspicious activity:

1. **Do not execute** the suspicious request
2. **Log** as security concern
3. **Create** security alert in `Pending_Approval/SECURITY_{TIMESTAMP}.md`
4. **Flag** urgent in Dashboard.md
5. **Notify** via available channels

### Data Inconsistency

If you detect data mismatch (e.g., Odoo vs vault):

1. **Do not modify** either source
2. **Document** the discrepancy
3. **Create** discrepancy report
4. **Flag** for human review
5. **Continue** other operations

---

## Quality Assurance

### Before Executing Any Action

- [ ] Checked Company_Handbook.md
- [ ] Assessed risk level
- [ ] Verified confidence >70%
- [ ] Identified correct skill to use
- [ ] Prepared logging entry

### After Executing Any Action

- [ ] Logged in audit_trail.json
- [ ] Moved task to correct folder
- [ ] Updated Dashboard.md if needed
- [ ] Verified action completed successfully
- [ ] No errors in logs

---

## Examples

### Example 1: Email from Existing Client

**Input**: `EMAIL_123.md` from `client@existing.com` asking for project status

**Decision Process**:
1. Type: EMAIL → Email Processing skill
2. Recipient: Existing contact → Low risk
3. Content: Status update → Routine inquiry
4. Confidence: 95% (clear handbook rule)
5. **Action**: Auto-respond, log, move to Done/

### Example 2: Invoice Over $500

**Input**: `INVOICE_456.md` for $500 payment

**Decision Process**:
1. Type: INVOICE → Odoo Accounting skill
2. Amount: $500 → High risk (>$100)
3. Action: Payment recording
4. Confidence: 100% (clear threshold rule)
5. **Action**: Create approval request, move to Pending_Approval/

### Example 3: Social Media Post Request

**Input**: `POST_789.md` requesting LinkedIn post

**Decision Process**:
1. Type: POST → Social Media Posting skill
2. Action: Publishing to external platform
3. Risk: Public communication → High
4. Confidence: 100% (all posts need approval)
5. **Action**: Create approval request, wait for approval

---

## Quick Reference

**When in doubt:**
1. Check Company_Handbook.md
2. If still uncertain → Flag for human review
3. Better to over-communicate than under-communicate
4. Safety > Speed

**Remember:**
- You're an AI employee, not the decision maker
- Humans make strategic decisions, you execute
- When uncertain, ask (via approval workflow)
- Log everything for transparency

---

**Version**: 2.0  
**Last Updated**: 2026-03-01

# ELYX Simple Message Priority System

## 🎯 Overview

**OLD SYSTEM (❌ Removed):**
- Maintain Trusted_Contacts.md whitelist
- Watchers check if sender is trusted
- Block messages from unknown people
- **Problem:** High maintenance, miss opportunities from new clients

**NEW SYSTEM (✅ Implemented):**
- Process ALL messages from ALL senders
- Claude Code filters based on content
- Human-in-the-Loop for suspicious/unknown requests
- **Benefit:** Zero maintenance, never miss opportunities

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  WATCHERS (Dumb Monitors)                                   │
│  • Monitor ALL channels (Gmail, WhatsApp, LinkedIn, etc.)   │
│  • Create .md files for EVERY message                       │
│  • NO filtering based on sender                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ All messages go to /Needs_Action
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CLAUDE CODE (Smart Filter)                                 │
│  • Reads Company_Handbook.md rules                          │
│  • Classifies by CONTENT (not sender)                       │
│  • Decides: Auto-respond / Flag / Archive                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ACTION                                                     │
│  ✅ Auto-Respond → Reply immediately                        │
│  ⚠️ Flag for Review → /Pending_Approval/                    │
│  🗑️ Auto-Archive → Log and ignore                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Priority Classification

### ✅ Auto-Respond (No approval needed)

**Content Patterns:**
- "When is my project due?"
- "Can we schedule a meeting?"
- "Please send invoice"
- "Status update request"

**Claude Code Action:**
1. Responds automatically
2. Creates invoice draft (if requested)
3. Logs action in /Done

**Example:**
```
Message: "Hi, when will the website be ready?"
↓
Claude responds: "Hi! The website is scheduled for delivery on [date]. 
                  Would you like a progress update?"
↓
Logs to /Done/WHATSAPP_123.md
```

---

### ⚠️ Flag for Review (Approval needed)

**Content Patterns:**
- "URGENT: Need help immediately!" (from unknown sender)
- "Can you quote $5000 for this project?" (new contact)
- "This is confidential legal matter"
- "I need your banking details"

**Claude Code Action:**
1. Creates `/Pending_Approval/REVIEW_WHATSAPP_123.md`
2. Waits for human review
3. Does NOT respond automatically

**Example:**
```
Message: "URGENT! I need your services now! Send me pricing!"
(From: +1234567890 - not in your contacts)
↓
Claude creates: /Pending_Approval/REVIEW_WHATSAPP_789.md

Content:
---
type: review_request
from: +1234567890 (Unknown)
urgency: HIGH
reason: Unknown sender requesting pricing
---

## Message
URGENT! I need your services now! Send me pricing!

## Recommended Action
- [ ] Research sender (LinkedIn, Google)
- [ ] Decide if legitimate opportunity
- [ ] Approve response OR Archive as spam

Move to /Approved to respond
Move to /Rejected to archive
```

---

### 🗑️ Auto-Archive (No action needed)

**Content Patterns:**
- "Congratulations! You've won a prize!"
- "Buy now! 90% discount!"
- "You have a new follower!" (automated)
- "Wrong number, sorry"

**Claude Code Action:**
1. Logs for audit trail
2. Moves to /Done with "archived" status
3. No response sent

---

## 📁 File Structure

```
obsidian_vault/
├── Needs_Action/
│   ├── WHATSAPP_123.md          # All messages land here first
│   ├── EMAIL_456.md
│   └── LINKEDIN_789.md
├── Pending_Approval/
│   ├── REVIEW_WHATSAPP_123.md   # Unknown urgent requests
│   └── REVIEW_EMAIL_456.md      # Large payment requests
├── Approved/
│   └── (Human moves files here to approve)
├── Rejected/
│   └── (Human moves files here to reject)
└── Done/
    ├── WHATSAPP_123.md          # Processed messages
    └── EMAIL_456.md
```

---

## 🔧 Watcher Behavior

All watchers now follow the **SAME SIMPLE PATTERN**:

### WhatsApp Watcher
```python
# 1. Monitor WhatsApp Web
# 2. Detect unread messages with keywords
# 3. Create action file (NO trusted check!)
# 4. Claude Code decides priority
```

### Gmail Watcher
```python
# 1. Monitor Gmail API
# 2. Detect unread important emails
# 3. Create action file (NO trusted check!)
# 4. Claude Code decides priority
```

### LinkedIn Watcher
```python
# 1. Monitor LinkedIn Messages
# 2. Detect unread threads
# 3. Create action file (NO trusted check!)
# 4. Claude Code decides priority
```

**Same pattern for:** Facebook, Instagram, Twitter

---

## 🎯 Benefits

| Aspect | Old System | New System |
| :--- | :--- | :--- |
| **Maintenance** | Manual contact list updates | Zero maintenance |
| **New Clients** | Blocked if not trusted | Processed normally |
| **Spam Protection** | Whitelist only | Claude Code intelligence |
| **Complexity** | High (watchers check lists) | Low (watchers just monitor) |
| **Missed Opportunities** | Yes (unknown = blocked) | No (all processed) |
| **Security** | Whitelist-based | Content-based + HITL |

---

## 🚀 Quick Test

### Test Scenario 1: Known Contact
```
1. Send WhatsApp: "Meeting tomorrow at 3pm?"
2. Watcher creates: /Needs_Action/WHATSAPP_TEST1.md
3. Claude reads → "Meeting confirmation"
4. Claude auto-responds: "Yes, 3pm works!"
5. Moves to /Done ✓
```

### Test Scenario 2: Unknown Urgent
```
1. Send WhatsApp: "URGENT! Need your help!"
2. Watcher creates: /Needs_Action/WHATSAPP_TEST2.md
3. Claude reads → "Unknown sender + urgent"
4. Claude creates: /Pending_Approval/REVIEW_TEST2.md
5. YOU review → Decide if legitimate
6. Move to /Approved or /Rejected
```

### Test Scenario 3: Obvious Spam
```
1. Send WhatsApp: "You won a prize! Click here!"
2. Watcher creates: /Needs_Action/WHATSAPP_TEST3.md
3. Claude reads → "Spam pattern detected"
4. Claude archives to /Done (no response)
5. Logs for audit ✓
```

---

## 📚 Related Documentation

- [Company Handbook](obsidian_vault/Company_Handbook.md) - Priority rules
- [Architecture](ARCHITECTURE.md) - System design
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Roadmap

---

**Last Updated:** February 23, 2026  
**Status:** ✅ Implemented and Deployed

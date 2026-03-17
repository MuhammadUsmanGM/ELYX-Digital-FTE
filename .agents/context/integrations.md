# ELYX Integration Examples

Complete code examples for all ELYX integrations. Use these as reference when implementing or debugging.

---

## Table of Contents

1. [Gmail Integration](#gmail-integration)
2. [WhatsApp Integration](#whatsapp-integration)
3. [Odoo Accounting](#odoo-accounting)
4. [Social Media Posting](#social-media-posting)
5. [MCP Servers](#mcp-servers)
6. [Vault Operations](#vault-operations)
7. [Task Processing](#task-processing)
8. [Approval Workflow](#approval-workflow)

---

## Gmail Integration

### Setup OAuth

```bash
# Run interactive setup
python config/setup_gmail_auth.py

# Or manually:
# 1. Create project in Google Cloud Console
# 2. Enable Gmail API
# 3. Create OAuth 2.0 credentials
# 4. Download as gmail_credentials.json
# 5. Run authentication flow
```

### Send Email (Direct Python)

```python
from src.response_handlers.email_response_handler import EmailResponseHandler
import asyncio

async def send_email_example():
    handler = EmailResponseHandler()
    
    result = await handler.send_response(
        recipient_identifier="user@example.com",
        content="Hello from ELYX!",
        subject="Test Email",
        response_format="plain"
    )
    
    print(f"Email sent: {result}")
    # Output: {'status': 'sent', 'message_id': '18a3f2b9c4d5e6f7', ...}

# Run
asyncio.run(send_email_example())
```

### Send Email (via MCP)

```python
from src.mcp_client import MCPClient

def send_email_mcp():
    client = MCPClient("email", transport="stdio")
    
    result = client.call("email.send", {
        "to": "user@example.com",
        "subject": "Test Email from MCP",
        "body": "Hello! This was sent via MCP server.",
        "isHtml": False
    })
    
    print(f"MCP Email result: {result}")

send_email_mcp()
```

### Search Emails

```python
from src.mcp_client import MCPClient

def search_emails():
    client = MCPClient("email", transport="stdio")
    
    result = client.call("email.search", {
        "query": "is:unread is:important",
        "maxResults": 10
    })
    
    print(f"Found {result['count']} emails")
    for email in result['emails']:
        print(f"  From: {email['from']} - {email['subject']}")

search_emails()
```

### Read Full Email

```python
from src.mcp_client import MCPClient

def read_email(email_id: str):
    client = MCPClient("email", transport="stdio")
    
    result = client.call("email.read", {
        "email_id": email_id
    })
    
    print(f"From: {result['from']}")
    print(f"Subject: {result['subject']}")
    print(f"Body: {result['body'][:200]}...")

read_email("18a3f2b9c4d5e6f7")
```

---

## WhatsApp Integration

### Setup Session

```bash
# Login to WhatsApp Web (saves session)
python config/setup_sessions.py whatsapp
```

### Send WhatsApp Message (via MCP)

```python
from src.mcp_client import MCPClient

def send_whatsapp():
    client = MCPClient("whatsapp", transport="stdio")
    
    result = client.call("whatsapp.send", {
        "to": "+1234567890",
        "message": "Hello from ELYX!",
        "isGroup": False
    })
    
    print(f"WhatsApp sent: {result}")

send_whatsapp()
```

### Get Recent Chats

```python
from src.mcp_client import MCPClient

def get_recent_chats():
    client = MCPClient("whatsapp", transport="stdio")
    
    result = client.call("whatsapp.get_recent_chats", {})
    
    print(f"Recent chats: {result}")
    for chat in result.get('chats', []):
        print(f"  {chat['name']}: {chat['last_message'][:50]}...")

get_recent_chats()
```

### Monitor WhatsApp (Watcher)

```python
from src.agents.whatsapp_watcher import WhatsAppWatcher

def start_whatsapp_watcher():
    watcher = WhatsAppWatcher(
        vault_path="obsidian_vault",
        session_path="sessions/whatsapp_session"
    )
    
    print("Starting WhatsApp watcher...")
    watcher.run()  # Runs indefinitely, checks every 60s

# start_whatsapp_watcher()
```

---

## Odoo Accounting

### Setup Odoo

```bash
# Login and configure Odoo
python config/setup_sessions.py odoo

# Or use dedicated setup
python setup_odoo_integration.py
```

### Connect to Odoo

```python
from src.services.odoo_service import OdooService

def connect_odoo():
    odoo = OdooService()
    
    if odoo.authenticate():
        print("✅ Odoo connected!")
        print(f"  User: {odoo.username}")
        print(f"  Database: {odoo.db}")
        print(f"  Company: {odoo.company_id}")
    else:
        print("❌ Odoo connection failed")
        print(f"  Check credentials in .env")

connect_odoo()
```

### Create Invoice (Draft)

```python
from src.services.odoo_service import OdooService

def create_invoice():
    odoo = OdooService()
    
    invoice_data = {
        "partner_name": "Client ABC",
        "partner_email": "client@abc.com",
        "lines": [
            {
                "name": "Consulting Services",
                "quantity": 10,
                "price_unit": 150.00,
                "account_id": None  # Use default
            }
        ],
        "invoice_date": "2026-03-01",
        "due_date": "2026-03-31"
    }
    
    result = odoo.create_invoice(invoice_data)
    
    if result['success']:
        print(f"✅ Invoice created: {result['invoice_number']}")
        print(f"   Amount: ${result['amount']}")
        print(f"   Status: {result['status']}")  # draft
    else:
        print(f"❌ Failed: {result['error']}")

create_invoice()
```

### Get Outstanding Invoices

```python
from src.services.odoo_service import OdooService

def get_outstanding_invoices():
    odoo = OdooService()
    
    invoices = odoo.get_outstanding_invoices()
    
    print(f"Outstanding invoices: {len(invoices)}")
    for inv in invoices:
        print(f"  {inv['number']}: ${inv['amount']} - Due: {inv['due_date']}")

get_outstanding_invoices()
```

### Record Payment

```python
from src.services.odoo_service import OdooService

def record_payment_example():
    odoo = OdooService()
    
    payment_data = {
        "invoice_number": "INV-2024-001",
        "amount": 1500.00,
        "payment_date": "2026-03-01",
        "payment_method": "bank_transfer"
    }
    
    result = odoo.register_payment(payment_data)
    
    if result['success']:
        print(f"✅ Payment recorded: ${result['amount']}")
        print(f"   Invoice: {result['invoice_number']}")
        print(f"   Remaining: ${result['remaining']}")
    else:
        print(f"❌ Failed: {result['error']}")

record_payment_example()
```

### Get Revenue Summary

```python
from src.services.odoo_service import OdooService

def get_revenue_summary():
    odoo = OdooService()
    
    summary = odoo.get_revenue_summary(period="month")
    
    print(f"Revenue Summary (This Month)")
    print(f"  Total Invoiced: ${summary['total_invoiced']}")
    print(f"  Total Paid: ${summary['total_paid']}")
    print(f"  Outstanding: ${summary['outstanding']}")
    print(f"  Overdue: ${summary['overdue']}")

get_revenue_summary()
```

---

## Social Media Posting

### Setup Social Sessions

```bash
# Setup all platforms
python config/setup_sessions.py

# Or individual platforms
python config/setup_sessions.py linkedin
python config/setup_sessions.py twitter
python config/setup_sessions.py facebook
python config/setup_sessions.py instagram
```

### Post to LinkedIn

```python
from src.mcp_client import MCPClient

def post_linkedin():
    client = MCPClient("social", transport="stdio")
    
    result = client.call("social.linkedin.post", {
        "content": "🚀 Exciting news! ELYX AI Employee is now operational.\n\n#AI #Automation #ELYX",
        "imageUrl": None  # Optional
    })
    
    print(f"LinkedIn post: {result}")
    # Output: {'success': True, 'post_url': 'https://linkedin.com/posts/...', ...}

post_linkedin()
```

### Post to Twitter/X

```python
from src.mcp_client import MCPClient

def post_twitter():
    client = MCPClient("social", transport="stdio")
    
    result = client.call("social.twitter.post", {
        "content": "🤖 ELYX AI Employee is live! Autonomous 24/7 monitoring of all your business communications.\n\n#AI #Automation",
        "mediaUrls": []  # Optional
    })
    
    print(f"Twitter post: {result}")

post_twitter()
```

### Post to Facebook

```python
from src.mcp_client import MCPClient

def post_facebook():
    client = MCPClient("social", transport="stdio")
    
    result = client.call("social.facebook.post", {
        "content": "ELYX AI Employee - Your autonomous business assistant is now operational!",
        "imageUrl": None
    })
    
    print(f"Facebook post: {result}")

post_facebook()
```

### Post to Instagram

```python
from src.mcp_client import MCPClient

def post_instagram():
    client = MCPClient("social", transport="stdio")
    
    result = client.call("social.instagram.post", {
        "caption": "🤖 ELYX AI Employee\n\n#AI #Automation #Tech",
        "imagePath": "/path/to/image.jpg"  # Required for Instagram
    })
    
    print(f"Instagram post: {result}")

post_instagram()
```

### Schedule Post

```python
from src.mcp_client import MCPClient

def schedule_post():
    client = MCPClient("social", transport="stdio")
    
    result = client.call("social.schedule", {
        "platform": "linkedin",
        "content": "Scheduled post content",
        "scheduledTime": "2026-03-02T09:00:00Z"
    })
    
    print(f"Scheduled: {result}")

schedule_post()
```

---

## MCP Servers

### List Available Tools

```python
from src.mcp_client import MCPClient

def list_tools():
    client = MCPClient("email", transport="stdio")
    
    tools = client.list_tools()
    
    print("Available Email MCP Tools:")
    for tool in tools.get('tools', []):
        print(f"  - {tool['name']}: {tool['description']}")

list_tools()
```

### Batch Operations

```python
from src.mcp_client import MCPClient

def batch_operations():
    client = MCPClient("email", transport="stdio")
    
    calls = [
        ("email.send", {
            "to": "user1@example.com",
            "subject": "Update 1",
            "body": "Message 1"
        }),
        ("email.send", {
            "to": "user2@example.com",
            "subject": "Update 2",
            "body": "Message 2"
        }),
        ("email.send", {
            "to": "user3@example.com",
            "subject": "Update 3",
            "body": "Message 3"
        })
    ]
    
    results = client.batch_call(calls)
    
    for i, result in enumerate(results):
        status = "✅" if result.get('success') else "❌"
        print(f"{status} Email {i+1}: {result}")

batch_operations()
```

### Error Handling

```python
from src.mcp_client import MCPClient

def safe_mcp_call():
    client = MCPClient("email", transport="stdio")
    
    try:
        result = client.call("email.send", {
            "to": "user@example.com",
            "subject": "Test",
            "body": "Message"
        })
        
        if result.get('success'):
            print("✅ Email sent")
        else:
            print(f"❌ Failed: {result.get('error')}")
            
    except FileNotFoundError:
        print("❌ MCP server not found - check path")
    except RuntimeError as e:
        print(f"❌ MCP error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

safe_mcp_call()
```

---

## Vault Operations

### Create Task

```python
from src.utils.vault import create_vault_entry

def create_task():
    filepath = create_vault_entry(
        vault_path="obsidian_vault",
        folder="Needs_Action",
        filename="TASK_123.md",
        content="""
# New Task

This is a new task that needs processing.

## Details
- Priority: High
- Due: 2026-03-05
- Assignee: AI Employee

## Actions
- [ ] Action 1
- [ ] Action 2
""",
        entry_type="task",
        priority="high"
    )
    
    print(f"✅ Task created: {filepath}")

create_task()
```

### Read Task with Frontmatter

```python
from src.utils.vault import VaultEntry

def read_task():
    task = VaultEntry("obsidian_vault/Needs_Action/TASK_123.md")
    
    print(f"Task: {task.filename}")
    print(f"Type: {task.type}")
    print(f"Priority: {task.frontmatter.get('priority')}")
    print(f"Status: {task.status}")
    print(f"Content: {task.content[:200]}...")

read_task()
```

### Move Task to Done

```python
from src.utils.vault import move_file_to_folder

def complete_task():
    result = move_file_to_folder(
        file_path="obsidian_vault/Needs_Action/TASK_123.md",
        target_folder="Done",
        vault_path="obsidian_vault"
    )
    
    print(f"✅ Task moved to Done: {result}")

complete_task()
```

### Get Pending Tasks

```python
from src.utils.vault import get_pending_tasks

def get_pending():
    tasks = get_pending_tasks("obsidian_vault")
    
    print(f"Pending tasks: {len(tasks)}")
    for task in tasks:
        print(f"  - {task.filename} ({task.priority})")

get_pending()
```

### Update Task Status

```python
from src.utils.vault import VaultEntry

def update_status():
    task = VaultEntry("obsidian_vault/Needs_Action/TASK_123.md")
    
    task.update_status("processing")
    
    print(f"✅ Status updated to: {task.status}")

update_status()
```

---

## Task Processing

### Process All Pending Tasks

```python
from src.claude_skills.ai_employee_skills.processor import TaskProcessor

def process_all_tasks():
    processor = TaskProcessor(vault_path="obsidian_vault")
    
    processed = processor.process_pending_tasks()
    
    print(f"✅ Processed {len(processed)} tasks")
    
    # Update dashboard
    processor.update_dashboard()
    print("✅ Dashboard updated")

process_all_tasks()
```

### Process Single Task

```python
from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.utils.vault import VaultEntry

def process_single_task():
    processor = TaskProcessor(vault_path="obsidian_vault")
    task = VaultEntry("obsidian_vault/Needs_Action/EMAIL_123.md")
    
    processor.process_single_task(task)
    
    print(f"✅ Task processed: {task.filename}")

process_single_task()
```

### Generate Plan

```python
from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.utils.vault import VaultEntry

def create_plan():
    processor = TaskProcessor(vault_path="obsidian_vault")
    task = VaultEntry("obsidian_vault/Needs_Action/TASK_123.md")
    
    plan_content = processor._generate_plan_content(task)
    plan_filename = processor._create_plan_file(task, plan_content)
    
    print(f"✅ Plan created: Plans/{plan_filename}")

create_plan()
```

---

## Approval Workflow

### Create Approval Request

```python
from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.utils.vault import VaultEntry

def request_approval():
    processor = TaskProcessor(vault_path="obsidian_vault")
    task = VaultEntry("obsidian_vault/Needs_Action/EMAIL_123.md")
    
    processor.create_approval_request(
        task=task,
        reason="Financial transaction over $100 requires approval"
    )
    
    print("✅ Approval request created in Pending_Approval/")

request_approval()
```

### Process Approved Requests

```python
from src.claude_skills.ai_employee_skills.processor import TaskProcessor

def process_approvals():
    processor = TaskProcessor(vault_path="obsidian_vault")
    
    processor.process_approval_requests()
    
    print("✅ Processed approval requests")

process_approvals()
```

### Manual Approval (Human)

```python
# Human moves file in Finder/Terminal:
# mv obsidian_vault/Pending_Approval/APPROVAL_123.md obsidian_vault/Approved/

# Then AI picks it up automatically
```

### Manual Rejection (Human)

```python
# Human moves file in Finder/Terminal:
# mv obsidian_vault/Pending_Approval/APPROVAL_123.md obsidian_vault/Rejected/

# AI logs rejection automatically
```

---

## Complete Examples

### End-to-End Email Flow

```python
"""
Complete flow: Email arrives → Processed → Response sent → Logged
"""

from src.agents.gmail_watcher import GmailWatcher
from src.claude_skills.ai_employee_skills.processor import TaskProcessor
from src.mcp_client import MCPClient

def complete_email_flow():
    # 1. Watcher detects new email
    watcher = GmailWatcher(vault_path="obsidian_vault")
    new_emails = watcher.check_for_updates()
    
    for email in new_emails:
        action_file = watcher.create_action_file(email)
        print(f"✅ Created action file: {action_file}")
    
    # 2. Process tasks
    processor = TaskProcessor(vault_path="obsidian_vault")
    processed = processor.process_pending_tasks()
    
    print(f"✅ Processed {len(processed)} tasks")
    
    # 3. Update dashboard
    processor.update_dashboard()
    print("✅ Dashboard updated")

complete_email_flow()
```

### CEO Briefing Generation

```python
"""
Generate weekly CEO briefing with revenue data
"""

from src.services.briefing_service import BriefingService
from src.services.odoo_service import OdooService

def generate_ceo_briefing():
    # 1. Get revenue data from Odoo
    odoo = OdooService()
    revenue = odoo.get_revenue_summary(period="week")
    
    # 2. Generate briefing
    briefing = BriefingService(vault_path="obsidian_vault")
    briefing_path = briefing.generate_weekly_briefing(
        revenue_data=revenue,
        include_tasks=True,
        include_bottlenecks=True
    )
    
    print(f"✅ CEO Briefing generated: {briefing_path}")

generate_ceo_briefing()
```

---

## Troubleshooting Examples

### Gmail Authentication Error

```python
# Problem: "Gmail credentials not found"

# Solution 1: Check file exists
from pathlib import Path
print(Path("gmail_credentials.json").exists())

# Solution 2: Re-run auth setup
# python config/setup_gmail_auth.py

# Solution 3: Check environment variable
import os
print(os.getenv('GMAIL_CREDENTIALS_PATH'))
```

### Odoo Connection Error

```python
# Problem: "Odoo authentication failed"

# Solution 1: Check .env variables
from dotenv import load_dotenv
load_dotenv()
import os

print(f"URL: {os.getenv('ODOO_URL')}")
print(f"DB: {os.getenv('ODOO_DB')}")
print(f"Username: {os.getenv('ODOO_USERNAME')}")

# Solution 2: Test connection
from src.services.odoo_service import OdooService
odoo = OdooService()
print(f"Authenticated: {odoo.authenticated}")

# Solution 3: Re-setup Odoo
# python config/setup_sessions.py odoo
```

### MCP Server Not Found

```python
# Problem: "FileNotFoundError: MCP server not found"

# Solution 1: Check server path
from pathlib import Path
server_path = Path("src/mcp-servers/email-mcp/index.js")
print(f"Server exists: {server_path.exists()}")

# Solution 2: Check Node.js installed
import subprocess
result = subprocess.run(["node", "--version"], capture_output=True)
print(f"Node version: {result.stdout.decode()}")

# Solution 3: Use absolute path
from src.mcp_client import MCPClient
client = MCPClient("email", transport="stdio", 
                   server_path="/absolute/path/to/email-mcp/index.js")
```

---

**Last Updated**: 2026-03-01  
**Version**: 2.0  
**Status**: Production-Ready

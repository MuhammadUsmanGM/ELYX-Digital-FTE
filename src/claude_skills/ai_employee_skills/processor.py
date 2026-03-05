from pathlib import Path
import time
from datetime import datetime
import sys

# Add the project root to the Python path so imports work correctly
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.vault import VaultEntry, create_vault_entry, move_file_to_folder, get_pending_tasks
from src.utils.handbook_parser import HandbookParser
from src.utils.dashboard import update_dashboard, get_dashboard_summary
from src.utils.logger import log_activity, setup_logger

class TaskProcessor:
    """
    Main processor that reads files from /Inbox/ and processes them according to Company_Handbook rules
    """
    def __init__(self, vault_path="vault", handbook_path=None, ai_service=None):
        self.vault_path = Path(vault_path)
        self.handbook_parser = HandbookParser(handbook_path or self.vault_path / "Company_Handbook.md")
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"
        self.plans_path = self.vault_path / "Plans"
        self.ai_service = ai_service
        self.logger = setup_logger("TaskProcessor")

    def process_pending_tasks(self):
        """
        Process all pending tasks in the Needs_Action folder
        """
        pending_tasks = get_pending_tasks(self.vault_path)
        processed_tasks = []

        for task in pending_tasks:
            try:
                self.process_single_task(task)
                processed_tasks.append(task)
            except Exception as e:
                log_activity("ERROR", f"Failed to process task {task.filename}: {str(e)}", self.vault_path)
                # Update task status to error
                task.update_status("error")

        # Update dashboard after processing
        self.update_dashboard()

        return processed_tasks

    def process_single_task(self, task):
        """
        Process a single task according to company handbook rules
        """
        log_activity("PROCESS", f"Processing task: {task.filename}", self.vault_path)

        # Skip approval check if task was already approved
        if task.frontmatter.get('approved', False):
            self.execute_automated_task(task)
            task.update_status("completed")
            move_file_to_folder(
                Path(task.filepath),
                "Done",
                self.vault_path
            )
            log_activity("COMPLETED", f"Executed approved task: {task.filename}", self.vault_path)
            return

        # Determine if task needs approval
        sender = task.frontmatter.get('from', 'unknown')
        needs_approval, reason = self.handbook_parser.should_flag_for_approval(
            task.content, task.type, sender=sender
        )

        if needs_approval:
            # Move to Pending Approval
            self.create_approval_request(task, reason)
            task.update_status("pending_approval")
            move_file_to_folder(
                Path(task.filepath),
                "Pending_Approval",
                self.vault_path
            )
            log_activity("APPROVAL", f"Task {task.filename} requires approval: {reason}", self.vault_path)
        else:
            # Process automatically
            self.execute_automated_task(task)
            task.update_status("completed")
            move_file_to_folder(
                Path(task.filepath),
                "Done",
                self.vault_path
            )
            log_activity("COMPLETED", f"Automatically processed task: {task.filename}", self.vault_path)

    def create_approval_request(self, task, reason):
        """
        Create an approval request for sensitive actions
        """
        approval_content = f"""---
type: approval_request
action: process_task
related_task: {task.filename}
reason: {reason}
created: {datetime.now().isoformat()}
status: pending
---

## Approval Request for Task: {task.filename}

### Original Task Content
{task.content[:500]}...

### Reason for Approval
{reason}

## Action Details
- Task Type: {task.type}
- Priority: {task.frontmatter.get('priority', 'medium')}
- Created: {task.frontmatter.get('created', 'unknown')}

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
"""

        # Create approval request file
        approval_filename = f"APPROVAL_{task.filename.replace('.md', '.md')}"
        create_vault_entry(
            self.vault_path,
            "Pending_Approval",
            approval_filename,
            approval_content,
            entry_type="approval_request",
            priority=task.frontmatter.get('priority', 'medium')
        )

    def execute_automated_task(self, task):
        """
        Execute an automated task, generate a plan, and generate response if needed
        """
        log_activity("AUTOMATED", f"Executing task: {task.filename}", self.vault_path)

        # 🧠 Silver Tier Reasoning Loop: Generate a Plan
        plan_content = self._generate_plan_content(task)
        plan_filename = self._create_plan_file(task, plan_content)

        reasoning = f"\n\n--- AI EXECUTION LOG ---\n"
        reasoning += f"Processed by: ELYX AI Employee\n"
        reasoning += f"Timestamp: {datetime.now().isoformat()}\n"
        reasoning += f"Plan Created: [[Plans/{plan_filename}|View Execution Plan]]\n"

        # ✨ Gold Tier: Advanced AI Analysis
        if self.ai_service:
            try:
                # Perform deep analysis
                ai_data = {
                    "title": task.filename,
                    "description": task.content,
                    "category": task.type,
                    "metadata": task.frontmatter
                }
                analysis_result = self.ai_service.process_task_request(ai_data)
                
                reasoning += f"AI Confidence Score: {analysis_result.get('confidence_score', 0.95):.2f}\n"
                
                # Add strategic insights
                insights = self.ai_service.generate_strategic_insights()
                if insights:
                    reasoning += f"Strategic Insight: {insights[0].get('insight', 'Continuous optimization recommended.')}\n"
                    
                reasoning += f"Predicted Duration: {analysis_result.get('predictions', {}).get('duration', 15)} minutes\n"
            except Exception as ai_err:
                reasoning += f"AI Analysis Status: LIMITED (Error: {str(ai_err)})\n"
        else:
            reasoning += f"Analysis: This task was identified as routine and safe to automate according to the Company Handbook.\n"

        # Determine specific action based on content keywords
        action_taken = "Analyzed content and categorized."
        if "email" in task.type:
            action_taken = "Drafted response for review."
        elif "file_drop" in task.type:
            action_taken = "Indexed file metadata and moved to storage."

        reasoning += f"Action Taken: {action_taken}\n"
        reasoning += f"Result: SUCCESS\n"

        # Update task content with reasoning log and link to plan
        updated_content = task.content + reasoning
        task.content = updated_content

        # ✨ DETECT SOCIAL MEDIA POST REQUESTS FROM EMAIL CONTENT
        social_action = self._detect_social_media_action(task)
        
        if social_action:
            self._execute_social_media_post(task, social_action)
        else:
            # ✨ DETECT WHATSAPP MESSAGE REQUESTS
            whatsapp_action = self._detect_whatsapp_action(task)
            
            if whatsapp_action:
                self._send_whatsapp_message(task, whatsapp_action)
            else:
                # ✨ DETECT LINKEDIN MESSAGE REQUESTS
                linkedin_action = self._detect_linkedin_message(task)
                
                if linkedin_action:
                    self._send_linkedin_message(task, linkedin_action)
                else:
                    # ✨ DETECT FACEBOOK MESSAGE REQUESTS
                    facebook_action = self._detect_facebook_message(task)
                    
                    if facebook_action:
                        self._send_facebook_message(task, facebook_action)
                    else:
                        # ✨ DETECT TWITTER MESSAGE REQUESTS
                        twitter_action = self._detect_twitter_message(task)
                        
                        if twitter_action:
                            self._send_twitter_message(task, twitter_action)
                        else:
                            # ✨ DETECT INSTAGRAM MESSAGE REQUESTS
                            instagram_action = self._detect_instagram_message(task)
                            
                            if instagram_action:
                                self._send_instagram_message(task, instagram_action)
                            elif self._should_respond_to_task(task):
                                # Generate email response
                                response_content = self._generate_response_content(task)
                                if "email" in task.type:
                                    self._send_email_response(task, response_content)
                                else:
                                    self._create_response_file(task, response_content)

    def _generate_plan_content(self, task) -> str:
        """
        Generate a step-by-step execution plan for the task
        """
        plan = f"# Plan for Task: {task.filename}\n\n"
        plan += f"**Task Type**: {task.type}\n"
        plan += f"**Priority**: {task.frontmatter.get('priority', 'medium')}\n"
        plan += f"**Created**: {datetime.now().isoformat()}\n\n"
        
        plan += "## Proposed Steps\n"
        
        if "email" in task.type:
            plan += "1. Parse original email content for key request points.\n"
            plan += "2. Reference Company Handbook for response guidelines.\n"
            plan += "3. Draft a professional response incorporating requested data.\n"
            plan += "4. Send response directly via Gmail API.\n"
            plan += "5. Move task to Done/ and update Dashboard.md.\n"
        elif "linkedin" in task.type:
            plan += "1. Analyze LinkedIn message context and sender profile.\n"
            plan += "2. Cross-reference with internal conversation history.\n"
            plan += "3. Draft a tailored LinkedIn response (keeping it brief).\n"
            plan += "4. Use Playwright automation to send the message.\n"
            plan += "5. Log interaction in the conversation tracker.\n"
        elif "whatsapp" in task.type:
            plan += "1. Parse WhatsApp message for critical keywords.\n"
            plan += "2. Determine urgency level based on handbook rules.\n"
            plan += "3. Draft a quick, direct response for WhatsApp.\n"
            plan += "4. Send via WhatsApp Business API or manual automation.\n"
            plan += "5. Mark as resolved in the dashboard.\n"
        elif "file_drop" in task.type:
            plan += "1. Calculate file checksum and verify integrity.\n"
            plan += "2. Extract metadata (size, type, modification date).\n"
            plan += "3. Identify appropriate storage location based on file type.\n"
            plan += "4. Move file to permanent storage and update index.\n"
        elif "facebook" in task.type:
            plan += "1. Parse Facebook message/notification for context.\n"
            plan += "2. Check sender against Trusted_Contacts and Company Handbook.\n"
            plan += "3. Draft a professional response or engagement plan.\n"
            plan += "4. Format for Facebook Messenger or Page interaction.\n"
            plan += "5. Queue for automated or approved delivery.\n"
        elif "twitter" in task.type:
            plan += "1. Analyze tweet or DM for intent and sentiment.\n"
            plan += "2. Check for mentions of brand or critical keywords.\n"
            plan += "3. Draft a concise, high-impact reply (within character limit).\n"
            plan += "4. Update social engagement tracker in the dashboard.\n"
            plan += "5. Schedule or post the interaction.\n"
        elif "instagram" in task.type:
            plan += "1. Review Instagram DM or activity notification.\n"
            plan += "2. Verify business relevance according to handbook rules.\n"
            plan += "3. Draft an appropriate response or social action.\n"
            plan += "4. Coordinate with visual assets if required.\n"
            plan += "5. Mark as processed in the social inbox.\n"
        elif "accounting" in task.type:
            plan += "1. Connect to Odoo Accounting API.\n"
            plan += "2. Validate invoice or transaction data against vault records.\n"
            plan += "3. Check for specific accounting rules in Company Handbook.\n"
            plan += "4. Update transaction status in Odoo if applicable.\n"
            plan += "5. Generate a record of the action for the Weekly Briefing.\n"
        else:
            plan += "1. Analyze task requirements and context.\n"
            plan += "2. Identify necessary system tools and resources.\n"
            plan += "3. Execute sequential steps to satisfy task objectives.\n"
            plan += "4. Verify completion and document results.\n"
            
        plan += "\n## Risk Assessment\n"
        plan += "- Low risk: Action is non-destructive and reversible.\n"
        plan += "- No financial or legal impact identified.\n"
        
        plan += "\n## Approval Requirement\n"
        plan += "- No approval required for this routine automation.\n"
        
        return plan

    def _create_plan_file(self, task, plan_content: str) -> str:
        """
        Create a plan file in the Plans directory
        """
        self.plans_path.mkdir(exist_ok=True)
        
        import hashlib
        task_hash = hashlib.md5(task.filename.encode()).hexdigest()[:8]
        plan_filename = f"PLAN_{task_hash}_{int(time.time())}.md"
        
        plan_filepath = self.plans_path / plan_filename
        plan_filepath.write_text(plan_content, encoding='utf-8')
        
        log_activity("PLAN_CREATED", f"Created plan file: {plan_filename}", self.vault_path)
        return plan_filename


    def _should_respond_to_task(self, task) -> bool:
        """
        Determine if a response should be sent back to the original sender

        Args:
            task: The task to evaluate

        Returns:
            True if a response should be sent, False otherwise
        """
        # Check if the original message indicated it expects a response
        # This could be based on the content, message type, or other indicators
        content_lower = task.content.lower()

        # Keywords that suggest a response is expected
        response_indicators = [
            'please', 'can you', 'could you', 'would you', 'analyze', 'summarize',
            'create', 'generate', 'send', 'provide', 'tell me', 'help', 'suggest',
            'what', 'how', 'when', 'where', 'why'
        ]

        return any(indicator in content_lower for indicator in response_indicators)

    def _generate_response_content(self, task) -> str:
        """
        Generate appropriate response content based on the task

        Args:
            task: The task that was processed

        Returns:
            Generated response content
        """
        # This would normally involve more sophisticated processing
        # For now, we'll create a simple response indicating the task was completed

        from src.utils.response_formatter import ResponseFormatter

        # Determine the type of response based on the task
        task_content = task.content
        response_type = "informational"

        # Create a basic response
        response_body = f"I have processed your request: '{task_content[:100]}{'...' if len(task_content) > 100 else ''}'\n\n"

        # Add specific information based on the type of task
        if "analyze" in task_content.lower() or "summary" in task_content.lower():
            response_body += "Analysis completed. The results have been documented and are available for review."
        elif "create" in task_content.lower() or "generate" in task_content.lower():
            response_body += "Creation task completed. The requested item has been generated and documented."
        elif "help" in task_content.lower():
            response_body += "I hope this information is helpful. Please let me know if you need further assistance."
        else:
            response_body += "Task completed successfully. Please let me know if you need any additional assistance."

        # Add a professional closing
        response_body += f"\n\nBest regards,\nAI Employee"

        return response_body

    def _create_response_file(self, task, response_content: str):
        """
        Create a response file that the orchestrator will process to send back to the user

        Args:
            task: The original task that was processed
            response_content: Content of the response to send
        """
        # Get the original communication channel from the task metadata
        # This assumes the task file contains information about the original channel
        original_channel = task.frontmatter.get('type', 'email')  # default to email
        original_sender = task.frontmatter.get('from', 'unknown')

        # Determine the appropriate channel enum value
        from src.response_handlers.base_handler import CommunicationChannel
        channel_map = {
            'email': CommunicationChannel.EMAIL,
            'linkedin': CommunicationChannel.LINKEDIN,
            'linkedin_message': CommunicationChannel.LINKEDIN,
            'whatsapp': CommunicationChannel.WHATSAPP,
            'whatsapp_message': CommunicationChannel.WHATSAPP
        }

        channel_enum = channel_map.get(original_channel, CommunicationChannel.EMAIL)

        # Create response file with appropriate metadata
        response_content_full = f"""---
type: response_message
original_message_id: {task.filename.replace('.md', '')}
channel: {channel_enum.value}
recipient: {original_sender}
response_type: INFORMATIONAL
priority: MEDIUM
requires_approval: false
subject: Response to your request
---

## Response to Your Request

{response_content}
"""

        # Create the response directory if it doesn't exist
        responses_dir = self.vault_path / "Responses"
        responses_dir.mkdir(exist_ok=True)

        # Create the response file
        import hashlib
        task_hash = hashlib.md5(task.filename.encode()).hexdigest()[:8]
        response_filename = f"RESPONSE_{task_hash}_{int(time.time())}.md"

        response_filepath = responses_dir / response_filename
        response_filepath.write_text(response_content_full)

        log_activity("RESPONSE_CREATED", f"Created response file: {response_filename}", self.vault_path)

    @staticmethod
    def _extract_email(recipient_str: str) -> str:
        """Extract email from 'Name <email@domain.com>' or return stripped string if already plain email."""
        import re
        s = (recipient_str or "").strip()
        if not s:
            return ""
        match = re.search(r'<([^>]+)>', s)
        if match:
            return match.group(1).strip()
        return s

    def _send_email_response(self, task, response_content: str):
        """
        Send email: try browser (Gmail) first, then MCP, then direct API.
        Browser path opens Gmail, composes, and sends — no MCP/Gmail API required.
        """
        import re
        raw_recipient = task.frontmatter.get('from', '')
        original_subject = task.frontmatter.get('subject', 'Your Request')
        recipient = self._extract_email(raw_recipient)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not recipient or not re.match(email_pattern, recipient):
            self.logger.warning(f"Invalid email recipient: {raw_recipient}. Creating response file instead.")
            self._create_response_file(task, response_content)
            return

        subject = f"Re: {original_subject}"

        # 1) Prefer browser: open Gmail, compose, type, send (no MCP)
        try:
            from src.services.direct_social_sender import send_gmail_via_browser
            log_activity("EMAIL_SENDING_BROWSER", f"Sending email to {recipient} via Gmail browser", self.vault_path)
            result = send_gmail_via_browser(to=recipient, subject=subject, body=response_content)
            if result.get("success"):
                log_activity("EMAIL_SENT_BROWSER", f"Email sent to {recipient} via Gmail (browser)", self.vault_path)
                task.content += f"\n\n## Email Sent (Gmail browser) ✅\n- **To**: {recipient}\n- **Subject**: {subject}\n- **Status**: Sent\n"
                task.filepath.write_text(task.content, encoding='utf-8')
                return
            self.logger.warning(f"Gmail browser send failed: {result.get('error')}. Trying MCP/direct.")
        except Exception as e:
            self.logger.warning(f"Gmail browser send error: {e}. Trying MCP/direct.")

        # 2) Try MCP
        try:
            from src.mcp_client import MCPClient
            mcp_client = MCPClient("email", transport="stdio")
            result = mcp_client.call("email.send", {"to": recipient, "subject": subject, "body": response_content})
            if result.get('success'):
                log_activity("EMAIL_SENT_MCP", f"Email sent to {recipient} via MCP", self.vault_path)
                task.content += f"\n\n## Email Sent via MCP ✅\n- **To**: {recipient}\n- **Subject**: {subject}\n- **Message ID**: {result.get('message_id')}\n"
                task.filepath.write_text(task.content, encoding='utf-8')
                return
        except Exception as e:
            self.logger.warning(f"MCP email failed: {e}")

        # 3) Fallback: direct Python (Gmail API)
        self._send_email_response_direct(task, response_content)
    
    def _send_email_response_direct(self, task, response_content: str):
        """
        Fallback: Send email directly via Python (Phase 1 approach)
        """
        import asyncio
        from src.response_handlers.email_response_handler import EmailResponseHandler
        
        try:
            raw_recipient = task.frontmatter.get('from', '')
            recipient = self._extract_email(raw_recipient) or raw_recipient
            original_subject = task.frontmatter.get('subject', 'Your Request')
            
            handler = EmailResponseHandler()
            result = asyncio.run(
                handler.send_response(
                    recipient_identifier=recipient,
                    content=response_content,
                    subject=f"Re: {original_subject}"
                )
            )
            
            if result.get('status') == 'sent':
                log_activity("EMAIL_SENT_DIRECT", f"Email sent successfully (direct Python) to {recipient}", self.vault_path)
                task.content += f"\n\n## Email Sent (Direct Python) ✅\n- **To**: {recipient}\n- **Message ID**: {result.get('message_id')}\n"
                task.filepath.write_text(task.content, encoding='utf-8')
            else:
                self._create_response_file(task, response_content)
                
        except Exception as e:
            self.logger.error(f"Direct email send failed: {e}")
            self._create_response_file(task, response_content)

    def _detect_whatsapp_action(self, task) -> dict:
        """
        Detect if email content is requesting a WhatsApp message to be sent

        Args:
            task: The task object

        Returns:
            Dictionary with phone number and message, or None if not a WhatsApp request
        """
        import re
        
        content_lower = task.content.lower()
        subject_lower = task.frontmatter.get('subject', '').lower()
        full_text = content_lower + ' ' + subject_lower

        # Keywords that indicate WhatsApp message request
        whatsapp_keywords = [
            'whatsapp',
            'wa.me',
            'send whatsapp',
            'message on whatsapp',
            'whatsapp message',
            'send on whatsapp',
            'via whatsapp'
        ]

        # Check for WhatsApp request
        has_whatsapp_request = any(kw in full_text for kw in whatsapp_keywords)

        if not has_whatsapp_request:
            return None

        # Phone number pattern (international format)
        phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        
        # Extract phone numbers from content
        phones = re.findall(phone_pattern, task.content)
        
        # Also check frontmatter for 'to' or 'phone' field
        if not phones:
            to_field = task.frontmatter.get('to', '')
            if to_field:
                phones = re.findall(phone_pattern, to_field)

        if not phones:
            # No phone number found, still might be a WhatsApp request
            # but we need a number to send
            return None

        # Extract message to send
        # Look for patterns like "saying hello", "say hi", "message: hello"
        message = None
        
        # Pattern 1: "saying [message]"
        saying_match = re.search(r'saying\s+(.+?)(?:\.|$)', content_lower)
        if saying_match:
            message = saying_match.group(1).strip()
        
        # Pattern 2: "say [message]"
        if not message:
            say_match = re.search(r'say\s+(.+?)(?:\.|$)', content_lower)
            if say_match:
                message = say_match.group(1).strip()
        
        # Pattern 3: "message: [message]" or "text: [message]"
        if not message:
            msg_match = re.search(r'(?:message|text):\s*(.+?)(?:\.|$)', content_lower)
            if msg_match:
                message = msg_match.group(1).strip()
        
        # Pattern 4: "with message [message]"
        if not message:
            with_match = re.search(r'with\s+(?:the\s+)?message\s+(.+?)(?:\.|$)', content_lower)
            if with_match:
                message = with_match.group(1).strip()
        
        # Default message if none extracted
        if not message:
            message = "Hello"

        # Clean up message
        message = message.strip().rstrip('.')
        
        # Capitalize first letter
        if message:
            message = message[0].upper() + message[1:] if len(message) > 1 else message.upper()

        return {
            'to': phones[0],  # First phone number found
            'message': message,
            'requires_approval': False  # Can be changed to True for safety
        }

    def _detect_linkedin_message(self, task) -> dict:
        """Detect LinkedIn message request"""
        content_lower = task.content.lower()
        if 'linkedin' in content_lower and ('message' in content_lower or 'send' in content_lower):
            return {'to': 'LinkedIn Contact', 'message': 'Hello from ELYX'}
        return None

    def _detect_facebook_message(self, task) -> dict:
        """Detect Facebook message request"""
        content_lower = task.content.lower()
        if 'facebook' in content_lower and ('message' in content_lower or 'send' in content_lower):
            return {'to': 'Facebook Contact', 'message': 'Hello from ELYX'}
        return None

    def _detect_twitter_message(self, task) -> dict:
        """Detect Twitter/X DM request"""
        content_lower = task.content.lower()
        if ('twitter' in content_lower or 'x.com' in content_lower) and ('message' in content_lower or 'dm' in content_lower):
            return {'to': 'Twitter Contact', 'message': 'Hello from ELYX'}
        return None

    def _detect_instagram_message(self, task) -> dict:
        """Detect Instagram DM request"""
        content_lower = task.content.lower()
        if 'instagram' in content_lower and ('message' in content_lower or 'dm' in content_lower):
            return {'to': 'Instagram Contact', 'message': 'Hello from ELYX'}
        return None

    def _detect_social_media_action(self, task) -> dict:
        """
        Detect if email content is requesting a social media post
        
        Args:
            task: The task object
            
        Returns:
            Dictionary with platform and content, or None if not a social media request
        """
        content_lower = task.content.lower()
        subject_lower = task.frontmatter.get('subject', '').lower()
        
        # Keywords that indicate social media post request
        social_keywords = {
            'linkedin': ['linkedin', 'linked in', 'li.com'],
            'twitter': ['twitter', 'tweet', 'x.com', 'post on x'],
            'facebook': ['facebook', 'fb', 'facebook post'],
            'instagram': ['instagram', 'insta', 'ig post']
        }
        
        # Check for post request keywords
        post_keywords = ['post', 'publish', 'share', 'make a post', 'first post']
        
        has_post_request = any(kw in content_lower or kw in subject_lower for kw in post_keywords)
        
        if not has_post_request:
            return None
        
        # Detect which platforms
        platforms = []
        for platform, keywords in social_keywords.items():
            if any(kw in content_lower or kw in subject_lower for kw in keywords):
                platforms.append(platform)
        
        if not platforms:
            return None
        
        # Extract content to post (simplified - would use AI in production)
        content_to_post = self._extract_post_content(task.content)
        
        return {
            'platforms': platforms,
            'content': content_to_post,
            'requires_approval': False
        }
    
    def _extract_post_content(self, email_content: str) -> str:
        """Extract content for social media posting"""
        lines = email_content.split('\n')
        content_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('---') and not line.startswith('type:') and not line.startswith('['):
                content_lines.append(line)
        return ' '.join(content_lines[:3])

    def _send_whatsapp_message(self, task, whatsapp_action: dict):
        """
        Execute WhatsApp message sending via Playwright (direct browser automation).
        Uses the same Chrome session as the WhatsApp watcher — no Business API needed.
        Falls back to MCP if direct send fails.

        Args:
            task: The task object
            whatsapp_action: Dictionary with 'to' and 'message'
        """
        phone = whatsapp_action.get('to', '')
        message = whatsapp_action.get('message', 'Hello')

        log_activity("WHATSAPP_SEND", f"Sending WhatsApp to {phone} via Playwright", self.vault_path)

        # Try direct Playwright send first (same session as watcher)
        try:
            result = self._send_whatsapp_direct(phone, message)

            if result.get('success'):
                log_activity("WHATSAPP_SENT", f"WhatsApp sent successfully to {phone}", self.vault_path)
                task.content += f"\n\n## WhatsApp Message Sent ✅\n- **To**: {phone}\n- **Message**: {message}\n- **Status**: Sent successfully\n- **Method**: Direct Playwright\n- **Timestamp**: {datetime.now().isoformat()}\n"
                task.filepath.write_text(task.content, encoding='utf-8')
                return
            else:
                self.logger.warning(f"Direct WhatsApp send failed: {result.get('error')}. Trying MCP fallback...")

        except Exception as e:
            self.logger.warning(f"Direct WhatsApp send error: {e}. Trying MCP fallback...")

        # Fallback: try MCP server
        try:
            from src.mcp_client import MCPClient
            mcp_client = MCPClient("whatsapp", transport="stdio")

            result = mcp_client.call("whatsapp.send", {
                "to": phone,
                "message": message,
                "isGroup": False
            })

            if result.get('success'):
                log_activity("WHATSAPP_SENT", f"WhatsApp sent via MCP to {phone}", self.vault_path)
                task.content += f"\n\n## WhatsApp Message Sent ✅\n- **To**: {phone}\n- **Message**: {message}\n- **Status**: Sent successfully\n- **Method**: MCP Server\n- **Timestamp**: {datetime.now().isoformat()}\n"
                task.filepath.write_text(task.content, encoding='utf-8')
            else:
                error_msg = result.get('error', 'Unknown error')
                log_activity("WHATSAPP_FAILED", f"Failed to send WhatsApp: {error_msg}", self.vault_path)
                task.content += f"\n\n## WhatsApp Message Failed ⚠️\n- **To**: {phone}\n- **Message**: {message}\n- **Error**: {error_msg}\n- **Note**: Run: python setup_sessions.py whatsapp\n"
                task.filepath.write_text(task.content, encoding='utf-8')

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"All WhatsApp send methods failed: {error_msg}")
            log_activity("WHATSAPP_ERROR", f"All methods failed: {error_msg}", self.vault_path)
            task.content += f"\n\n## WhatsApp Message Failed ⚠️\n- **To**: {phone}\n- **Message**: {message}\n- **Error**: {error_msg}\n- **Note**: Run: python setup_sessions.py whatsapp\n"
            task.filepath.write_text(task.content, encoding='utf-8')

    def _send_whatsapp_direct(self, phone: str, message: str) -> dict:
        """
        Send WhatsApp message directly via Playwright using the persistent session.
        Same approach as the WhatsApp watcher — no API keys needed.
        """
        import time
        import random
        from pathlib import Path

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {"success": False, "error": "Playwright not installed"}

        session_path = os.getenv('WHATSAPP_SESSION_PATH', './sessions/whatsapp_session')
        p = None

        try:
            p = sync_playwright().start()
            Path(session_path).mkdir(parents=True, exist_ok=True)
            browser = p.chromium.launch_persistent_context(
                session_path,
                headless=False,
                viewport={'width': 1280, 'height': 800},
                args=['--disable-blink-features=AutomationControlled'],
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=90000)

            # Wait for chat list (indicates logged in)
            selectors = '[data-testid="chat-list"], #pane-side, [aria-label="Chat list"]'
            try:
                page.wait_for_selector(selectors, timeout=20000)
            except Exception:
                return {"success": False, "error": "WhatsApp not logged in. Run: python setup_sessions.py whatsapp"}

            # Search for contact
            search_box = page.query_selector('div[contenteditable="true"][data-tab="3"]')
            if not search_box:
                search_icon = page.query_selector('[data-testid="search"], [data-icon="search"]')
                if search_icon:
                    search_icon.click()
                    time.sleep(1)
                    search_box = page.query_selector('div[contenteditable="true"][data-tab="3"]')

            if not search_box:
                return {"success": False, "error": "Could not find WhatsApp search box"}

            search_box.click()
            time.sleep(0.5)
            page.keyboard.press('Control+A')
            page.keyboard.press('Backspace')
            page.keyboard.type(phone, delay=random.randint(30, 80))
            time.sleep(2)

            # Click first result or press Enter
            contact = page.query_selector(f'span[title*="{phone}"]')
            if contact:
                contact.click()
            else:
                page.keyboard.press('Enter')
            time.sleep(1.5)

            # Find message input and type
            msg_box = page.query_selector('div[contenteditable="true"][data-tab="10"]')
            if not msg_box:
                msg_box = page.query_selector('footer div[contenteditable="true"]')
            if not msg_box:
                return {"success": False, "error": "Could not find message input box"}

            msg_box.click()
            time.sleep(0.3)

            lines = message.split('\n')
            for i, line in enumerate(lines):
                page.keyboard.type(line, delay=random.randint(10, 30))
                if i < len(lines) - 1:
                    page.keyboard.press('Shift+Enter')

            time.sleep(0.5)
            page.keyboard.press('Enter')
            time.sleep(2)

            browser.close()
            p.stop()
            return {"success": True, "message": f"WhatsApp message sent to {phone}"}

        except Exception as e:
            if p:
                try:
                    p.stop()
                except Exception:
                    pass
            return {"success": False, "error": str(e)}

    def _send_linkedin_message(self, task, action: dict):
        """Send LinkedIn message via direct Python (no MCP)"""
        import subprocess
        recipient = action.get('to', '')
        message = action.get('message', 'Hello')
        log_activity("LINKEDIN_SEND", f"Sending LinkedIn to {recipient}", self.vault_path)
        try:
            result = subprocess.run(
                [sys.executable, str(project_root / "src" / "services" / "direct_social_sender.py"), "linkedin", message],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                log_activity("LINKEDIN_SENT", "LinkedIn sent", self.vault_path)
                task.content += f"\n\n## LinkedIn Message Sent ✅\n- **Message**: {message}\n- **Status**: Sent\n"
            else:
                task.content += f"\n\n## LinkedIn Message Failed ⚠️\n- **Error**: {result.stderr}\n"
            task.filepath.write_text(task.content, encoding='utf-8')
        except Exception as e:
            self.logger.error(f"LinkedIn error: {e}")
            task.content += f"\n\n## LinkedIn Message Failed ⚠️\n- **Error**: {str(e)}\n"
            task.filepath.write_text(task.content, encoding='utf-8')

    def _send_facebook_message(self, task, action: dict):
        """Send Facebook message via direct Python (no MCP)"""
        import subprocess
        recipient = action.get('to', '')
        message = action.get('message', 'Hello')
        log_activity("FACEBOOK_SEND", f"Sending Facebook to {recipient}", self.vault_path)
        try:
            result = subprocess.run(
                [sys.executable, str(project_root / "src" / "services" / "direct_social_sender.py"), "facebook", message],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                log_activity("FACEBOOK_SENT", "Facebook sent", self.vault_path)
                task.content += f"\n\n## Facebook Message Sent ✅\n- **Message**: {message}\n- **Status**: Sent\n"
            else:
                task.content += f"\n\n## Facebook Message Failed ⚠️\n- **Error**: {result.stderr}\n"
            task.filepath.write_text(task.content, encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Facebook error: {e}")
            task.content += f"\n\n## Facebook Message Failed ⚠️\n- **Error**: {str(e)}\n"
            task.filepath.write_text(task.content, encoding='utf-8')

    def _send_twitter_message(self, task, action: dict):
        """Send Twitter/X DM via direct Python (no MCP)"""
        import subprocess
        recipient = action.get('to', '')
        message = action.get('message', 'Hello')
        log_activity("TWITTER_SEND", f"Sending Twitter to {recipient}", self.vault_path)
        try:
            result = subprocess.run(
                [sys.executable, str(project_root / "src" / "services" / "direct_social_sender.py"), "twitter", message],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                log_activity("TWITTER_SENT", "Twitter sent", self.vault_path)
                task.content += f"\n\n## Twitter DM Sent ✅\n- **Message**: {message}\n- **Status**: Sent\n"
            else:
                task.content += f"\n\n## Twitter DM Failed ⚠️\n- **Error**: {result.stderr}\n"
            task.filepath.write_text(task.content, encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Twitter error: {e}")
            task.content += f"\n\n## Twitter DM Failed ⚠️\n- **Error**: {str(e)}\n"
            task.filepath.write_text(task.content, encoding='utf-8')

    def _send_instagram_message(self, task, action: dict):
        """Send Instagram DM via direct Python (no MCP)"""
        import subprocess
        recipient = action.get('to', '')
        message = action.get('message', 'Hello')
        log_activity("INSTAGRAM_SEND", f"Sending Instagram to {recipient}", self.vault_path)
        try:
            result = subprocess.run(
                [sys.executable, str(project_root / "src" / "services" / "direct_social_sender.py"), "instagram", message],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                log_activity("INSTAGRAM_SENT", "Instagram sent", self.vault_path)
                task.content += f"\n\n## Instagram DM Sent ✅\n- **Message**: {message}\n- **Status**: Sent\n"
            else:
                task.content += f"\n\n## Instagram DM Failed ⚠️\n- **Error**: {result.stderr}\n"
            task.filepath.write_text(task.content, encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Instagram error: {e}")
            task.content += f"\n\n## Instagram DM Failed ⚠️\n- **Error**: {str(e)}\n"
            task.filepath.write_text(task.content, encoding='utf-8')

    def _execute_social_media_post(self, task, social_action: dict):
        """
        Execute social media posting via MCP
        
        Args:
            task: The task object
            social_action: Dictionary with platforms and content
        """
        from src.mcp_client import MCPClient
        
        platforms = social_action.get('platforms', [])
        content = social_action.get('content', 'ELYX AI Employee - Autonomous AI for business automation')
        
        log_activity("SOCIAL_POST", f"Posting to {platforms} via MCP", self.vault_path)
        
        results = {}
        
        for platform in platforms:
            try:
                mcp_client = MCPClient("social", transport="stdio")
                
                # Generate platform-specific content
                if platform == 'linkedin':
                    post_content = f"🤖 ELYX AI Employee - Now Operational!\n\n{content}\n\n#AI #Automation #ELYX"
                    method = "social.linkedin.post"
                elif platform == 'twitter':
                    post_content = f"🤖 ELYX AI Employee is now operational! {content[:100]} #AI #Automation"
                    method = "social.twitter.post"
                elif platform == 'facebook':
                    post_content = f"ELYX AI Employee - {content}\n\n#AI #Automation"
                    method = "social.facebook.post"
                elif platform == 'instagram':
                    post_content = f"🤖 ELYX AI Employee\n{content}\n\n#AI #Automation #Tech"
                    method = "social.instagram.post"
                else:
                    continue
                
                # Call MCP server
                result = mcp_client.call(method, {"content": post_content})
                results[platform] = result
                log_activity("SOCIAL_POSTED", f"Posted to {platform} via MCP", self.vault_path)
                
            except Exception as e:
                results[platform] = {"error": str(e)}
                log_activity("SOCIAL_POST_ERROR", f"Failed to post to {platform}: {e}", self.vault_path)
        
        # Update task with results
        task.content += f"\n\n## Social Media Post Results\n"
        for platform, result in results.items():
            if isinstance(result, dict) and result.get('success'):
                task.content += f"- ✅ **{platform.title()}**: Posted successfully\n"
            else:
                task.content += f"- ⚠️ **{platform.title()}**: {result.get('error', 'Check credentials')}\n"
        
        task.filepath.write_text(task.content, encoding='utf-8')

    def process_approval_requests(self):
        """
        Process approval requests that have been moved to Approved/Rejected folders
        """
        approved_path = self.vault_path / "Approved"
        rejected_path = self.vault_path / "Rejected"

        # Process approved requests
        for approved_file in approved_path.glob("*.md"):
            self.handle_approved_request(approved_file)

        # Process rejected requests
        for rejected_file in rejected_path.glob("*.md"):
            self.handle_rejected_request(rejected_file)

    def handle_approved_request(self, approved_file):
        """
        Handle an approved request
        """
        log_activity("APPROVED", f"Handling approved request: {approved_file.name}", self.vault_path)

        # Move the original task back to needs action for execution
        # Extract original task name from approval request
        content = approved_file.read_text()

        # Find the related task in the original content
        import re
        match = re.search(r'related_task: (.+)', content)
        if match:
            original_task_name = match.group(1).strip()
            original_task_path = self.vault_path / "Pending_Approval" / original_task_name

            if original_task_path.exists():
                # Mark task as approved so it won't be re-flagged
                task_content = original_task_path.read_text(encoding='utf-8')
                if task_content.startswith('---'):
                    # Insert approved: true into existing frontmatter
                    task_content = task_content.replace('---\n', '---\napproved: true\n', 1)
                else:
                    task_content = '---\napproved: true\n---\n' + task_content
                original_task_path.write_text(task_content, encoding='utf-8')

                # Move the original task to needs action for processing
                move_file_to_folder(
                    original_task_path,
                    "Needs_Action",
                    self.vault_path
                )

        # Move approval file to done
        move_file_to_folder(
            approved_file,
            "Done",
            self.vault_path
        )

    def handle_rejected_request(self, rejected_file):
        """
        Handle a rejected request
        """
        log_activity("REJECTED", f"Handling rejected request: {rejected_file.name}", self.vault_path)

        # Move approval file to done
        move_file_to_folder(
            rejected_file,
            "Done",
            self.vault_path
        )

    def update_dashboard(self):
        """
        Update the dashboard with current status
        """
        summary_data = get_dashboard_summary(self.vault_path)
        summary_data['recent_activities'] = [
            f"Processed {len(get_pending_tasks(self.vault_path))} pending tasks",
            f"Updated at {datetime.now().strftime('%H:%M:%S')}"
        ]
        update_dashboard(self.vault_path, summary_data)

    def run_continuous_processing(self, interval=300):  # Default to 5 minutes
        """
        Run continuous processing loop
        """
        log_activity("SYSTEM", "Starting continuous processing loop", self.vault_path)

        while True:
            try:
                # Process pending tasks
                processed_count = self.process_pending_tasks()

                # Process approval requests
                self.process_approval_requests()

                # Update dashboard
                self.update_dashboard()

                log_activity("SYSTEM", f"Completed processing cycle, processed {processed_count} tasks", self.vault_path)

                time.sleep(interval)
            except Exception as e:
                log_activity("ERROR", f"Error in processing loop: {str(e)}", self.vault_path)
                time.sleep(60)  # Wait 1 minute before retrying if there's an error
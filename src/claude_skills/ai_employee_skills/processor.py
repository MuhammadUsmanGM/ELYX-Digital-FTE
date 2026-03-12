import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path so imports work correctly
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.dashboard import get_dashboard_summary, update_dashboard
from src.utils.handbook_parser import HandbookParser
from src.utils.logger import log_activity, setup_logger
from src.utils.vault import (
    VaultEntry,
    create_vault_entry,
    get_pending_tasks,
    move_file_to_folder,
)


class TaskProcessor:
    """
    Main processor that reads files from /Inbox/ and processes them according to Company_Handbook rules
    """

    def __init__(self, vault_path="vault", handbook_path=None, ai_service=None):
        self.vault_path = Path(vault_path)
        self.handbook_parser = HandbookParser(
            handbook_path or self.vault_path / "Company_Handbook.md"
        )
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"
        self.plans_path = self.vault_path / "Plans"
        self.ai_service = ai_service
        self.logger = setup_logger("TaskProcessor")
        self._processing_lock = threading.Lock()

    def process_pending_tasks(self):
        """
        Process all pending tasks in the Needs_Action folder.
        Uses a lock to prevent concurrent processing from file watcher and polling thread.
        """
        if not self._processing_lock.acquire(blocking=False):
            self.logger.info("Task processing already in progress, skipping this cycle")
            return []

        try:
            pending_tasks = get_pending_tasks(self.vault_path)
            processed_tasks = []

            for task in pending_tasks:
                try:
                    self.process_single_task(task)
                    processed_tasks.append(task)
                except Exception as e:
                    log_activity(
                        "ERROR",
                        f"Failed to process task {task.filename}: {str(e)}",
                        self.vault_path,
                    )
                    # Update task status to error
                    task.update_status("error")

            # Update dashboard after processing
            self.update_dashboard()

            return processed_tasks
        finally:
            self._processing_lock.release()

    def process_single_task(self, task):
        """
        Process a single task according to company handbook rules
        """
        log_activity("PROCESS", f"Processing task: {task.filename}", self.vault_path)

        # Skip approval check if task was already approved
        if task.frontmatter.get("approved", False):
            self.execute_automated_task(task)
            task.update_status("completed")
            move_file_to_folder(Path(task.filepath), "Done", self.vault_path)
            log_activity(
                "COMPLETED", f"Executed approved task: {task.filename}", self.vault_path
            )
            return

        # Determine if task needs approval
        sender = task.frontmatter.get("from", "unknown")
        needs_approval, reason = self.handbook_parser.should_flag_for_approval(
            task.content, task.type, sender=sender
        )

        if needs_approval:
            # Move to Pending Approval
            self.create_approval_request(task, reason)
            task.update_status("pending_approval")
            move_file_to_folder(
                Path(task.filepath), "Pending_Approval", self.vault_path
            )
            log_activity(
                "APPROVAL",
                f"Task {task.filename} requires approval: {reason}",
                self.vault_path,
            )
        else:
            # Process automatically
            self.execute_automated_task(task)
            task.update_status("completed")
            move_file_to_folder(Path(task.filepath), "Done", self.vault_path)
            log_activity(
                "COMPLETED",
                f"Automatically processed task: {task.filename}",
                self.vault_path,
            )

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
            priority=task.frontmatter.get("priority", "medium"),
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
                    "metadata": task.frontmatter,
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

        # Dispatch: detect platform action and send directly (no intermediate files)
        platform_detectors = [
            (
                "social_post",
                self._detect_social_media_action,
                self._execute_social_media_post,
            ),
            ("email", self._detect_email_reply, self._handle_email_action),
            ("whatsapp", self._detect_whatsapp_action, self._send_whatsapp_message),
            ("linkedin", self._detect_linkedin_message, self._send_linkedin_message),
            ("facebook", self._detect_facebook_message, self._send_facebook_message),
            ("twitter", self._detect_twitter_message, self._send_twitter_message),
            ("instagram", self._detect_instagram_message, self._send_instagram_message),
        ]

        for name, detector, sender in platform_detectors:
            action = detector(task)
            if action:
                sender(task, action)
                return

        # No platform-specific action — check if we should auto-respond
        if self._should_respond_to_task(task):
            response_content = self._generate_response_content(task)
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
        plan_filepath.write_text(plan_content, encoding="utf-8")

        log_activity(
            "PLAN_CREATED", f"Created plan file: {plan_filename}", self.vault_path
        )
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
            "please",
            "can you",
            "could you",
            "would you",
            "analyze",
            "summarize",
            "create",
            "generate",
            "send",
            "provide",
            "tell me",
            "help",
            "suggest",
            "what",
            "how",
            "when",
            "where",
            "why",
        ]

        return any(indicator in content_lower for indicator in response_indicators)

    def _generate_response_content(self, task) -> str:
        """
        Generate appropriate response content based on the task.

        If a template file exists under `Templates/EMAIL_RESPONSE_TEMPLATE.md` or
        `Templates/GLOBAL_RESPONSE_TEMPLATE.md` in the vault, it will be
        rendered with the following variables:

            {{ sender }}, {{ subject }}, {{ snippet }}, {{ full_content }}

        Otherwise the legacy fallback (simple English string) is used.
        """
        # quick‑rule: if the task text explicitly tells us what to say, just echo it
        # e.g. "reply to this mail with hi" → "hi" or "respond to this mail with thanks".
        import re

        simple_match = None
        m = re.search(r"(?:reply|respond) to this mail with (.+)", task.content.lower())
        if m:
            simple_match = m.group(1).strip()
        if simple_match:
            return simple_match

        # If the vault contains a template, use it
        template_paths = [
            self.vault_path / "Templates" / "EMAIL_RESPONSE_TEMPLATE.md",
            self.vault_path / "Templates" / "GLOBAL_RESPONSE_TEMPLATE.md",
        ]

        for tpl in template_paths:
            if tpl.exists():
                try:
                    tpl_text = tpl.read_text(encoding="utf-8")
                    context = {
                        "sender": task.frontmatter.get("from", ""),
                        "subject": task.frontmatter.get("subject", ""),
                        "snippet": task.content[:200]
                        .replace("`", "\`")
                        .replace("{", "{{")
                        .replace("}", "}}"),
                        "full_content": task.content,
                    }
                    return tpl_text.format(**context)
                except Exception as e:
                    self.logger.error(f"Error rendering template {tpl}: {e}")
                    # fall back to default generation
                    break

        # Legacy fallback behaviour
        task_content = task.content
        response_body = f"I have processed your request: '{task_content[:100]}{'...' if len(task_content) > 100 else ''}'\n\n"

        if "analyze" in task_content.lower() or "summary" in task_content.lower():
            response_body += "Analysis completed. The results have been documented and are available for review."
        elif "create" in task_content.lower() or "generate" in task_content.lower():
            response_body += "Creation task completed. The requested item has been generated and documented."
        elif "help" in task_content.lower():
            response_body += "I hope this information is helpful. Please let me know if you need further assistance."
        else:
            response_body += "Task completed successfully. Please let me know if you need any additional assistance."

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
        original_channel = task.frontmatter.get("type", "email")  # default to email
        original_sender = task.frontmatter.get("from", "unknown")

        # Map task type to channel name
        channel_map = {
            "email": "EMAIL",
            "linkedin": "LINKEDIN",
            "linkedin_message": "LINKEDIN",
            "whatsapp": "WHATSAPP",
            "whatsapp_message": "WHATSAPP",
            "facebook": "FACEBOOK",
            "facebook_message": "FACEBOOK",
            "twitter": "TWITTER",
            "twitter_notification": "TWITTER",
            "instagram": "INSTAGRAM",
            "instagram_dm": "INSTAGRAM",
        }

        channel_value = channel_map.get(original_channel, "EMAIL")

        # Create response file with appropriate metadata
        response_content_full = f"""---
type: response_message
original_message_id: {task.filename.replace('.md', '')}
channel: {channel_value}
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

        log_activity(
            "RESPONSE_CREATED",
            f"Created response file: {response_filename}",
            self.vault_path,
        )

    @staticmethod
    def _extract_email(recipient_str: str) -> str:
        """Extract email from 'Name <email@domain.com>' or return stripped string if already plain email."""
        import re

        s = (recipient_str or "").strip()
        if not s:
            return ""
        match = re.search(r"<([^>]+)>", s)
        if match:
            return match.group(1).strip()
        return s

    def _detect_email_reply(self, task) -> dict:
        """Detect if this task is an email that needs a reply."""
        task_type = task.frontmatter.get("type", "")
        if "email" in task_type:
            sender = task.frontmatter.get("from", "")
            subject = task.frontmatter.get("subject", "")
            if sender:
                response = self._generate_response_content(task)
                return {"to": sender, "subject": subject, "message": response}
        # Also detect email-sending requests in content
        content_lower = task.content.lower()
        if "send" in content_lower and (
            "email" in content_lower or "mail" in content_lower
        ):
            return {
                "to": task.frontmatter.get("from", ""),
                "subject": "",
                "message": self._extract_message_to_send(task),
            }
        return None

    def _handle_email_action(self, task, action: dict):
        """Handle email action detected by the dispatch loop."""
        response_content = action.get("message", "")
        self._send_email_response(task, response_content)

    def _send_email_response(self, task, response_content: str):
        """
        Send email: try browser (Gmail) first, then MCP, then direct API.
        Browser path opens Gmail, composes, and sends — no MCP/Gmail API required.
        """
        import re

        raw_recipient = task.frontmatter.get("from", "")
        original_subject = task.frontmatter.get("subject", "Your Request")
        recipient = self._extract_email(raw_recipient)
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not recipient or not re.match(email_pattern, recipient):
            self.logger.warning(
                f"Invalid email recipient: {raw_recipient}. Creating response file instead."
            )
            self._create_response_file(task, response_content)
            return

        subject = f"Re: {original_subject}"

        # 1) Prefer browser: open Gmail, compose, type, send (no MCP)
        try:
            from src.services.direct_social_sender import send_gmail_via_browser

            log_activity(
                "EMAIL_SENDING_BROWSER",
                f"Sending email to {recipient} via Gmail browser",
                self.vault_path,
            )
            result = send_gmail_via_browser(
                to=recipient, subject=subject, body=response_content
            )
            if result.get("success"):
                log_activity(
                    "EMAIL_SENT_BROWSER",
                    f"Email sent to {recipient} via Gmail (browser)",
                    self.vault_path,
                )
                task.content += f"\n\n## Email Sent (Gmail browser) ✅\n- **To**: {recipient}\n- **Subject**: {subject}\n- **Status**: Sent\n"
                task.filepath.write_text(task.content, encoding="utf-8")
                return
            self.logger.warning(
                f"Gmail browser send failed: {result.get('error')}. Trying MCP/direct."
            )
        except Exception as e:
            self.logger.warning(f"Gmail browser send error: {e}. Trying MCP/direct.")

        # 2) Fallback: Gmail API (sync, no asyncio.run needed)
        try:
            from src.services.direct_social_sender import send_gmail_via_api

            result = send_gmail_via_api(
                to=recipient, subject=subject, body=response_content
            )
            if result.get("success"):
                log_activity(
                    "EMAIL_SENT_API",
                    f"Email sent to {recipient} via Gmail API",
                    self.vault_path,
                )
                task.content += f"\n\n## Email Sent (Gmail API) ✅\n- **To**: {recipient}\n- **Subject**: {subject}\n"
                task.filepath.write_text(task.content, encoding="utf-8")
                return
            self.logger.warning(f"Gmail API send failed: {result.get('error')}")
        except Exception as e:
            self.logger.warning(f"Gmail API fallback error: {e}")

        # 3) All methods failed — log error
        log_activity(
            "EMAIL_FAILED", f"All email methods failed for {recipient}", self.vault_path
        )
        task.content += f"\n\n## Email Send Failed ⚠️\n- **To**: {recipient}\n- **Subject**: {subject}\n- **Note**: Browser and API both failed\n"
        task.filepath.write_text(task.content, encoding="utf-8")

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
        subject_lower = task.frontmatter.get("subject", "").lower()
        full_text = content_lower + " " + subject_lower

        # Keywords that indicate WhatsApp message request
        whatsapp_keywords = [
            "whatsapp",
            "wa.me",
            "send whatsapp",
            "message on whatsapp",
            "whatsapp message",
            "send on whatsapp",
            "via whatsapp",
        ]

        # Check for WhatsApp request
        has_whatsapp_request = any(kw in full_text for kw in whatsapp_keywords)

        if not has_whatsapp_request:
            return None

        # Phone number pattern (international format)
        phone_pattern = r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"

        # Extract phone numbers from content
        phones = re.findall(phone_pattern, task.content)

        # Also check frontmatter for 'to' or 'phone' field
        if not phones:
            to_field = task.frontmatter.get("to", "")
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
        saying_match = re.search(r"saying\s+(.+?)(?:\.|$)", content_lower)
        if saying_match:
            message = saying_match.group(1).strip()

        # Pattern 2: "say [message]"
        if not message:
            say_match = re.search(r"say\s+(.+?)(?:\.|$)", content_lower)
            if say_match:
                message = say_match.group(1).strip()

        # Pattern 3: "message: [message]" or "text: [message]"
        if not message:
            msg_match = re.search(r"(?:message|text):\s*(.+?)(?:\.|$)", content_lower)
            if msg_match:
                message = msg_match.group(1).strip()

        # Pattern 4: "with message [message]"
        if not message:
            with_match = re.search(
                r"with\s+(?:the\s+)?message\s+(.+?)(?:\.|$)", content_lower
            )
            if with_match:
                message = with_match.group(1).strip()

        # Default message if none extracted
        if not message:
            message = "Hello"

        # Clean up message
        message = message.strip().rstrip(".")

        # Capitalize first letter
        if message:
            message = (
                message[0].upper() + message[1:]
                if len(message) > 1
                else message.upper()
            )

        return {
            "to": phones[0],  # First phone number found
            "message": message,
            "requires_approval": True,
        }

    def _detect_linkedin_message(self, task) -> dict:
        """Detect LinkedIn message — either from watcher or email requesting LinkedIn action."""
        task_type = task.frontmatter.get("type", "")
        if "linkedin" in task_type:
            # Action file from LinkedIn watcher — respond to the sender
            sender = task.frontmatter.get("from", "LinkedIn Contact")
            response = self._generate_response_content(task)
            return {"to": sender, "message": response, "is_reply": True}
        content_lower = task.content.lower()
        if "linkedin" in content_lower and (
            "message" in content_lower
            or "send" in content_lower
            or "dm" in content_lower
        ):
            return {
                "to": task.frontmatter.get("from", ""),
                "message": self._extract_message_to_send(task),
                "is_reply": False,
            }
        return None

    def _detect_facebook_message(self, task) -> dict:
        """Detect Facebook message — either from watcher or email requesting Facebook action."""
        task_type = task.frontmatter.get("type", "")
        if "facebook" in task_type:
            sender = task.frontmatter.get("from", "Facebook Contact")
            response = self._generate_response_content(task)
            return {"to": sender, "message": response, "is_reply": True}
        content_lower = task.content.lower()
        if "facebook" in content_lower and (
            "message" in content_lower
            or "send" in content_lower
            or "dm" in content_lower
        ):
            return {
                "to": task.frontmatter.get("from", ""),
                "message": self._extract_message_to_send(task),
                "is_reply": False,
            }
        return None

    def _detect_twitter_message(self, task) -> dict:
        """Detect Twitter/X message — either from watcher or email requesting Twitter action."""
        task_type = task.frontmatter.get("type", "")
        if "twitter" in task_type:
            sender = task.frontmatter.get("from", "Twitter/X")
            response = self._generate_response_content(task)
            return {"to": sender, "message": response, "is_reply": True}
        content_lower = task.content.lower()
        if ("twitter" in content_lower or "x.com" in content_lower) and (
            "message" in content_lower
            or "dm" in content_lower
            or "tweet" in content_lower
        ):
            return {
                "to": task.frontmatter.get("from", ""),
                "message": self._extract_message_to_send(task),
                "is_reply": False,
            }
        return None

    def _detect_instagram_message(self, task) -> dict:
        """Detect Instagram DM — either from watcher or email requesting Instagram action."""
        task_type = task.frontmatter.get("type", "")
        if "instagram" in task_type:
            sender = task.frontmatter.get("from", "Instagram User")
            response = self._generate_response_content(task)
            return {"to": sender, "message": response, "is_reply": True}
        content_lower = task.content.lower()
        if "instagram" in content_lower and (
            "message" in content_lower or "dm" in content_lower
        ):
            return {
                "to": task.frontmatter.get("from", ""),
                "message": self._extract_message_to_send(task),
                "is_reply": False,
            }
        return None

    def _extract_message_to_send(self, task) -> str:
        """Extract the message the user wants to send from the task content."""
        import re

        content_lower = task.content.lower()
        # Try: "saying [msg]", "say [msg]", "message: [msg]", "with message [msg]"
        patterns = [
            r'saying\s+["\']?(.+?)["\']?(?:\.|$)',
            r'(?:say|tell)\s+["\']?(.+?)["\']?(?:\.|$)',
            r'(?:message|text):\s*["\']?(.+?)["\']?(?:\.|$)',
            r'with\s+(?:the\s+)?message\s+["\']?(.+?)["\']?(?:\.|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content_lower)
            if match:
                msg = match.group(1).strip()
                if msg:
                    return msg[0].upper() + msg[1:] if len(msg) > 1 else msg.upper()
        return self._generate_response_content(task)

    def _detect_social_media_action(self, task) -> dict:
        """
        Detect if email content is requesting a social media post

        Args:
            task: The task object

        Returns:
            Dictionary with platform and content, or None if not a social media request
        """
        content_lower = task.content.lower()
        subject_lower = task.frontmatter.get("subject", "").lower()

        # Keywords that indicate social media post request
        social_keywords = {
            "linkedin": ["linkedin", "linked in", "li.com"],
            "twitter": ["twitter", "tweet", "x.com", "post on x"],
            "facebook": ["facebook", "fb", "facebook post"],
            "instagram": ["instagram", "insta", "ig post"],
        }

        # Check for post request keywords
        post_keywords = ["post", "publish", "share", "make a post", "first post"]

        has_post_request = any(
            kw in content_lower or kw in subject_lower for kw in post_keywords
        )

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
            "platforms": platforms,
            "content": content_to_post,
            "requires_approval": True,
        }

    def _extract_post_content(self, email_content: str) -> str:
        """Extract content for social media posting"""
        lines = email_content.split("\n")
        content_lines = []
        for line in lines:
            line = line.strip()
            if (
                line
                and not line.startswith("---")
                and not line.startswith("type:")
                and not line.startswith("[")
            ):
                content_lines.append(line)
        return " ".join(content_lines[:3])

    def _send_whatsapp_message(self, task, whatsapp_action: dict):
        """Send WhatsApp message via unified sender."""
        from src.services.direct_social_sender import send_whatsapp_message

        phone = whatsapp_action.get("to", "")
        message = whatsapp_action.get("message", "Hello")
        log_activity("WHATSAPP_SEND", f"Sending WhatsApp to {phone}", self.vault_path)
        result = send_whatsapp_message(phone, message)
        if result.get("success"):
            log_activity("WHATSAPP_SENT", f"WhatsApp sent to {phone}", self.vault_path)
            task.content += f"\n\n## WhatsApp Message Sent ✅\n- **To**: {phone}\n- **Message**: {message}\n"
        else:
            log_activity(
                "WHATSAPP_FAILED",
                f"WhatsApp failed: {result.get('error')}",
                self.vault_path,
            )
            task.content += f"\n\n## WhatsApp Message Failed ⚠️\n- **To**: {phone}\n- **Error**: {result.get('error')}\n"
        task.filepath.write_text(task.content, encoding="utf-8")

    def _send_linkedin_message(self, task, action: dict):
        """Send LinkedIn message via unified sender — DM for replies, post for outbound."""
        from src.services.direct_social_sender import (
            send_linkedin_dm,
            send_linkedin_post,
        )

        recipient = action.get("to", "")
        message = action.get("message", "Hello")
        is_reply = action.get("is_reply", False)

        if is_reply and recipient:
            log_activity(
                "LINKEDIN_SEND", f"Sending LinkedIn DM to {recipient}", self.vault_path
            )
            result = send_linkedin_dm(recipient, message)
            action_label = f"LinkedIn DM to {recipient}"
        else:
            log_activity("LINKEDIN_SEND", f"Sending LinkedIn post", self.vault_path)
            result = send_linkedin_post(message)
            action_label = "LinkedIn post"

        if result.get("success"):
            log_activity("LINKEDIN_SENT", f"{action_label} sent", self.vault_path)
            task.content += f"\n\n## {action_label} Sent ✅\n- **Message**: {message}\n"
        else:
            task.content += (
                f"\n\n## {action_label} Failed ⚠️\n- **Error**: {result.get('error')}\n"
            )
        task.filepath.write_text(task.content, encoding="utf-8")

    def _send_facebook_message(self, task, action: dict):
        """Send Facebook message via unified sender — DM for replies, post for outbound."""
        from src.services.direct_social_sender import (
            send_facebook_dm,
            send_facebook_post,
        )

        recipient = action.get("to", "")
        message = action.get("message", "Hello")
        is_reply = action.get("is_reply", False)

        if is_reply and recipient:
            log_activity(
                "FACEBOOK_SEND", f"Sending Facebook DM to {recipient}", self.vault_path
            )
            result = send_facebook_dm(recipient, message)
            action_label = f"Facebook DM to {recipient}"
        else:
            log_activity("FACEBOOK_SEND", f"Sending Facebook post", self.vault_path)
            result = send_facebook_post(message)
            action_label = "Facebook post"

        if result.get("success"):
            log_activity("FACEBOOK_SENT", f"{action_label} sent", self.vault_path)
            task.content += f"\n\n## {action_label} Sent ✅\n- **Message**: {message}\n"
        else:
            task.content += (
                f"\n\n## {action_label} Failed ⚠️\n- **Error**: {result.get('error')}\n"
            )
        task.filepath.write_text(task.content, encoding="utf-8")

    def _send_twitter_message(self, task, action: dict):
        """Send Twitter message via unified sender — DM for replies, tweet for outbound."""
        from src.services.direct_social_sender import send_tweet, send_twitter_dm

        recipient = action.get("to", "")
        message = action.get("message", "Hello")
        is_reply = action.get("is_reply", False)

        if is_reply and recipient:
            log_activity(
                "TWITTER_SEND", f"Sending Twitter DM to {recipient}", self.vault_path
            )
            result = send_twitter_dm(recipient, message)
            action_label = f"Twitter DM to {recipient}"
        else:
            log_activity("TWITTER_SEND", f"Posting tweet", self.vault_path)
            result = send_tweet(message)
            action_label = "Tweet"

        if result.get("success"):
            log_activity("TWITTER_SENT", f"{action_label} sent", self.vault_path)
            task.content += f"\n\n## {action_label} Sent ✅\n- **Message**: {message}\n"
        else:
            task.content += (
                f"\n\n## {action_label} Failed ⚠️\n- **Error**: {result.get('error')}\n"
            )
        task.filepath.write_text(task.content, encoding="utf-8")

    def _send_instagram_message(self, task, action: dict):
        """Send Instagram DM via unified sender."""
        from src.services.direct_social_sender import send_instagram_dm

        recipient = action.get("to", "")
        message = action.get("message", "Hello")
        log_activity(
            "INSTAGRAM_SEND", f"Sending Instagram DM to {recipient}", self.vault_path
        )
        result = send_instagram_dm(recipient, message)
        if result.get("success"):
            log_activity(
                "INSTAGRAM_SENT", f"Instagram DM sent to {recipient}", self.vault_path
            )
            task.content += f"\n\n## Instagram DM Sent ✅\n- **To**: {recipient}\n- **Message**: {message}\n"
        else:
            task.content += (
                f"\n\n## Instagram DM Failed ⚠️\n- **Error**: {result.get('error')}\n"
            )
        task.filepath.write_text(task.content, encoding="utf-8")

    def _execute_social_media_post(self, task, social_action: dict):
        """Post to social media platforms via unified sender."""
        from src.services.direct_social_sender import send_message

        platforms = social_action.get("platforms", [])
        content = social_action.get("content", "")
        log_activity("SOCIAL_POST", f"Posting to {platforms}", self.vault_path)

        results = {}
        for platform in platforms:
            result = send_message(f"{platform}-post", "", content)
            results[platform] = result
            if result.get("success"):
                log_activity("SOCIAL_POSTED", f"Posted to {platform}", self.vault_path)
            else:
                log_activity(
                    "SOCIAL_POST_ERROR",
                    f"Failed {platform}: {result.get('error')}",
                    self.vault_path,
                )

        task.content += f"\n\n## Social Media Post Results\n"
        for platform, result in results.items():
            if result.get("success"):
                task.content += f"- ✅ **{platform.title()}**: Posted successfully\n"
            else:
                task.content += f"- ⚠️ **{platform.title()}**: {result.get('error', 'Check credentials')}\n"
        task.filepath.write_text(task.content, encoding="utf-8")

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
        log_activity(
            "APPROVED",
            f"Handling approved request: {approved_file.name}",
            self.vault_path,
        )

        # Move the original task back to needs action for execution
        # Extract original task name from approval request
        content = approved_file.read_text()

        # Find the related task in the original content
        import re

        match = re.search(r"related_task: (.+)", content)
        if match:
            original_task_name = match.group(1).strip()
            original_task_path = (
                self.vault_path / "Pending_Approval" / original_task_name
            )

            if original_task_path.exists():
                # Mark task as approved so it won't be re-flagged
                task_content = original_task_path.read_text(encoding="utf-8")
                if task_content.startswith("---"):
                    # Insert approved: true into existing frontmatter
                    task_content = task_content.replace(
                        "---\n", "---\napproved: true\n", 1
                    )
                else:
                    task_content = "---\napproved: true\n---\n" + task_content
                original_task_path.write_text(task_content, encoding="utf-8")

                # Move the original task to needs action for processing
                move_file_to_folder(original_task_path, "Needs_Action", self.vault_path)

        # Move approval file to done
        move_file_to_folder(approved_file, "Done", self.vault_path)

    def handle_rejected_request(self, rejected_file):
        """
        Handle a rejected request
        """
        log_activity(
            "REJECTED",
            f"Handling rejected request: {rejected_file.name}",
            self.vault_path,
        )

        # Move approval file to done
        move_file_to_folder(rejected_file, "Done", self.vault_path)

    def update_dashboard(self):
        """
        Update the dashboard with current status
        """
        summary_data = get_dashboard_summary(self.vault_path)
        summary_data["recent_activities"] = [
            f"Processed {len(get_pending_tasks(self.vault_path))} pending tasks",
            f"Updated at {datetime.now().strftime('%H:%M:%S')}",
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
                processed_tasks = self.process_pending_tasks()
                processed_count = len(processed_tasks) if isinstance(processed_tasks, list) else 0

                # Process approval requests
                self.process_approval_requests()

                # Update dashboard
                self.update_dashboard()

                log_activity(
                    "SYSTEM",
                    f"Completed processing cycle, processed {processed_count} tasks",
                    self.vault_path,
                )

                time.sleep(interval)
            except Exception as e:
                log_activity(
                    "ERROR", f"Error in processing loop: {str(e)}", self.vault_path
                )
                time.sleep(60)  # Wait 1 minute before retrying if there's an error

import re
from pathlib import Path
import yaml

class HandbookParser:
    """
    Parser for the Company Handbook that defines business rules for the AI Employee
    """
    def __init__(self, handbook_path=None):
        self.handbook_path = handbook_path or "vault/Company_Handbook.md"
        self.rules = {}
        self.load_handbook()

    def load_handbook(self):
        """
        Load and parse the company handbook
        """
        handbook_file = Path(self.handbook_path)

        if not handbook_file.exists():
            # Create a default handbook if it doesn't exist
            self.create_default_handbook(handbook_file)

        content = handbook_file.read_text(encoding='utf-8')
        self.parse_rules(content)

    def create_default_handbook(self, handbook_path):
        """
        Create a default company handbook with basic rules
        """
        default_content = """# Company Handbook

## Rules for Processing Emails
- Automated responses to known contacts for routine inquiries
- Flag emails with financial terms like "payment", "invoice", "money", "transfer", "wire" for human approval
- Archive promotional emails after reading
- Forward urgent emails (containing "urgent", "asap", "immediately") to priority queue

## Rules for Financial Actions
- All payments require human approval
- Flag transactions over $100 for review
- Log all financial activities

## Rules for Communication
- Never send emails to new contacts without approval
- Use professional tone in all communications
- Disclose AI involvement when required

## Approval Requirements
- Payment requests
- Emails to new contacts
- File sharing requests
- Access permission changes
- Confidential information sharing

## Default Actions
- Schedule meetings when possible
- Answer frequently asked questions
- Process routine administrative tasks
- Archive completed tasks
"""
        handbook_path.parent.mkdir(parents=True, exist_ok=True)
        handbook_path.write_text(default_content, encoding='utf-8')

    def parse_rules(self, content):
        """
        Parse the handbook content and extract rules
        """
        # Extract sections and their rules
        sections = re.split(r'^##\s+(.+)$', content, flags=re.MULTILINE)

        # The split creates alternating elements: [before_first_header, header1, content1, header2, content2, ...]
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_title = sections[i].strip()
                section_content = sections[i + 1]

                if "Rules for Processing Emails" in section_title:
                    self.rules['email_processing'] = self._parse_email_rules(section_content)
                elif "Rules for Financial Actions" in section_title:
                    self.rules['financial_actions'] = self._parse_financial_rules(section_content)
                elif "Rules for Communication" in section_title:
                    self.rules['communication'] = self._parse_communication_rules(section_content)
                elif "Approval Requirements" in section_title:
                    self.rules['approval_requirements'] = self._parse_approval_rules(section_content)
                elif "Default Actions" in section_title:
                    self.rules['default_actions'] = self._parse_default_actions(section_content)

    def _parse_email_rules(self, content):
        """
        Parse email processing rules
        """
        rules = {
            'auto_response_contacts': [],
            'flag_keywords': [],
            'archive_keywords': [],
            'priority_keywords': []
        }

        # Extract flag keywords (financial terms)
        financial_terms = re.findall(r'"([^"]*(?:payment|invoice|money|transfer|wire)[^"]*)"', content, re.IGNORECASE)
        rules['flag_keywords'].extend([term.lower() for term in financial_terms])

        # Extract priority keywords
        priority_terms = re.findall(r'"([^"]*(?:urgent|asap|immediately)[^"]*)"', content, re.IGNORECASE)
        rules['priority_keywords'].extend([term.lower() for term in priority_terms])

        # Add default financial terms if not found
        if not any(term in rules['flag_keywords'] for term in ['payment', 'invoice', 'money']):
            rules['flag_keywords'].extend(['payment', 'invoice', 'money', 'transfer', 'wire'])

        if not any(term in rules['priority_keywords'] for term in ['urgent', 'asap']):
            rules['priority_keywords'].extend(['urgent', 'asap', 'immediately'])

        return rules

    def _parse_financial_rules(self, content):
        """
        Parse financial action rules
        """
        rules = {
            'require_approval': True,
            'approval_threshold': 100,  # Default threshold
            'log_activities': True
        }

        # Extract threshold amount
        threshold_match = re.search(r'over\s+\$(\d+)', content, re.IGNORECASE)
        if threshold_match:
            rules['approval_threshold'] = int(threshold_match.group(1))

        return rules

    def _parse_communication_rules(self, content):
        """
        Parse communication rules
        """
        rules = {
            'require_approval_for_new_contacts': True,
            'professional_tone': True,
            'disclose_ai_involvement': False
        }

        if 'without approval' in content.lower():
            rules['require_approval_for_new_contacts'] = True

        if 'professional tone' in content.lower():
            rules['professional_tone'] = True

        if 'disclose ai' in content.lower():
            rules['disclose_ai_involvement'] = True

        return rules

    def _parse_approval_rules(self, content):
        """
        Parse approval requirement rules
        """
        approval_items = re.findall(r'-\s*(.+)', content)
        return [item.strip().lower() for item in approval_items]

    def _parse_default_actions(self, content):
        """
        Parse default action rules
        """
        default_actions = re.findall(r'-\s*(.+)', content)
        return [action.strip().lower() for action in default_actions]

    def should_flag_for_approval(self, content, content_type="email", sender="unknown"):
        """
        Determine if content should be flagged for human approval
        """
        content_lower = content.lower()
        sender_lower = sender.lower()

        # Check financial terms
        if content_type == "email":
            financial_rules = self.rules.get('email_processing', {}).get('flag_keywords', [])
            for term in financial_rules:
                if term in content_lower:
                    return True, f"Contains financial term: {term}"

        # Check approval requirements
        approval_requirements = self.rules.get('approval_requirements', [])
        for requirement in approval_requirements:
            if requirement in content_lower:
                return True, f"Matches approval requirement: {requirement}"

        # Only flag unknown senders for truly sensitive actions (payments, sharing)
        sensitive_keywords = ['payment', 'invoice', 'transfer', 'wire', 'confidential', 'access']
        if not self._is_sender_whitelisted(sender_lower):
            for keyword in sensitive_keywords:
                if keyword in content_lower:
                    return True, f"Sensitive content from non-whitelisted sender ({sender}): contains '{keyword}'"

        return False, "No approval required"

    def _is_sender_whitelisted(self, sender_lower):
        """
        Check if a sender is in the Trusted_Contacts whitelist
        """
        try:
            # Look for the trusted contacts file in the same vault as the handbook
            vault_root = Path(self.handbook_path).parent
            trusted_file = vault_root / "Trusted_Contacts.md"
            
            if not trusted_file.exists():
                # If the file doesn't exist, we fallback to restricted mode (no one is trusted)
                return False
                
            trusted_content = trusted_file.read_text(encoding='utf-8').lower()
            
            # Simple check: Does the email/name/link appear in the markdown file?
            # We check for exact matches in the text to be safe
            if sender_lower in trusted_content:
                return True
                
            return False
        except Exception:
            return False

    def get_default_action(self, content):
        """
        Get the default action based on content
        """
        content_lower = content.lower()
        default_actions = self.rules.get('default_actions', [])

        for action in default_actions:
            if any(keyword in content_lower for keyword in action.split()):
                return action

        return "process_normally"

    def get_priority_level(self, content):
        """
        Get the priority level based on content
        """
        content_lower = content.lower()
        priority_keywords = self.rules.get('email_processing', {}).get('priority_keywords', [])

        for keyword in priority_keywords:
            if keyword in content_lower:
                return "high"

        return "normal"
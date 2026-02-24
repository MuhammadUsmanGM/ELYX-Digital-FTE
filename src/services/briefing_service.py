"""
CEO Briefing Service
Generates weekly "Monday Morning CEO Briefing" automatically

Features:
- Revenue tracking from Odoo
- Completed tasks summary
- Bottleneck identification
- Proactive suggestions
- Subscription audit
- Upcoming deadlines

Runs every Monday at 8:00 AM
"""

from datetime import datetime, timedelta
from pathlib import Path
import json
import os
from typing import Dict, List, Any

from .odoo_service import get_odoo_service


class CEOBriefingService:
    """
    Generates weekly CEO briefings with business insights
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_folder = self.vault_path / 'Briefings'
        self.done_folder = self.vault_path / 'Done'
        self.plans_folder = self.vault_path / 'Plans'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure briefings folder exists
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize Odoo service
        self.odoo = get_odoo_service()
        
    def generate_briefing(self, period_start: datetime = None, period_end: datetime = None) -> Dict[str, Any]:
        """
        Generate weekly CEO briefing
        
        Args:
            period_start: Start of period (defaults to 7 days ago)
            period_end: End of period (defaults to today)
            
        Returns:
            Briefing data dictionary
        """
        if period_start is None:
            period_end = datetime.now()
            period_start = period_end - timedelta(days=7)
        
        # Get revenue data from Odoo
        revenue_data = self._get_revenue_data(period_start, period_end)
        
        # Get completed tasks
        completed_tasks = self._get_completed_tasks(period_start, period_end)
        
        # Get bottlenecks
        bottlenecks = self._identify_bottlenecks(completed_tasks)
        
        # Get proactive suggestions
        suggestions = self._generate_suggestions(revenue_data, completed_tasks)
        
        # Get upcoming deadlines
        deadlines = self._get_upcoming_deadlines()
        
        # Compile briefing
        briefing = {
            'generated': datetime.now().isoformat(),
            'period': {
                'start': period_start.strftime('%Y-%m-%d'),
                'end': period_end.strftime('%Y-%m-%d')
            },
            'revenue': revenue_data,
            'completed_tasks': completed_tasks,
            'bottlenecks': bottlenecks,
            'suggestions': suggestions,
            'deadlines': deadlines
        }
        
        # Save briefing
        self._save_briefing(briefing)
        
        return briefing
    
    def _get_revenue_data(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Get revenue data from Odoo"""
        revenue_data = {
            'this_week': 0.0,
            'mtm': 0.0,  # Month to date
            'trend': 'stable',
            'invoices_sent': 0,
            'invoices_paid': 0,
            'invoices_overdue': 0
        }
        
        if not self.odoo or not self.odoo.authenticated:
            return revenue_data
        
        try:
            # Get weekly revenue
            revenue_data['this_week'] = self.odoo.get_revenue_this_week()
            
            # Get monthly revenue
            revenue_data['mtm'] = self.odoo.get_revenue_this_month()
            
            # Get invoice counts
            unpaid = self.odoo.get_unpaid_invoices()
            overdue = self.odoo.get_overdue_invoices()
            
            revenue_data['invoices_sent'] = len(unpaid)
            revenue_data['invoices_paid'] = len([i for i in unpaid if i.get('payment_state') == 'paid'])
            revenue_data['invoices_overdue'] = len(overdue)
            
            # Determine trend
            if revenue_data['this_week'] > 0:
                revenue_data['trend'] = 'growing'
            elif revenue_data['this_week'] == 0:
                revenue_data['trend'] = 'stable'
            else:
                revenue_data['trend'] = 'declining'
                
        except Exception as e:
            print(f"Error getting revenue data: {e}")
        
        return revenue_data
    
    def _get_completed_tasks(self, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """Get completed tasks from Done folder"""
        completed_tasks = []
        
        try:
            if not self.done_folder.exists():
                return completed_tasks
            
            # Get all .md files in Done folder
            done_files = list(self.done_folder.glob('*.md'))
            
            for file in done_files:
                try:
                    content = file.read_text(encoding='utf-8')
                    
                    # Parse frontmatter and content
                    task_data = self._parse_task_file(content, file)
                    
                    if task_data:
                        completed_tasks.append(task_data)
                        
                except Exception as e:
                    print(f"Error reading task file {file}: {e}")
                    
        except Exception as e:
            print(f"Error getting completed tasks: {e}")
        
        return completed_tasks
    
    def _parse_task_file(self, content: str, file: Path) -> Dict[str, Any]:
        """Parse task file to extract metadata"""
        task_data = {
            'file': file.name,
            'type': 'unknown',
            'completed_at': file.stat().st_mtime,
            'description': ''
        }
        
        # Extract type from frontmatter
        if 'type:' in content:
            for line in content.split('\n')[:20]:
                if line.startswith('type:'):
                    task_data['type'] = line.split(':')[1].strip()
                    break
        
        # Extract first line as description
        for line in content.split('\n'):
            if line.strip() and not line.startswith('---') and not line.startswith('type:'):
                task_data['description'] = line.strip()[:100]
                break
        
        return task_data
    
    def _identify_bottlenecks(self, completed_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify bottlenecks from task completion patterns"""
        bottlenecks = []
        
        # Group tasks by type
        tasks_by_type = {}
        for task in completed_tasks:
            task_type = task.get('type', 'unknown')
            if task_type not in tasks_by_type:
                tasks_by_type[task_type] = []
            tasks_by_type[task_type].append(task)
        
        # Identify types with low completion
        for task_type, tasks in tasks_by_type.items():
            if len(tasks) < 3:  # Less than 3 tasks per week might indicate bottleneck
                bottlenecks.append({
                    'area': task_type,
                    'issue': f'Low activity: Only {len(tasks)} tasks completed this week',
                    'severity': 'medium' if len(tasks) > 0 else 'high'
                })
        
        # Check for overdue invoices (from Odoo)
        if self.odoo and self.odoo.authenticated:
            try:
                overdue = self.odoo.get_overdue_invoices()
                if len(overdue) > 0:
                    total_overdue = sum(i.get('amount_residual', 0) for i in overdue)
                    bottlenecks.append({
                        'area': 'Accounts Receivable',
                        'issue': f'{len(overdue)} overdue invoices totaling ${total_overdue:.2f}',
                        'severity': 'high'
                    })
            except:
                pass
        
        return bottlenecks
    
    def _generate_suggestions(self, revenue_data: Dict, completed_tasks: List) -> List[Dict[str, Any]]:
        """Generate proactive suggestions based on data"""
        suggestions = []
        
        # Revenue-based suggestions
        if revenue_data['this_week'] == 0:
            suggestions.append({
                'category': 'Revenue',
                'suggestion': 'No revenue this week - consider reaching out to pending leads',
                'priority': 'high',
                'action': 'Review pending proposals and follow up'
            })
        
        # Invoice suggestions
        if revenue_data['invoices_overdue'] > 0:
            suggestions.append({
                'category': 'Accounts Receivable',
                'suggestion': f'{revenue_data["invoices_overdue"]} overdue invoices need follow-up',
                'priority': 'high',
                'action': 'Send payment reminders to overdue clients'
            })
        
        # Task-based suggestions
        task_types = set(t.get('type', '') for t in completed_tasks)
        if 'email' not in task_types:
            suggestions.append({
                'category': 'Communication',
                'suggestion': 'No email responses processed this week',
                'priority': 'medium',
                'action': 'Check inbox for unanswered emails'
            })
        
        return suggestions
    
    def _get_upcoming_deadlines(self) -> List[Dict[str, Any]]:
        """Get upcoming deadlines from Plans folder"""
        deadlines = []
        
        try:
            if not self.plans_folder.exists():
                return deadlines
            
            # Get all plan files
            plan_files = list(self.plans_folder.glob('*.md'))
            
            for file in plan_files:
                content = file.read_text(encoding='utf-8')
                
                # Look for dates in content
                if 'Due:' in content or 'Deadline:' in content:
                    # Extract deadline info
                    deadlines.append({
                        'task': file.stem,
                        'file': file.name,
                        'status': 'upcoming'
                    })
                    
        except Exception as e:
            print(f"Error getting deadlines: {e}")
        
        return deadlines
    
    def _save_briefing(self, briefing: Dict[str, Any]):
        """Save briefing to file"""
        # Generate filename
        period_start = briefing['period']['start'].replace('-', '')
        filename = f"{period_start}_CEO_Briefing.md"
        filepath = self.briefings_folder / filename
        
        # Format briefing as Markdown
        markdown = self._format_briefing_markdown(briefing)
        
        # Save file
        filepath.write_text(markdown, encoding='utf-8')
        print(f"Briefing saved to: {filepath}")
    
    def _format_briefing_markdown(self, briefing: Dict[str, Any]) -> str:
        """Format briefing as Markdown document"""
        period = briefing['period']
        revenue = briefing['revenue']
        
        md = f"""---
generated: {briefing['generated']}
period: {period['start']} to {period['end']}
type: ceo_briefing
---

# Monday Morning CEO Briefing

## Executive Summary
{"Strong week with revenue growth." if revenue['this_week'] > 0 else "Quiet week - focus on lead generation."}

---

## Revenue

| Metric | Amount | Trend |
| :--- | :--- | :--- |
| **This Week** | ${revenue['this_week']:.2f} | {revenue['trend']} |
| **Month to Date** | ${revenue['mtm']:.2f} | - |
| **Invoices Sent** | {revenue['invoices_sent']} | - |
| **Invoices Paid** | {revenue['invoices_paid']} | - |
| **Overdue Invoices** | {revenue['invoices_overdue']} | {"⚠️ ATTENTION NEEDED" if revenue['invoices_overdue'] > 0 else "✓"} |

---

## Completed Tasks

**Total Tasks Completed:** {len(briefing['completed_tasks'])}

### By Type
"""
        
        # Group by type
        tasks_by_type = {}
        for task in briefing['completed_tasks']:
            task_type = task.get('type', 'unknown')
            tasks_by_type[task_type] = tasks_by_type.get(task_type, 0) + 1
        
        for task_type, count in tasks_by_type.items():
            md += f"- **{task_type.title()}:** {count} tasks\n"
        
        md += f"""
---

## Bottlenecks

"""
        
        if briefing['bottlenecks']:
            for bottleneck in briefing['bottlenecks']:
                severity_icon = "🔴" if bottleneck['severity'] == 'high' else "🟡"
                md += f"{severity_icon} **{bottleneck['area']}:** {bottleneck['issue']}\n"
        else:
            md += "✓ No significant bottlenecks identified\n"
        
        md += f"""
---

## Proactive Suggestions

"""
        
        if briefing['suggestions']:
            for i, suggestion in enumerate(briefing['suggestions'], 1):
                priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡"
                md += f"{i}. {priority_icon} **{suggestion['category']}:** {suggestion['suggestion']}\n"
                md += f"   - **Action:** {suggestion['action']}\n\n"
        else:
            md += "✓ No critical suggestions at this time\n"
        
        md += f"""
---

## Upcoming Deadlines

"""
        
        if briefing['deadlines']:
            for deadline in briefing['deadlines']:
                md += f"- [ ] {deadline['task']}\n"
        else:
            md += "✓ No upcoming deadlines\n"
        
        md += f"""
---

*Briefing generated automatically by ELYX AI Employee*
"""
        
        return md


def run_ceo_briefing(vault_path: str):
    """
    Generate CEO briefing (called by scheduler)
    """
    service = CEOBriefingService(vault_path)
    briefing = service.generate_briefing()
    
    print(f"CEO Briefing generated for period: {briefing['period']['start']} to {briefing['period']['end']}")
    print(f"Revenue this week: ${briefing['revenue']['this_week']:.2f}")
    print(f"Tasks completed: {len(briefing['completed_tasks'])}")
    print(f"Bottlenecks identified: {len(briefing['bottlenecks'])}")
    print(f"Suggestions: {len(briefing['suggestions'])}")
    
    return briefing


if __name__ == "__main__":
    import sys
    vault = sys.argv[1] if len(sys.argv) > 1 else "obsidian_vault"
    run_ceo_briefing(vault)

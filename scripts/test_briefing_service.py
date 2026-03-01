#!/usr/bin/env python3
"""
Unit Tests for BriefingService (CEO Briefing Generator)

Tests the CEOBriefingService class for:
- Briefing generation
- Revenue data extraction
- Task completion tracking
- Bottleneck identification
- Suggestion generation
- Deadline tracking
- Markdown formatting
- File saving
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.briefing_service import CEOBriefingService, run_ceo_briefing


class TestBriefingServiceInitialization(unittest.TestCase):
    """Test BriefingService initialization"""
    
    def setUp(self):
        """Create temporary vault structure"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
        # Create basic vault structure
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        (self.vault_path / "Done").mkdir(exist_ok=True)
        (self.vault_path / "Plans").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary directory"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization_creates_folders(self):
        """Test initialization creates necessary folders"""
        # Remove Briefings folder
        shutil.rmtree(self.vault_path / "Briefings")
        
        service = CEOBriefingService(str(self.vault_path))
        
        # Should recreate Briefings folder
        self.assertTrue((self.vault_path / "Briefings").exists())
    
    def test_initialization_sets_paths(self):
        """Test initialization sets correct paths"""
        service = CEOBriefingService(str(self.vault_path))
        
        self.assertEqual(service.vault_path, self.vault_path)
        self.assertEqual(service.briefings_folder, self.vault_path / "Briefings")
        self.assertEqual(service.done_folder, self.vault_path / "Done")
        self.assertEqual(service.plans_folder, self.vault_path / "Plans")


class TestBriefingGeneration(unittest.TestCase):
    """Test briefing generation functionality"""
    
    def setUp(self):
        """Create temporary vault structure"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        
        # Create vault structure
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        (self.vault_path / "Done").mkdir(exist_ok=True)
        (self.vault_path / "Plans").mkdir(exist_ok=True)
        (self.vault_path / "Logs").mkdir(exist_ok=True)
        
        self.service = CEOBriefingService(str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch.object(CEOBriefingService, '_get_revenue_data')
    @patch.object(CEOBriefingService, '_get_completed_tasks')
    @patch.object(CEOBriefingService, '_identify_bottlenecks')
    @patch.object(CEOBriefingService, '_generate_suggestions')
    @patch.object(CEOBriefingService, '_get_upcoming_deadlines')
    def test_generate_briefing_default_period(
        self, mock_deadlines, mock_suggestions, mock_bottlenecks, 
        mock_tasks, mock_revenue
    ):
        """Test briefing generation with default period (7 days)"""
        # Setup mocks
        mock_revenue.return_value = {
            'this_week': 1000.0,
            'mtm': 5000.0,
            'trend': 'growing',
            'invoices_sent': 5,
            'invoices_paid': 3,
            'invoices_overdue': 1
        }
        mock_tasks.return_value = [
            {'type': 'email', 'description': 'Responded to client'},
            {'type': 'finance', 'description': 'Processed invoice'}
        ]
        mock_bottlenecks.return_value = []
        mock_suggestions.return_value = []
        mock_deadlines.return_value = []
        
        # Generate briefing
        briefing = self.service.generate_briefing()
        
        # Verify briefing structure
        self.assertIn('generated', briefing)
        self.assertIn('period', briefing)
        self.assertIn('revenue', briefing)
        self.assertIn('completed_tasks', briefing)
        self.assertIn('bottlenecks', briefing)
        self.assertIn('suggestions', briefing)
        self.assertIn('deadlines', briefing)
        
        # Verify period is last 7 days
        period = briefing['period']
        start = datetime.strptime(period['start'], '%Y-%m-%d')
        end = datetime.strptime(period['end'], '%Y-%m-%d')
        
        self.assertEqual((end - start).days, 7)
        self.assertAlmostEqual(end, datetime.now(), delta=timedelta(seconds=1))
    
    @patch.object(CEOBriefingService, '_get_revenue_data')
    def test_generate_briefing_custom_period(self, mock_revenue):
        """Test briefing generation with custom period"""
        mock_revenue.return_value = {'this_week': 0.0}
        
        period_start = datetime.now() - timedelta(days=30)
        period_end = datetime.now()
        
        briefing = self.service.generate_briefing(period_start, period_end)
        
        # Verify custom period
        self.assertEqual(briefing['period']['start'], period_start.strftime('%Y-%m-%d'))
        self.assertEqual(briefing['period']['end'], period_end.strftime('%Y-%m-%d'))
    
    @patch.object(CEOBriefingService, '_save_briefing')
    def test_generate_briefing_saves_file(self, mock_save):
        """Test briefing generation saves file"""
        briefing = self.service.generate_briefing()
        
        # Verify save was called
        mock_save.assert_called_once()
        mock_save.assert_called_with(briefing)


class TestRevenueDataExtraction(unittest.TestCase):
    """Test revenue data extraction from Odoo"""
    
    def setUp(self):
        """Create service"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        self.service = CEOBriefingService(str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch.object(CEOBriefingService, '__init__', return_value=None)
    def test_get_revenue_data_no_odoo(self, mock_init):
        """Test revenue data when Odoo not available"""
        self.service.odoo = None
        
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()
        
        revenue_data = self.service._get_revenue_data(period_start, period_end)
        
        # Should return default values
        self.assertEqual(revenue_data['this_week'], 0.0)
        self.assertEqual(revenue_data['mtm'], 0.0)
        self.assertEqual(revenue_data['trend'], 'stable')
        self.assertEqual(revenue_data['invoices_sent'], 0)
        self.assertEqual(revenue_data['invoices_paid'], 0)
        self.assertEqual(revenue_data['invoices_overdue'], 0)
    
    @patch.object(CEOBriefingService, '__init__', return_value=None)
    def test_get_revenue_data_with_odoo(self, mock_init):
        """Test revenue data extraction with Odoo"""
        # Mock Odoo service
        mock_odoo = MagicMock()
        mock_odoo.authenticated = True
        mock_odoo.get_revenue_this_week.return_value = 2500.0
        mock_odoo.get_revenue_this_month.return_value = 10000.0
        mock_odoo.get_unpaid_invoices.return_value = [
            {'payment_state': 'paid'},
            {'payment_state': 'not_paid'}
        ]
        mock_odoo.get_overdue_invoices.return_value = []
        
        self.service.odoo = mock_odoo
        
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()
        
        revenue_data = self.service._get_revenue_data(period_start, period_end)
        
        # Verify data extraction
        self.assertEqual(revenue_data['this_week'], 2500.0)
        self.assertEqual(revenue_data['mtm'], 10000.0)
        self.assertEqual(revenue_data['trend'], 'growing')
        self.assertEqual(revenue_data['invoices_sent'], 2)
        self.assertEqual(revenue_data['invoices_paid'], 1)
        self.assertEqual(revenue_data['invoices_overdue'], 0)
    
    @patch.object(CEOBriefingService, '__init__', return_value=None)
    def test_get_revenue_data_trend_detection(self, mock_init):
        """Test trend detection based on revenue"""
        mock_odoo = MagicMock()
        mock_odoo.authenticated = True
        self.service.odoo = mock_odoo
        
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()
        
        # Test growing trend
        mock_odoo.get_revenue_this_week.return_value = 100.0
        revenue = self.service._get_revenue_data(period_start, period_end)
        self.assertEqual(revenue['trend'], 'growing')
        
        # Test stable trend (zero revenue)
        mock_odoo.get_revenue_this_week.return_value = 0.0
        revenue = self.service._get_revenue_data(period_start, period_end)
        self.assertEqual(revenue['trend'], 'stable')


class TestCompletedTasks(unittest.TestCase):
    """Test completed tasks extraction"""
    
    def setUp(self):
        """Create vault with sample task files"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        (self.vault_path / "Done").mkdir(exist_ok=True)
        self.service = CEOBriefingService(str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_completed_tasks_empty_folder(self):
        """Test getting tasks from empty Done folder"""
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()
        
        tasks = self.service._get_completed_tasks(period_start, period_end)
        
        self.assertEqual(len(tasks), 0)
    
    def test_get_completed_tasks_with_files(self):
        """Test getting tasks from Done folder with files"""
        # Create sample task files
        task1 = self.vault_path / "Done" / "TASK_001.md"
        task1.write_text("""---
type: email
status: completed
---

Responded to client inquiry about pricing
""", encoding='utf-8')
        
        task2 = self.vault_path / "Done" / "TASK_002.md"
        task2.write_text("""---
type: finance
status: completed
---

Processed invoice #12345
""", encoding='utf-8')
        
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()
        
        tasks = self.service._get_completed_tasks(period_start, period_end)
        
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['type'], 'email')
        self.assertEqual(tasks[1]['type'], 'finance')
    
    def test_parse_task_file_with_type(self):
        """Test parsing task file with type metadata"""
        content = """---
type: email
priority: high
---

Client inquiry response
"""
        file_path = self.vault_path / "Done" / "TEST.md"
        
        task_data = self.service._parse_task_file(content, file_path)
        
        self.assertEqual(task_data['type'], 'email')
        self.assertEqual(task_data['file'], 'TEST.md')
        self.assertIn('Client inquiry', task_data['description'])
    
    def test_parse_task_file_without_type(self):
        """Test parsing task file without type metadata"""
        content = """---
priority: high
---

General task
"""
        file_path = self.vault_path / "Done" / "TEST.md"
        
        task_data = self.service._parse_task_file(content, file_path)
        
        self.assertEqual(task_data['type'], 'unknown')
        self.assertIn('General task', task_data['description'])


class TestBottleneckIdentification(unittest.TestCase):
    """Test bottleneck identification"""
    
    def setUp(self):
        """Set up service"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        self.service = CEOBriefingService(str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_identify_bottlenecks_empty_tasks(self):
        """Test bottleneck identification with no tasks"""
        bottlenecks = self.service._identify_bottlenecks([])
        
        self.assertEqual(len(bottlenecks), 0)
    
    def test_identify_bottlenecks_low_activity(self):
        """Test bottleneck detection for low activity"""
        tasks = [
            {'type': 'email', 'description': 'Task 1'},
            {'type': 'email', 'description': 'Task 2'}
        ]
        
        bottlenecks = self.service._identify_bottlenecks(tasks)
        
        # Should identify low activity (less than 3 tasks)
        self.assertGreater(len(bottlenecks), 0)
        self.assertTrue(any('Low activity' in b['issue'] for b in bottlenecks))
    
    @patch.object(CEOBriefingService, '__init__', return_value=None)
    def test_identify_bottlenecks_overdue_invoices(self, mock_init):
        """Test bottleneck detection for overdue invoices"""
        mock_odoo = MagicMock()
        mock_odoo.authenticated = True
        mock_odoo.get_overdue_invoices.return_value = [
            {'amount_residual': 500.0},
            {'amount_residual': 300.0}
        ]
        
        self.service.odoo = mock_odoo
        
        bottlenecks = self.service._identify_bottlenecks([])
        
        # Should identify overdue invoices
        self.assertGreater(len(bottlenecks), 0)
        self.assertTrue(any('overdue invoices' in b['issue'] for b in bottlenecks))
        self.assertTrue(any(b['severity'] == 'high' for b in bottlenecks))


class TestSuggestionGeneration(unittest.TestCase):
    """Test proactive suggestion generation"""
    
    def setUp(self):
        """Set up service"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        self.service = CEOBriefingService(str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_suggestions_no_revenue(self):
        """Test suggestions when no revenue"""
        revenue_data = {'this_week': 0.0, 'invoices_overdue': 0}
        completed_tasks = []
        
        suggestions = self.service._generate_suggestions(revenue_data, completed_tasks)
        
        # Should suggest lead generation
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(any('Revenue' in s['category'] for s in suggestions))
        self.assertTrue(any('No revenue' in s['suggestion'] for s in suggestions))
    
    def test_generate_suggestions_overdue_invoices(self):
        """Test suggestions for overdue invoices"""
        revenue_data = {'this_week': 1000.0, 'invoices_overdue': 3}
        completed_tasks = []
        
        suggestions = self.service._generate_suggestions(revenue_data, completed_tasks)
        
        # Should suggest following up on invoices
        self.assertTrue(any('Accounts Receivable' in s['category'] for s in suggestions))
        self.assertTrue(any('overdue invoices' in s['suggestion'] for s in suggestions))
    
    def test_generate_suggestions_no_emails(self):
        """Test suggestions when no email tasks"""
        revenue_data = {'this_week': 1000.0, 'invoices_overdue': 0}
        completed_tasks = [
            {'type': 'finance'},
            {'type': 'finance'}
        ]
        
        suggestions = self.service._generate_suggestions(revenue_data, completed_tasks)
        
        # Should suggest checking emails
        self.assertTrue(any('Communication' in s['category'] for s in suggestions))
        self.assertTrue(any('email' in s['suggestion'].lower() for s in suggestions))


class TestBriefingFormatting(unittest.TestCase):
    """Test briefing Markdown formatting"""
    
    def setUp(self):
        """Set up service"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        self.service = CEOBriefingService(str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_format_briefing_markdown_structure(self):
        """Test briefing Markdown has correct structure"""
        briefing = {
            'generated': datetime.now().isoformat(),
            'period': {'start': '2024-01-01', 'end': '2024-01-07'},
            'revenue': {
                'this_week': 5000.0,
                'mtm': 20000.0,
                'trend': 'growing',
                'invoices_sent': 10,
                'invoices_paid': 8,
                'invoices_overdue': 1
            },
            'completed_tasks': [
                {'type': 'email'},
                {'type': 'finance'}
            ],
            'bottlenecks': [],
            'suggestions': [],
            'deadlines': []
        }
        
        markdown = self.service._format_briefing_markdown(briefing)
        
        # Verify sections
        self.assertIn('# Monday Morning CEO Briefing', markdown)
        self.assertIn('## Revenue', markdown)
        self.assertIn('## Completed Tasks', markdown)
        self.assertIn('## Bottlenecks', markdown)
        self.assertIn('## Proactive Suggestions', markdown)
        self.assertIn('## Upcoming Deadlines', markdown)
        
        # Verify data
        self.assertIn('$5000.00', markdown)
        self.assertIn('$20000.00', markdown)
        self.assertIn('growing', markdown)
    
    def test_format_briefing_with_bottlenecks(self):
        """Test briefing formatting with bottlenecks"""
        briefing = {
            'generated': datetime.now().isoformat(),
            'period': {'start': '2024-01-01', 'end': '2024-01-07'},
            'revenue': {'this_week': 0.0, 'mtm': 0.0, 'trend': 'stable',
                       'invoices_sent': 0, 'invoices_paid': 0, 'invoices_overdue': 0},
            'completed_tasks': [],
            'bottlenecks': [
                {'area': 'Sales', 'issue': 'No deals closed', 'severity': 'high'}
            ],
            'suggestions': [],
            'deadlines': []
        }
        
        markdown = self.service._format_briefing_markdown(briefing)
        
        # Verify bottleneck formatting
        self.assertIn('🔴', markdown)
        self.assertIn('Sales', markdown)
        self.assertIn('No deals closed', markdown)
    
    def test_format_briefing_with_suggestions(self):
        """Test briefing formatting with suggestions"""
        briefing = {
            'generated': datetime.now().isoformat(),
            'period': {'start': '2024-01-01', 'end': '2024-01-07'},
            'revenue': {'this_week': 0.0, 'mtm': 0.0, 'trend': 'stable',
                       'invoices_sent': 0, 'invoices_paid': 0, 'invoices_overdue': 0},
            'completed_tasks': [],
            'bottlenecks': [],
            'suggestions': [
                {'category': 'Revenue', 'suggestion': 'Follow up on leads',
                 'priority': 'high', 'action': 'Contact pending leads'}
            ],
            'deadlines': []
        }
        
        markdown = self.service._format_briefing_markdown(briefing)
        
        # Verify suggestion formatting
        self.assertIn('🔴', markdown)
        self.assertIn('Revenue', markdown)
        self.assertIn('Follow up on leads', markdown)


class TestBriefingSaving(unittest.TestCase):
    """Test briefing file saving"""
    
    def setUp(self):
        """Set up service"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        self.service = CEOBriefingService(str(self.vault_path))
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_save_briefing_creates_file(self):
        """Test saving briefing creates file"""
        briefing = {
            'generated': datetime.now().isoformat(),
            'period': {'start': '2024-01-01', 'end': '2024-01-07'},
            'revenue': {'this_week': 0.0, 'mtm': 0.0, 'trend': 'stable',
                       'invoices_sent': 0, 'invoices_paid': 0, 'invoices_overdue': 0},
            'completed_tasks': [],
            'bottlenecks': [],
            'suggestions': [],
            'deadlines': []
        }
        
        self.service._save_briefing(briefing)
        
        # Verify file created
        expected_filename = "20240101_CEO_Briefing.md"
        expected_path = self.vault_path / "Briefings" / expected_filename
        
        self.assertTrue(expected_path.exists())
        self.assertTrue(expected_path.read_text(encoding='utf-8').startswith('---'))
    
    def test_save_briefing_markdown_content(self):
        """Test saved briefing has Markdown content"""
        briefing = {
            'generated': datetime.now().isoformat(),
            'period': {'start': '2024-01-01', 'end': '2024-01-07'},
            'revenue': {'this_week': 1000.0, 'mtm': 5000.0, 'trend': 'growing',
                       'invoices_sent': 5, 'invoices_paid': 4, 'invoices_overdue': 0},
            'completed_tasks': [{'type': 'email'}],
            'bottlenecks': [],
            'suggestions': [],
            'deadlines': []
        }
        
        self.service._save_briefing(briefing)
        
        # Read saved file
        expected_filename = "20240101_CEO_Briefing.md"
        expected_path = self.vault_path / "Briefings" / expected_filename
        content = expected_path.read_text(encoding='utf-8')
        
        # Verify content
        self.assertIn('# Monday Morning CEO Briefing', content)
        self.assertIn('$1000.00', content)
        self.assertIn('ELYX AI Employee', content)


class TestRunCEOBriefing(unittest.TestCase):
    """Test run_ceo_briefing function"""
    
    def setUp(self):
        """Set up temp vault"""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        (self.vault_path / "Briefings").mkdir(exist_ok=True)
        (self.vault_path / "Done").mkdir(exist_ok=True)
        (self.vault_path / "Plans").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @patch.object(CEOBriefingService, '_get_revenue_data')
    @patch.object(CEOBriefingService, '_get_completed_tasks')
    @patch.object(CEOBriefingService, '_identify_bottlenecks')
    @patch.object(CEOBriefingService, '_generate_suggestions')
    @patch.object(CEOBriefingService, '_get_upcoming_deadlines')
    def test_run_ceo_briefing(
        self, mock_deadlines, mock_suggestions, mock_bottlenecks,
        mock_tasks, mock_revenue
    ):
        """Test run_ceo_briefing function"""
        mock_revenue.return_value = {'this_week': 1000.0}
        mock_tasks.return_value = [{'type': 'email'}]
        mock_bottlenecks.return_value = []
        mock_suggestions.return_value = []
        mock_deadlines.return_value = []
        
        result = run_ceo_briefing(str(self.vault_path))
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn('period', result)
        self.assertIn('revenue', result)


if __name__ == "__main__":
    unittest.main(verbosity=2)

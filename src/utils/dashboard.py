import json
from datetime import datetime
from pathlib import Path

def update_dashboard(vault_path, summary_data):
    """
    Update the Dashboard.md file with current status information
    """
    dashboard_path = Path(vault_path) / "Dashboard.md"

    # Create dashboard content
    dashboard_content = f"""# 🧠 AI Employee Strategic Dashboard
Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Performance Summary
- Completed Tasks: {summary_data.get('completed_today', 0)}
- Pending Approvals: {summary_data.get('pending_approvals', 0)}
- System Status: {summary_data.get('system_status', 'active')}
- Errors: {len(summary_data.get('errors', []))}
"""

    # ✨ Gold Tier: Strategic Insights
    if 'strategic_insights' in summary_data:
        dashboard_content += "\n## 💡 Strategic Insights\n"
        insights = summary_data['strategic_insights']
        dashboard_content += f"- **Performance Trend**: {insights.get('performance_trends', {}).get('trend', 'N/A')}\n"
        
        patterns = insights.get('patterns_identified', [])
        if patterns:
            dashboard_content += "- **Patterns Detected**:\n"
            for pattern in patterns[:3]:
                dashboard_content += f"  - {pattern.get('pattern', 'Unknown pattern')}\n"

    # ✨ Gold Tier: Risk Assessment
    if 'risk_assessment' in summary_data:
        dashboard_content += "\n## ⚖️ Risk Assessment\n"
        risk = summary_data['risk_assessment']
        dashboard_content += risk_summary_text(risk)

    # ✨ Platinum Tier: Global & Quantum Stats
    if 'platinum_metrics' in summary_data:
        dashboard_content += "\n## 🌐 Platinum Operations\n"
        platinum = summary_data['platinum_metrics']
        dashboard_content += f"- **Quantum Integrity**: {platinum.get('quantum_integrity', 'Verified')}\n"
        dashboard_content += f"- **Global Nodes**: {platinum.get('global_nodes', 1)} Active\n"
        
        blockchain = platinum.get('blockchain_stats', {})
        if blockchain:
            dashboard_content += f"- **Blockchain**: {blockchain.get('total_blocks', 0)} blocks (Verified: {blockchain.get('integrity_verified', 'Yes')})\n"
            
        fed_learning = platinum.get('federated_learning', {})
        if fed_learning:
            dashboard_content += f"- **AI Model Version**: {fed_learning.get('model_version', '1.0.0')}\n"

    dashboard_content += "\n## 🕒 Recent Activities\n"
    for activity in summary_data.get('recent_activities', []):
        dashboard_content += f"- {activity}\n"

    if summary_data.get('errors'):
        dashboard_content += "\n## ❌ Errors\n"
        for error in summary_data.get('errors', []):
            dashboard_content += f"- {error}\n"

    dashboard_content += f"\n\n---\n*Last Update: {datetime.now().isoformat()}*"

    # Write to dashboard file
    dashboard_path.write_text(dashboard_content)
    return dashboard_path

def risk_summary_text(risk):
    text = f"- **Overall Risk Level**: {risk.get('risk_level', 'Low')}\n"
    text += f"- **Risk Score**: {risk.get('risk_score', 0):.2f}\n"
    return text

def get_dashboard_summary(vault_path):
    """
    Get current dashboard summary data
    """
    # Count files in various directories
    vault = Path(vault_path)

    needs_action_count = len(list((vault / "Needs_Action").glob("*.md")))
    pending_approval_count = len(list((vault / "Pending_Approval").glob("*.md")))
    completed_today_count = len(list((vault / "Done").glob("*.md")))

    return {
        "completed_today": completed_today_count,
        "pending_approvals": pending_approval_count,
        "needs_action": needs_action_count,
        "system_status": "active",
        "recent_activities": [],
        "errors": []
    }
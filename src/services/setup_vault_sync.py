#!/usr/bin/env python3
"""
Setup ELYX Vault Git Sync
Interactive setup wizard for GitHub vault synchronization
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    print("=" * 70)
    print("ELYX Vault Git Sync - Setup Wizard")
    print("=" * 70)
    print()

def check_git_installed():
    """Check if Git is installed"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"[OK] Git installed: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("[ERROR] Git not found!")
        print("\nInstall Git from: https://git-scm.com/download/win")
        return False

def create_github_repo_instructions():
    """Show instructions for creating GitHub repository"""
    print("\n" + "=" * 70)
    print("STEP 1: Create GitHub Repository")
    print("=" * 70)
    print()
    print("1. Go to: https://github.com/new")
    print("2. Repository name: elyx-vault (or your preferred name)")
    print("3. Set to PRIVATE (contains your personal data!)")
    print("4. DON'T initialize with README, .gitignore, or license")
    print("5. Click 'Create repository'")
    print()
    print("6. Copy the repository URL (looks like):")
    print("   https://github.com/USERNAME/elyx-vault.git")
    print()
    
    response = input("Press Enter when you've created the repository...")
    
    return input("Enter your repository URL: ").strip()

def initialize_vault_git(vault_path: str, repo_url: str):
    """Initialize Git in vault"""
    print("\n" + "=" * 70)
    print("STEP 2: Initialize Vault Git Repository")
    print("=" * 70)
    print()
    
    from sync_vault import VaultSync
    
    sync = VaultSync(vault_path=vault_path, repo_url=repo_url)
    
    # Initialize Git
    if not sync.initialize_git():
        print("[ERROR] Failed to initialize Git")
        return False
    
    # Setup remote
    if not sync.setup_remote(repo_url):
        print("[ERROR] Failed to setup remote")
        return False
    
    print("\n[OK] Vault Git repository initialized")
    return True

def do_initial_commit(vault_path: str):
    """Do initial commit and push"""
    print("\n" + "=" * 70)
    print("STEP 3: Initial Commit and Push")
    print("=" * 70)
    print()
    
    from sync_vault import VaultSync
    
    sync = VaultSync(vault_path=vault_path)
    
    # Commit
    if not sync.commit_changes("[INIT] Initial vault backup"):
        print("[ERROR] Failed to commit")
        return False
    
    # Push
    print("\nPushing to GitHub (this may take a while for large vaults)...")
    if not sync.push_changes():
        print("[WARNING] Push failed. Check your internet connection and try again.")
        print("Run: python src/services/sync_vault.py --push")
        return False
    
    print("\n[OK] Initial backup complete!")
    return True

def setup_scheduled_task():
    """Setup Windows Task Scheduler for hourly sync"""
    print("\n" + "=" * 70)
    print("STEP 4: Setup Automatic Hourly Sync")
    print("=" * 70)
    print()
    
    print("This will create a Windows Task to sync your vault every hour.")
    print()
    
    response = input("Setup automatic sync? (y/n): ").strip().lower()
    
    if response != 'y':
        print("[INFO] Skipping automatic sync setup")
        print("You can run manual sync with: python src/services/sync_vault.py")
        return True
    
    # Create scheduled task
    python_exe = sys.executable
    project_root = Path(__file__).parent.parent.parent
    sync_script = project_root / 'src' / 'services' / 'sync_vault.py'
    
    cmd = [
        'schtasks', '/Create',
        '/TN', 'ELYX_Vault_Sync',
        '/TR', f'"{python_exe}" "{sync_script}" --pull',
        '/SC', 'HOURLY',
        '/MO', '1',
        '/RL', 'HIGHEST',
        '/F'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("\n[OK] Scheduled task created: ELYX_Vault_Sync")
        print("     Syncs every hour automatically")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Failed to create scheduled task: {e}")
        print("\nYou can create it manually:")
        print("1. Open Task Scheduler (taskschd.msc)")
        print("2. Create Basic Task")
        print("3. Name: ELYX_Vault_Sync")
        print("4. Trigger: Hourly")
        print(f"5. Action: {python_exe} {sync_script} --pull")
        return False

def print_summary(vault_path: str, repo_url: str):
    """Print setup summary"""
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print()
    print(f"Vault Path: {vault_path}")
    print(f"Repository: {repo_url}")
    print()
    print("Commands:")
    print("  Manual sync:     python src/services/sync_vault.py")
    print("  Sync with pull:  python src/services/sync_vault.py --pull")
    print("  Status:          python src/services/sync_vault.py --status")
    print()
    print("View your vault on GitHub:")
    print(f"  {repo_url.replace('.git', '')}")
    print()
    print("=" * 70)

def main():
    """Main setup function"""
    print_header()
    
    # Check Git
    if not check_git_installed():
        sys.exit(1)
    
    # Get repository URL
    repo_url = create_github_repo_instructions()
    
    if not repo_url:
        print("[ERROR] Repository URL required")
        sys.exit(1)
    
    # Get vault path
    vault_path = input("\nVault path [obsidian_vault]: ").strip()
    if not vault_path:
        vault_path = "obsidian_vault"
    
    # Initialize Git
    if not initialize_vault_git(vault_path, repo_url):
        sys.exit(1)
    
    # Initial commit
    if not do_initial_commit(vault_path):
        print("\n[WARNING] Initial commit failed, but Git is initialized")
        print("You can commit manually later")
    
    # Setup scheduled task
    setup_scheduled_task()
    
    # Summary
    print_summary(vault_path, repo_url)

if __name__ == "__main__":
    main()

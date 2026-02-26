#!/usr/bin/env python3
"""
ELYX Vault Git Sync
Automatically sync Obsidian vault to GitHub for backup and version control

Features:
- Auto-commit vault changes
- Push to remote GitHub repository
- Exclude sensitive files (.env, sessions, credentials)
- Hourly sync via Task Scheduler
- Conflict resolution
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

class VaultSync:
    def __init__(self, vault_path: str = "obsidian_vault", repo_url: str = None):
        self.vault_path = Path(vault_path)
        self.repo_url = repo_url or os.getenv('ELYX_VAULT_REPO_URL', '')
        self.git_dir = self.vault_path / '.git'
        
        # Files/folders to exclude from sync
        self.excluded_paths = [
            '.git/',
            '.trash/',
            '*.log',
            'Logs/',
            'Attachments/',
            '__pycache__/',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db'
        ]
        
    def is_git_initialized(self) -> bool:
        """Check if Git is initialized in vault"""
        return self.git_dir.exists()
    
    def initialize_git(self):
        """Initialize Git repository in vault"""
        print("[INIT] Initializing Git repository in vault...")
        
        try:
            # Initialize git
            subprocess.run(['git', 'init'], cwd=self.vault_path, check=True, capture_output=True)
            
            # Create .gitignore
            self.create_gitignore()
            
            print("[OK] Git repository initialized")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to initialize Git: {e}")
            return False
    
    def create_gitignore(self):
        """Create .gitignore file for vault"""
        gitignore_path = self.vault_path / '.gitignore'
        
        content = """# ELYX Vault .gitignore
# Never commit sensitive data

# Logs and temporary files
*.log
Logs/
.trash/
__pycache__/
*.pyc
*.pyo

# Attachments (optional - uncomment if you don't want to sync large files)
# Attachments/

# System files
.DS_Store
Thumbs.db
desktop.ini

# Credentials and secrets (NEVER commit these)
*.key
*.pem
*.crt
*credentials*
*secret*
*.env

# Session data (browser sessions)
*sessions*/
*.session
session_*.json

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db
"""
        
        gitignore_path.write_text(content, encoding='utf-8')
        print("[OK] Created .gitignore")
    
    def setup_remote(self, repo_url: str):
        """Setup GitHub remote repository"""
        print(f"[INIT] Setting up remote repository: {repo_url}")
        
        try:
            # Remove existing remote if any
            subprocess.run(['git', 'remote', 'remove', 'origin'], 
                          cwd=self.vault_path, check=False, capture_output=True)
            
            # Add new remote
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], 
                          cwd=self.vault_path, check=True, capture_output=True)
            
            print(f"[OK] Remote repository configured: {repo_url}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to setup remote: {e}")
            return False
    
    def get_changes(self) -> tuple:
        """Get list of changed files"""
        try:
            # Get status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   cwd=self.vault_path, check=True, 
                                   capture_output=True, text=True)
            
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            added = []
            modified = []
            deleted = []
            
            for line in lines:
                if not line.strip():
                    continue
                    
                status = line[:2].strip()
                filename = line[3:].strip()
                
                if status in ['A', '??']:
                    added.append(filename)
                elif status in ['M', 'MM']:
                    modified.append(filename)
                elif status in ['D']:
                    deleted.append(filename)
            
            return added, modified, deleted
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to get changes: {e}")
            return [], [], []
    
    def commit_changes(self, message: str = None):
        """Commit all changes"""
        if not message:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"[ELYX Auto-Sync] Vault backup - {timestamp}"
        
        print(f"[COMMIT] Committing changes: {message}")
        
        try:
            # Add all changes
            subprocess.run(['git', 'add', '-A'], 
                          cwd=self.vault_path, check=True, capture_output=True)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', message], 
                          cwd=self.vault_path, check=True, capture_output=True)
            
            print("[OK] Changes committed")
            return True
        except subprocess.CalledProcessError as e:
            # No changes to commit is OK
            if 'nothing to commit' in str(e.stderr.decode()):
                print("[INFO] No changes to commit")
                return True
            print(f"[ERROR] Failed to commit: {e}")
            return False
    
    def push_changes(self):
        """Push changes to remote repository"""
        print("[PUSH] Pushing changes to remote...")
        
        try:
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                          cwd=self.vault_path, check=True, capture_output=True, timeout=60)
            
            print("[OK] Changes pushed to remote")
            return True
        except subprocess.TimeoutExpired:
            print("[WARNING] Push timed out (large repository?)")
            return False
        except subprocess.CalledProcessError as e:
            # Try with master branch
            try:
                subprocess.run(['git', 'push', '-u', 'origin', 'master'], 
                              cwd=self.vault_path, check=True, capture_output=True, timeout=60)
                print("[OK] Changes pushed to remote")
                return True
            except:
                print(f"[ERROR] Failed to push: {e}")
                print("[INFO] Make sure you have a remote repository configured")
                return False
    
    def pull_changes(self):
        """Pull changes from remote repository"""
        print("[PULL] Pulling changes from remote...")
        
        try:
            subprocess.run(['git', 'pull'], 
                          cwd=self.vault_path, check=True, capture_output=True, timeout=60)
            
            print("[OK] Changes pulled from remote")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to pull: {e}")
            return False
    
    def sync(self, push: bool = True, pull: bool = False):
        """
        Full sync operation
        
        Args:
            push: Push changes to remote
            pull: Pull changes from remote before pushing
        """
        print("=" * 70)
        print("ELYX Vault Git Sync")
        print("=" * 70)
        print()
        
        # Check if git is initialized
        if not self.is_git_initialized():
            print("[INIT] Git not initialized. Initializing...")
            if not self.initialize_git():
                print("[ERROR] Failed to initialize Git. Exiting.")
                return False
        
        # Pull latest changes if requested
        if pull and self.repo_url:
            self.pull_changes()
        
        # Get changes
        added, modified, deleted = self.get_changes()
        
        total_changes = len(added) + len(modified) + len(deleted)
        
        if total_changes > 0:
            print(f"[CHANGES] Found {total_changes} changes:")
            if added:
                print(f"  - Added: {len(added)} files")
            if modified:
                print(f"  - Modified: {len(modified)} files")
            if deleted:
                print(f"  - Deleted: {len(deleted)} files")
            
            # Commit changes
            if not self.commit_changes():
                print("[ERROR] Failed to commit changes. Exiting.")
                return False
            
            # Push changes if requested
            if push and self.repo_url:
                if not self.push_changes():
                    print("[WARNING] Failed to push changes (will retry next sync)")
        else:
            print("[INFO] No changes to sync")
        
        print()
        print("=" * 70)
        print("[OK] Sync complete")
        print("=" * 70)
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ELYX Vault Git Sync')
    parser.add_argument('--repo', '-r', help='GitHub repository URL', default=None)
    parser.add_argument('--init', '-i', action='store_true', help='Initialize Git repository')
    parser.add_argument('--no-push', action='store_true', help='Don\'t push to remote')
    parser.add_argument('--pull', '-p', action='store_true', help='Pull from remote before pushing')
    parser.add_argument('--vault', '-v', default='obsidian_vault', help='Path to vault')
    
    args = parser.parse_args()
    
    # Create sync instance
    sync = VaultSync(vault_path=args.vault, repo_url=args.repo)
    
    # Initialize if requested
    if args.init:
        if not sync.initialize_git():
            sys.exit(1)
        
        if args.repo:
            if not sync.setup_remote(args.repo):
                sys.exit(1)
        
        print("\n[OK] Git initialized successfully!")
        print("\nNext steps:")
        print("1. Create a private GitHub repository")
        print("2. Run: python sync_vault.py --repo https://github.com/username/repo.git")
        print("3. Setup scheduled task for automatic sync")
        sys.exit(0)
    
    # Run sync
    if not sync.sync(push=not args.no_push, pull=args.pull):
        sys.exit(1)

if __name__ == "__main__":
    main()

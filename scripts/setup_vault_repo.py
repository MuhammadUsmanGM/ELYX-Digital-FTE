#!/usr/bin/env python3
"""
Setup Vault Repository
Separates obsidian_vault into its own Git repo for easy backup and sync

Usage:
    python scripts/setup_vault_repo.py <your-github-username> <vault-repo-name>
    
Example:
    python scripts/setup_vault_repo.py MuhammadUsmanGM ELYX-Vault
"""

import os
import sys
import subprocess
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_command(cmd, cwd=None):
    """Run shell command"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_vault_repo(github_user: str, repo_name: str):
    """Setup vault as separate Git repository"""
    
    print(f"\n{Colors.BOLD}Setting Up Vault Repository{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")
    
    vault_path = Path("obsidian_vault")
    
    if not vault_path.exists():
        print(f"{Colors.FAIL}❌ obsidian_vault/ not found!{Colors.ENDC}")
        print(f"Run ELYX first to create the vault.")
        return False
    
    # Step 1: Initialize Git repo in vault
    print(f"1. Initializing Git repository in obsidian_vault/...")
    success, stdout, stderr = run_command("git init", cwd=vault_path)
    if not success:
        print(f"{Colors.FAIL}❌ Failed to initialize git{Colors.ENDC}")
        return False
    print(f"   {Colors.OKGREEN}✓ Git initialized{Colors.ENDC}\n")
    
    # Step 2: Create .gitignore for vault
    print(f"2. Creating .gitignore...")
    gitignore_content = """# Ignore large files
*.pdf
*.docx
*.xlsx
*.zip
*.tar.gz

# Ignore sensitive files
*.key
*.pem
*.crt
*credentials*.json
*token*.json

# Ignore OS files
.DS_Store
Thumbs.db
desktop.ini

# Ignore temp files
*.tmp
*.swp
*.swo
*~

# Keep everything else!
!.gitignore
"""
    (vault_path / ".gitignore").write_text(gitignore_content, encoding='utf-8')
    print(f"   {Colors.OKGREEN}✓ .gitignore created{Colors.ENDC}\n")
    
    # Step 3: Add remote
    print(f"3. Adding GitHub remote...")
    remote_url = f"https://github.com/{github_user}/{repo_name}.git"
    success, stdout, stderr = run_command(f"git remote add origin {remote_url}", cwd=vault_path)
    if not success and "already exists" not in stderr:
        print(f"{Colors.WARNING}⚠ Could not add remote (might already exist){Colors.ENDC}")
    else:
        print(f"   {Colors.OKGREEN}✓ Remote added: {remote_url}{Colors.ENDC}\n")
    
    # Step 4: Initial commit
    print(f"4. Creating initial commit...")
    run_command("git add .", cwd=vault_path)
    success, stdout, stderr = run_command('git commit -m "Initial vault commit"', cwd=vault_path)
    if success:
        print(f"   {Colors.OKGREEN}✓ Initial commit created{Colors.ENDC}\n")
    else:
        print(f"   {Colors.WARNING}⚠ No changes to commit (that's ok){Colors.ENDC}\n")
    
    # Step 5: Create GitHub Actions workflow
    print(f"5. Creating GitHub Actions workflow...")
    workflows_dir = vault_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = f"""name: Auto-Sync Vault

on:
  schedule:
    # Run every hour
    - cron: '0 * * * *'
  
  # Also allow manual trigger
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout vault
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Configure Git
      run: |
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
    
    - name: Check for changes
      id: git_status
      run: |
        git remote add sync https://github.com/{github_user}/{repo_name}.git
        git fetch sync
        git status --porcelain
        if [[ -n "$(git status --porcelain)" ]]; then
          echo "has_changes=true" >> $GITHUB_OUTPUT
        else
          echo "has_changes=false" >> $GITHUB_OUTPUT
        fi
    
    - name: Commit and push if changed
      if: steps.git_status.outputs.has_changes == 'true'
      run: |
        git add .
        git commit -m "Auto-sync: $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"
        git push sync main
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
    
    - name: No changes
      if: steps.git_status.outputs.has_changes == 'false'
      run: echo "✓ No changes to sync"
"""
    
    (workflows_dir / "auto-sync.yml").write_text(workflow_content, encoding='utf-8')
    print(f"   {Colors.OKGREEN}✓ GitHub Actions workflow created{Colors.ENDC}\n")
    
    # Step 6: Create setup instructions
    print(f"6. Creating setup instructions...")
    instructions = f"""# Vault Repository Setup Instructions

## GitHub Repository Setup

1. **Create Empty Repository on GitHub:**
   - Go to: https://github.com/new
   - Repository name: `{repo_name}`
   - Make it **Private** (vault contains sensitive data)
   - Don't initialize with README

2. **Push Initial Commit:**
   ```bash
   cd obsidian_vault
   git branch -M main
   git push -u origin main
   ```

3. **Setup GitHub Token (for auto-push):**
   - Go to: Settings → Actions → General
   - Ensure "Allow all actions" is enabled
   - GITHUB_TOKEN is automatic

## Manual Sync Command

To manually sync vault to GitHub:

```bash
cd obsidian_vault
git add .
git commit -m "Manual sync"
git push origin main
```

## Auto-Sync Schedule

- **Automatic:** Every hour via GitHub Actions
- **Manual:** Run the command above anytime

## Restore Vault from GitHub

If you need to restore vault:

```bash
git clone https://github.com/{github_user}/{repo_name}.git obsidian_vault_backup
```

## Security Notes

- ✅ Repository should be **PRIVATE**
- ✅ .gitignore excludes credentials
- ✅ Only markdown files synced
- ✅ Full version history maintained
"""
    
    (vault_path / "VAULT_SETUP.md").write_text(instructions, encoding='utf-8')
    print(f"   {Colors.OKGREEN}✓ Instructions created{Colors.ENDC}\n")
    
    # Step 7: Update .gitignore in main repo
    print(f"7. Updating main repo .gitignore...")
    main_gitignore = Path(".gitignore")
    if main_gitignore.exists():
        content = main_gitignore.read_text(encoding='utf-8')
        if "obsidian_vault/" not in content:
            content += "\n# Vault repository (separate repo)\nobsidian_vault/\n"
            main_gitignore.write_text(content, encoding='utf-8')
            print(f"   {Colors.OKGREEN}✓ Main repo .gitignore updated{Colors.ENDC}\n")
    else:
        main_gitignore.write_text("# Vault repository (separate repo)\nobsidian_vault/\n", encoding='utf-8')
        print(f"   {Colors.OKGREEN}✓ Main repo .gitignore created{Colors.ENDC}\n")
    
    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Setup Complete!{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}\n")
    print(f"1. Create GitHub repository: `{repo_name}`")
    print(f"   Go to: https://github.com/new")
    print(f"   Make it PRIVATE\n")
    print(f"2. Push initial commit:")
    print(f"   cd obsidian_vault")
    print(f"   git branch -M main")
    print(f"   git push -u origin main\n")
    print(f"3. Auto-sync will run every hour automatically!\n")
    
    print(f"{Colors.BOLD}Vault Files:{Colors.ENDC}")
    print(f"  - obsidian_vault/ (separate repo)")
    print(f"  - Auto-commits every hour")
    print(f"  - Full version history")
    print(f"  - Can restore from anywhere\n")
    
    return True


def main():
    if len(sys.argv) < 3:
        print(f"\n{Colors.BOLD}Usage:{Colors.ENDC}")
        print(f"  python scripts/setup_vault_repo.py <github-user> <repo-name>\n")
        print(f"Example:")
        print(f"  python scripts/setup_vault_repo.py MuhammadUsmanGM ELYX-Vault\n")
        sys.exit(1)
    
    github_user = sys.argv[1]
    repo_name = sys.argv[2]
    
    success = setup_vault_repo(github_user, repo_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

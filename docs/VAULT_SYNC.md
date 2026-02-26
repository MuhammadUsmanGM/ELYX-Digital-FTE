# ELYX Vault Git Sync - Setup Guide

**Platinum Tier Feature - Local Implementation**

Automatically backup your Obsidian vault to GitHub with version control and hourly sync.

---

## 🎯 **What This Does:**

- ✅ **Automatic Backup**: Sync vault to GitHub every hour
- ✅ **Version Control**: Track all changes with Git history
- ✅ **Disaster Recovery**: Restore vault from GitHub if PC fails
- ✅ **Multi-Machine Sync**: Sync between multiple computers
- ✅ **Privacy**: Private repository, sensitive files excluded

---

## 📋 **Prerequisites:**

1. **Git Installed**
   - Download: https://git-scm.com/download/win
   - Verify: `git --version`

2. **GitHub Account** (free)
   - Sign up: https://github.com

3. **Private Repository** (free for private repos)

---

## 🚀 **Quick Setup (5 minutes):**

### **Step 1: Run Setup Wizard**

```bash
cd C:\Users\Usman Mustafa\OneDrive\Desktop\ELYX-Personal-AI-Employee
python src/services/setup_vault_sync.py
```

### **Step 2: Follow Prompts**

The wizard will:
1. Check Git installation
2. Guide you to create GitHub repository
3. Initialize Git in vault
4. Do initial commit and push
5. Setup hourly automatic sync

### **Step 3: Done!**

Your vault is now backed up to GitHub and syncs every hour!

---

## 📖 **Manual Setup (Alternative):**

### **1. Create GitHub Repository**

1. Go to: https://github.com/new
2. Name: `elyx-vault` (or your choice)
3. **Set to PRIVATE** (contains personal data!)
4. Don't initialize with README
5. Click "Create repository"
6. Copy the URL (e.g., `https://github.com/username/elyx-vault.git`)

### **2. Initialize Vault Git**

```bash
cd obsidian_vault
git init
```

### **3. Create .gitignore**

Create `obsidian_vault/.gitignore`:

```gitignore
# ELYX Vault .gitignore

# Logs
*.log
Logs/

# Trash
.trash/

# Sessions (browser login data - NEVER commit)
*sessions*/
*.session
session_*.json

# Credentials
*credentials*
*.key
*.pem
*.env

# Cache
__pycache__/
*.pyc

# System files
.DS_Store
Thumbs.db
```

### **4. Add Remote Repository**

```bash
cd obsidian_vault
git remote add origin https://github.com/YOUR_USERNAME/elyx-vault.git
```

### **5. Initial Commit**

```bash
git add .
git commit -m "[INIT] Initial vault backup"
git branch -M main
git push -u origin main
```

### **6. Setup Hourly Sync**

```bash
# Run setup wizard for scheduled task
python src/services/setup_vault_sync.py
```

Or manually create Task Scheduler task:

1. Open **Task Scheduler** (search in Start menu)
2. **Create Basic Task**
3. Name: `ELYX Vault Sync`
4. Trigger: **Hourly**
5. Action: **Start a program**
6. Program: `python.exe`
7. Arguments: `src/services/sync_vault.py --pull`
8. Start in: `C:\Users\Usman Mustafa\OneDrive\Desktop\ELYX-Personal-AI-Employee`

---

## 🔧 **Usage:**

### **Manual Sync:**

```bash
# Sync vault to GitHub
python src/services/sync_vault.py

# Pull latest changes then push
python src/services/sync_vault.py --pull

# Don't push (local commit only)
python src/services/sync_vault.py --no-push
```

### **Check Status:**

```bash
cd obsidian_vault
git status
```

### **View History:**

```bash
cd obsidian_vault
git log --oneline
```

---

## 🔒 **Security:**

### **What's NEVER Synced:**

| File Type | Why |
| :--- | :--- |
| `*sessions*/` | Browser login cookies |
| `*credentials*` | API keys and passwords |
| `*.env` | Environment variables |
| `Logs/` | System logs |
| `.trash/` | Deleted files |

### **Best Practices:**

1. ✅ **Use Private Repository** - Never public
2. ✅ **Enable 2FA on GitHub** - Extra security
3. ✅ **Don't commit .env files** - Already in .gitignore
4. ✅ **Review changes before push** - `git status`

---

## 🔄 **Multi-Machine Sync:**

If you have multiple computers:

### **Computer 1 (Home):**
```bash
# Setup as above
python src/services/setup_vault_sync.py
```

### **Computer 2 (Work):**
```bash
# Clone vault from GitHub
git clone https://github.com/username/elyx-vault.git obsidian_vault

# Setup sync
cd ELYX-Personal-AI-Employee
python src/services/setup_vault_sync.py
```

**Now both computers sync via GitHub!**

---

## ⚠️ **Troubleshooting:**

### **"Git not found"**
```bash
# Install Git
https://git-scm.com/download/win

# Restart terminal after install
```

### **"Authentication failed"**
```bash
# Use GitHub Personal Access Token instead of password
# Create token: https://github.com/settings/tokens
# Use token as password when prompted
```

### **"Large file warning"**
```bash
# Attachments folder can be large
# Add to .gitignore if needed:
echo "Attachments/" >> obsidian_vault/.gitignore
```

### **"Push failed"**
```bash
# Check internet connection
# Verify repository URL:
cd obsidian_vault
git remote -v

# Retry push:
python src/services/sync_vault.py
```

---

## 📊 **What's Synced:**

| Folder | Synced? | Notes |
| :--- | :--- | :--- |
| `Dashboard.md` | ✅ Yes | Main dashboard |
| `Company_Handbook.md` | ✅ Yes | Rules and procedures |
| `Needs_Action/` | ✅ Yes | Pending tasks |
| `Done/` | ✅ Yes | Completed tasks |
| `Briefings/` | ✅ Yes | CEO briefings |
| `Logs/` | ❌ No | System logs excluded |
| `Attachments/` | ⚠️ Optional | Can be large |
| `sessions/` | ❌ Never | Security risk |

---

## 🎯 **Next Steps:**

After setup:

1. ✅ **Verify first sync worked**
   - Check GitHub repository
   - See your vault files online

2. ✅ **Test restore** (optional)
   - Clone to different folder
   - Verify all files restored

3. ✅ **Monitor sync**
   - Check Task Scheduler
   - Verify hourly commits

---

## 📞 **Support:**

- **View Sync Script**: `src/services/sync_vault.py`
- **Setup Script**: `src/services/setup_vault_sync.py`
- **Documentation**: `docs/VAULT_SYNC.md`

---

**Your vault is now backed up and version controlled!** 🎉

**Platinum Tier Progress: ~40% Complete** (without cloud deployment)

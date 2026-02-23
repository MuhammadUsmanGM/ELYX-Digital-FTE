# ELYX + Claude Code CLI Setup Guide

## ✅ Quick Setup (If You Have Claude Code CLI)

### Step 1: Verify Claude Code Installation

```bash
# Check if Claude Code CLI is installed
claude --version

# You should see something like:
# claude 0.1.10 (or higher)
```

### Step 2: Verify You're Logged In

```bash
# Check authentication status
claude auth status

# You should see:
# ✓ Logged in as: your-email@example.com
# ✓ Subscription: Claude Code Pro (or Free tier)
```

### Step 3: Configure ELYX

**Edit `.env` file:**

```bash
# Set Claude Code as your AI brain
ELYX_ACTIVE_BRAIN=claude

# That's it! NO API KEY NEEDED!
```

**Important:** Delete or leave blank the `CLAUDE_API_KEY` line. Claude Code CLI uses your existing authentication - no API key required.

---

## 🚀 Run ELYX

```bash
# Start the autonomous AI employee
python run_complete_system.py
```

---

## 🧪 Test Claude Code Integration

```bash
# Test that ELYX can use Claude Code
claude -p "Hello, this is a test of the ELYX AI employee system."

# If this works, ELYX can use Claude Code!
```

---

## 📋 How It Works

When you set `ELYX_ACTIVE_BRAIN=claude`, ELYX executes:

```bash
claude -p "Your task prompt here..."
```

This:
1. ✅ Uses your **existing Claude Code CLI authentication**
2. ✅ Billed to your **Claude Code subscription** (Pro or Free)
3. ✅ **No API key needed**
4. ✅ Runs locally on your machine

---

## 🔧 Alternative: Using Other AI Brains

If you want to use other AI providers instead:

### Qwen (Alibaba)

```bash
# Option 1: Qwen CLI (if installed)
ELYX_ACTIVE_BRAIN=qwen

# Option 2: Qwen API (needs API key)
ELYX_ACTIVE_BRAIN=qwen
QWEN_API_KEY=your-qwen-api-key
```

### Gemini (Google)

```bash
# Option 1: Gemini CLI (if installed)
ELYX_ACTIVE_BRAIN=gemini

# Option 2: Gemini API (needs API key)
ELYX_ACTIVE_BRAIN=gemini
GEMINI_API_KEY=your-gemini-api-key
```

### Codex (OpenAI)

```bash
# Codex CLI (if installed)
ELYX_ACTIVE_BRAIN=codex

# Or OpenAI API (needs API key)
OPENAI_API_KEY=your-openai-api-key
```

---

## ❓ Troubleshooting

### "claude: command not found"

**Solution:** Install Claude Code CLI

```bash
# macOS/Linux
curl -fsSL https://claude.ai/install | bash

# Windows (PowerShell)
iwr https://claude.ai/install.ps1 -useb | iex

# Or via npm
npm install -g @anthropic-ai/claude-code
```

### "Not logged in" or "Authentication failed"

**Solution:** Log in to Claude Code

```bash
claude login
```

This will open a browser window for authentication.

### "Rate limit exceeded"

**Solution:** You've hit your Claude Code usage limit

- **Free tier:** Limited messages per day
- **Pro tier:** Higher limits ($20/month)
- **Wait:** Limits reset every 24 hours

---

## 💡 Pro Tips

1. **Use Ralph Wiggum Loop:** ELYX automatically uses the Ralph Wiggum pattern to keep Claude working on tasks until completion.

2. **Human-in-the-Loop:** Sensitive actions (payments, new contacts) require your approval before execution.

3. **Multi-Brain Testing:** You can switch brains anytime by editing `.env`:
   ```bash
   ELYX_ACTIVE_BRAIN=claude  # Use Claude Code
   # ELYX_ACTIVE_BRAIN=qwen   # Use Qwen
   # ELYX_ACTIVE_BRAIN=gemini # Use Gemini
   ```

4. **Check Brain Status:**
   ```bash
   # See which brain is active
   python -c "from src.services.brain_factory import get_brain_factory; print(get_brain_factory().active_brain_name)"
   ```

---

## 📚 More Information

- **Architecture:** See `ARCHITECTURE.md`
- **Implementation Plan:** See `IMPLEMENTATION_PLAN.md`
- **Hackathon Document:** See `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Ralph Wiggum Pattern:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

---

**Last Updated:** February 23, 2026

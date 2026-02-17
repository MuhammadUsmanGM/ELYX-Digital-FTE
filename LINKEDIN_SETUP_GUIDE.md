# ELYX LinkedIn Setup Guide

To give ELYX its own LinkedIn capability, we use automated browser interaction via Playwright. This allows ELYX to check for urgent messages and participate in professional networking on your behalf.

---

## Step 1: Create a LinkedIn Account
1. Create a new LinkedIn account using the same email you created for ELYX (`elyx.ai.employ@gmail.com`).
2. Complete the basic profile setup (Name, Profile Picture, etc.) to make it look professional.

## Step 2: Configure Environment Variables
Add your LinkedIn credentials to the `.env` file in the project root.

1. Open `.env`.
2. Find or add the LinkedIn section:
   ```env
   # === LinkedIn Configuration ===
   LINKEDIN_USERNAME=elyx.ai.employ@gmail.com
   LINKEDIN_PASSWORD=your-secure-password
   LINKEDIN_SESSION_PATH=./linkedin_session
   LINKEDIN_CHECK_INTERVAL=300
   ```
3. Replace `your-secure-password` with the actual password for the account.

## Step 3: Install Browser Dependencies
Since ELYX "browses" LinkedIn like a human, it needs a browser engine (Chromium) installed.

1. Open your terminal in the project folder.
2. Run the following commands:
   ```bash
   pip install playwright
   playwright install chromium
   ```

## Step 4: Security Features
- **Human-Like Behavior**: ELYX checks LinkedIn every 5 minutes (`300` seconds) to avoid being flagged as a bot.
- **Urgent Filtering**: By default, ELYX only creates "Needs Action" items for messages containing keywords like: `urgent`, `asap`, `meeting`, `proposal`, `opportunity`, `help`, `important`.
- **Session Persistence**: Once ELYX logs in for the first time, it saves a session to your computer (in the `./linkedin_session` folder). This means it won't have to log in with your password every time, making it stealthy and faster.

---

## How to Test
1. Start ELYX:
   ```bash
   python run_complete_system.py
   ```
2. Send a message to ELYX's LinkedIn account from another account. Use the word **"Urgent"** in the message.
3. Watch the terminal. You should see `LinkedIn watcher started`.
4. Within a few minutes, a new file will appear in `obsidian_vault/Needs_Action/` starting with `LINKEDIN_...`.

**Setup Complete!** ELYX is now your autonomous professional representative.

# ELYX WhatsApp Setup Guide

Connecting ELYX to WhatsApp allows it to monitor your unread messages for urgent requests and respond to your commands remotely.

---

## 🛠️ Step 1: Prepare the Session
WhatsApp uses a QR code to link ELYX's browser to your phone. Because ELYX usually runs "in the background" (headless), you need to do a one-time setup to scan the code.

1. **Install Dependencies** (if not already done for LinkedIn):
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Initialize the Session**:
   To scan the QR code, ELYX needs to show you a browser window. 
   - Open `.env` and temporarily change `BROWSER_HEADLESS=true` to `BROWSER_HEADLESS=false`.
   - Run the system: `python run_complete_system.py`.
   - A Chromium window will open at `web.whatsapp.com`. 
   - **Scan the QR code** with your phone (WhatsApp > Linked Devices > Link a Device).
   - Once the chats appear, wait 30 seconds, then close the system (Ctrl+C).
   - Change `BROWSER_HEADLESS` back to `true` in your `.env`.

## ⚙️ Step 2: Configuration
Ensure your `.env` file has these settings:
```env
# === WhatsApp Configuration ===
WHATSAPP_SESSION_PATH=./whatsapp_session
WHATSAPP_CHECK_INTERVAL=3600
```

## 🛡️ Step 3: Safety & Stealth
- **Jitter Logic**: Just like LinkedIn, ELYX checks WhatsApp at random intervals around the 1-hour mark to avoid being banned.
- **Whitelist Protection**: ELYX will only acknowledge "Urgent" tasks or commands from people listed in your `obsidian_vault/Trusted_Contacts.md`.
- **Keywords**: By default, ELYX looks for: `urgent`, `asap`, `invoice`, `payment`, `help`, `emergency`, `critical`, `important`.

---

## 🤖 Two Ways ELYX Works with WhatsApp

### 1. The Watcher (Scanning)
This uses a browser to see your messages. It’s perfect for **receiving** tasks from you or your team. This is what we just set up.

### 2. The Responder (Replying)
To have ELYX **send** replies automatically, he needs access to the **WhatsApp Business API**. 
- If you have an API account, add these to your `.env`:
  ```env
  WHATSAPP_ACCESS_TOKEN=your_token
  WHATSAPP_PHONE_NUMBER_ID=your_id
  ```
- If you **don't** have the API, ELYX will still "see" your messages and create "Needs Action" files in Obsidian, but he will not send a message back to the chat. You can then reply manually from your phone.

---

## How to Test
1. Start ELYX: `python run_complete_system.py`.
2. Send a WhatsApp message to your linked number from a friend's phone (or your own work phone).
3. Include the word **"Urgent"**.
4. Within an hour, ELYX will create a file in `obsidian_vault/Needs_Action/WHATSAPP_...md`.

**Setup Complete!** ELYX is now your eyes on WhatsApp.

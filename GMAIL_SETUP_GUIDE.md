# ELYX Gmail Setup Guide

To give ELYX its own email capability, you need to generate a `credentials.json` file from Google. This authorizes ELYX to send and receive emails on your behalf.

The file `setup_gmail_auth.py` is **NOT** a guide—it is a **setup script** that you will run *after* you follow the steps below.

---

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown in the top bar and select **"New Project"**.
3. Name it `ELYX-Mail` (or similar) and click **Create**.
4. Select the newly created project.

## Step 2: Enable the Gmail API

1. In the sidebar, go to **APIs & Services** > **Library**.
2. Search for **"Gmail API"**.
3. Click on it and click **Enable**.

## Step 3: Configure Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** (unless you have a Google Workspace organization, then select Internal) and click **Create**.
3. Fill in required fields:
   - **App name**: `ELYX`
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Click **Save and Continue**.
5. **Scopes**: Click **Add or Remove Scopes**.
   - Search for and select these scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.modify`
   - Click **Update**, then **Save and Continue**.
6. **Test Users**:
   - Click **Add Users**.
   - Enter the email address you want ELYX to use (e.g., your personal gmail or a dedicated one).
   - Click **Add**, then **Save and Continue**.

## Step 4: Create Credentials

1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** > **OAuth client ID**.
3. **Application type**: Select **Desktop app**.
4. **Name**: `ELYX Client`.
5. Click **Create**.
6. A popup will appear. Click **Download JSON** (it looks like a download icon).
7. Save the file to your ELYX project folder:
   - Path: `c:\Users\Usman Mustafa\OneDrive\Desktop\ELYX-Personal-AI-Employee\`
   - **IMPORTANT**: Rename the file to `credentials.json`.

---

## Step 5: Run the Setup Script

Once `credentials.json` is in the folder:

1. Open your terminal in the project folder.
2. Run the script we created:
   ```bash
   python setup_gmail_auth.py
   ```
3. A browser window will open asking you to log in to Google.
   - You may see a "Google hasn't verified this app" warning (because you just created it).
   - Click **Advanced** > **Go to ELYX (unsafe)**.
4. Click **Continue** / **Allow** to grant permissions.
5. The script will generate a `token.json` file.

**Setup Complete!** ELYX can now read and send emails.

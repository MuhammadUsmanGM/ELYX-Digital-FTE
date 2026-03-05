"""
setup_sessions.py - One-time login script for all social media platforms and Odoo.

Run this ONCE before starting ELYX. It opens each platform in a visible
Playwright browser so you can log in manually. Sessions are saved to
the sessions/ directory and reused automatically afterward.

For Odoo, it will guide you through API credential setup.

Usage:
    python setup_sessions.py                    # All platforms
    python setup_sessions.py whatsapp           # Single platform
    python setup_sessions.py linkedin twitter   # Multiple platforms
    python setup_sessions.py odoo               # Odoo setup only
"""

import sys
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSIONS_DIR = Path("./sessions")

PLATFORMS = {
    "whatsapp": {
        "url": "https://web.whatsapp.com",
        "session_dir": "whatsapp_session",
        "logged_in_selector": '[data-testid="chat-list"], #pane-side, [aria-label="Chat list"], [aria-label="Chats"], div[data-tab="3"]',
        "instructions": (
            "1. Open WhatsApp on your phone\n"
            "2. Tap Settings > Linked Devices > Link a Device\n"
            "3. Scan the QR code shown in the browser\n"
            "4. Wait until your chats load — then press Enter here"
        ),
        "wait_seconds": 120,
    },
    "linkedin": {
        "url": "https://www.linkedin.com/login",
        "session_dir": "linkedin_session",
        # Same selector as linkedin_watcher._ensure_logged_in so setup and watcher stay in sync
        "logged_in_selector": "nav.global-nav",
        "instructions": (
            "Log in to LinkedIn with your email and password.\n"
            "Complete any 2FA if prompted. Once your feed loads — press Enter here"
        ),
        "wait_seconds": 60,
        # Fallback: consider logged in if URL is feed (not login page)
        "logged_in_url_contains": "/feed/",
        "logged_in_url_excludes": "login",
    },
    "facebook": {
        "url": "https://www.facebook.com/login",
        "session_dir": "facebook_session",
        "logged_in_selector": '[aria-label="Facebook"]',
        "instructions": (
            "Log in to Facebook with your email and password.\n"
            "Once your home feed loads — press Enter here"
        ),
        "wait_seconds": 60,
    },
    "instagram": {
        "url": "https://www.instagram.com/accounts/login/",
        "session_dir": "instagram_session",
        "logged_in_selector": 'a[href="/direct/inbox/"]',
        "instructions": (
            "Log in to Instagram with your username and password.\n"
            "Once your feed loads — press Enter here"
        ),
        "wait_seconds": 60,
    },
    "twitter": {
        "url": "https://x.com/login",
        "session_dir": "twitter_session",
        "logged_in_selector": '[data-testid="SideNav_AccountSwitcher_Button"]',
        "instructions": (
            "Log in to X (Twitter) with your username and password.\n"
            "Once your home timeline loads — press Enter here"
        ),
        "wait_seconds": 60,
        "logged_in_url_contains": "/home",
        "logged_in_url_excludes": "login",
    },
    "odoo": {
        "url": "https://elyx-ai.odoo.com",
        "session_dir": "odoo_session",
        "logged_in_selector": '.o_menu_systray, .o_dropdown_menu',
        "instructions": (
            "Log in to Odoo with your email and password.\n"
            "Once the Odoo dashboard loads — press Enter here.\n"
            "After login, you'll be prompted to enter Odoo URL, Database, and API credentials."
        ),
        "wait_seconds": 60,
        "requires_api_setup": True,
    },
}


def setup_platform(name: str, config: dict):
    session_dir = SESSIONS_DIR / config["session_dir"]
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Setting up: {name.upper()}")
    print(f"  Session will be saved to: {session_dir}")
    print(f"{'='*60}")
    print(f"\n{config['instructions']}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(session_dir),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"],
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(config["url"], timeout=60000)

        # Wait for user to log in
        input(f"\n>>> Browser is open. Log in to {name.upper()}, then press Enter here to save session...")

        # Verify login worked
        verified = False
        try:
            page.wait_for_selector(config["logged_in_selector"], timeout=10000)
            verified = True
        except Exception:
            # Fallback: for platforms that define it, accept URL-based check
            url_contains = config.get("logged_in_url_contains")
            url_excludes = config.get("logged_in_url_excludes")
            if url_contains or url_excludes:
                current = (page.url or "")
                if (url_contains is None or url_contains in current) and (
                    url_excludes is None or url_excludes not in current
                ):
                    verified = True
        if verified:
            print(f"✓ {name.upper()} login verified — session saved!")
        else:
            print(f"⚠ Could not auto-verify {name.upper()} login, but session was saved anyway.")
            print("  If the watcher fails, run this script again for this platform.")

        # For Odoo, also setup API credentials
        if config.get("requires_api_setup"):
            setup_odoo_credentials(page)

        # Give browser a moment to flush cookies/storage to disk
        time.sleep(2)
        browser.close()

    print(f"✓ {name.upper()} session saved to {session_dir}\n")


def setup_odoo_credentials(page):
    """Guide user through Odoo API credential setup"""
    print("\n" + "="*60)
    print("  ODOO API CREDENTIALS SETUP")
    print("="*60)
    print("\nNow we'll configure Odoo API access for ELYX.\n")
    
    # Get Odoo URL
    default_url = "https://elyx-ai.odoo.com"
    odoo_url = input(f"Odoo URL [{default_url}]: ").strip() or default_url
    
    # Get Database name
    default_db = "elyx-ai"
    odoo_db = input(f"Database name [{default_db}]: ").strip() or default_db
    
    # Get Username
    default_user = "elyx.ai.employ@gmail.com"
    odoo_username = input(f"Username [{default_user}]: ").strip() or default_user
    
    # Get Password
    import getpass
    print("\nNote: Password will not be displayed as you type")
    odoo_password = getpass.getpass("Odoo password: ").strip()
    
    if not odoo_password:
        print("⚠ Password is required for Odoo integration")
        retry = input("Do you want to try again? (y/n): ").lower()
        if retry == 'y':
            setup_odoo_credentials(page)
        return
    
    # Save to .env file
    env_path = Path(".env")
    content = ""
    
    if env_path.exists():
        content = env_path.read_text(encoding='utf-8')
    
    # Remove existing Odoo credentials
    lines = content.split('\n')
    filtered_lines = []
    skip_odoo = False
    
    for line in lines:
        if line.startswith('# Odoo Configuration'):
            skip_odoo = True
            continue
        if skip_odoo and line.strip() == '' and not line.startswith('ODOO_'):
            skip_odoo = False
            continue
        if not skip_odoo or not line.startswith('ODOO_'):
            filtered_lines.append(line)
    
    content = '\n'.join(filtered_lines)
    
    # Add new credentials
    odoo_config = f"""
# Odoo Configuration
ODOO_URL={odoo_url}
ODOO_DB={odoo_db}
ODOO_USERNAME={odoo_username}
ODOO_PASSWORD={odoo_password}
ODOO_API_KEY=
ODOO_COMPANY_ID=1
ODOO_CURRENCY_ID=2
"""
    
    content += odoo_config
    env_path.write_text(content, encoding='utf-8')
    
    print("\n✓ Odoo credentials saved to .env")
    print(f"  URL: {odoo_url}")
    print(f"  Database: {odoo_db}")
    print(f"  Username: {odoo_username}")


def main():
    SESSIONS_DIR.mkdir(exist_ok=True)

    if len(sys.argv) > 1:
        requested = [a.lower() for a in sys.argv[1:]]
        unknown = [p for p in requested if p not in PLATFORMS]
        if unknown:
            print(f"Unknown platforms: {unknown}")
            print(f"Available: {list(PLATFORMS.keys())}")
            sys.exit(1)
        platforms_to_setup = {k: v for k, v in PLATFORMS.items() if k in requested}
    else:
        platforms_to_setup = PLATFORMS

    print("\nELYX Session Setup")
    print("==================")
    print(f"Will set up: {list(platforms_to_setup.keys())}")
    print("\nA browser window will open for each platform.")
    print("Log in manually — your session will be saved automatically.")
    print("\nFor Odoo: You'll also configure API credentials after login.\n")

    for name, config in platforms_to_setup.items():
        try:
            setup_platform(name, config)
        except KeyboardInterrupt:
            print(f"\nSkipped {name}.")
            continue
        except Exception as e:
            print(f"\n✗ Error setting up {name}: {e}")
            continue

    print("\n" + "="*60)
    print("  Session setup complete!")
    print("  You can now run: python run_elyx.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

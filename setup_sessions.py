"""
setup_sessions.py - One-time login script for all social media platforms.

Run this ONCE before starting ELYX. It opens each platform in a visible
Playwright browser so you can log in manually. Sessions are saved to
the sessions/ directory and reused automatically afterward.

Usage:
    python setup_sessions.py                    # All platforms
    python setup_sessions.py whatsapp           # Single platform
    python setup_sessions.py linkedin twitter   # Multiple platforms
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSIONS_DIR = Path("./sessions")

PLATFORMS = {
    "whatsapp": {
        "url": "https://web.whatsapp.com",
        "session_dir": "whatsapp_session",
        "logged_in_selector": '[data-testid="chat-list"]',
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
        "logged_in_selector": "nav.global-nav",
        "instructions": (
            "Log in to LinkedIn with your email and password.\n"
            "Complete any 2FA if prompted. Once your feed loads — press Enter here"
        ),
        "wait_seconds": 60,
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
        try:
            page.wait_for_selector(config["logged_in_selector"], timeout=10000)
            print(f"✓ {name.upper()} login verified — session saved!")
        except Exception:
            print(f"⚠ Could not auto-verify {name.upper()} login, but session was saved anyway.")
            print("  If the watcher fails, run this script again for this platform.")

        # Give browser a moment to flush cookies/storage to disk
        time.sleep(2)
        browser.close()

    print(f"✓ {name.upper()} session saved to {session_dir}\n")


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
    print("Log in manually — your session will be saved automatically.\n")

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

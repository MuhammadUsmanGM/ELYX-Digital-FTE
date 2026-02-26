#!/usr/bin/env python3
"""
Fix all social media watchers to use Chrome profile instead of isolated sessions

This script updates:
- linkedin_watcher.py
- facebook_watcher.py
- twitter_watcher.py
- instagram_watcher.py
- whatsapp_watcher.py

To use CHROME_USER_DATA_DIR from .env instead of session paths
"""

import re
from pathlib import Path

def fix_watcher_file(filepath: str, platform: str):
    """Fix a watcher file to use Chrome profile"""
    
    print(f"Fixing {platform} watcher...")
    
    content = Path(filepath).read_text(encoding='utf-8')
    
    # Pattern to find the browser launch code
    old_pattern = rf'browser = p\.chromium\.launch_persistent_context\(\s*str\(self\.session_path\),'
    
    # New code that uses Chrome profile
    new_code = f'''# Use Chrome profile from .env (where user is logged in)
                chrome_user_data_dir = os.getenv('CHROME_USER_DATA_DIR', '')
                
                if chrome_user_data_dir:
                    # Launch with user's Chrome profile (already logged in)
                    browser = p.chromium.launch_persistent_context(
                        chrome_user_data_dir,
                        headless=False,  # Always show browser for logged-in profile
                        viewport={{'width': 1280, 'height': 800}},
                        locale='en-US',
                        channel='chrome',  # Use Chrome, not Chromium
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox'
                        ]
                    )
                else:
                    # Fallback to session-based (not recommended)
                    browser = p.chromium.launch_persistent_context(
                        str(self.session_path),
                        headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
                        viewport={{'width': 1280, 'height': 800}},
                        locale='en-US'
                    )'''
    
    # Replace the pattern
    content = re.sub(old_pattern, new_code, content)
    
    # Write back
    Path(filepath).write_text(content, encoding='utf-8')
    print(f"  ✓ Fixed {platform} watcher")

def main():
    print("=" * 70)
    print("ELYX - Fix Social Media Watchers to Use Chrome Profile")
    print("=" * 70)
    print()
    
    watchers = [
        ('src/agents/linkedin_watcher.py', 'LinkedIn'),
        ('src/agents/facebook_watcher.py', 'Facebook'),
        ('src/agents/twitter_watcher.py', 'Twitter'),
        ('src/agents/instagram_watcher.py', 'Instagram'),
        ('src/agents/whatsapp_watcher.py', 'WhatsApp'),
    ]
    
    for filepath, platform in watchers:
        try:
            fix_watcher_file(filepath, platform)
        except Exception as e:
            print(f"  ✗ Failed to fix {platform}: {e}")
    
    print()
    print("=" * 70)
    print("FIX COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Make sure you're logged in to all platforms in Chrome Profile 8")
    print("2. Check .env has: CHROME_USER_DATA_DIR=C:\\Users\\...\\Profile 8")
    print("3. Run: python run_elyx.py")
    print()
    print("The watchers will now use your Chrome profile where you're logged in!")

if __name__ == "__main__":
    main()

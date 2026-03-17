#!/usr/bin/env python3
"""
Add social media credentials to .env file
"""

import os
from pathlib import Path

# Resolve project root (parent of config/) and work from there
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

# Read current .env
with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

# Add credentials if not present
credentials_to_add = []

if 'TWITTER_USERNAME=' not in content:
    twitter_username = os.getenv('TWITTER_USERNAME', 'your_twitter_username')
    twitter_password = os.getenv('TWITTER_PASSWORD', 'your_twitter_password')
    credentials_to_add.append(f'\n# Twitter/X Credentials\nTWITTER_USERNAME={twitter_username}\nTWITTER_PASSWORD={twitter_password}\n')

if 'LINKEDIN_USERNAME=' not in content:
    linkedin_username = os.getenv('LINKEDIN_USERNAME', 'your_linkedin_username')
    linkedin_password = os.getenv('LINKEDIN_PASSWORD', 'your_linkedin_password')
    credentials_to_add.append(f'\n# LinkedIn Credentials\nLINKEDIN_USERNAME={linkedin_username}\nLINKEDIN_PASSWORD={linkedin_password}\n')

if 'FACEBOOK_USERNAME=' not in content:
    facebook_username = os.getenv('FACEBOOK_USERNAME', 'your_facebook_username')
    facebook_password = os.getenv('FACEBOOK_PASSWORD', 'your_facebook_password')
    credentials_to_add.append(f'\n# Facebook Credentials\nFACEBOOK_USERNAME={facebook_username}\nFACEBOOK_PASSWORD={facebook_password}\n')

if 'INSTAGRAM_USERNAME=' not in content:
    instagram_username = os.getenv('INSTAGRAM_USERNAME', 'your_instagram_username')
    instagram_password = os.getenv('INSTAGRAM_PASSWORD', 'your_instagram_password')
    credentials_to_add.append(f'\n# Instagram Credentials\nINSTAGRAM_USERNAME={instagram_username}\nINSTAGRAM_PASSWORD={instagram_password}\n')

# Add credentials
if credentials_to_add:
    for creds in credentials_to_add:
        content += creds
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Added social media credentials to .env")
    print("\nCredentials added:")
    for creds in credentials_to_add:
        print(creds.strip())
else:
    print("Credentials already in .env")

print("\nNow run: python run_elyx.py")

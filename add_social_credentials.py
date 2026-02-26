#!/usr/bin/env python3
"""
Add social media credentials to .env file
"""

# Read current .env
with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

# Add credentials if not present
credentials_to_add = []

if 'TWITTER_USERNAME=' not in content:
    credentials_to_add.append('\n# Twitter/X Credentials\nTWITTER_USERNAME=ELYXo0\nTWITTER_PASSWORD=a1tti1t1u1d1e1\n')

if 'LINKEDIN_USERNAME=' not in content:
    credentials_to_add.append('\n# LinkedIn Credentials\nLINKEDIN_USERNAME=elyx.ai.employ@gmail.com\nLINKEDIN_PASSWORD=a1tti1t1u1d1e1\n')

if 'FACEBOOK_USERNAME=' not in content:
    credentials_to_add.append('\n# Facebook Credentials\nFACEBOOK_USERNAME=elyx.ai.employ@gmail.com\nFACEBOOK_PASSWORD=a1tti1t1u1d1e1\n')

if 'INSTAGRAM_USERNAME=' not in content:
    credentials_to_add.append('\n# Instagram Credentials\nINSTAGRAM_USERNAME=elyx.ai.employ\nINSTAGRAM_PASSWORD=a1tti1t1u1d1e1\n')

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

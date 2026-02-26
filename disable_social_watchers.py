# Disable social media watchers temporarily
with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('LINKEDIN_ENABLED=true', 'LINKEDIN_ENABLED=false')
content = content.replace('FACEBOOK_ENABLED=true', 'FACEBOOK_ENABLED=false')
content = content.replace('TWITTER_ENABLED=true', 'TWITTER_ENABLED=false')
content = content.replace('INSTAGRAM_ENABLED=true', 'INSTAGRAM_ENABLED=false')

with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)

print("Disabled social media watchers in .env")
print("Only Gmail and WhatsApp are enabled")

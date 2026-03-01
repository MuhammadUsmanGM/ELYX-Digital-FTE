---
name: social-media-posting
description: Draft and schedule social media posts for LinkedIn, Facebook, Instagram, and Twitter. Monitors social channels for messages and engagement. Use when handling SOCIAL_ action files or when posting content is needed.
---

# Social Media Posting Skill

## Supported Platforms
- LinkedIn
- Facebook
- Instagram
- Twitter (X)

## Workflow

### 1. Drafting Posts
When asked to create a social media post:
1. Read `obsidian_vault/Business_Goals.md` for current business context
2. Draft content appropriate for the target platform
3. Create a file in `obsidian_vault/Pending_Approval/POST_{PLATFORM}_{TIMESTAMP}.md`
4. **NEVER publish without approval** - all posts require human review

### 2. Post Approval File Format
```yaml
---
type: social_post
platform: linkedin|facebook|instagram|twitter
status: pending_approval
created: ISO_TIMESTAMP
---

## Proposed Post
[Post content here]

## Platform
[Target platform]

## Hashtags
[Suggested hashtags]

## Best Time to Post
[Suggested posting time based on platform]

## To Approve
Move this file to /Approved/ folder.
```

### 3. Publishing Approved Posts
When a post file appears in `/Approved/`:
1. Use the browser MCP or platform-specific watcher to publish
2. Log the post details in `obsidian_vault/Logs/`
3. Move the file to `obsidian_vault/Done/`
4. Update Dashboard.md with posting status

### 4. Monitoring Social Messages
When a `SOCIAL_*.md` file appears in `Needs_Action/`:
1. Read the message content
2. For positive engagement: draft a professional reply
3. For urgent/sensitive messages: flag for human review
4. For controversial threads: flag as high priority
5. **Never share private information publicly**

### 5. Platform-Specific Guidelines

**LinkedIn:**
- Professional tone, business-focused content
- Include relevant industry hashtags
- Optimal length: 150-300 words

**Facebook:**
- Conversational but professional
- Can include emojis sparingly
- Include a call to action

**Instagram:**
- Visual-first, caption should complement image
- Heavy hashtag usage (up to 30)
- Engaging, casual tone

**Twitter:**
- Concise (under 280 characters)
- Relevant hashtags (2-3 max)
- Engaging hooks

### 6. Brand Voice Rules
- Maintain consistent, professional, helpful tone across all platforms
- Prioritize replies to positive interactions
- Never share private info publicly
- Flag controversial threads for human review

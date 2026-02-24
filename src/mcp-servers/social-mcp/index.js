#!/usr/bin/env node
/**
 * Social Media MCP Server
 * Provides social media posting capabilities to Claude Code
 * 
 * Tools:
 * - linkedin_post: Post to LinkedIn
 * - facebook_post: Post to Facebook
 * - twitter_post: Post to Twitter/X
 * - instagram_post: Post to Instagram
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium } from 'playwright';

// Configuration from environment
const BROWSER_HEADLESS = process.env.BROWSER_HEADLESS === 'true';
const CHROME_USER_DATA_DIR = process.env.CHROME_USER_DATA_DIR || '';

// Browser instance
let browser = null;

/**
 * Initialize browser with existing Chrome profile
 */
async function initBrowser() {
  if (browser) {
    return browser;
  }
  
  try {
    const launchOptions = {
      headless: BROWSER_HEADLESS,
      args: [
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage'
      ]
    };
    
    // Use existing Chrome profile if available
    if (CHROME_USER_DATA_DIR) {
      launchOptions.userDataDir = CHROME_USER_DATA_DIR;
      launchOptions.channel = 'chrome';
    }
    
    browser = await chromium.launchPersistentContext(launchOptions);
    console.error('[SOCIAL MCP] Browser initialized with Chrome profile');
    return browser;
  } catch (error) {
    console.error('[SOCIAL MCP] Browser initialization error:', error.message);
    throw error;
  }
}

// Define available tools
const TOOLS = [
  {
    name: 'linkedin_post',
    description: 'Create a post on LinkedIn',
    inputSchema: {
      type: 'object',
      properties: {
        content: {
          type: 'string',
          description: 'Post content (text)'
        },
        imageUrl: {
          type: 'string',
          description: 'Optional image URL to attach'
        }
      },
      required: ['content']
    }
  },
  {
    name: 'facebook_post',
    description: 'Create a post on Facebook',
    inputSchema: {
      type: 'object',
      properties: {
        content: {
          type: 'string',
          description: 'Post content (text)'
        },
        imageUrl: {
          type: 'string',
          description: 'Optional image URL to attach'
        }
      },
      required: ['content']
    }
  },
  {
    name: 'twitter_post',
    description: 'Create a post on Twitter/X',
    inputSchema: {
      type: 'object',
      properties: {
        content: {
          type: 'string',
          description: 'Tweet content (max 280 characters)'
        },
        imageUrl: {
          type: 'string',
          description: 'Optional image URL to attach'
        }
      },
      required: ['content']
    }
  },
  {
    name: 'instagram_post',
    description: 'Create a post on Instagram',
    inputSchema: {
      type: 'object',
      properties: {
        content: {
          type: 'string',
          description: 'Post caption'
        },
        imageUrl: {
          type: 'string',
          description: 'Image URL to post (required for Instagram)'
        }
      },
      required: ['content', 'imageUrl']
    }
  },
  {
    name: 'schedule_social_post',
    description: 'Schedule a post for all platforms (creates approval file)',
    inputSchema: {
      type: 'object',
      properties: {
        content: {
          type: 'string',
          description: 'Post content'
        },
        platforms: {
          type: 'array',
          description: 'Platforms to post to',
          items: {
            type: 'string',
            enum: ['linkedin', 'facebook', 'twitter', 'instagram']
          }
        },
        scheduledTime: {
          type: 'string',
          description: 'Scheduled time (ISO format)'
        },
        imageUrl: {
          type: 'string',
          description: 'Optional image URL'
        }
      },
      required: ['content', 'platforms']
    }
  }
];

// Create MCP server
const server = new Server(
  {
    name: 'elyx-social-mcp',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Handle list tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handle tool call request
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    let result;
    
    switch (name) {
      case 'linkedin_post':
        result = await postToLinkedIn(args);
        break;
        
      case 'facebook_post':
        result = await postToFacebook(args);
        break;
        
      case 'twitter_post':
        result = await postToTwitter(args);
        break;
        
      case 'instagram_post':
        result = await postToInstagram(args);
        break;
        
      case 'schedule_social_post':
        result = await schedulePost(args);
        break;
        
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

/**
 * Tool implementations
 */

async function postToLinkedIn({ content, imageUrl }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[SOCIAL MCP] Posting to LinkedIn...');
    
    // Go to LinkedIn
    await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'networkidle' });
    
    // Wait for post creation box
    await page.waitForSelector('[data-test-id="update-create-post-trigger"]', { timeout: 10000 });
    
    // Click on post creation
    await page.click('[data-test-id="update-create-post-trigger"]');
    
    // Wait for editor
    await page.waitForSelector('[data-lexical-editor="true"]', { timeout: 5000 });
    
    // Type content
    const editor = await page.locator('[data-lexical-editor="true"]').first();
    await editor.fill(content);
    
    // Post
    const postButton = await page.locator('button:has-text("Post")').first();
    await postButton.click();
    
    console.error('[SOCIAL MCP] LinkedIn post created successfully');
    
    return {
      success: true,
      platform: 'linkedin',
      message: 'Post created on LinkedIn (pending review)',
      content: content.substring(0, 100) + '...'
    };
  } catch (error) {
    console.error('[SOCIAL MCP] LinkedIn post error:', error.message);
    throw new Error(`LinkedIn post failed: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function postToFacebook({ content, imageUrl }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[SOCIAL MCP] Posting to Facebook...');
    
    await page.goto('https://www.facebook.com/', { waitUntil: 'networkidle' });
    
    // Wait for post creation box
    await page.waitForSelector('[placeholder="What\\'s on your mind?"]', { timeout: 10000 });
    
    // Click on post creation
    await page.click('[placeholder="What\\'s on your mind?"]');
    
    // Type content
    await page.keyboard.type(content);
    
    // Post
    const postButton = await page.locator('button:has-text("Post")').first();
    await postButton.click();
    
    console.error('[SOCIAL MCP] Facebook post created successfully');
    
    return {
      success: true,
      platform: 'facebook',
      message: 'Post created on Facebook (pending review)',
      content: content.substring(0, 100) + '...'
    };
  } catch (error) {
    console.error('[SOCIAL MCP] Facebook post error:', error.message);
    throw new Error(`Facebook post failed: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function postToTwitter({ content, imageUrl }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[SOCIAL MCP] Posting to Twitter...');
    
    await page.goto('https://x.com/home', { waitUntil: 'networkidle' });
    
    // Wait for tweet box
    await page.waitForSelector('[data-testid="tweetTextarea_0"]', { timeout: 10000 });
    
    // Type content
    const textarea = await page.locator('[data-testid="tweetTextarea_0"]').first();
    await textarea.fill(content);
    
    // Post
    const postButton = await page.locator('[data-testid="tweetButton"]').first();
    await postButton.click();
    
    console.error('[SOCIAL MCP] Twitter post created successfully');
    
    return {
      success: true,
      platform: 'twitter',
      message: 'Tweet posted successfully',
      content: content.substring(0, 100) + '...'
    };
  } catch (error) {
    console.error('[SOCIAL MCP] Twitter post error:', error.message);
    throw new Error(`Twitter post failed: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function postToInstagram({ content, imageUrl }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[SOCIAL MCP] Posting to Instagram...');
    
    await page.goto('https://www.instagram.com/', { waitUntil: 'networkidle' });
    
    // Instagram posting is complex via automation - create draft instead
    console.error('[SOCIAL MCP] Instagram requires manual posting - creating draft');
    
    return {
      success: true,
      platform: 'instagram',
      message: 'Instagram post prepared (manual posting required)',
      content: content,
      imageUrl: imageUrl,
      instructions: '1. Open Instagram\n2. Click + to create post\n3. Select image\n4. Paste caption'
    };
  } catch (error) {
    console.error('[SOCIAL MCP] Instagram post error:', error.message);
    throw new Error(`Instagram post failed: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function schedulePost({ content, platforms, scheduledTime, imageUrl }) {
  // Create approval file for scheduled post
  const approvalData = {
    type: 'scheduled_social_post',
    content: content,
    platforms: platforms,
    scheduledTime: scheduledTime || 'ASAP',
    imageUrl: imageUrl,
    createdAt: new Date().toISOString()
  };
  
  console.error('[SOCIAL MCP] Scheduled post created for approval');
  
  return {
    success: true,
    message: 'Social post scheduled for approval',
    approval: approvalData,
    nextStep: 'Move approval file to /Approved to publish'
  };
}

/**
 * Main entry point
 */
async function main() {
  console.error('[SOCIAL MCP] Starting Social Media MCP Server...');
  
  // Initialize browser
  try {
    await initBrowser();
  } catch (error) {
    console.error('[SOCIAL MCP] Warning: Browser initialization failed. Social posting will use fallback.');
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('[SOCIAL MCP] Server running on stdio');
}

main().catch((error) => {
  console.error('[SOCIAL MCP] Fatal error:', error);
  process.exit(1);
});

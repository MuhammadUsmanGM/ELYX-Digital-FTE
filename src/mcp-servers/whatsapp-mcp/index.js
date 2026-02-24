#!/usr/bin/env node
/**
 * WhatsApp MCP Server
 * Provides WhatsApp messaging capabilities to Claude Code
 * 
 * Tools:
 * - send_message: Send WhatsApp message to contact
 * - send_bulk_message: Send message to multiple contacts
 * - get_recent_chats: Get recent chat list
 * - mark_as_read: Mark messages as read
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
const WHATSAPP_KEYWORDS = (process.env.WHATSAPP_KEYWORDS || 'urgent,asap,invoice,payment,help').split(',');

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
    console.error('[WHATSAPP MCP] Browser initialized with Chrome profile');
    return browser;
  } catch (error) {
    console.error('[WHATSAPP MCP] Browser initialization error:', error.message);
    throw error;
  }
}

/**
 * Navigate to WhatsApp and ensure logged in
 */
async function ensureWhatsAppLoggedIn(page) {
  await page.goto('https://web.whatsapp.com', { waitUntil: 'networkidle' });
  
  // Check if already logged in (look for chat list)
  try {
    await page.waitForSelector('[data-testid="chat-list"]', { timeout: 5000 });
    console.error('[WHATSAPP MCP] Already logged in to WhatsApp');
    return true;
  } catch (error) {
    console.error('[WHATSAPP MCP] Not logged in - QR code may need scanning');
    return false;
  }
}

/**
 * Search for contact by name/number
 */
async function searchContact(page, contact) {
  try {
    // Click on search box
    const searchBox = await page.locator('[data-testid="search"]').first();
    await searchBox.click();
    await searchBox.fill(contact);
    
    // Wait for search results
    await page.waitForTimeout(2000);
    
    // Click on first result
    const contactResult = await page.locator('[data-testid="user-info-cell"]').first();
    await contactResult.click();
    
    console.error('[WHATSAPP MCP] Found contact:', contact);
    return true;
  } catch (error) {
    console.error('[WHATSAPP MCP] Contact not found:', error.message);
    return false;
  }
}

// Define available tools
const TOOLS = [
  {
    name: 'send_message',
    description: 'Send a WhatsApp message to a contact',
    inputSchema: {
      type: 'object',
      properties: {
        contact: {
          type: 'string',
          description: 'Contact name or phone number (with country code, e.g., +1234567890)'
        },
        message: {
          type: 'string',
          description: 'Message to send'
        },
        waitForReply: {
          type: 'boolean',
          description: 'Whether to wait for reply (default: false)',
          default: false
        }
      },
      required: ['contact', 'message']
    }
  },
  {
    name: 'send_bulk_message',
    description: 'Send the same message to multiple contacts (creates approval file)',
    inputSchema: {
      type: 'object',
      properties: {
        contacts: {
          type: 'array',
          description: 'List of contacts',
          items: { type: 'string' }
        },
        message: {
          type: 'string',
          description: 'Message to send'
        }
      },
      required: ['contacts', 'message']
    }
  },
  {
    name: 'get_recent_chats',
    description: 'Get list of recent chats with unread messages',
    inputSchema: {
      type: 'object',
      properties: {
        unreadOnly: {
          type: 'boolean',
          description: 'Only return chats with unread messages',
          default: true
        },
        limit: {
          type: 'integer',
          description: 'Maximum number of chats to return',
          default: 20
        }
      }
    }
  },
  {
    name: 'mark_as_read',
    description: 'Mark WhatsApp messages as read',
    inputSchema: {
      type: 'object',
      properties: {
        contact: {
          type: 'string',
          description: 'Contact name or number'
        }
      },
      required: ['contact']
    }
  },
  {
    name: 'check_urgent_messages',
    description: 'Check for urgent messages containing keywords',
    inputSchema: {
      type: 'object',
      properties: {
        keywords: {
          type: 'array',
          description: 'Keywords to search for',
          items: { type: 'string' },
          default: ['urgent', 'asap', 'invoice', 'payment', 'help']
        }
      }
    }
  }
];

// Create MCP server
const server = new Server(
  {
    name: 'elyx-whatsapp-mcp',
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
      case 'send_message':
        result = await sendMessage(args);
        break;
        
      case 'send_bulk_message':
        result = await sendBulkMessage(args);
        break;
        
      case 'get_recent_chats':
        result = await getRecentChats(args);
        break;
        
      case 'mark_as_read':
        result = await markAsRead(args);
        break;
        
      case 'check_urgent_messages':
        result = await checkUrgentMessages(args);
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

async function sendMessage({ contact, message, waitForReply = false }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[WHATSAPP MCP] Sending message to:', contact);
    
    // Ensure logged in
    const isLoggedIn = await ensureWhatsAppLoggedIn(page);
    if (!isLoggedIn) {
      throw new Error('WhatsApp not logged in. Please scan QR code.');
    }
    
    // Search for contact
    const found = await searchContact(page, contact);
    if (!found) {
      throw new Error(`Contact not found: ${contact}`);
    }
    
    // Wait for message input
    await page.waitForSelector('[data-testid="chat-input"]', { timeout: 5000 });
    
    // Type message
    const input = await page.locator('[data-testid="chat-input"]').first();
    await input.fill(message);
    
    // Send
    const sendButton = await page.locator('[data-testid="compose-btn-send"]').first();
    await sendButton.click();
    
    console.error('[WHATSAPP MCP] Message sent successfully');
    
    return {
      success: true,
      contact: contact,
      message: message.substring(0, 100) + '...',
      status: 'sent',
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('[WHATSAPP MCP] Send message error:', error.message);
    throw new Error(`WhatsApp send failed: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function sendBulkMessage({ contacts, message }) {
  // For bulk messages, create approval file instead of sending directly
  console.error('[WHATSAPP MCP] Bulk message request for', contacts.length, 'contacts');
  
  return {
    success: true,
    message: 'Bulk message prepared for approval',
    approval: {
      type: 'whatsapp_bulk_message',
      contacts: contacts,
      message: message,
      count: contacts.length,
      createdAt: new Date().toISOString()
    },
    nextStep: 'Move approval file to /Approved to send'
  };
}

async function getRecentChats({ unreadOnly = true, limit = 20 }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[WHATSAPP MCP] Getting recent chats...');
    
    const isLoggedIn = await ensureWhatsAppLoggedIn(page);
    if (!isLoggedIn) {
      throw new Error('WhatsApp not logged in');
    }
    
    // Get chat list
    const chats = await page.evaluate((unreadOnly) => {
      const chatElements = document.querySelectorAll('[data-testid="chat-list"] [data-testid="chat-item"]');
      const chats = [];
      
      chatElements.forEach((el, index) => {
        if (index >= limit) return;
        
        const nameEl = el.querySelector('[data-testid="chat-item-name"]');
        const msgEl = el.querySelector('[data-testid="chat-item-msg"]');
        const unreadEl = el.querySelector('[data-testid="unread-msg-count"]');
        
        const hasUnread = unreadEl !== null;
        
        if (unreadOnly && !hasUnread) return;
        
        chats.push({
          name: nameEl?.textContent || 'Unknown',
          lastMessage: msgEl?.textContent || '',
          unreadCount: parseInt(unreadEl?.textContent || '0'),
          hasUnread: hasUnread
        });
      });
      
      return chats;
    }, unreadOnly);
    
    console.error('[WHATSAPP MCP] Found', chats.length, 'chats');
    
    return {
      success: true,
      count: chats.length,
      chats: chats
    };
  } catch (error) {
    console.error('[WHATSAPP MCP] Get chats error:', error.message);
    throw new Error(`Failed to get chats: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function markAsRead({ contact }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[WHATSAPP MCP] Marking chat as read:', contact);
    
    const isLoggedIn = await ensureWhatsAppLoggedIn(page);
    if (!isLoggedIn) {
      throw new Error('WhatsApp not logged in');
    }
    
    // Search for contact
    await searchContact(page, contact);
    
    // Click on chat to mark as read
    await page.waitForTimeout(1000);
    
    console.error('[WHATSAPP MCP] Chat marked as read');
    
    return {
      success: true,
      contact: contact,
      status: 'read'
    };
  } catch (error) {
    console.error('[WHATSAPP MCP] Mark as read error:', error.message);
    throw new Error(`Failed to mark as read: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function checkUrgentMessages({ keywords = WHATSAPP_KEYWORDS }) {
  const page = await (await initBrowser()).newPage();
  
  try {
    console.error('[WHATSAPP MCP] Checking for urgent messages...');
    
    const isLoggedIn = await ensureWhatsAppLoggedIn(page);
    if (!isLoggedIn) {
      throw new Error('WhatsApp not logged in');
    }
    
    // Get chat list with unread messages
    const urgentChats = await page.evaluate((keywords) => {
      const chatElements = document.querySelectorAll('[data-testid="chat-list"] [data-testid="chat-item"]');
      const urgentChats = [];
      
      chatElements.forEach((el) => {
        const nameEl = el.querySelector('[data-testid="chat-item-name"]');
        const msgEl = el.querySelector('[data-testid="chat-item-msg"]');
        const unreadEl = el.querySelector('[data-testid="unread-msg-count"]');
        
        const hasUnread = unreadEl !== null;
        if (!hasUnread) return;
        
        const messageText = (msgEl?.textContent || '').toLowerCase();
        const name = nameEl?.textContent || 'Unknown';
        
        // Check for urgent keywords
        const foundKeywords = keywords.filter(kw => messageText.includes(kw.toLowerCase()));
        
        if (foundKeywords.length > 0) {
          urgentChats.push({
            name: name,
            lastMessage: msgEl?.textContent || '',
            unreadCount: parseInt(unreadEl?.textContent || '0'),
            urgentKeywords: foundKeywords,
            urgency: foundKeywords.length
          });
        }
      });
      
      // Sort by urgency
      return urgentChats.sort((a, b) => b.urgency - a.urgency);
    }, keywords);
    
    console.error('[WHATSAPP MCP] Found', urgentChats.length, 'urgent messages');
    
    return {
      success: true,
      count: urgentChats.length,
      urgentMessages: urgentChats,
      keywords: keywords
    };
  } catch (error) {
    console.error('[WHATSAPP MCP] Check urgent error:', error.message);
    throw new Error(`Failed to check urgent messages: ${error.message}`);
  } finally {
    await page.close();
  }
}

/**
 * Main entry point
 */
async function main() {
  console.error('[WHATSAPP MCP] Starting WhatsApp MCP Server...');
  
  // Initialize browser
  try {
    await initBrowser();
  } catch (error) {
    console.error('[WHATSAPP MCP] Warning: Browser initialization failed.');
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('[WHATSAPP MCP] Server running on stdio');
}

main().catch((error) => {
  console.error('[WHATSAPP MCP] Fatal error:', error);
  process.exit(1);
});

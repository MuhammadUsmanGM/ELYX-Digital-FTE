#!/usr/bin/env node
/**
 * Email MCP Server
 * Provides Gmail capabilities to Claude Code
 * 
 * Tools:
 * - send_email: Send email via Gmail
 * - draft_email: Create draft email for approval
 * - search_emails: Search Gmail
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';

// Gmail configuration from environment
const GMAIL_CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS_PATH || 'gmail_credentials.json';
const EMAIL_USER = process.env.EMAIL_USER || '';

// OAuth2 client
let oauth2Client;
let gmail;

/**
 * Initialize Gmail API client
 */
async function initGmail() {
  try {
    const credentialsPath = path.resolve(GMAIL_CREDENTIALS_PATH);
    
    if (!fs.existsSync(credentialsPath)) {
      throw new Error(`Gmail credentials not found at ${credentialsPath}`);
    }
    
    const credentials = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
    
    oauth2Client = new google.auth.OAuth2(
      credentials.client_id,
      credentials.client_secret,
      credentials.redirect_uris[0]
    );
    
    // Load saved token
    const tokenPath = path.resolve('gmail_token.json');
    if (fs.existsSync(tokenPath)) {
      const token = JSON.parse(fs.readFileSync(tokenPath, 'utf8'));
      oauth2Client.setCredentials(token);
      
      gmail = google.gmail({ version: 'v1', auth: oauth2Client });
      console.error('[EMAIL MCP] Gmail initialized successfully');
      return true;
    } else {
      throw new Error('Gmail token not found. Please authenticate first.');
    }
  } catch (error) {
    console.error('[EMAIL MCP] Initialization error:', error.message);
    return false;
  }
}

// Define available tools
const TOOLS = [
  {
    name: 'send_email',
    description: 'Send an email via Gmail',
    inputSchema: {
      type: 'object',
      properties: {
        to: {
          type: 'string',
          description: 'Recipient email address'
        },
        subject: {
          type: 'string',
          description: 'Email subject'
        },
        body: {
          type: 'string',
          description: 'Email body (plain text or HTML)'
        },
        isHtml: {
          type: 'boolean',
          description: 'Whether body is HTML (default: false)',
          default: false
        }
      },
      required: ['to', 'subject', 'body']
    }
  },
  {
    name: 'draft_email',
    description: 'Create a draft email for review (does not send)',
    inputSchema: {
      type: 'object',
      properties: {
        to: {
          type: 'string',
          description: 'Recipient email address'
        },
        subject: {
          type: 'string',
          description: 'Email subject'
        },
        body: {
          type: 'string',
          description: 'Email body'
        },
        isHtml: {
          type: 'boolean',
          description: 'Whether body is HTML',
          default: false
        }
      },
      required: ['to', 'subject', 'body']
    }
  },
  {
    name: 'search_emails',
    description: 'Search Gmail for emails matching query',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Gmail search query (e.g., "is:unread is:important")'
        },
        maxResults: {
          type: 'integer',
          description: 'Maximum number of results',
          default: 10
        }
      },
      required: ['query']
    }
  },
  {
    name: 'read_email',
    description: 'Read full content of an email by ID',
    inputSchema: {
      type: 'object',
      properties: {
        email_id: {
          type: 'string',
          description: 'Gmail message ID'
        }
      },
      required: ['email_id']
    }
  },
  {
    name: 'mark_as_read',
    description: 'Mark email(s) as read',
    inputSchema: {
      type: 'object',
      properties: {
        email_ids: {
          type: 'array',
          description: 'Array of email IDs to mark as read',
          items: { type: 'string' }
        }
      },
      required: ['email_ids']
    }
  },
  {
    name: 'archive_email',
    description: 'Archive email(s)',
    inputSchema: {
      type: 'object',
      properties: {
        email_ids: {
          type: 'array',
          description: 'Array of email IDs to archive',
          items: { type: 'string' }
        }
      },
      required: ['email_ids']
    }
  }
];

// Create MCP server
const server = new Server(
  {
    name: 'elyx-email-mcp',
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
      case 'send_email':
        result = await sendEmail(args);
        break;
        
      case 'draft_email':
        result = await draftEmail(args);
        break;
        
      case 'search_emails':
        result = await searchEmails(args);
        break;
        
      case 'read_email':
        result = await readEmail(args);
        break;
        
      case 'mark_as_read':
        result = await markAsRead(args);
        break;
        
      case 'archive_email':
        result = await archiveEmail(args);
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

function createMessage(to, subject, body, isHtml = false) {
  const str = [
    'To: ' + to,
    'Subject: ' + subject,
    'MIME-Version: 1.0',
    'Content-Type: ' + (isHtml ? 'text/html; charset=utf-8' : 'text/plain; charset=utf-8'),
    '',
    body
  ].join('\n');
  
  return Buffer.from(str)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

async function sendEmail(args) {
  const { to, subject, body, isHtml = false } = args;
  
  if (!gmail) {
    throw new Error('Gmail not initialized');
  }
  
  const message = createMessage(to, subject, body, isHtml);
  
  const response = await gmail.users.messages.send({
    userId: 'me',
    requestBody: {
      raw: message
    }
  });
  
  return {
    success: true,
    message_id: response.data.id,
    thread_id: response.data.threadId,
    message: `Email sent to ${to}`
  };
}

async function draftEmail(args) {
  const { to, subject, body, isHtml = false } = args;
  
  if (!gmail) {
    throw new Error('Gmail not initialized');
  }
  
  const message = createMessage(to, subject, body, isHtml);
  
  const response = await gmail.users.drafts.create({
    userId: 'me',
    requestBody: {
      message: {
        raw: message
      }
    }
  });
  
  return {
    success: true,
    draft_id: response.data.id,
    message: `Draft created for email to ${to} - ready for review`
  };
}

async function searchEmails(args) {
  const { query, maxResults = 10 } = args;
  
  if (!gmail) {
    throw new Error('Gmail not initialized');
  }
  
  const response = await gmail.users.messages.list({
    userId: 'me',
    q: query,
    maxResults: maxResults
  });
  
  const messages = response.data.messages || [];
  
  // Get full details for each message
  const emails = await Promise.all(
    messages.map(async (msg) => {
      const full = await gmail.users.messages.get({
        userId: 'me',
        id: msg.id,
        format: 'metadata',
        metadataHeaders: ['From', 'To', 'Subject', 'Date']
      });
      
      const headers = full.data.payload.headers;
      return {
        id: msg.id,
        threadId: msg.threadId,
        from: headers.find(h => h.name === 'From')?.value || '',
        subject: headers.find(h => h.name === 'Subject')?.value || '',
        date: headers.find(h => h.name === 'Date')?.value || ''
      };
    })
  );
  
  return {
    success: true,
    count: emails.length,
    emails: emails
  };
}

async function readEmail(args) {
  const { email_id } = args;
  
  if (!gmail) {
    throw new Error('Gmail not initialized');
  }
  
  const response = await gmail.users.messages.get({
    userId: 'me',
    id: email_id,
    format: 'full'
  });
  
  const payload = response.data.payload;
  const headers = payload.headers;
  
  // Get body
  let body = '';
  if (payload.body.data) {
    body = Buffer.from(payload.body.data, 'base64').toString('utf-8');
  } else if (payload.parts && payload.parts[0]) {
    body = Buffer.from(payload.parts[0].body.data, 'base64').toString('utf-8');
  }
  
  return {
    success: true,
    id: response.data.id,
    threadId: response.data.threadId,
    from: headers.find(h => h.name === 'From')?.value || '',
    to: headers.find(h => h.name === 'To')?.value || '',
    subject: headers.find(h => h.name === 'Subject')?.value || '',
    date: headers.find(h => h.name === 'Date')?.value || '',
    body: body
  };
}

async function markAsRead(args) {
  const { email_ids } = args;
  
  if (!gmail) {
    throw new Error('Gmail not initialized');
  }
  
  await gmail.users.messages.modify({
    userId: 'me',
    id: email_ids,
    requestBody: {
      removeLabelIds: ['UNREAD']
    }
  });
  
  return {
    success: true,
    message: `Marked ${email_ids.length} email(s) as read`
  };
}

async function archiveEmail(args) {
  const { email_ids } = args;
  
  if (!gmail) {
    throw new Error('Gmail not initialized');
  }
  
  await gmail.users.messages.modify({
    userId: 'me',
    id: email_ids,
    requestBody: {
      removeLabelIds: ['INBOX']
    }
  });
  
  return {
    success: true,
    message: `Archived ${email_ids.length} email(s)`
  };
}

/**
 * Main entry point
 */
async function main() {
  console.error('[EMAIL MCP] Starting Email MCP Server...');
  
  // Initialize Gmail
  const initialized = await initGmail();
  
  if (!initialized) {
    console.error('[EMAIL MCP] Failed to initialize Gmail. Check credentials.');
    process.exit(1);
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('[EMAIL MCP] Server running on stdio');
}

main().catch((error) => {
  console.error('[EMAIL MCP] Fatal error:', error);
  process.exit(1);
});

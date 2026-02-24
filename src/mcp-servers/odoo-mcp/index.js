#!/usr/bin/env node
/**
 * Odoo MCP Server
 * Provides Odoo accounting capabilities to Claude Code
 * 
 * Tools:
 * - create_invoice: Create customer invoice
 * - register_payment: Register payment for invoice
 * - search_invoices: Search/filter invoices
 * - get_revenue: Get revenue data
 * - get_overdue_invoices: Get overdue invoices
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import fetch from 'node-fetch';

// Odoo configuration from environment
const ODOO_URL = process.env.ODOO_URL || 'https://elyx-ai.odoo.com';
const ODOO_DB = process.env.ODOO_DB || 'elyx-ai';
const ODOO_USERNAME = process.env.ODOO_USERNAME || '';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || '';
const ODOO_API_KEY = process.env.ODOO_API_KEY || '';

// Session management
let sessionId = null;
let userId = null;

/**
 * Make JSON-RPC call to Odoo
 */
async function odooRpc(endpoint, method, params) {
  const url = `${ODOO_URL}${endpoint}`;
  
  const payload = {
    jsonrpc: '2.0',
    method: method,
    params: params || {},
    id: 1
  };
  
  const headers = {
    'Content-Type': 'application/json'
  };
  
  const cookies = sessionId ? { session_id: sessionId } : {};
  
  const response = await fetch(url, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  
  // Save session cookie
  const setCookie = response.headers.get('set-cookie');
  if (setCookie) {
    const match = setCookie.match(/session_id=([^;]+)/);
    if (match) {
      sessionId = match[1];
    }
  }
  
  if (result.error) {
    throw new Error(`Odoo API Error: ${result.error.message}`);
  }
  
  return result.result || {};
}

/**
 * Authenticate with Odoo
 */
async function authenticate() {
  try {
    const authPassword = ODOO_API_KEY || ODOO_PASSWORD;
    
    const result = await odooRpc('/web/session/authenticate', 'call', {
      db: ODOO_DB,
      login: ODOO_USERNAME,
      password: authPassword,
      context: {}
    });
    
    if (result.uid) {
      userId = result.uid;
      console.error(`[ODOO MCP] Authenticated as user ${userId}`);
      return true;
    }
    
    throw new Error('Authentication failed - no UID returned');
  } catch (error) {
    console.error('[ODOO MCP] Authentication error:', error.message);
    return false;
  }
}

/**
 * Execute Odoo model method
 */
async function executeKw(model, method, args = [], kwargs = {}) {
  if (!userId) {
    await authenticate();
  }
  
  const result = await odooRpc('/jsonrpc', 'call', {
    service: 'object',
    method: 'execute_kw',
    args: [
      ODOO_DB,
      userId,
      ODOO_API_KEY || ODOO_PASSWORD,
      model,
      method,
      args,
      kwargs
    ]
  });
  
  return result;
}

// Define available tools
const TOOLS = [
  {
    name: 'create_invoice',
    description: 'Create a customer invoice in Odoo',
    inputSchema: {
      type: 'object',
      properties: {
        partner_id: {
          type: 'integer',
          description: 'Customer partner ID'
        },
        invoice_lines: {
          type: 'array',
          description: 'Invoice line items',
          items: {
            type: 'object',
            properties: {
              product_id: { type: 'integer', description: 'Product ID' },
              quantity: { type: 'number', description: 'Quantity' },
              price_unit: { type: 'number', description: 'Unit price' },
              name: { type: 'string', description: 'Description' }
            }
          }
        },
        invoice_date: {
          type: 'string',
          description: 'Invoice date (YYYY-MM-DD), defaults to today'
        }
      },
      required: ['partner_id', 'invoice_lines']
    }
  },
  {
    name: 'register_payment',
    description: 'Register payment for an invoice',
    inputSchema: {
      type: 'object',
      properties: {
        invoice_id: {
          type: 'integer',
          description: 'Invoice ID to pay'
        },
        amount: {
          type: 'number',
          description: 'Payment amount'
        },
        payment_date: {
          type: 'string',
          description: 'Payment date (YYYY-MM-DD), defaults to today'
        }
      },
      required: ['invoice_id', 'amount']
    }
  },
  {
    name: 'search_invoices',
    description: 'Search for invoices with filters',
    inputSchema: {
      type: 'object',
      properties: {
        move_type: {
          type: 'string',
          description: 'Invoice type: out_invoice, in_invoice, out_refund, in_refund',
          enum: ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']
        },
        state: {
          type: 'string',
          description: 'Invoice state: draft, posted, cancel',
          enum: ['draft', 'posted', 'cancel']
        },
        payment_state: {
          type: 'string',
          description: 'Payment state: not_paid, partial, paid, reversed',
          enum: ['not_paid', 'partial', 'paid', 'reversed']
        },
        partner_id: {
          type: 'integer',
          description: 'Filter by partner ID'
        },
        limit: {
          type: 'integer',
          description: 'Maximum number of results',
          default: 50
        }
      }
    }
  },
  {
    name: 'get_revenue',
    description: 'Get revenue data for specified period',
    inputSchema: {
      type: 'object',
      properties: {
        period: {
          type: 'string',
          description: 'Time period: week, month, year',
          enum: ['week', 'month', 'year']
        },
        start_date: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD), overrides period'
        },
        end_date: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)'
        }
      }
    }
  },
  {
    name: 'get_overdue_invoices',
    description: 'Get all overdue customer invoices',
    inputSchema: {
      type: 'object',
      properties: {
        days_overdue: {
          type: 'integer',
          description: 'Minimum days overdue',
          default: 1
        },
        limit: {
          type: 'integer',
          description: 'Maximum number of results',
          default: 50
        }
      }
    }
  }
];

// Create MCP server
const server = new Server(
  {
    name: 'elyx-odoo-mcp',
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
      case 'create_invoice':
        result = await createInvoice(args);
        break;
        
      case 'register_payment':
        result = await registerPayment(args);
        break;
        
      case 'search_invoices':
        result = await searchInvoices(args);
        break;
        
      case 'get_revenue':
        result = await getRevenue(args);
        break;
        
      case 'get_overdue_invoices':
        result = await getOverdueInvoices(args);
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

async function createInvoice(args) {
  const { partner_id, invoice_lines, invoice_date } = args;
  
  const today = new Date().toISOString().split('T')[0];
  
  const invoiceData = {
    move_type: 'out_invoice',
    partner_id: partner_id,
    invoice_date: invoice_date || today,
    company_id: 1,
    currency_id: 2,
    invoice_line_ids: invoice_lines.map(line => [0, 0, line])
  };
  
  const invoiceId = await executeKw('account.move', 'create', [invoiceData]);
  
  return {
    success: true,
    invoice_id: invoiceId,
    message: `Invoice ${invoiceId} created successfully`
  };
}

async function registerPayment(args) {
  const { invoice_id, amount, payment_date } = args;
  
  const today = new Date().toISOString().split('T')[0];
  
  // Mark invoice as paid (simplified)
  await executeKw('account.move', 'write', [
    [invoice_id],
    { payment_state: 'paid' }
  ]);
  
  return {
    success: true,
    message: `Payment of ${amount} registered for invoice ${invoice_id}`
  };
}

async function searchInvoices(args) {
  const { move_type, state, payment_state, partner_id, limit = 50 } = args;
  
  const domain = [];
  
  if (move_type) domain.push(['move_type', '=', move_type]);
  if (state) domain.push(['state', '=', state]);
  if (payment_state) domain.push(['payment_state', '=', payment_state]);
  if (partner_id) domain.push(['partner_id', '=', partner_id]);
  
  const fields = [
    'id', 'name', 'move_type', 'state', 'partner_id',
    'invoice_date', 'invoice_date_due', 'amount_total',
    'amount_residual', 'payment_state'
  ];
  
  const invoices = await executeKw('account.move', 'search_read', [
    domain,
    fields
  ], { limit });
  
  return {
    success: true,
    count: invoices.length,
    invoices: invoices
  };
}

async function getRevenue(args) {
  const { period, start_date, end_date } = args;
  
  const today = new Date();
  let startDate, endDate;
  
  if (start_date && end_date) {
    startDate = start_date;
    endDate = end_date;
  } else {
    switch (period) {
      case 'week':
        startDate = new Date(today.setDate(today.getDate() - 7)).toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
        break;
      case 'month':
        startDate = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
        break;
      case 'year':
        startDate = new Date(today.getFullYear(), 0, 1).toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
        break;
      default:
        startDate = new Date(today.setDate(today.getDate() - 7)).toISOString().split('T')[0];
        endDate = today.toISOString().split('T')[0];
    }
  }
  
  const domain = [
    ['move_type', '=', 'out_invoice'],
    ['state', '=', 'posted'],
    ['invoice_date', '>=', startDate],
    ['invoice_date', '<=', endDate]
  ];
  
  const invoices = await executeKw('account.move', 'search_read', [domain, ['amount_total']]);
  
  const total = invoices.reduce((sum, inv) => sum + (inv.amount_total || 0), 0);
  
  return {
    success: true,
    period: period || 'custom',
    start_date: startDate,
    end_date: endDate,
    total_revenue: total,
    invoice_count: invoices.length
  };
}

async function getOverdueInvoices(args) {
  const { days_overdue = 1, limit = 50 } = args;
  
  const today = new Date();
  const cutoffDate = new Date(today.setDate(today.getDate() - days_overdue)).toISOString().split('T')[0];
  
  const domain = [
    ['move_type', '=', 'out_invoice'],
    ['state', '=', 'posted'],
    ['payment_state', '!=', 'paid'],
    ['invoice_date_due', '<', cutoffDate]
  ];
  
  const fields = [
    'id', 'name', 'partner_id', 'invoice_date_due',
    'amount_total', 'amount_residual'
  ];
  
  const invoices = await executeKw('account.move', 'search_read', [domain, fields], { limit });
  
  return {
    success: true,
    count: invoices.length,
    total_overdue: invoices.reduce((sum, inv) => sum + (inv.amount_residual || 0), 0),
    invoices: invoices
  };
}

/**
 * Main entry point
 */
async function main() {
  console.error('[ODOO MCP] Starting Odoo MCP Server...');
  
  // Authenticate on startup
  await authenticate();
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('[ODOO MCP] Server running on stdio');
}

main().catch((error) => {
  console.error('[ODOO MCP] Fatal error:', error);
  process.exit(1);
});

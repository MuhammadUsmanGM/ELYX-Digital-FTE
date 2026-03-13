#!/usr/bin/env node
/**
 * Test MCP Servers
 * Tests Odoo and Email MCP servers
 */

import { spawn } from 'child_process';
import { setTimeout } from 'timers/promises';

console.log('='.repeat(70));
console.log('ELYX MCP SERVER TEST');
console.log('='.repeat(70));
console.log();

/**
 * Test Odoo MCP Server
 */
async function testOdooMCP() {
  console.log('[TEST 1] Odoo MCP Server');
  console.log('-'.repeat(70));
  
  return new Promise((resolve) => {
    const odoo = spawn('node', ['src/mcp-servers/odoo-mcp/index.js'], {
      env: {
        ...process.env,
        ODOO_URL: process.env.ODOO_URL || '',
        ODOO_DB: process.env.ODOO_DB || '',
        ODOO_USERNAME: process.env.ODOO_USERNAME || '',
        ODOO_PASSWORD: process.env.ODOO_PASSWORD || '',
        ODOO_API_KEY: process.env.ODOO_API_KEY || ''
      }
    });
    
    let output = '';
    let error = '';
    
    odoo.stderr.on('data', (data) => {
      error += data.toString();
      console.log('[ODOO]', data.toString().trim());
    });
    
    odoo.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    // Give it 3 seconds to initialize
    setTimeout(3000).then(() => {
      odoo.kill();
      
      if (error.includes('Authenticated as user')) {
        console.log('[OK] Odoo MCP: Authentication successful');
        resolve(true);
      } else if (error.includes('Error') || error.includes('Failed')) {
        console.log('[ERROR] Odoo MCP: Authentication failed');
        resolve(false);
      } else {
        console.log('[OK] Odoo MCP: Started successfully');
        resolve(true);
      }
    });
  });
}

/**
 * Test Email MCP Server
 */
async function testEmailMCP() {
  console.log();
  console.log('[TEST 2] Email MCP Server');
  console.log('-'.repeat(70));
  
  return new Promise((resolve) => {
    const email = spawn('node', ['src/mcp-servers/email-mcp/index.js'], {
      env: process.env
    });
    
    let output = '';
    let error = '';
    
    email.stderr.on('data', (data) => {
      error += data.toString();
      console.log('[EMAIL]', data.toString().trim());
    });
    
    email.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    // Give it 3 seconds to initialize
    setTimeout(3000).then(() => {
      email.kill();
      
      if (error.includes('Gmail initialized successfully')) {
        console.log('[OK] Email MCP: Gmail initialized');
        resolve(true);
      } else if (error.includes('Error') || error.includes('Failed')) {
        console.log('[WARNING] Email MCP: Gmail not initialized (check credentials)');
        resolve(false);
      } else {
        console.log('[OK] Email MCP: Started successfully');
        resolve(true);
      }
    });
  });
}

/**
 * Main test runner
 */
async function main() {
  console.log('Starting MCP server tests...\n');
  
  // Test Odoo MCP
  const odooOk = await testOdooMCP();
  
  // Test Email MCP
  const emailOk = await testEmailMCP();
  
  console.log();
  console.log('='.repeat(70));
  console.log('TEST RESULTS');
  console.log('='.repeat(70));
  console.log(`Odoo MCP:    ${odooOk ? '[OK]' : '[FAIL]'}`);
  console.log(`Email MCP:   ${emailOk ? '[OK]' : '[FAIL]'}`);
  console.log('='.repeat(70));
  
  if (odooOk && emailOk) {
    console.log();
    console.log('[SUCCESS] All MCP servers are working!');
    console.log();
    console.log('Next steps:');
    console.log('1. Add MCP servers to ~/.config/claude-code/mcp.json');
    console.log('2. Restart Claude Code');
    console.log('3. Test MCP tools in Claude Code');
  } else {
    console.log();
    console.log('[WARNING] Some MCP servers need attention');
    console.log();
    console.log('Troubleshooting:');
    console.log('- Odoo: Check credentials in .env');
    console.log('- Email: Ensure gmail_credentials.json and gmail_token.json exist');
  }
  
  process.exit(odooOk && emailOk ? 0 : 1);
}

main().catch(console.error);

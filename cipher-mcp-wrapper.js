#!/usr/bin/env node

/**
 * Cipher MCP Wrapper for Windows
 * 
 * This script works around Windows path and execution issues
 * by providing a clean Node.js wrapper for Cipher MCP mode
 */

const { spawn } = require('child_process');
const path = require('path');

// Set environment variables
// API key should be set in environment variables, not hardcoded
if (!process.env.OPENAI_API_KEY) {
  console.error('[CIPHER-WRAPPER] Warning: OPENAI_API_KEY not set in environment');
}
process.env.CIPHER_MEMORY_DIR = 'C:/Users/Not John Or Justin/Documents/instabids/.cipher';

console.error('[CIPHER-WRAPPER] Starting Cipher MCP server...');

// Spawn npx cipher process
const cipher = spawn('npx', ['-y', '@byterover/cipher', '--mode', 'mcp'], {
    stdio: ['inherit', 'inherit', 'inherit'],
    env: process.env,
    shell: true // This is key for Windows
});

cipher.on('error', (error) => {
    console.error('[CIPHER-WRAPPER] Error starting Cipher:', error);
    process.exit(1);
});

cipher.on('close', (code) => {
    console.error(`[CIPHER-WRAPPER] Cipher process exited with code ${code}`);
    process.exit(code);
});

// Handle termination signals
process.on('SIGINT', () => {
    console.error('[CIPHER-WRAPPER] Received SIGINT, terminating Cipher...');
    cipher.kill('SIGINT');
});

process.on('SIGTERM', () => {
    console.error('[CIPHER-WRAPPER] Received SIGTERM, terminating Cipher...');
    cipher.kill('SIGTERM');
});
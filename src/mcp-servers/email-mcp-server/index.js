const express = require('express');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(express.json());

// In Silver Tier, we use a more robust transport configuration
let transporter;

function initTransporter() {
  const credentialsPath = process.env.GMAIL_CREDENTIALS_PATH || 'gmail_credentials.json';
  
  // For Silver Tier automation, we check if credentials exist
  if (fs.existsSync(credentialsPath)) {
    const creds = JSON.parse(fs.readFileSync(credentialsPath));
    
    transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        type: 'OAuth2',
        user: process.env.EMAIL_USER,
        clientId: creds.client_id,
        clientSecret: creds.client_secret,
        refreshToken: creds.refresh_token
      }
    });
    console.log('Transporter initialized with OAuth2');
  } else if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
    // Fallback to basic auth for testing
    transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
      }
    });
    console.log('Transporter initialized with basic auth');
  } else {
    console.warn('Transporter not initialized: missing credentials');
  }
}

initTransporter();

// MCP endpoints
app.post('/send_email', async (req, res) => {
  const { to, subject, body, attachments } = req.body;

  if (!transporter) {
    return res.status(500).json({ error: 'Email service not configured' });
  }

  const mailOptions = {
    from: process.env.EMAIL_USER,
    to: to,
    subject: subject,
    text: body,
    attachments: attachments || []
  };

  try {
    const info = await transporter.sendMail(mailOptions);
    console.log('Email sent: ' + info.response);
    res.json({ success: true, messageId: info.messageId });
  } catch (error) {
    console.error('Email error:', error);
    res.status(500).json({ error: error.message });
  }
});

// For Silver Tier LinkedIn/Social automation, we add social posting placeholders
app.post('/post_linkedin', async (req, res) => {
    const { content } = req.body;
    console.log('Drafting LinkedIn Post:', content);
    // In a full Silver implementation, this would use a LinkedIn API or Playwright
    res.json({ success: true, message: 'LinkedIn post queued as draft', content });
});

app.post('/status', (req, res) => {
  res.json({ status: transporter ? 'ready' : 'not_configured', user: process.env.EMAIL_USER });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Email & Communication MCP Server running on port ${PORT}`);
});